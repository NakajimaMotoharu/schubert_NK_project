package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.platform.StoppedBackupFixture;
import dev.codex.schubert.nk.batch.repository.BackupStepRepository;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository;
import dev.codex.schubert.nk.batch.repository.ExpiryAuditRepository;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.batch.repository.SuccessRunLookup;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PARENT455001/002 actual-data envelope, independent literal outcomes and full-row reread. */
final class MorningCompletionEvidenceTest {
  static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-13T02:03:00.123456789Z"), ZoneOffset.UTC);

  static MorningCompletionEvidence fixture(String mode) throws Exception {
    var input = MorningPrestartEvidenceTest.input(mode);
    var rows = input.backup().rows();
    var stopped = new StoppedBackupFixture(mode.equals("failed") ? 30 : 0, true);
    return new MorningCompletionEvidence(
        mode.equals("failed")
            ? MorningBackupUnitCycle.Outcome.FAILED
            : MorningBackupUnitCycle.Outcome.SUCCESS,
        new MorningDatabaseSession.BackupBegins(
            rows.current().get(0).attempt(), rows.current().get(1).attempt()),
        mode.equals("failed")
            ? Optional.empty()
            : Optional.of(MorningPrestartEvidenceTest.MANIFEST),
        rows,
        stopped.receipt,
        stopped.cycle,
        input.cleanup(),
        input.expiry());
  }

  @Test
  void parent455001BackupFailureIsWarningNotAnAbsoluteGate() throws Exception {
    for (String mode : List.of("new", "reused", "failed")) {
      var f = fixture(mode);
      var result = f.completion(MorningPrestartEvidenceTest.EPOCH.activation(), CLOCK);
      assertEquals(
          mode.equals("failed")
              ? MaintenanceCompletion.Outcome.WARNING
              : MaintenanceCompletion.Outcome.SUCCESS,
          result.outcome());
      assertEquals(Instant.parse("2026-09-13T02:03:00.123456Z"), result.endedAt());
      assertEquals(MorningPrestartEvidenceTest.EPOCH.activation(), result.activation());
      assertEquals("MorningCompletionEvidence[actual=<redacted>]", f.toString());
    }
    var f = fixture("new");
    assertThrows(IOException.class, () -> f.completion(MorningCompletedMainTest.ACTIVATION, CLOCK));
    assertThrows(
        IOException.class,
        () ->
            f.completion(
                MorningPrestartEvidenceTest.EPOCH.activation(),
                Clock.fixed(MorningPrestartEvidenceTest.START.minusSeconds(1), ZoneOffset.UTC)));
  }

  @Test
  void parent455002FreshFullDatabaseAndReceiptsAreRequired() throws Exception {
    for (String mode : List.of("new", "reused", "failed")) {
      var f = fixture(mode);
      var events = new ArrayList<String>();
      MorningDatabaseSession.Access db = database(f, events, "");
      f.verify(
          db,
          CLOCK,
          () -> {
            events.add("owner");
            return 10_000_000_000L;
          });
      assertEquals(
          List.of(
              "owner",
              "recheckConsistent",
              "owner",
              "observeBackup",
              "owner",
              "owner",
              mode.equals("failed") ? "observeCleanupBackupUnavailable" : "observeCleanup",
              "owner",
              "owner",
              "cleanupReferences",
              "owner",
              "owner",
              "recheckExpiry",
              "owner",
              "recheckConsistent",
              "owner"),
          events);
      for (String failed :
          List.of(
              "recheckConsistent",
              "observeBackup",
              "observeCleanup",
              "cleanupReferences",
              "recheckExpiry")) {
        if (mode.equals("failed") && failed.equals("observeCleanup")) continue;
        assertThrows(
            IOException.class,
            () -> f.verify(database(f, new ArrayList<>(), failed), CLOCK, () -> 10_000_000_000L));
      }
    }
  }

  static MorningDatabaseSession.Access database(
      MorningCompletionEvidence f, List<String> events, String fault) {
    return (MorningDatabaseSession.Access)
        Proxy.newProxyInstance(
            MorningCompletionEvidenceTest.class.getClassLoader(),
            new Class<?>[] {MorningDatabaseSession.Access.class},
            (proxy, method, args) -> {
              String name = method.getName();
              events.add(name);
              if (name.equals(fault)) throw new IOException("fixed DB fault");
              return switch (name) {
                case "recheckConsistent" -> {
                  assertEquals(MorningPrestartEvidenceTest.RUN, args[0]);
                  yield null;
                }
                case "observeBackup" -> {
                  assertEquals(f.begins(), args[0]);
                  assertEquals(f.manifest(), args[1]);
                  assertEquals(Instant.parse("2026-09-13T02:03:00.123456Z"), args[2]);
                  yield f.backup();
                }
                case "observeCleanup", "observeCleanupBackupUnavailable" -> {
                  assertEquals(MorningPrestartEvidenceTest.RUN, args[0]);
                  yield f.cleanup().terminal();
                }
                case "cleanupReferences" -> {
                  assertEquals(f.cleanup().terminal(), args[0]);
                  yield f.cleanup().references();
                }
                case "recheckExpiry" -> {
                  assertEquals(f.expiry(), args[0]);
                  yield null;
                }
                default -> throw new AssertionError("unexpected DB operation " + name);
              };
            });
  }

  /** COMP203002: all eight independent compound boundaries are mandatory, never cached. */
  @Test
  void comp203002ChangedCompoundBoundaryRefusesBeforeOrAfterItsDatabaseRead() throws Exception {
    var reads = List.of("observeBackup", "observeCleanup", "cleanupReferences", "recheckExpiry");
    for (int failAt = 0; failAt <= 8; failAt++) {
      var f = fixture("new");
      var events = new ArrayList<String>();
      var calls = new java.util.concurrent.atomic.AtomicInteger();
      var failure = new IOException("independent peer/graph changed");
      int refused = failAt;
      dev.codex.schubert.nk.batch.platform.BackupUnitStartClient.RetirementGate boundary =
          () -> {
            int call = calls.incrementAndGet();
            events.add("boundary" + call);
            if (call == refused) throw failure;
          };
      var db = database(f, events, "");
      if (failAt == 0) {
        f.verify(
            db,
            CLOCK,
            () -> 10_000_000_000L,
            (id, at) -> MorningPrestartEvidenceTest.RUN,
            boundary);
        assertEquals(8, calls.get());
        for (int i = 0; i < 4; i++) {
          int before = events.indexOf("boundary" + (2 * i + 1));
          int read = events.indexOf(reads.get(i));
          int after = events.indexOf("boundary" + (2 * i + 2));
          assertTrue(before < read && read < after);
        }
      } else {
        assertSame(
            failure,
            assertThrows(
                IOException.class,
                () ->
                    f.verify(
                        db,
                        CLOCK,
                        () -> 10_000_000_000L,
                        (id, at) -> MorningPrestartEvidenceTest.RUN,
                        boundary)));
        assertEquals(failAt, calls.get());
        assertEquals(failAt / 2, events.stream().filter(reads::contains).count());
        assertEquals("boundary" + failAt, events.getLast());
      }
    }
    var f = fixture("new");
    assertThrows(
        NullPointerException.class,
        () ->
            f.verify(
                database(f, new ArrayList<>(), ""),
                CLOCK,
                () -> 10_000_000_000L,
                (id, at) -> MorningPrestartEvidenceTest.RUN,
                null));
  }

  @Test
  void parent539001BeginsAndTargetAndOutcomeMustMatchTheActualPair() throws Exception {
    var f = fixture("new");
    var otherRun =
        new BatchRun(
            UUID.fromString("87654321-9abc-def0-8123-456789abcdef"),
            f.begins().database().run().cutoff());
    var database = f.begins().database();
    var config = f.begins().configuration();
    var foreign =
        new BatchStepAttempt(
            config.id(),
            otherRun,
            config.step(),
            config.attempt(),
            config.startedAt(),
            config.skipped());
    for (var begins :
        List.of(
            new MorningDatabaseSession.BackupBegins(database, foreign),
            new MorningDatabaseSession.BackupBegins(
                new BatchStepAttempt(
                    91000,
                    database.run(),
                    database.step(),
                    database.attempt(),
                    database.startedAt(),
                    database.skipped()),
                config),
            new MorningDatabaseSession.BackupBegins(
                database,
                new BatchStepAttempt(
                    91001,
                    config.run(),
                    config.step(),
                    config.attempt(),
                    config.startedAt(),
                    config.skipped())))) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new MorningCompletionEvidence(
                  f.backupOutcome(),
                  begins,
                  f.manifest(),
                  f.backup(),
                  f.backupReceipt(),
                  f.backupCycle(),
                  f.cleanup(),
                  f.expiry()));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCompletionEvidence(
                f.backupOutcome(),
                f.begins(),
                f.manifest(),
                f.backup(),
                f.expiry().receipt(),
                f.backupCycle(),
                f.cleanup(),
                f.expiry()));
    var failedReceipt = new StoppedBackupFixture(30, true);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCompletionEvidence(
                f.backupOutcome(),
                f.begins(),
                f.manifest(),
                f.backup(),
                failedReceipt.receipt,
                f.backupCycle(),
                f.cleanup(),
                f.expiry()));
  }

  @Test
  void parent539002WarningCompletionAndActualStepTimeBoundariesAreIndependent() throws Exception {
    var f = fixture("new");
    for (String time : List.of("2026-09-13T02:00:30Z", "2026-09-13T02:01:30Z")) {
      var error =
          assertThrows(
              IOException.class,
              () ->
                  f.completion(
                      MorningPrestartEvidenceTest.EPOCH.activation(),
                      Clock.fixed(Instant.parse(time), ZoneOffset.UTC)));
      assertEquals("Morning completion evidence unavailable", error.getMessage());
      assertNull(error.getCause());
    }
    var rows = new ArrayList<>(f.cleanup().terminal().entries());
    var first = rows.getFirst();
    rows.set(
        0,
        new CleanupTerminalRepository.Entry(
            first.attempt(),
            first.endedAt(),
            new BatchStepResult(
                BatchStepResult.Status.WARNING,
                2,
                1,
                1,
                10,
                BatchStepResult.Reason.PROTECTED_RECORDS)));
    var cleanup =
        new MorningCleanupExecution.Completion(
            new CleanupTerminalRepository.Snapshot(rows),
            ExpiryReceiptFixture.cleanupReceipt(10, "c".repeat(32)),
            f.cleanup().references());
    var warning =
        new MorningCompletionEvidence(
            f.backupOutcome(),
            f.begins(),
            f.manifest(),
            f.backup(),
            f.backupReceipt(),
            f.backupCycle(),
            cleanup,
            f.expiry());
    assertEquals(
        MaintenanceCompletion.Outcome.WARNING,
        warning.completion(MorningPrestartEvidenceTest.EPOCH.activation(), CLOCK).outcome());
    var expiry =
        expiry(f, BatchStepResult.Status.WARNING, BatchStepResult.Reason.PROTECTED_RECORDS, 10);
    var expiryWarning =
        new MorningCompletionEvidence(
            f.backupOutcome(),
            f.begins(),
            f.manifest(),
            f.backup(),
            f.backupReceipt(),
            f.backupCycle(),
            f.cleanup(),
            expiry);
    assertEquals(
        MaintenanceCompletion.Outcome.WARNING,
        expiryWarning.completion(MorningPrestartEvidenceTest.EPOCH.activation(), CLOCK).outcome());
    for (var invalid :
        List.of(
            expiry(f, BatchStepResult.Status.WARNING, BatchStepResult.Reason.PROTECTED_RECORDS, 0),
            expiry(f, BatchStepResult.Status.SUCCESS, BatchStepResult.Reason.NONE, 10),
            expiry(f, BatchStepResult.Status.FAILED, BatchStepResult.Reason.COMMAND_FAILURE, 30))) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new MorningCompletionEvidence(
                  f.backupOutcome(),
                  f.begins(),
                  f.manifest(),
                  f.backup(),
                  f.backupReceipt(),
                  f.backupCycle(),
                  f.cleanup(),
                  invalid));
    }
  }

  private static MorningDatabaseSession.ExpiryObservation expiry(
      MorningCompletionEvidence f,
      BatchStepResult.Status status,
      BatchStepResult.Reason reason,
      int code)
      throws Exception {
    long success = status == BatchStepResult.Status.SUCCESS ? 2 : 1;
    long failure = status == BatchStepResult.Status.SUCCESS ? 0 : 1;
    var result = new BatchStepResult(status, 2, success, failure, 200, reason);
    var audit =
        new ExpiryAuditRepository.Snapshot(
            status.name(),
            Instant.parse("2026-09-05T15:00:00Z"),
            3L,
            1L,
            2,
            success,
            failure,
            200,
            Instant.parse("2026-09-13T02:02:01Z"),
            reason.code(),
            reason.summary());
    return new MorningDatabaseSession.ExpiryObservation(
        f.expiry().begins(),
        Instant.parse("2026-09-13T02:02:01Z"),
        result,
        audit,
        ExpiryReceiptFixture.receipt(code, "d".repeat(32)));
  }

  @Test
  void parent539003DefaultOriginalLookupAcceptsOnlyTheExactRetainedRun() throws Exception {
    var f = fixture("new");
    var events = new ArrayList<String>();
    var delegate = database(f, events, "");
    var lookups = new java.util.concurrent.atomic.AtomicInteger();
    var db =
        (MorningDatabaseSession.Access)
            Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {MorningDatabaseSession.Access.class},
                (proxy, method, args) -> {
                  if (method.getName().equals("cleanupReferences")) {
                    var lookup = (SuccessRunLookup) args[2];
                    assertEquals(
                        MorningPrestartEvidenceTest.RUN,
                        lookup.resolve(
                            UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
                            Instant.parse("2026-09-13T02:03:00.123456Z")));
                    var rejected =
                        assertThrows(
                            IOException.class,
                            () ->
                                lookup.resolve(
                                    UUID.fromString("87654321-9abc-def0-8123-456789abcdef"),
                                    Instant.parse("2026-09-13T02:03:00.123456Z")));
                    assertEquals("Morning completion evidence unavailable", rejected.getMessage());
                    assertNull(rejected.getCause());
                    lookups.addAndGet(2);
                  }
                  try {
                    return method.invoke(delegate, args);
                  } catch (java.lang.reflect.InvocationTargetException failure) {
                    throw failure.getCause();
                  }
                });
    f.verify(db, CLOCK, () -> 10_000_000_000L);
    assertEquals(2, lookups.get());
    assertEquals(1, Collections.frequency(events, "cleanupReferences"));
  }

  @Test
  void parent455004MismatchedManifestReceiptAndNullContractReject() throws Exception {
    var f = fixture("new");
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCompletionEvidence(
                MorningBackupUnitCycle.Outcome.FAILED,
                f.begins(),
                f.manifest(),
                f.backup(),
                f.backupReceipt(),
                f.backupCycle(),
                f.cleanup(),
                f.expiry()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCompletionEvidence(
                f.backupOutcome(),
                f.begins(),
                Optional.empty(),
                f.backup(),
                f.backupReceipt(),
                f.backupCycle(),
                f.cleanup(),
                f.expiry()));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningCompletionEvidence(
                null,
                f.begins(),
                f.manifest(),
                f.backup(),
                f.backupReceipt(),
                f.backupCycle(),
                f.cleanup(),
                f.expiry()));
    assertThrows(NullPointerException.class, () -> f.verify(null, CLOCK, () -> 10_000_000_000L));
    assertThrows(
        NullPointerException.class,
        () -> f.verify(database(f, new ArrayList<>(), ""), null, () -> 10_000_000_000L));
    assertThrows(
        NullPointerException.class,
        () -> f.verify(database(f, new ArrayList<>(), ""), CLOCK, null));
    assertThrows(NullPointerException.class, () -> f.completion(null, CLOCK));
    assertThrows(
        NullPointerException.class,
        () -> f.completion(MorningPrestartEvidenceTest.EPOCH.activation(), null));
  }

  /** SSC218/PARENT540001: envelope admission, not upstream invalid record fabrication. */
  @Test
  void parent540001BackupOutcomeRequiresTheActualStatusAndFixedFailureReason() throws Exception {
    var success = fixture("new");
    var failure = fixture("failed");
    rejected(failure, success.backup(), failure.cleanup(), failure.expiry());
    for (var status : List.of(BatchStepResult.Status.FAILED, BatchStepResult.Status.WARNING)) {
      var rows = new ArrayList<BackupStepRepository.Terminal>();
      for (var old : success.backup().current()) {
        rows.add(
            new BackupStepRepository.Terminal(
                old.attempt(),
                old.ended(),
                new BatchStepResult(status, 1, 0, 1, 0, BatchStepResult.Reason.IO_FAILURE),
                Optional.of("IO_FAILURE"),
                Optional.of("batch file operation failed")));
      }
      var observation = new MorningDatabaseSession.BackupObservation(rows, List.of());
      // Failed Backup must be COMMAND_FAILURE; successful Backup cannot be WARNING.
      var envelope = status == BatchStepResult.Status.FAILED ? failure : success;
      rejected(envelope, observation, envelope.cleanup(), envelope.expiry());
    }
  }

  @Test
  void parent540002ForeignBackupPairIsRejectedAndUpstreamPairIsImmutable() throws Exception {
    var f = fixture("new");
    var foreign =
        new BatchRun(
            UUID.fromString("87654321-9abc-def0-8123-456789abcdef"),
            Instant.parse("2026-09-12T15:00:00Z"));
    var rows = new ArrayList<BackupStepRepository.Terminal>();
    for (var old : f.backup().current()) {
      rows.add(
          new BackupStepRepository.Terminal(
              onRun(old.attempt(), foreign),
              old.ended(),
              old.result(),
              old.errorCode(),
              old.errorSummary()));
    }
    var pair = new MorningDatabaseSession.BackupObservation(rows, List.of());
    rows.set(0, f.backup().current().getFirst());
    assertEquals(foreign, pair.current().getFirst().attempt().run());
    assertEquals(foreign, pair.current().getLast().attempt().run());
    assertThrows(
        UnsupportedOperationException.class,
        () -> pair.current().set(0, f.backup().current().getFirst()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(rows, List.of()));
    rejected(f, pair, f.cleanup(), f.expiry());
  }

  @Test
  void parent540003CleanupRunAndUnavailableReasonAreBoundToBackupOutcome() throws Exception {
    var f = fixture("new");
    var foreign =
        new BatchRun(
            UUID.fromString("87654321-9abc-def0-8123-456789abcdef"),
            Instant.parse("2026-09-12T15:00:00Z"));
    var foreignRows = new ArrayList<CleanupTerminalRepository.Entry>();
    for (var row : f.cleanup().terminal().entries()) {
      foreignRows.add(
          new CleanupTerminalRepository.Entry(
              onRun(row.attempt(), foreign), row.endedAt(), row.result(), row.progressSeal()));
    }
    rejected(f, f.backup(), cleanup(f, foreignRows), f.expiry());
    var unavailable =
        new BatchStepResult(
            BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.BACKUP_UNAVAILABLE);
    var rows = new ArrayList<>(f.cleanup().terminal().entries());
    var first = rows.getFirst();
    rows.set(0, new CleanupTerminalRepository.Entry(first.attempt(), first.endedAt(), unavailable));
    rejected(f, f.backup(), cleanup(f, rows), f.expiry());
    var failed = fixture("failed");
    rows = new ArrayList<>(failed.cleanup().terminal().entries());
    var last = rows.getLast();
    rows.set(6, new CleanupTerminalRepository.Entry(last.attempt(), last.endedAt(), unavailable));
    rejected(failed, failed.backup(), cleanup(failed, rows), failed.expiry());
    rows = new ArrayList<>(failed.cleanup().terminal().entries());
    rows.set(0, first);
    rejected(failed, failed.backup(), cleanup(failed, rows), failed.expiry());
  }

  @Test
  void parent540004ExpiryMustBelongToTheSameRunEvenWhenAllTerminalValuesAreValid()
      throws Exception {
    var f = fixture("new");
    var foreign =
        new BatchRun(
            UUID.fromString("87654321-9abc-def0-8123-456789abcdef"),
            Instant.parse("2026-09-12T15:00:00Z"));
    var old = f.expiry();
    var expiry =
        new MorningDatabaseSession.ExpiryObservation(
            new MorningDatabaseSession.ExpiryBegins(
                onRun(old.begins().current(), foreign), Optional.empty()),
            old.ended(),
            old.result(),
            old.audit(),
            old.receipt());
    rejected(f, f.backup(), f.cleanup(), expiry);
  }

  private static BatchStepAttempt onRun(BatchStepAttempt old, BatchRun run) {
    return new BatchStepAttempt(
        old.id(), run, old.step(), old.attempt(), old.startedAt(), old.skipped());
  }

  private static MorningCleanupExecution.Completion cleanup(
      MorningCompletionEvidence f, List<CleanupTerminalRepository.Entry> rows) {
    return new MorningCleanupExecution.Completion(
        new CleanupTerminalRepository.Snapshot(rows),
        f.cleanup().receipt(),
        f.cleanup().references());
  }

  private static void rejected(
      MorningCompletionEvidence f,
      MorningDatabaseSession.BackupObservation backup,
      MorningCleanupExecution.Completion cleanup,
      MorningDatabaseSession.ExpiryObservation expiry) {
    var error =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new MorningCompletionEvidence(
                    f.backupOutcome(),
                    f.begins(),
                    f.manifest(),
                    backup,
                    f.backupReceipt(),
                    f.backupCycle(),
                    cleanup,
                    expiry));
    assertEquals("Morning completion evidence invalid", error.getMessage());
    assertNull(error.getCause());
  }
}
