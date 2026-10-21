package dev.codex.schubert.nk.api.maintenance;

import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.AuthenticationInfrastructureException;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.api.security.LoginReplayService;
import dev.codex.schubert.nk.api.security.LogoutReplayService;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only Login/Logout saved-reference inspection, not authentication or deletion permission.
 * Caller owns transaction, row locks and key lifetime; no commit, rollback, close or wire output.
 * NK-DAT-001/NK-AUT-001; OPS-009/AUT-001/004/MQ-008; UI212/232/234/241/251; SS324
 * section12.2/331/352; QA-046/SSC-049/BUG-014; PG-D-120; PT-DB-INBOX-009..016.
 */
@NullMarked
public final class AuthenticationInboxInspector {
  private final ResponseSnapshotCodec snapshots;
  private final InboxResponseInspector structure;
  private final LoginReplayService login;
  private final LogoutReplayService logout;

  public AuthenticationInboxInspector(
      ResponseSnapshotCodec snapshots, AuthContextCodec contexts, ContextHash hashes) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
    Objects.requireNonNull(contexts, "contexts");
    Objects.requireNonNull(hashes, "hashes");
    structure = new InboxResponseInspector(snapshots);
    login = new LoginReplayService(snapshots, contexts, hashes);
    logout = new LogoutReplayService(snapshots, hashes);
  }

  /**
   * False preserves an unsupported/inconsistent row. Null caller arguments violate the contract.
   */
  public boolean isConsistent(
      Connection connection, ResponseSnapshotIdentity identity, InboxCompletion completion) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(completion, "completion");
    boolean isLogin = identity.responseLayoutId().equals("LGNRSP01");
    if (!isLogin && !identity.responseLayoutId().equals("LOGRSP01")) return false;
    if (isLogin != identity.ownerUserId().isEmpty()) return false;
    if (!structure.isStructurallyValid(identity, completion)) return false;
    try {
      if (connection.getAutoCommit()) return false;
      byte[] restored;
      if (isLogin) {
        restored =
            login.restore(
                connection,
                completion,
                identity.requestMessageId(),
                identity.requestMessageId(),
                completion.completedAt(),
                false);
      } else {
        byte[] original = snapshots.decrypt(identity, completion.responseSnapshot().orElseThrow());
        try {
          var context = HeaderCodec.standard().peek(original).authenticationContext().orElseThrow();
          restored =
              logout.restore(
                  connection,
                  completion,
                  identity.ownerUserId().orElseThrow(),
                  context,
                  identity.requestMessageId(),
                  identity.requestMessageId(),
                  completion.completedAt(),
                  false);
        } finally {
          Arrays.fill(original, (byte) 0);
        }
      }
      Arrays.fill(restored, (byte) 0);
      return true;
    } catch (SQLException
        | AuthenticationInfrastructureException
        | ResponseSnapshotException
        | IllegalStateException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      return false;
    }
  }
}
