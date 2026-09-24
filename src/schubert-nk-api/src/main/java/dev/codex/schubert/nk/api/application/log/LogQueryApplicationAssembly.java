package dev.codex.schubert.nk.api.application.log;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.persistence.LogQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Production Log search graph. The caller owns the database and key-bearing codecs for the whole
 * receive-group lifetime. NK-ADM-001/NK-MSG-001; RD FUN-008/AUT-002/MQ-006..010;
 * UI225/232/235/241/242; SS311/312/314/323/324/332/351/352; PG256/PT-ADM-075.
 */
public final class LogQueryApplicationAssembly {
  private LogQueryApplicationAssembly() {}

  public static LogQueryApplicationService create(
      DataSource database,
      FingerprintKeyRing fingerprints,
      ResponseSnapshotCodec snapshots,
      Clock clock)
      throws NoSuchAlgorithmException {
    Objects.requireNonNull(database, "database");
    Objects.requireNonNull(fingerprints, "fingerprints");
    Objects.requireNonNull(snapshots, "snapshots");
    Objects.requireNonNull(clock, "clock");
    return new LogQueryApplicationService(
        database,
        new AuthenticationContextVerifier(new ContextHash()),
        new LogQueryRepository(),
        new JdbcInboxCoordinator(fingerprints),
        new LogReplayService(snapshots),
        clock);
  }
}
