package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.time.format.DateTimeFormatterBuilder;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/** SSC108/134: ten actual step rows and five actual gate frames; data only, not issue authority. */
@NullMarked
final class MorningPrestartEvidence {
  static final List<String> GATES =
      List.of("POSTGRES", "RELEASE_BOM", "STOP_SET", "BROKER_OPS", "BACKUP_RETENTION");
  private static final List<String> MAGIC =
      List.of("NKPG1", "NKREL1", "NKSTOP1", "NKBROKER1", "NKBRET1");

  private MorningPrestartEvidence() {}

  static String encode(
      StartupPermitRecords.Epoch epoch,
      String broker,
      MorningBackupCompletion backup,
      MorningCleanupExecution.Completion cleanup,
      MorningDatabaseSession.ExpiryObservation expiry,
      Optional<String> manifestSha,
      Map<String, byte[]> gateFrames)
      throws IOException {
    return encode(
        epoch,
        broker,
        backup,
        cleanup,
        expiry,
        manifestSha,
        gateFrames,
        () -> MessageDigest.getInstance("SHA-256"));
  }

  static String encode(
      StartupPermitRecords.Epoch epoch,
      String broker,
      MorningBackupCompletion backup,
      MorningCleanupExecution.Completion cleanup,
      MorningDatabaseSession.ExpiryObservation expiry,
      Optional<String> manifestSha,
      Map<String, byte[]> gateFrames,
      StartupPermitRecords.DigestFactory digest)
      throws IOException {
    Objects.requireNonNull(digest);
    Objects.requireNonNull(backup);
    Objects.requireNonNull(cleanup);
    Objects.requireNonNull(expiry);
    Objects.requireNonNull(manifestSha);
    var gates = new HashMap<String, byte[]>();
    Map.copyOf(gateFrames).forEach((id, frame) -> gates.put(id, frame.clone()));
    var text = MorningGateEvidence.header("NKPRESTART2", epoch, backup.morning(), broker);
    require(gates.keySet().equals(Set.copyOf(GATES)));
    var producers = new HashSet<String>();
    for (String value :
        List.of(
            backup.morning(),
            broker,
            invocation(backup.receipt()),
            invocation(cleanup.receipt()),
            invocation(expiry.receipt()))) require(producers.add(value));
    var run = epoch.activation().run();
    var rows = backup.rows();
    require(rows.prior().isEmpty() || manifestSha.isPresent());
    for (int index = 0; index < 2; index++) {
      var row = rows.current().get(index);
      require(row.attempt().run().equals(run));
      require(
          (backup.receipt().exitCode() == 0)
              == (row.result().status() != BatchStepResult.Status.FAILED));
      Optional<String> prior = Optional.empty();
      if (!rows.prior().isEmpty()) {
        var original = rows.prior().get(index);
        prior =
            Optional.of(
                reference(
                    row.attempt(),
                    original.attempt(),
                    original.ended(),
                    original.result(),
                    checkedHash(manifestSha.orElseThrow())));
      }
      step(
          text,
          row.attempt(),
          row.ended(),
          row.result(),
          index == 0 ? "BACKUP" : "CONFIG",
          index == 0 ? invocation(backup.receipt()) : backup.morning(),
          index == 0 ? backup.receipt().exitCode() : backup.localExitCode(),
          prior);
    }
    for (int index = 0; index < CleanupTerminalRepository.STEPS.size(); index++) {
      var row = cleanup.terminal().entries().get(index);
      require(row.attempt().run().equals(run));
      var original = cleanup.references().get(index);
      var prior =
          original.isPresent()
              ? Optional.of(
                  reference(
                      row.attempt(),
                      original.orElseThrow().attempt(),
                      original.orElseThrow().endedAt(),
                      original.orElseThrow().result(),
                      "-"))
              : Optional.<String>empty();
      step(
          text,
          row.attempt(),
          row.endedAt(),
          row.result(),
          "CLEANUP",
          invocation(cleanup.receipt()),
          cleanup.receipt().exitCode(),
          prior);
    }
    require(expiry.begins().current().run().equals(run));
    require(
        expiry.receipt().exitCode()
            == (expiry.result().status() == BatchStepResult.Status.WARNING ? 10 : 0));
    var originalExpiry = expiry.begins().prior();
    var expiryReference =
        originalExpiry.isPresent()
            ? Optional.of(
                reference(
                    expiry.begins().current(),
                    originalExpiry.orElseThrow().handle(),
                    Objects.requireNonNull(originalExpiry.orElseThrow().audit().ended()),
                    new BatchStepResult(
                        BatchStepResult.Status.SUCCESS,
                        originalExpiry.orElseThrow().audit().target(),
                        originalExpiry.orElseThrow().audit().success(),
                        originalExpiry.orElseThrow().audit().failure(),
                        originalExpiry.orElseThrow().audit().estimatedBytes(),
                        BatchStepResult.Reason.NONE),
                    "-"))
            : Optional.<String>empty();
    step(
        text,
        expiry.begins().current(),
        expiry.ended(),
        expiry.result(),
        "EXPIRY",
        invocation(expiry.receipt()),
        expiry.receipt().exitCode(),
        expiryReference);
    for (int index = 0; index < GATES.size(); index++) {
      byte[] snapshot = Objects.requireNonNull(gates.get(GATES.get(index)), "actual gate frame");
      String frame = new String(snapshot, StandardCharsets.US_ASCII);
      require(
          frame.startsWith(
                  MorningGateEvidence.header(MAGIC.get(index), epoch, backup.morning(), broker)
                      .toString())
              && frame.endsWith("\n"));
      for (int position = 0; position < snapshot.length; position++) {
        byte value = snapshot[position];
        require(value == '\n' || (value >= 32 && value <= 126));
      }
      text.append("GATE|")
          .append(GATES.get(index))
          .append("|SUCCESS|")
          .append(sha(snapshot, digest))
          .append('\n');
    }
    // Ten closed rows (IDs<=12 digits, attempts<=2, UTC year<=9999, counts<=19) and five
    // 64-hex digests have a fixed upper bound below 8192 bytes, hence below the SS 65536 limit.
    return text.toString();
  }

  private static void step(
      StringBuilder text,
      BatchStepAttempt handle,
      Instant ended,
      BatchStepResult result,
      String producer,
      String invocation,
      int receipt,
      Optional<String> reference)
      throws IOException {
    require(
        (result.reason() == BatchStepResult.Reason.ALREADY_SUCCESSFUL) == reference.isPresent());
    text.append(handle.step())
        .append('|')
        .append(handle.id())
        .append('|')
        .append(handle.attempt())
        .append('|')
        .append(time(handle.startedAt()))
        .append('|')
        .append(time(ended))
        .append('|')
        .append(result.status())
        .append('|')
        .append(result.target())
        .append('|')
        .append(result.success())
        .append('|')
        .append(result.failure())
        .append('|')
        .append(result.bytes())
        .append('|')
        .append(result.reason())
        .append('|')
        .append(producer)
        .append('|')
        .append(invocation)
        .append('|')
        .append(receipt)
        .append('|')
        .append(reference.orElse("-"))
        .append('\n');
  }

  private static String reference(
      BatchStepAttempt current,
      BatchStepAttempt handle,
      Instant ended,
      BatchStepResult result,
      String artifact)
      throws IOException {
    require(result.status() == BatchStepResult.Status.SUCCESS);
    require(
        !handle.skipped()
            && handle.businessDate().equals(current.businessDate())
            && handle.step() == current.step()
            && handle.id() != current.id()
            && handle.attempt() < current.attempt()
            && !ended.isAfter(current.startedAt()));
    return handle.run().id()
        + ","
        + time(handle.run().cutoff())
        + ","
        + handle.id()
        + ","
        + handle.attempt()
        + ","
        + time(handle.startedAt())
        + ","
        + time(ended)
        + ",SUCCESS,"
        + result.target()
        + ","
        + result.success()
        + ","
        + result.failure()
        + ","
        + result.bytes()
        + ",NONE,"
        + artifact;
  }

  private static String invocation(BackupUnitReceiptGate.TerminalReceipt receipt) {
    return receipt.invocation().toString().replace("-", "");
  }

  private static String time(Instant value) {
    return new DateTimeFormatterBuilder().appendInstant(6).toFormatter().format(value);
  }

  private static String checkedHash(String value) throws IOException {
    require(value.matches("[0-9a-f]{64}"));
    return value;
  }

  private static String sha(byte[] frame, StartupPermitRecords.DigestFactory factory)
      throws IOException {
    try {
      return HexFormat.of()
          .formatHex(Objects.requireNonNull(factory.create(), "SHA-256 instance").digest(frame));
    } catch (NoSuchAlgorithmException unavailable) {
      StorageIoException.preserveFatal(unavailable);
      throw new IOException("prestart digest unavailable");
    }
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw new IOException("actual prestart evidence unavailable");
  }
}
