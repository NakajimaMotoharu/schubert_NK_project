package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.batch.repository.BackupFailureSnapshot;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * SSC124 fixed FAILED correlation, NOT deletion/lock/startup authority.
 * NK-OPS-001/NK-BAT-001/BAK001/OPS009/UI251/SS341/343; CFREQ001..006.
 */
@NullMarked
public record CleanupFailedBackupRequest(
    UUID run,
    UUID activation,
    Instant cutoff,
    UUID boot,
    UUID epoch,
    UUID backupInvocation,
    BigInteger backupStarted,
    BigInteger backupEnded,
    int backupExit,
    BackupFailureSnapshot failure)
    implements CleanupProfile {
  private static final BigInteger U64 = new BigInteger("18446744073709551615");
  private static final UUID NIL = new UUID(0, 0);
  private static final String[] KEYS = {
    "run",
    "activation",
    "cutoff",
    "boot",
    "epoch",
    "backup_invocation",
    "backup_started_monotonic",
    "backup_ended_monotonic",
    "backup_exit",
    "database",
    "configuration"
  };

  public CleanupFailedBackupRequest {
    new MaintenanceActivation(new BatchRun(run, cutoff), activation);
    Objects.requireNonNull(boot);
    Objects.requireNonNull(epoch);
    Objects.requireNonNull(backupInvocation);
    Objects.requireNonNull(backupStarted);
    Objects.requireNonNull(backupEnded);
    Objects.requireNonNull(failure);
    if (boot.equals(NIL)
        || epoch.equals(NIL)
        || backupInvocation.equals(NIL)
        || backupStarted.signum() < 1
        || backupStarted.compareTo(U64) > 0
        || backupEnded.compareTo(backupStarted) < 0
        || backupEnded.compareTo(U64) > 0
        || backupExit < 1
        || backupExit > 255
        || !failure.database().run().equals(new BatchRun(run, cutoff))) throw invalid();
  }

  public byte[] encode() {
    return ("NKCLEANFAIL1\nrun="
            + run
            + "\nactivation="
            + activation
            + "\ncutoff="
            + cutoff
            + "\nboot="
            + boot
            + "\nepoch="
            + epoch
            + "\nbackup_invocation="
            + backupInvocation
            + "\nbackup_started_monotonic="
            + backupStarted
            + "\nbackup_ended_monotonic="
            + backupEnded
            + "\nbackup_exit="
            + backupExit
            + "\ndatabase="
            + row(failure.database(), failure.endedAt())
            + "\nconfiguration="
            + row(failure.configuration(), failure.endedAt())
            + "\n")
        .getBytes(StandardCharsets.US_ASCII);
  }

  private static String row(BatchStepAttempt handle, Instant ended) {
    return handle.id()
        + ","
        + handle.attempt()
        + ","
        + handle.businessDate()
        + ","
        + handle.startedAt()
        + ","
        + ended
        + ",FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed";
  }

  public static CleanupFailedBackupRequest consume(byte[] owned) {
    Objects.requireNonNull(owned);
    byte[] canonical = new byte[0];
    try {
      if (owned.length < 1 || owned.length > CleanupProfile.MAXIMUM_BYTES) throw invalid();
      for (byte value : owned) if (value != 10 && (value < 32 || value > 126)) throw invalid();
      String[] rows = new String(owned, StandardCharsets.US_ASCII).split("\n", -1);
      if (rows.length != KEYS.length + 2
          || !rows[0].equals("NKCLEANFAIL1")
          || !rows[rows.length - 1].isEmpty()) throw invalid();
      var values = new String[KEYS.length];
      for (int i = 0; i < KEYS.length; i++) {
        if (!rows[i + 1].startsWith(KEYS[i] + "=")) throw invalid();
        values[i] = rows[i + 1].substring(KEYS[i].length() + 1);
      }
      var run = new BatchRun(UUID.fromString(values[0]), Instant.parse(values[2]));
      var db = handle(run, BatchStep.BACKUP_DB, values[9]);
      var config = handle(run, BatchStep.BACKUP_CONFIG, values[10]);
      if (!db.ended().equals(config.ended())) throw invalid();
      var result =
          new CleanupFailedBackupRequest(
              run.id(),
              UUID.fromString(values[1]),
              run.cutoff(),
              UUID.fromString(values[3]),
              UUID.fromString(values[4]),
              UUID.fromString(values[5]),
              new BigInteger(values[6]),
              new BigInteger(values[7]),
              Integer.parseInt(values[8]),
              new BackupFailureSnapshot(db.handle(), config.handle(), db.ended()));
      canonical = result.encode();
      if (!Arrays.equals(owned, canonical)) throw invalid();
      return result;
    } catch (java.time.DateTimeException | IllegalArgumentException invalid) {
      throw invalid();
    } finally {
      Arrays.fill(owned, (byte) 0);
      Arrays.fill(canonical, (byte) 0);
    }
  }

  private record Row(BatchStepAttempt handle, Instant ended) {}

  private static Row handle(BatchRun run, BatchStep step, String value) {
    String[] fields = value.split(",", -1);
    if (fields.length != 12
        || !fields[5].equals("FAILED")
        || !fields[6].equals("1")
        || !fields[7].equals("0")
        || !fields[8].equals("1")
        || !fields[9].equals("0")
        || !fields[10].equals("COMMAND_FAILURE")
        || !fields[11].equals("batch command failed")) throw invalid();
    var handle =
        new BatchStepAttempt(
            Long.parseLong(fields[0]),
            run,
            step,
            Integer.parseInt(fields[1]),
            Instant.parse(fields[3]),
            false);
    if (!handle.businessDate().toString().equals(fields[2])) throw invalid();
    return new Row(handle, Instant.parse(fields[4]));
  }

  /** Comparison data only; caller MUST supply actual kernel/manager-stable observation. */
  public boolean receiptMatches(InspectorUnitSnapshot actual) {
    Objects.requireNonNull(actual);
    return actual.isTarget(InspectorUnitSnapshot.Target.BACKUP)
        && actual.backupTerminalAfter(Optional.empty()).orElse(null)
            == MorningBackupUnitCycle.Outcome.FAILED
        && actual.invocationId().equals(Optional.of(backupInvocation))
        && actual.normalExitCode() == backupExit
        && actual.executionStart().equals(backupStarted)
        && actual.executionEnd().equals(backupEnded);
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("failed cleanup profile invalid");
  }

  @Override
  public String toString() {
    return "CleanupFailedBackupRequest[data=<redacted>]";
  }
}
