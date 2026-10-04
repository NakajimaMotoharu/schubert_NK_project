package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupUnitStartClient;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * NK-OPS-001; OPS009; UI251; SS342/343 SSC185; PT-OPS-TXOWNER001..004. The peer gate must never
 * access the borrowed DB. Repository owner callbacks run inside its TX.
 */
@NullMarked
final class MorningCompletionChecks {
  private final BackupUnitStartClient.RetirementGate peer;
  private final BackupUnitStartClient.RetirementGate database;

  MorningCompletionChecks(
      BackupUnitStartClient.RetirementGate peer, BackupUnitStartClient.RetirementGate database) {
    this.peer = Objects.requireNonNull(peer);
    this.database = Objects.requireNonNull(database);
  }

  /** Only call between transactions; authenticate the same peer on BOTH sides of the DB read. */
  void verify() throws IOException {
    peer.verify();
    database.verify();
    peer.verify();
  }

  /** Pure owner check, also valid while the same borrowed connection has autoCommit=false. */
  MaintenanceOwnerFrame.Guard ownerGuard(MaintenanceOwnerFrame.Guard remainingBudget) {
    Objects.requireNonNull(remainingBudget);
    return () -> {
      peer.verify();
      return remainingBudget.remainingNanos();
    };
  }
}
