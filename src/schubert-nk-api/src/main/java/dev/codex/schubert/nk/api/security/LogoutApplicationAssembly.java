package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.Objects;

/**
 * Existing Logout transaction participants, no extra authorization or transaction. NK-AUT-001;
 * AUT004/MQ006..010; UI226234241; SS312314324; SSC149; PT-AUT-LOGOUT-ASSEMBLY-001..003. Callers
 * retain keys through listener termination.
 */
public final class LogoutApplicationAssembly {
  private LogoutApplicationAssembly() {}

  public static LogoutInboxService create(
      FingerprintKeyRing fingerprints, ResponseSnapshotCodec snapshots, Clock clock)
      throws NoSuchAlgorithmException {
    Objects.requireNonNull(fingerprints, "fingerprints");
    Objects.requireNonNull(snapshots, "snapshots");
    Objects.requireNonNull(clock, "clock");
    var hashes = new ContextHash();
    return new LogoutInboxService(
        new JdbcInboxCoordinator(fingerprints),
        new AuthSessionRevocationService(hashes),
        new LogoutReplayService(snapshots, hashes),
        hashes,
        clock);
  }
}
