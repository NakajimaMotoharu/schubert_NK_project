package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.Objects;

/**
 * Production Login transaction graph for the API sync dispatcher. The caller retains ownership of
 * all key-bearing codecs and closes them only after the listener has stopped. No test substitute,
 * transaction, broker or connection is created here. NK-AUT-001/NK-MSG-002; RD AUT-001/002,
 * MQ-006..010; UI226/232/234/241; SS311/312/314/323/324/332; PT-AUT-INBOX-007..008.
 */
public final class LoginApplicationAssembly {
  private LoginApplicationAssembly() {}

  public static LoginInboxService create(
      FingerprintKeyRing fingerprints,
      AuthContextCodec contexts,
      ResponseSnapshotCodec snapshots,
      Clock clock)
      throws NoSuchAlgorithmException {
    Objects.requireNonNull(fingerprints, "fingerprints");
    Objects.requireNonNull(contexts, "contexts");
    Objects.requireNonNull(snapshots, "snapshots");
    Objects.requireNonNull(clock, "clock");
    var hashes = new ContextHash();
    return new LoginInboxService(
        new JdbcInboxCoordinator(fingerprints),
        new AuthenticationService(
            new LoginAttemptRepository(),
            new PasswordHasher(),
            new AuthSessionService(hashes, contexts),
            new LoginAuditWriter()),
        new LoginReplayService(snapshots, contexts, hashes),
        clock);
  }
}
