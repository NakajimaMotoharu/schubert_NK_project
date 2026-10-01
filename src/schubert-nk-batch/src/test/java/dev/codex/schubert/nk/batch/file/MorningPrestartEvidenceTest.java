package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.time.*;
import java.util.*;
import org.junit.jupiter.api.Test;

/** ISSSTEP004..007/SSC134: literal SS343 golden vectors, independent SQL-shaped input. */
final class MorningPrestartEvidenceTest {
  static final BackupManifest MANIFEST = BackupStepFixture.manifest();
  static final BatchRun RUN = MANIFEST.run();
  static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  static final Instant END = START.plusSeconds(3);
  static final String MORNING = "a".repeat(32), BROKER = "b".repeat(32);
  static final StartupPermitRecords.Epoch EPOCH =
      new StartupPermitRecords.Epoch(
          StartupPermitRecords.State.INVALID,
          UUID.fromString("11111111-1111-1111-1111-111111111111"),
          UUID.fromString("22222222-2222-2222-2222-222222222222"),
          new MaintenanceActivation(RUN, UUID.fromString("44444444-4444-4444-4444-444444444444")),
          Optional.empty());
  static final String HEADER =
      """
      boot_id=11111111-1111-1111-1111-111111111111
      epoch_id=22222222-2222-2222-2222-222222222222
      run_id=12345678-9abc-def0-8123-456789abcdef
      cutoff_utc=2026-09-12T15:00:00.000000Z
      activation_id=44444444-4444-4444-4444-444444444444
      morning_invocation_id=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      broker_invocation_id=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
      """;
  static final List<String> IDS =
      List.of("POSTGRES", "RELEASE_BOM", "STOP_SET", "BROKER_OPS", "BACKUP_RETENTION");
  static final List<String> MAGIC = List.of("NKPG1", "NKREL1", "NKSTOP1", "NKBROKER1", "NKBRET1");

  record Input(
      MorningBackupCompletion backup,
      MorningCleanupExecution.Completion cleanup,
      MorningDatabaseSession.ExpiryObservation expiry) {}

  static Map<String, String> texts() {
    var result = new LinkedHashMap<String, String>();
    for (int i = 0; i < 5; i++)
      result.put(IDS.get(i), MAGIC.get(i) + "\n" + HEADER + "FIXTURE|" + IDS.get(i) + "\n");
    return result;
  }

  static Map<String, byte[]> bytes(Map<String, String> text) {
    var result = new LinkedHashMap<String, byte[]>();
    text.forEach((id, value) -> result.put(id, value.getBytes(StandardCharsets.UTF_8)));
    return result;
  }

  static Map<String, byte[]> gates() {
    return bytes(texts());
  }

  static BatchStepResult success(long count, long bytes) {
    return new BatchStepResult(
        BatchStepResult.Status.SUCCESS, count, count, 0, bytes, BatchStepResult.Reason.NONE);
  }

  static BatchStepResult skip(BatchStepResult.Reason reason) {
    return new BatchStepResult(BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, reason);
  }

  static BackupStepRepository.Terminal terminal(
      BatchStepAttempt handle, Instant end, BatchStepResult value) {
    String code =
        value.status() == BatchStepResult.Status.SKIPPED
            ? "ALREADY_SUCCESSFUL"
            : value.status() == BatchStepResult.Status.FAILED ? "COMMAND_FAILURE" : null;
    String summary =
        code == null
            ? null
            : code.equals("ALREADY_SUCCESSFUL")
                ? "step already successful for business date"
                : "batch command failed";
    return new BackupStepRepository.Terminal(
        handle, end, value, Optional.ofNullable(code), Optional.ofNullable(summary));
  }

  static Input input(String mode) throws Exception {
    boolean failed = mode.equals("failed"), reused = mode.equals("reused");
    Instant backupEnd = reused ? END.plusSeconds(1) : END;
    var begins =
        reused
            ? new MorningDatabaseSession.BackupBegins(
                new BatchStepAttempt(90003, RUN, BatchStep.BACKUP_DB, 2, backupEnd, true),
                new BatchStepAttempt(90004, RUN, BatchStep.BACKUP_CONFIG, 2, backupEnd, true))
            : new MorningDatabaseSession.BackupBegins(
                MANIFEST.databaseStep(), MANIFEST.configurationStep());
    var actualRows = new ArrayList<BackupStepRepository.Terminal>();
    var priorRows = new ArrayList<BackupStepRepository.Terminal>();
    int i = 0;
    for (var handle : List.of(begins.database(), begins.configuration())) {
      var result =
          (failed || mode.equals("corrupt-failed-row"))
              ? new BatchStepResult(
                  BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE)
              : reused
                  ? skip(BatchStepResult.Reason.ALREADY_SUCCESSFUL)
                  : success(i == 0 ? 1 : 2, i == 0 ? 26 : 67);
      actualRows.add(terminal(handle, backupEnd, result));
      if (reused)
        priorRows.add(
            terminal(
                i == 0 ? MANIFEST.databaseStep() : MANIFEST.configurationStep(),
                END,
                success(i == 0 ? 1 : 2, i == 0 ? 26 : 67)));
      i++;
    }
    var observation = new MorningDatabaseSession.BackupObservation(actualRows, priorRows);
    MorningDatabaseSession.Access db =
        new MorningDatabaseSession.Access() {
          public void requireUnused(BatchRun r) {
            throw new AssertionError();
          }

          public void requireConsistent(BatchRun r) {
            throw new AssertionError();
          }

          public MorningDatabaseSession.BackupBegins beginBackup(
              BatchRun r, Instant t, boolean recover) {
            throw new AssertionError();
          }

          public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
            throw new AssertionError();
          }

          public void failBackup(
              MorningDatabaseSession.BackupBegins b,
              Instant end,
              BatchStepResult d,
              BatchStepResult c) {
            assertTrue(failed);
            assertEquals(begins, b);
            assertEquals(backupEnd, end);
            assertEquals("COMMAND_FAILURE", d.reason().name());
            assertEquals(d, c);
          }

          public MorningDatabaseSession.BackupObservation observeBackup(
              MorningDatabaseSession.BackupBegins b,
              Optional<BackupManifest> manifest,
              Instant now,
              dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner) {
            assertEquals(begins, b);
            assertEquals(!failed, manifest.isPresent());
            return observation;
          }
        };
    var backup =
        MorningBackupCompletion.complete(
            failed ? MorningBackupUnitCycle.Outcome.FAILED : MorningBackupUnitCycle.Outcome.SUCCESS,
            ExpiryReceiptFixture.backupReceipt(failed ? 30 : 0, "9".repeat(32)),
            begins,
            db,
            Clock.fixed(backupEnd, ZoneOffset.UTC),
            MorningProcessMain.archive(
                () -> {
                  assertFalse(failed);
                  return MANIFEST;
                }),
            MORNING,
            () -> 10_000_000_000L);
    var cleanupRows = new ArrayList<CleanupTerminalRepository.Entry>();
    var cleanupPrior = new ArrayList<Optional<CleanupTerminalRepository.Entry>>();
    Instant cleanStart = Instant.parse("2026-09-13T02:01:00Z"),
        cleanEnd = cleanStart.plusSeconds(1);
    for (int n = 0; n < 7; n++) {
      var step = CleanupTerminalRepository.STEPS.get(n);
      boolean skip = reused || (failed && n < 6);
      var started = reused ? cleanStart.plusSeconds(2) : cleanStart;
      var handle =
          new BatchStepAttempt((reused ? 110 : 100) + n, RUN, step, reused ? 2 : 1, started, skip);
      cleanupRows.add(
          new CleanupTerminalRepository.Entry(
              handle,
              skip ? started : cleanEnd,
              skip
                  ? skip(
                      reused
                          ? BatchStepResult.Reason.ALREADY_SUCCESSFUL
                          : BatchStepResult.Reason.BACKUP_UNAVAILABLE)
                  : success(1, 10)));
      cleanupPrior.add(
          reused
              ? Optional.of(
                  new CleanupTerminalRepository.Entry(
                      new BatchStepAttempt(100 + n, RUN, step, 1, cleanStart, false),
                      cleanEnd,
                      success(1, 10)))
              : Optional.empty());
    }
    var cleanup =
        new MorningCleanupExecution.Completion(
            new CleanupTerminalRepository.Snapshot(cleanupRows),
            ExpiryReceiptFixture.cleanupReceipt(0, "c".repeat(32)),
            cleanupPrior);
    Instant expiryStart = Instant.parse("2026-09-13T02:02:00Z"),
        expiryEnd = expiryStart.plusSeconds(1);
    var original = new BatchStepAttempt(107, RUN, BatchStep.CLEAN_EXPIRY, 1, expiryStart, false);
    var audit =
        new ExpiryAuditRepository.Snapshot(
            "SUCCESS",
            RUN.cutoff().minusSeconds(7 * 86400),
            3L,
            1L,
            2,
            2,
            0,
            200,
            expiryEnd,
            null,
            null);
    var current =
        reused
            ? new BatchStepAttempt(
                108, RUN, BatchStep.CLEAN_EXPIRY, 2, expiryStart.plusSeconds(3), true)
            : original;
    var expiry =
        new MorningDatabaseSession.ExpiryObservation(
            new MorningDatabaseSession.ExpiryBegins(
                current,
                reused
                    ? Optional.of(new ExpiryAuditRepository.Prior(original, audit))
                    : Optional.empty()),
            reused ? current.startedAt() : expiryEnd,
            reused ? skip(BatchStepResult.Reason.ALREADY_SUCCESSFUL) : success(2, 200),
            audit,
            ExpiryReceiptFixture.receipt(0, "d".repeat(32)));
    return new Input(backup, cleanup, expiry);
  }

  static String encode(Input input, Optional<String> manifest, Map<String, String> frames)
      throws IOException {
    return MorningPrestartEvidence.encode(
        EPOCH, BROKER, input.backup(), input.cleanup(), input.expiry(), manifest, bytes(frames));
  }

  @Test
  void issstep007ReferenceForeignRunWarningsAndMutableGateInput() throws Exception {
    var reused = input("reused");
    var current = reused.cleanup().terminal().entries().get(0).attempt();
    var prior = reused.cleanup().references().get(0).orElseThrow();
    var foreign = new BatchRun(new UUID(0, 99), RUN.cutoff());
    for (var handle :
        List.of(
            new BatchStepAttempt(
                prior.attempt().id(), RUN, current.step(), 1, prior.attempt().startedAt(), true),
            new BatchStepAttempt(
                prior.attempt().id(),
                foreign,
                current.step(),
                1,
                prior.attempt().startedAt(),
                false),
            new BatchStepAttempt(
                prior.attempt().id(),
                RUN,
                BatchStep.CLEAN_QUESTION,
                1,
                prior.attempt().startedAt(),
                false),
            new BatchStepAttempt(
                current.id(), RUN, current.step(), 1, prior.attempt().startedAt(), false),
            new BatchStepAttempt(
                prior.attempt().id(),
                RUN,
                current.step(),
                current.attempt(),
                prior.attempt().startedAt(),
                false))) {
      var changed = new CleanupTerminalRepository.Entry(handle, prior.endedAt(), prior.result());
      var references = new ArrayList<>(reused.cleanup().references());
      references.set(0, Optional.of(changed));
      var cleanup =
          new MorningCleanupExecution.Completion(
              reused.cleanup().terminal(), reused.cleanup().receipt(), references);
      assertThrows(
          IOException.class,
          () ->
              encode(
                  new Input(reused.backup(), cleanup, reused.expiry()),
                  Optional.of("1".repeat(64)),
                  texts()));
    }
    var warning =
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 1, 0, 0, 0, BatchStepResult.Reason.PROTECTED_RECORDS);
    for (var changed :
        List.of(
            new CleanupTerminalRepository.Entry(
                prior.attempt(), current.startedAt().plusSeconds(1), prior.result()),
            new CleanupTerminalRepository.Entry(prior.attempt(), prior.endedAt(), warning))) {
      var references = new ArrayList<>(reused.cleanup().references());
      references.set(0, Optional.of(changed));
      var cleanup =
          new MorningCleanupExecution.Completion(
              reused.cleanup().terminal(), reused.cleanup().receipt(), references);
      assertThrows(
          IOException.class,
          () ->
              encode(
                  new Input(reused.backup(), cleanup, reused.expiry()),
                  Optional.of("1".repeat(64)),
                  texts()));
    }
    var missing = new ArrayList<>(reused.cleanup().references());
    missing.set(0, Optional.empty());
    var noReference =
        new MorningCleanupExecution.Completion(
            reused.cleanup().terminal(), reused.cleanup().receipt(), missing);
    assertThrows(
        IOException.class,
        () ->
            encode(
                new Input(reused.backup(), noReference, reused.expiry()),
                Optional.of("1".repeat(64)),
                texts()));
    var ordinary = input("new");
    var foreignRows = new ArrayList<CleanupTerminalRepository.Entry>();
    for (var row : ordinary.cleanup().terminal().entries())
      foreignRows.add(
          new CleanupTerminalRepository.Entry(
              new BatchStepAttempt(
                  row.attempt().id(),
                  foreign,
                  row.attempt().step(),
                  1,
                  row.attempt().startedAt(),
                  false),
              row.endedAt(),
              row.result()));
    var foreignCleanup =
        new MorningCleanupExecution.Completion(
            new CleanupTerminalRepository.Snapshot(foreignRows),
            ordinary.cleanup().receipt(),
            ordinary.cleanup().references());
    assertThrows(
        IOException.class,
        () ->
            encode(
                new Input(ordinary.backup(), foreignCleanup, ordinary.expiry()),
                Optional.empty(),
                texts()));
    var expiry = ordinary.expiry();
    var foreignExpiry =
        new MorningDatabaseSession.ExpiryObservation(
            new MorningDatabaseSession.ExpiryBegins(
                new BatchStepAttempt(
                    107,
                    foreign,
                    BatchStep.CLEAN_EXPIRY,
                    1,
                    expiry.begins().current().startedAt(),
                    false),
                Optional.empty()),
            expiry.ended(),
            expiry.result(),
            expiry.audit(),
            expiry.receipt());
    assertThrows(
        IOException.class,
        () ->
            encode(
                new Input(ordinary.backup(), ordinary.cleanup(), foreignExpiry),
                Optional.empty(),
                texts()));
    var audit =
        new ExpiryAuditRepository.Snapshot(
            "WARNING",
            RUN.cutoff().minusSeconds(7 * 86400),
            3L,
            2L,
            2,
            1,
            0,
            100,
            expiry.ended(),
            "PROTECTED_RECORDS",
            "protected records retained");
    var warnResult =
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 2, 1, 0, 100, BatchStepResult.Reason.PROTECTED_RECORDS);
    var warnExpiry =
        new MorningDatabaseSession.ExpiryObservation(
            expiry.begins(),
            expiry.ended(),
            warnResult,
            audit,
            ExpiryReceiptFixture.receipt(10, "d".repeat(32)));
    assertTrue(
        encode(
                new Input(ordinary.backup(), ordinary.cleanup(), warnExpiry),
                Optional.empty(),
                texts())
            .contains("|WARNING|2|1|0|100|PROTECTED_RECORDS|EXPIRY|" + "d".repeat(32) + "|10|-\n"));
    var wrongReceipt =
        new MorningDatabaseSession.ExpiryObservation(
            expiry.begins(), expiry.ended(), warnResult, audit, expiry.receipt());
    assertThrows(
        IOException.class,
        () ->
            encode(
                new Input(ordinary.backup(), ordinary.cleanup(), wrongReceipt),
                Optional.empty(),
                texts()));
    var controls = texts();
    controls.put("POSTGRES", controls.get("POSTGRES") + "\u007f\n");
    assertThrows(IOException.class, () -> encode(ordinary, Optional.empty(), controls));
    var original = gates();
    var encoded =
        MorningPrestartEvidence.encode(
            EPOCH,
            BROKER,
            ordinary.backup(),
            ordinary.cleanup(),
            ordinary.expiry(),
            Optional.empty(),
            original,
            () -> {
              original.values().forEach(value -> Arrays.fill(value, (byte) 'x'));
              return java.security.MessageDigest.getInstance("SHA-256");
            });
    byte[] golden;
    try (var stream =
        Objects.requireNonNull(
            getClass().getResourceAsStream("/ops/issuer-prestart-new-golden.txt"))) {
      golden = stream.readAllBytes();
    }
    assertArrayEquals(golden, encoded.getBytes(StandardCharsets.US_ASCII));
  }

  @Test
  void issstep004ThreeFullGoldenVectorsUseTrueCurrentAndSeparatePrior() throws Exception {
    for (String mode : List.of("new", "failed", "reused")) {
      var input = input(mode);
      byte[] expected;
      try (var stream =
          Objects.requireNonNull(
              getClass().getResourceAsStream("/ops/issuer-prestart-" + mode + "-golden.txt"))) {
        expected = stream.readAllBytes();
      }
      assertArrayEquals(
          expected,
          encode(
                  input,
                  mode.equals("reused") ? Optional.of("1".repeat(64)) : Optional.empty(),
                  texts())
              .getBytes(StandardCharsets.US_ASCII),
          mode);
    }
  }

  @Test
  void issstep005MissingChangedBindingOrGateCannotEncode() throws Exception {
    var input = input("new");
    var good = texts();
    // A normal-zero worker with independently corrupted FAILED SQL rows is not a valid proof.
    var corrupt = input("corrupt-failed-row");
    assertThrows(IOException.class, () -> encode(corrupt, Optional.empty(), good));
    for (String key : IDS) {
      var missing = new HashMap<>(good);
      missing.remove(key);
      assertThrows(IOException.class, () -> encode(input, Optional.empty(), missing));
      for (String frame :
          List.of(
              "WRONG\n",
              good.get(key).stripTrailing(),
              good.get(key).replace(MORNING, "f".repeat(32)),
              good.get(key) + "private\r\n",
              good.get(key) + "非ASCII\n")) {
        var changed = new HashMap<>(good);
        changed.put(key, frame);
        assertThrows(IOException.class, () -> encode(input, Optional.empty(), changed));
      }
    }
    var extra = new HashMap<>(good);
    extra.put("EXTRA", "ignored");
    assertThrows(IOException.class, () -> encode(input, Optional.empty(), extra));
    var reused = input("reused");
    assertThrows(IOException.class, () -> encode(reused, Optional.empty(), good));
    assertThrows(IOException.class, () -> encode(reused, Optional.of("A".repeat(64)), good));
    var duplicateCleanup =
        new MorningCleanupExecution.Completion(
            input.cleanup().terminal(),
            ExpiryReceiptFixture.cleanupReceipt(0, "9".repeat(32)),
            input.cleanup().references());
    assertThrows(
        IOException.class,
        () ->
            encode(
                new Input(input.backup(), duplicateCleanup, input.expiry()),
                Optional.empty(),
                good));
    var foreignEpoch =
        new StartupPermitRecords.Epoch(
            StartupPermitRecords.State.INVALID,
            EPOCH.boot(),
            EPOCH.epoch(),
            new MaintenanceActivation(
                new BatchRun(new UUID(0, 1), RUN.cutoff()), EPOCH.activation().id()),
            Optional.empty());
    assertThrows(
        IOException.class,
        () ->
            MorningPrestartEvidence.encode(
                foreignEpoch,
                BROKER,
                input.backup(),
                input.cleanup(),
                input.expiry(),
                Optional.empty(),
                bytes(good)));
  }

  @Test
  void issstep006DigestNullAndUnknownFailureNeverBecomeGateSuccess() throws Exception {
    var input = input("new");
    assertThrows(
        IOException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH,
                BROKER,
                input.backup(),
                input.cleanup(),
                input.expiry(),
                Optional.empty(),
                gates(),
                () -> {
                  throw new NoSuchAlgorithmException("unavailable");
                }));
    var unknown = new IllegalStateException("PRIVATE_CRYPTO");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningPrestartEvidence.encode(
                    EPOCH,
                    BROKER,
                    input.backup(),
                    input.cleanup(),
                    input.expiry(),
                    Optional.empty(),
                    gates(),
                    () -> {
                      throw unknown;
                    })));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH,
                BROKER,
                input.backup(),
                input.cleanup(),
                input.expiry(),
                Optional.empty(),
                gates(),
                () -> null));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH, BROKER, null, input.cleanup(), input.expiry(), Optional.empty(), gates()));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH, BROKER, input.backup(), null, input.expiry(), Optional.empty(), gates()));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH, BROKER, input.backup(), input.cleanup(), null, Optional.empty(), gates()));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH, BROKER, input.backup(), input.cleanup(), input.expiry(), null, gates()));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH,
                BROKER,
                input.backup(),
                input.cleanup(),
                input.expiry(),
                Optional.empty(),
                null));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPrestartEvidence.encode(
                EPOCH,
                BROKER,
                input.backup(),
                input.cleanup(),
                input.expiry(),
                Optional.empty(),
                gates(),
                null));
  }
}
