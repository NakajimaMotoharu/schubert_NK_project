package dev.codex.schubert.nk.api.application.scenario;

import dev.codex.schubert.nk.api.file.ScenarioFileInspector;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.persistence.ScenarioRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Production Scenario dependency graph, without opening or admitting a storage root. The caller
 * owns the database, codecs and file capabilities. Never register this processor in a receive group
 * before exclusive full-root admission, probe and complete usage scan. NK-SCN-001; RD
 * FUN-003..005/AUT-001..004/MQ-006..010/FIL-001..009; UI232/234/237/241;
 * SS311/312/314/323/324/332/333/342; PG258/PT-SCN-009-T08.
 */
public final class ScenarioApplicationAssembly {
  private ScenarioApplicationAssembly() {}

  public static ScenarioApplicationService create(
      DataSource database,
      FingerprintKeyRing fingerprints,
      ResponseSnapshotCodec snapshots,
      ScenarioFilePublisher publisher,
      ScenarioFileInspector inspector,
      Clock clock)
      throws NoSuchAlgorithmException {
    Objects.requireNonNull(database, "database");
    Objects.requireNonNull(fingerprints, "fingerprints");
    Objects.requireNonNull(snapshots, "snapshots");
    Objects.requireNonNull(publisher, "publisher");
    Objects.requireNonNull(inspector, "inspector");
    Objects.requireNonNull(clock, "clock");
    return new ScenarioApplicationService(
        database,
        new AuthenticationContextVerifier(new ContextHash()),
        new ScenarioRepository(),
        new JdbcInboxCoordinator(fingerprints),
        new ScenarioReplayService(snapshots),
        publisher,
        inspector,
        clock);
  }
}
