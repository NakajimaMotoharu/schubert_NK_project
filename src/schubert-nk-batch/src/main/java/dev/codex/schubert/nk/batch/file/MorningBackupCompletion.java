package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate;
import dev.codex.schubert.nk.batch.platform.BackupUnitStartClient;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/** Actual parent bundle completion/rejection, not Outcome-to-receipt conversion. SSC134/ISSCOMP. */
@NullMarked
final class MorningBackupCompletion {
  private final long thread = Thread.currentThread().threadId();
  private final MorningDatabaseSession.Access database;
  private final MorningDatabaseSession.BackupBegins begins;
  private final Optional<BackupManifest> manifest;
  private final MaintenanceOwnerFrame.Guard owner;
  private final Clock clock;
  private final String retainedMorning;
  private final BackupUnitReceiptGate.TerminalReceipt retainedReceipt;
  private final MorningDatabaseSession.BackupObservation retainedRows;

  private MorningBackupCompletion(
      MorningDatabaseSession.Access database,
      MorningDatabaseSession.BackupBegins begins,
      Optional<BackupManifest> manifest,
      MaintenanceOwnerFrame.Guard owner,
      Clock clock,
      String morning,
      BackupUnitReceiptGate.TerminalReceipt receipt,
      MorningDatabaseSession.BackupObservation rows) {
    this.database = database;
    this.begins = begins;
    this.manifest = manifest;
    this.owner = owner;
    this.clock = clock;
    this.retainedMorning = morning;
    this.retainedReceipt = receipt;
    this.retainedRows = rows;
  }

  static MorningBackupCompletion complete(
      MorningBackupUnitCycle.Outcome outcome,
      BackupUnitReceiptGate.TerminalReceipt receipt,
      MorningDatabaseSession.BackupBegins begins,
      MorningDatabaseSession.Access database,
      Clock clock,
      MorningProcessMain.Archive archive,
      String morning,
      MaintenanceOwnerFrame.Guard owner)
      throws IOException {
    Objects.requireNonNull(outcome);
    Objects.requireNonNull(receipt);
    Objects.requireNonNull(begins);
    Objects.requireNonNull(database);
    Objects.requireNonNull(clock);
    Objects.requireNonNull(archive);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(owner);
    owner.check();
    if (!morning.matches("[0-9a-f]{32}")
        || morning.equals("0".repeat(32))
        || morning.equals(receipt.invocation().toString().replace("-", ""))
        || receipt.target() != BackupUnitStartClient.Target.BACKUP
        || (outcome == MorningBackupUnitCycle.Outcome.SUCCESS) != (receipt.exitCode() == 0))
      throw new IOException("actual parent completion binding unavailable");
    // On genuine non-zero this is the real parent rejection operation: it checks/commits the
    // begun bundle's known failure without invoking archive publication. UNKNOWN never arrives.
    MorningProcessMain.completeObservedBackup(outcome, begins, database, clock, archive);
    var actual =
        outcome == MorningBackupUnitCycle.Outcome.SUCCESS
            ? Optional.of(Objects.requireNonNull(archive.verifiedManifest()))
            : Optional.<BackupManifest>empty();
    var rows = database.observeBackup(begins, actual, now(clock), owner);
    owner.check();
    return new MorningBackupCompletion(
        database, begins, actual, owner, clock, morning, receipt, rows);
  }

  void recheck() throws IOException {
    if (Thread.currentThread().threadId() != thread)
      throw new IOException("parent completion owner unavailable");
    owner.check();
    if (!retainedRows.equals(database.observeBackup(begins, manifest, now(clock), owner)))
      throw new IOException("parent completion content changed");
    owner.check();
  }

  MorningDatabaseSession.BackupObservation rows() {
    return retainedRows;
  }

  BackupUnitReceiptGate.TerminalReceipt receipt() {
    return retainedReceipt;
  }

  String morning() {
    return retainedMorning;
  }

  /**
   * Only a normally returned real operation constructs this object; business status is separate.
   */
  int localExitCode() {
    return 0;
  }

  private static Instant now(Clock clock) {
    return Objects.requireNonNull(clock.instant(), "actual parent completion time")
        .truncatedTo(ChronoUnit.MICROS);
  }

  @Override
  public String toString() {
    return "MorningBackupCompletion[actual=<redacted>]";
  }
}
