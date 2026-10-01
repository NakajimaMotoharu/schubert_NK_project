package dev.codex.schubert.nk.api.application.admin;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.persistence.UserQueryRepository;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator;
import dev.codex.schubert.nk.api.security.AuthSessionRevocationService;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.api.security.PasswordHasher;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Existing ADMIN/current-auth/Inbox/User/Password/Revocation/audit participants. Caller owns
 * database and codecs until consumers stop. No synthetic authentication, ready or transaction.
 * NK-ADM-001; FUN009/AUT002003/MQ006..010/MON004; UI225226232236241242;
 * SS312314324332342343351352/SSC150; PT-ADM-ASSEMBLY-001..003.
 */
public final class UserApplicationAssembly {
  private UserApplicationAssembly() {}

  public static UserQueryApplicationService queries(
      DataSource database,
      FingerprintKeyRing fingerprints,
      ResponseSnapshotCodec snapshots,
      Clock clock)
      throws NoSuchAlgorithmException {
    require(database, fingerprints, snapshots, clock);
    return new UserQueryApplicationService(
        database,
        new AuthenticationContextVerifier(new ContextHash()),
        new UserQueryRepository(),
        new JdbcInboxCoordinator(fingerprints),
        new UserQueryReplayService(snapshots),
        clock);
  }

  public static UserMutationApplicationService mutations(
      DataSource database,
      FingerprintKeyRing fingerprints,
      ResponseSnapshotCodec snapshots,
      Clock clock)
      throws NoSuchAlgorithmException {
    require(database, fingerprints, snapshots, clock);
    var hashes = new ContextHash();
    return new UserMutationApplicationService(
        database,
        new AdminCommandAuthenticator(hashes),
        new JdbcInboxCoordinator(fingerprints),
        new UserCommandService(new PasswordHasher(), new AuthSessionRevocationService(hashes)),
        new UserMutationReplayService(snapshots),
        clock);
  }

  private static void require(
      DataSource database,
      FingerprintKeyRing fingerprints,
      ResponseSnapshotCodec snapshots,
      Clock clock) {
    Objects.requireNonNull(database, "database");
    Objects.requireNonNull(fingerprints, "fingerprints");
    Objects.requireNonNull(snapshots, "snapshots");
    Objects.requireNonNull(clock, "clock");
  }
}
