package dev.codex.schubert.nk.batch.repository;

import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.RUN;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.START;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.locked;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.query;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.sql;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import java.sql.Connection;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** CTERM001..003: independent SQL fixture/full-row data, no native Unit acceptance. SSC119. */
final class CleanupTerminalRepositoryTest {
  /** CTERM200001: literal same-day foreign run; current skip and prior success stay separate. */
  @Test
  void cterm200001DifferentRunNeedsExactRetainedOriginalAndCannotChangeEitherResult()
      throws Exception {
    insertCurrentSkips();
    var currentRun =
        new BatchRun(
            UUID.fromString("00000000-0000-4000-8000-000000000200"),
            Instant.parse("2026-09-13T02:00:02Z"));
    try (var admin = db.admin()) {
      sql(
          admin,
          "update schubert.batch_runs set run_id='00000000-0000-4000-8000-000000000200' where id between 2000 and 2006");
    }
    try (var raw = locked(db, false)) {
      var subject = new CleanupTerminalRepository(raw, () -> 10_000_000_000L);
      var current = subject.read(currentRun, OBSERVED);
      assertThrows(BatchRepositoryException.class, () -> subject.references(current));
      var calls = new ArrayList<UUID>();
      var prior =
          subject.references(
              current,
              (id, observed) -> {
                assertEquals(RUN.id(), id);
                assertEquals(Instant.parse("2026-09-13T02:00:02Z"), observed);
                calls.add(id);
                return RUN;
              });
      assertEquals(Collections.nCopies(14, RUN.id()), calls);
      for (int i = 0; i < 7; i++) {
        var old = prior.get(i).orElseThrow();
        var now = current.entries().get(i);
        assertEquals(1000 + i, old.attempt().id());
        assertEquals(RUN, old.attempt().run());
        assertEquals(STEPS[i], old.attempt().step().name());
        assertEquals(1, old.attempt().attempt());
        assertEquals(Instant.parse("2026-09-13T02:00:00Z"), old.attempt().startedAt());
        assertEquals(Instant.parse("2026-09-13T02:00:01Z"), old.endedAt());
        assertEquals(
            new BatchStepResult(
                BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE),
            old.result());
        assertEquals(2000 + i, now.attempt().id());
        assertEquals(currentRun, now.attempt().run());
        assertEquals(
            new BatchStepResult(
                BatchStepResult.Status.SKIPPED,
                0,
                0,
                0,
                0,
                BatchStepResult.Reason.ALREADY_SUCCESSFUL),
            now.result());
      }
      var io = new java.io.IOException("public synthetic original refusal");
      assertSame(
          io,
          assertThrows(
              java.io.IOException.class,
              () ->
                  subject.references(
                      current,
                      (id, at) -> {
                        throw io;
                      })));
      assertThrows(
          BatchRepositoryException.class,
          () -> subject.references(current, (id, at) -> currentRun));
      assertThrows(NullPointerException.class, () -> subject.references(current, null));
      assertEquals(current, subject.read(currentRun, OBSERVED));
      assertFalse(raw.getAutoCommit());
      assertFalse(raw.isClosed());
      assertEquals("14", query(raw, "select count(*) from schubert.batch_runs"));
      raw.rollback();
    }
  }

  /** CTERM010 / SS332 SSC199: public values; literal seven-slot/time/identity oracle. */
  @Test
  void ref201004CompleteProgressSealIsRetainedAndCursorOnlyChangesCannotPassReread()
      throws Exception {
    insertCurrentSkips();
    try (var c = locked(db, false)) {
      var subject = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      var current = subject.read(RUN, OBSERVED);
      var expected = subject.references(current);
      assertEquals(
          Optional.of(SuccessProgressSealTest.hash(SuccessProgressSealTest.INBOX_JSON)),
          expected.get(3).orElseThrow().progressSeal());
      assertEquals(
          Optional.of(SuccessProgressSealTest.hash(SuccessProgressSealTest.LOG_JSON)),
          expected.get(4).orElseThrow().progressSeal());
      for (int i : List.of(0, 1, 2, 5, 6))
        assertTrue(expected.get(i).orElseThrow().progressSeal().isEmpty());
      try (var admin = db.admin()) {
        sql(admin, "update schubert.log_cleanup_progress set after_id=2");
      }
      var changed = subject.references(current);
      assertNotEquals(expected, changed);
      assertNotEquals(expected.get(4), changed.get(4));
      for (int i : List.of(0, 1, 2, 3, 5, 6)) assertEquals(expected.get(i), changed.get(i));
      assertEquals(current, subject.read(RUN, OBSERVED));
      try (var admin = db.admin()) {
        sql(admin, "update schubert.log_cleanup_progress set after_id=1");
      }
      assertEquals(expected, subject.references(current));
      try (var admin = db.admin()) {
        sql(admin, "update schubert.inbox_inspection_progress set completed_at=null");
      }
      assertThrows(BatchRepositoryException.class, () -> subject.references(current));
      assertEquals(
          "25P02",
          assertThrows(java.sql.SQLException.class, () -> query(c, "select 1")).getSQLState());
      c.rollback(); // The borrowed failed TX is recovered only by its caller, never the repository.
      assertEquals(current, subject.read(RUN, OBSERVED));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      c.rollback();
    }
  }

  @Test
  void ref201005SealDataContractDoesNotGrantAuthorityToOtherStepsOrSkips() {
    var handle = new BatchStepAttempt(42, RUN, BatchStep.CLEAN_LOG, 1, START, false);
    var ended = START.plusSeconds(1);
    var result =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE);
    var value =
        new CleanupTerminalRepository.Entry(handle, ended, result, Optional.of("a".repeat(64)));
    assertEquals(Optional.of("a".repeat(64)), value.progressSeal());
    assertEquals(handle, value.attempt());
    assertEquals(ended, value.endedAt());
    assertEquals(result, value.result());
    for (String bad : List.of("", "A".repeat(64), "a".repeat(63), "g".repeat(64)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new CleanupTerminalRepository.Entry(handle, ended, result, Optional.of(bad)));
    var other = new BatchStepAttempt(42, RUN, BatchStep.CLEAN_TRANSFER, 1, START, false);
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupTerminalRepository.Entry(other, ended, result, value.progressSeal()));
    var skip = new BatchStepAttempt(42, RUN, BatchStep.CLEAN_LOG, 1, START, true);
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupTerminalRepository.Entry(skip, ended, result, value.progressSeal()));
    var warning =
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 1, 0, 0, 0, BatchStepResult.Reason.PROTECTED_RECORDS);
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupTerminalRepository.Entry(handle, ended, warning, value.progressSeal()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Entry(handle, ended, result, null));
  }

  @Test
  void cterm010PublicValuesRejectInvalidTimeDuplicateAndForeignRun() {
    var ended = Instant.parse("2026-09-13T02:00:01Z");
    var success =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE);
    var skipped =
        new BatchStepResult(
            BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.ALREADY_SUCCESSFUL);
    var entries = new ArrayList<CleanupTerminalRepository.Entry>();
    for (String step :
        List.of(
            "CLEAN_NOTIFICATION",
            "CLEAN_QUESTION",
            "CLEAN_SESSION",
            "CLEAN_INBOX_OUTBOX",
            "CLEAN_LOG",
            "CLEAN_BATCH_RUN",
            "CLEAN_TRANSFER")) {
      entries.add(
          new CleanupTerminalRepository.Entry(
              new BatchStepAttempt(
                  entries.size() + 1, RUN, BatchStep.valueOf(step), 1, START, false),
              ended,
              success));
    }
    var first = entries.getFirst();
    var maximum = Instant.parse("9999-12-31T23:59:59.999999Z");
    assertEquals(
        maximum, new CleanupTerminalRepository.Entry(first.attempt(), maximum, success).endedAt());
    for (Instant invalid : List.of(maximum.plusNanos(1000), ended.plusNanos(1))) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new CleanupTerminalRepository.Entry(first.attempt(), invalid, success));
    }
    var foreign =
        new BatchRun(UUID.fromString("00000000-0000-4000-8000-000000000003"), RUN.cutoff());
    for (boolean duplicate : List.of(false, true)) {
      var changed = new ArrayList<>(entries);
      var second = entries.get(1).attempt();
      changed.set(
          1,
          new CleanupTerminalRepository.Entry(
              new BatchStepAttempt(
                  duplicate ? 1 : 2, duplicate ? RUN : foreign, second.step(), 1, START, false),
              ended,
              success));
      assertThrows(
          IllegalArgumentException.class, () -> new CleanupTerminalRepository.Snapshot(changed));
      var rejected =
          changed.stream()
              .map(
                  e ->
                      Optional.of(
                          new CleanupTerminalRepository.RejectedEntry(
                              e.attempt(), Optional.of(e.endedAt()), Optional.of(e.result()))))
              .toList();
      assertThrows(
          IllegalArgumentException.class,
          () -> new CleanupTerminalRepository.RejectedSnapshot(RUN, rejected));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.RejectedEntry(
                first.attempt(), Optional.of(START.minusSeconds(1)), Optional.of(success)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.RejectedEntry(
                first.attempt(), Optional.of(START), Optional.of(skipped)));
    var skipAttempt = new BatchStepAttempt(100, RUN, BatchStep.CLEAN_NOTIFICATION, 2, START, true);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.RejectedEntry(
                skipAttempt, Optional.empty(), Optional.empty()));
    var accepted =
        entries.stream()
            .map(
                e ->
                    Optional.of(
                        new CleanupTerminalRepository.RejectedEntry(
                            e.attempt(), Optional.of(e.endedAt()), Optional.of(e.result()))))
            .toList();
    assertEquals(accepted, new CleanupTerminalRepository.RejectedSnapshot(RUN, accepted).entries());
    var wrongSlots = new ArrayList<>(accepted);
    Collections.reverse(wrongSlots);
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupTerminalRepository.RejectedSnapshot(RUN, wrongSlots));
    assertEquals(entries, new CleanupTerminalRepository.Snapshot(entries).entries());
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Snapshot(Arrays.asList(first, null)));
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupTerminalRepository.RejectedSnapshot(
                RUN, Arrays.asList(Optional.empty(), null)));
  }

  @Test
  void cterm006ProjectionFaultsAndOwnedJdbcResources() throws Exception {
    for (boolean rejected : List.of(false, true)) {
      for (String column :
          List.of(
              "step",
              "status",
              "id",
              "attempt",
              "started_at",
              "run_id",
              "business_date",
              "target_count",
              "success_count",
              "failure_count",
              "byte_count",
              "ended_at")) {
        var probe = new BatchJdbcProbe();
        probe.selectedSql = "select distinct on(step)";
        probe.columns.put(column, null);
        refusedProjection(probe, rejected);
      }
      for (var item :
          Map.<String, Object>ofEntries(
                  Map.entry("id", 1000L),
                  Map.entry("run_id", UUID.fromString("00000000-0000-4000-8000-000000000002")),
                  Map.entry("business_date", LocalDate.of(2026, 9, 14)),
                  Map.entry("step", "BACKUP_DB"),
                  Map.entry("status", "UNKNOWN"),
                  Map.entry("error_code", "UNKNOWN"),
                  Map.entry("error_summary", "synthetic wrong summary"),
                  Map.entry("target_count", -1L),
                  Map.entry("success_count", -1L),
                  Map.entry("failure_count", -1L),
                  Map.entry("byte_count", -1L),
                  Map.entry("started_at", OffsetDateTime.parse("2026-10-01T00:00:00Z")),
                  Map.entry("ended_at", OffsetDateTime.parse("2026-10-01T00:00:00Z")))
              .entrySet()) {
        var probe = new BatchJdbcProbe();
        probe.selectedSql = "select distinct on(step)";
        probe.columns.put(item.getKey(), item.getValue());
        refusedProjection(probe, rejected);
      }
      for (String fault : List.of("null-statement", "null-rows", "eighth", "duplicate")) {
        var probe = new BatchJdbcProbe();
        probe.selectedSql = "select distinct on(step)";
        probe.nullStatement = fault.equals("null-statement");
        probe.nullRows = fault.equals("null-rows");
        probe.extraLastRow = fault.equals("eighth");
        if (fault.equals("duplicate")) probe.columns.put("step", "CLEAN_NOTIFICATION");
        refusedProjection(probe, rejected);
      }
    }
  }

  @Test
  void cterm007TransactionAndRunningProjectionAreNotAuthority() throws Exception {
    for (var item :
        Map.<String, Object>of(
                "getAutoCommit",
                true,
                "isReadOnly",
                true,
                "getTransactionIsolation",
                Connection.TRANSACTION_SERIALIZABLE)
            .entrySet()) {
      var probe = new BatchJdbcProbe();
      probe.selectedSql = "select distinct on(step)";
      probe.connectionValues.put(item.getKey(), item.getValue());
      refusedProjection(probe, true);
      assertEquals(0, probe.selectedStatements);
    }
    var inconsistent = new BatchJdbcProbe();
    inconsistent.selectedSql = "maintenance_read_run_references";
    inconsistent.columns.put("identity_consistent", false);
    refusedProjection(inconsistent, true);
    for (String column :
        List.of(
            "ended_at",
            "target_count",
            "success_count",
            "failure_count",
            "byte_count",
            "error_code",
            "error_summary")) {
      var probe = new BatchJdbcProbe();
      probe.selectedSql = "select distinct on(step)";
      probe.columns.put("status", "RUNNING");
      probe.columns.put("ended_at", null);
      for (String count : List.of("target_count", "success_count", "failure_count", "byte_count"))
        probe.columns.put(count, 0L);
      probe.columns.put(
          column,
          switch (column) {
            case "ended_at" -> OffsetDateTime.parse("2026-09-13T02:00:01Z");
            case "error_code", "error_summary" -> "synthetic unexpected value";
            default -> 1L;
          });
      refusedProjection(probe, true);
    }
  }

  @Test
  void cterm008SqlBodyMustNotHideFatalOwnedClose() throws Exception {
    for (String path : List.of("read", "rejected", "references", "progress")) {
      seed();
      if (path.equals("references") || path.equals("progress")) insertCurrentSkips();
      for (var sample : JdbcResourceCases.all()) {
        var probe = new BatchJdbcProbe();
        probe.selectedSql =
            switch (path) {
              case "references" -> "and status='SUCCESS'";
              case "progress" -> "select proof_sha256";
              default -> "select distinct on(step)";
            };
        if (sample.primary() != null)
          probe.thrown.put(
              sample.body().substring(sample.body().indexOf('.') + 1), sample.primary());
        probe.thrown.put(
            sample.close().equals("row.close") ? "resultClose" : "statementClose",
            sample.secondary());
        try (var raw = locked(db, false)) {
          String sql =
              "select json_agg(to_jsonb(t) order by id)::text from schubert.batch_runs t where run_id='"
                  + RUN.id()
                  + "'";
          String before = query(raw, sql);
          var current =
              new CleanupTerminalRepository(raw, () -> 10_000_000_000L).read(RUN, OBSERVED);
          var subject = new CleanupTerminalRepository(probe.wrap(raw), () -> 10_000_000_000L);
          Throwable actual =
              assertThrows(
                  Throwable.class,
                  () -> {
                    switch (path) {
                      case "read" -> subject.read(RUN, OBSERVED);
                      case "rejected" -> subject.readRejected(RUN, OBSERVED);
                      case "references", "progress" -> subject.references(current);
                      default -> throw new AssertionError("unknown public path");
                    }
                  });
          sample.verify(actual);
          assertBorrowed(probe, raw);
          assertEquals(before, query(raw, sql), "read failure preserves all SQL rows/columns");
          raw.rollback();
        }
      }
    }
  }

  private void refusedProjection(BatchJdbcProbe probe, boolean rejected) throws Exception {
    try (var raw = locked(db, false)) {
      var subject = new CleanupTerminalRepository(probe.wrap(raw), () -> 10_000_000_000L);
      var failure =
          assertThrows(
              BatchRepositoryException.class,
              () -> {
                if (rejected) subject.readRejected(RUN, OBSERVED);
                else subject.read(RUN, OBSERVED);
              });
      assertEquals("batch repository operation failed", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertBorrowed(probe, raw);
      raw.rollback();
    }
  }

  /** REF201006: public JDBC projection/close failures; never exclude the new owned scopes. */
  @Test
  void ref201006ProgressProjectionAndChangedOriginalCannotReturnAProof() throws Exception {
    insertCurrentSkips();
    for (String fault : List.of("statement", "rows", "missing", "duplicate", "null", "invalid")) {
      var probe = new BatchJdbcProbe();
      probe.selectedSql = "select proof_sha256";
      switch (fault) {
        case "statement" -> probe.nullStatement = true;
        case "rows" -> probe.nullRows = true;
        case "missing" -> probe.empty = true;
        case "duplicate" -> probe.duplicate = true;
        case "null" -> probe.columns.put("proof_sha256", null);
        case "invalid" -> probe.columns.put("proof_sha256", "A".repeat(64));
        default -> throw new AssertionError("unknown literal fixture");
      }
      try (var raw = locked(db, false)) {
        var current = new CleanupTerminalRepository(raw, () -> 10_000_000_000L).read(RUN, OBSERVED);
        var subject = new CleanupTerminalRepository(probe.wrap(raw), () -> 10_000_000_000L);
        assertThrows(BatchRepositoryException.class, () -> subject.references(current));
        assertBorrowed(probe, raw);
        assertEquals(
            current, new CleanupTerminalRepository(raw, () -> 10_000_000_000L).read(RUN, OBSERVED));
        raw.rollback();
      }
    }
    try (var raw = locked(db, false)) {
      var subject = new CleanupTerminalRepository(raw, () -> 10_000_000_000L);
      var current = subject.read(RUN, OBSERVED);
      var changed =
          new BatchRun(UUID.fromString("00000000-0000-4000-8000-000000000999"), RUN.cutoff());
      int[] reads = {0};
      assertThrows(
          BatchRepositoryException.class,
          () -> subject.references(current, (id, observed) -> ++reads[0] == 1 ? RUN : changed));
      assertEquals(2, reads[0]);
      assertEquals(current, subject.read(RUN, OBSERVED));
      var wrongDay = new BatchRun(RUN.id(), RUN.cutoff().minusSeconds(86400));
      assertThrows(
          BatchRepositoryException.class,
          () -> subject.references(current, (id, observed) -> wrongDay));
      assertEquals(current, subject.read(RUN, OBSERVED));
      raw.rollback();
    }
  }

  @Test
  void cterm009FailedBackupProfileAndIndependentPriorIdentity() throws Exception {
    String skips =
        "update schubert.batch_runs set status='SKIPPED',ended_at=started_at,target_count=0,success_count=0,failure_count=0,byte_count=0,error_code='BACKUP_UNAVAILABLE',error_summary='verified backup unavailable' where id between 1000 and 1005";
    try (var admin = db.admin()) {
      sql(admin, skips);
    }
    try (var raw = locked(db, false)) {
      var subject = new CleanupTerminalRepository(raw, () -> 10_000_000_000L);
      var actual = subject.readBackupUnavailable(RUN, OBSERVED);
      assertEquals(0, actual.exitCode());
      for (int i = 0; i < 6; i++) {
        var entry = actual.entries().get(i);
        assertEquals(STEPS[i], entry.attempt().step().name());
        assertEquals(BatchStepResult.Status.SKIPPED, entry.result().status());
        assertEquals(BatchStepResult.Reason.BACKUP_UNAVAILABLE, entry.result().reason());
        assertEquals(0, entry.result().target());
        assertEquals(0, entry.result().success());
        assertEquals(0, entry.result().failure());
        assertEquals(0, entry.result().bytes());
        assertEquals(Instant.parse("2026-09-13T02:00:00Z"), entry.endedAt());
      }
      assertEquals(BatchStepResult.Status.SUCCESS, actual.entries().get(6).result().status());
      assertEquals(7, subject.readRejected(RUN, OBSERVED).entries().size());
      assertThrows(BatchRepositoryException.class, () -> subject.read(RUN, OBSERVED));
      raw.rollback();
    }
    for (String mutation : List.of("normal", "late", "reason", "transfer", "counts")) {
      seed();
      try (var admin = db.admin()) {
        if (!mutation.equals("normal")) sql(admin, skips);
        switch (mutation) {
          case "late" ->
              sql(
                  admin,
                  "update schubert.batch_runs set ended_at=started_at+interval '1 second' where id=1000");
          case "reason" ->
              sql(
                  admin,
                  "update schubert.batch_runs set error_code='ALREADY_SUCCESSFUL',error_summary='step already successful for business date' where id=1000");
          case "transfer" -> sql(admin, skips.replace("between 1000 and 1005", "=1006"));
          default -> {}
        }
      }
      try (var raw = locked(db, false)) {
        var probe = new BatchJdbcProbe();
        probe.selectedSql = "select distinct on(step)";
        if (mutation.equals("counts")) probe.columns.put("target_count", 1L);
        assertThrows(
            BatchRepositoryException.class,
            () ->
                new CleanupTerminalRepository(probe.wrap(raw), () -> 10_000_000_000L)
                    .readBackupUnavailable(RUN, OBSERVED));
        assertBorrowed(probe, raw);
        raw.rollback();
      }
    }
    seed();
    insertCurrentSkips();
    for (String fault :
        List.of(
            "null-statement",
            "null-rows",
            "missing",
            "duplicate",
            "step",
            "id",
            "attempt",
            "status",
            "not-skipped",
            "late-current")) {
      try (var raw = locked(db, false)) {
        var current = new CleanupTerminalRepository(raw, () -> 10_000_000_000L).read(RUN, OBSERVED);
        var probe = new BatchJdbcProbe();
        probe.selectedSql = "and status='SUCCESS'";
        switch (fault) {
          case "null-statement" -> probe.nullStatement = true;
          case "null-rows" -> probe.nullRows = true;
          case "missing" -> probe.empty = true;
          case "duplicate" -> probe.duplicate = true;
          case "step" -> probe.columns.put("step", "CLEAN_TRANSFER");
          case "id" -> probe.columns.put("id", 2000L);
          case "attempt" -> probe.columns.put("attempt", 2);
          case "status" -> {
            probe.columns.put("status", "WARNING");
            probe.columns.put("error_code", "PROTECTED_RECORDS");
            probe.columns.put("error_summary", "protected records retained");
          }
          case "not-skipped", "late-current" -> {
            var entries = new ArrayList<>(current.entries());
            var row = entries.getFirst();
            var attempt = row.attempt();
            if (fault.equals("not-skipped"))
              attempt =
                  new BatchStepAttempt(
                      attempt.id(),
                      attempt.run(),
                      attempt.step(),
                      attempt.attempt(),
                      attempt.startedAt(),
                      false);
            entries.set(
                0,
                new CleanupTerminalRepository.Entry(
                    attempt,
                    fault.equals("late-current") ? row.endedAt().plusSeconds(1) : row.endedAt(),
                    row.result()));
            current = new CleanupTerminalRepository.Snapshot(entries);
          }
          default -> throw new AssertionError("unregistered fixture");
        }
        var input = current;
        assertThrows(
            BatchRepositoryException.class,
            () ->
                new CleanupTerminalRepository(probe.wrap(raw), () -> 10_000_000_000L)
                    .references(input));
        assertBorrowed(probe, raw);
        raw.rollback();
      }
    }
  }

  private static void assertBorrowed(BatchJdbcProbe probe, Connection raw) throws Exception {
    assertEquals(0, probe.liveRows);
    assertEquals(0, probe.liveStatements);
    assertEquals(0, probe.commits);
    assertEquals(0, probe.rollbacks);
    assertEquals(0, probe.closes);
    assertEquals(0, probe.autoChanges);
    assertEquals(0, probe.saves);
    assertEquals(0, probe.deletes);
    assertFalse(raw.getAutoCommit());
    assertFalse(raw.isClosed());
  }

  @TempDir static Path root;
  static BatchDatabaseFixture db;
  private static final Instant OBSERVED = Instant.parse("2026-09-30T00:00:00Z");
  private static final String[] STEPS = {
    "CLEAN_NOTIFICATION",
    "CLEAN_QUESTION",
    "CLEAN_SESSION",
    "CLEAN_INBOX_OUTBOX",
    "CLEAN_LOG",
    "CLEAN_BATCH_RUN",
    "CLEAN_TRANSFER"
  };

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.batch_runs");
      for (int index = 0; index < 7; index++)
        sql(
            c,
            "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count) values("
                + (1000 + index)
                + ",'"
                + RUN.id()
                + "','2026-09-13','"
                + STEPS[index]
                + "',1,'2026-09-13T02:00:00Z','2026-09-13T02:00:01Z','SUCCESS',1,1,0,0)");
    }
  }

  private CleanupTerminalRepository.Snapshot read() throws Exception {
    try (var c = locked(db, false)) {
      var result = new CleanupTerminalRepository(c, () -> 10_000_000_000L).read(RUN, OBSERVED);
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      c.rollback();
      return result;
    }
  }

  @Test
  void cterm001FixedSevenFullColumnsWarningAndSkipRemainSeparate() throws Exception {
    var success = read();
    assertEquals(0, success.exitCode());
    assertEquals(7, success.entries().size());
    for (int index = 0; index < 7; index++) {
      var entry = success.entries().get(index);
      assertEquals(1000 + index, entry.attempt().id());
      assertEquals(STEPS[index], entry.attempt().step().name());
      assertEquals(RUN, entry.attempt().run());
      assertEquals(1, entry.attempt().attempt());
      assertEquals(Instant.parse("2026-09-13T02:00:00Z"), entry.attempt().startedAt());
      assertEquals(Instant.parse("2026-09-13T02:00:01Z"), entry.endedAt());
      assertEquals(
          new BatchStepResult(
              BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE),
          entry.result());
    }
    try (var c = db.admin()) {
      sql(
          c,
          "update schubert.batch_runs set status='WARNING',target_count=2,success_count=1,error_code='PROTECTED_RECORDS',error_summary='protected records retained' where id=1001");
      sql(
          c,
          "update schubert.batch_runs set status='SKIPPED',ended_at=started_at,target_count=0,success_count=0,error_code='ALREADY_SUCCESSFUL',error_summary='step already successful for business date' where id=1002");
    }
    var changed = read();
    assertEquals(10, changed.exitCode());
    assertEquals(0, changed.entries().get(1).result().failure());
    assertTrue(changed.entries().get(2).attempt().skipped());
    assertEquals(0, changed.entries().get(2).result().target());
    assertEquals("CleanupTerminalSnapshot[data=<redacted>]", changed.toString());
    assertThrows(UnsupportedOperationException.class, () -> changed.entries().clear());
  }

  @Test
  void cterm002MissingRunningFailedAndMalformedDiagnosticNeverPass() throws Exception {
    for (String mutation :
        List.of(
            "delete from schubert.batch_runs where id=1002",
            "update schubert.batch_runs set status='RUNNING',ended_at=null where id=1002",
            "update schubert.batch_runs set status='FAILED',error_code='SAFETY_FAILURE',error_summary='batch safety check failed' where id=1002",
            "update schubert.batch_runs set error_code='UNKNOWN',error_summary='PUBLIC' where id=1002",
            "update schubert.batch_runs set error_summary='PUBLIC_WRONG' where id=1002")) {
      seed();
      try (var c = db.admin()) {
        sql(c, mutation);
      }
      var failure = assertThrows(BatchRepositoryException.class, this::read);
      assertNull(failure.getCause());
      assertFalse(failure.toString().contains("PUBLIC"));
    }
    seed();
    try (var c = locked(db, false)) {
      assertThrows(
          BatchRepositoryException.class,
          () ->
              new CleanupTerminalRepository(
                      c,
                      () -> {
                        throw new java.io.IOException("PRIVATE");
                      })
                  .read(RUN, OBSERVED));
      var unknown = new AssertionError("PUBLIC_UNKNOWN");
      assertSame(
          unknown,
          assertThrows(
              AssertionError.class,
              () ->
                  new CleanupTerminalRepository(
                          c,
                          () -> {
                            throw unknown;
                          })
                      .read(RUN, OBSERVED)));
      c.rollback();
    }
    try (var c = locked(db, true)) {
      assertThrows(
          BatchRepositoryException.class,
          () -> new CleanupTerminalRepository(c, () -> 10_000_000_000L).read(RUN, OBSERVED));
    }
  }

  private void insertCurrentSkips() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.log_cleanup_progress");
      sql(c, "delete from schubert.inbox_inspection_progress");
      sql(
          c,
          """
          insert into schubert.log_cleanup_progress
          (run_id,cutoff,after_logged_at,after_id,target_count,deleted_count,skipped_count,completed_at)
          values ('12345678-9abc-def0-8123-456789abcdef','2026-09-12T15:00:00Z',
                  '2026-06-01T00:00:00Z',1,1,1,0,'2026-09-13T02:00:01Z')
          """);
      sql(
          c,
          """
          insert into schubert.inbox_inspection_progress
          (run_id,cutoff,after_message_id,inspected_count,deleted_count,protected_count,completed_at)
          values ('12345678-9abc-def0-8123-456789abcdef','2026-09-12T15:00:00Z',
                  '00000000-0000-4000-8000-000000000101',1,1,0,'2026-09-13T02:00:01Z')
          """);
      for (int index = 0; index < 7; index++)
        sql(
            c,
            "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values("
                + (2000 + index)
                + ",'"
                + RUN.id()
                + "','2026-09-13','"
                + STEPS[index]
                + "',2,'2026-09-13T02:00:02Z','2026-09-13T02:00:02Z','SKIPPED',0,0,0,0,'ALREADY_SUCCESSFUL','step already successful for business date')");
    }
  }

  @Test
  void issuerStep003CurrentSkipAndPriorSuccessAreSeparateCompleteRows() throws Exception {
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      assertEquals(
          Collections.nCopies(7, Optional.empty()),
          repository.references(repository.read(RUN, OBSERVED)));
      c.rollback();
    }
    insertCurrentSkips();
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      var current = repository.read(RUN, OBSERVED);
      var references = repository.references(current);
      assertEquals(7, references.size());
      for (int index = 0; index < 7; index++) {
        var now = current.entries().get(index);
        var original = references.get(index).orElseThrow();
        assertEquals(2000 + index, now.attempt().id());
        assertEquals(2, now.attempt().attempt());
        assertEquals(Instant.parse("2026-09-13T02:00:02Z"), now.endedAt());
        assertEquals(
            new BatchStepResult(
                BatchStepResult.Status.SKIPPED,
                0,
                0,
                0,
                0,
                BatchStepResult.Reason.ALREADY_SUCCESSFUL),
            now.result());
        assertEquals(1000 + index, original.attempt().id());
        assertEquals(RUN, original.attempt().run());
        assertEquals(STEPS[index], original.attempt().step().name());
        assertEquals(1, original.attempt().attempt());
        assertEquals(Instant.parse("2026-09-13T02:00:00Z"), original.attempt().startedAt());
        assertEquals(Instant.parse("2026-09-13T02:00:01Z"), original.endedAt());
        assertEquals(
            new BatchStepResult(
                BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE),
            original.result());
      }
      assertThrows(UnsupportedOperationException.class, () -> references.clear());
      assertThrows(NullPointerException.class, () -> repository.references(null));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      c.rollback();
    }
  }

  @Test
  void issuerStep003MissingForeignLateAndMalformedOriginalCannotBecomeReference() throws Exception {
    for (String mutation :
        List.of(
            "delete from schubert.batch_runs where id=1002",
            "update schubert.batch_runs set run_id='47700000-2222-4333-8444-555555555555' where id=1002",
            "update schubert.batch_runs set attempt=3 where id=1002",
            "update schubert.batch_runs set ended_at='2026-09-13T02:00:03Z' where id=1002",
            "update schubert.batch_runs set error_summary='PUBLIC_WRONG' where id=1002")) {
      seed();
      insertCurrentSkips();
      try (var c = locked(db, false)) {
        var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
        var current = repository.read(RUN, OBSERVED);
        try (var admin = db.admin()) {
          sql(admin, mutation);
        }
        assertThrows(BatchRepositoryException.class, () -> repository.references(current));
        c.rollback();
      }
    }
  }

  @Test
  void cterm003ValueInvariantNullAndMissingOwner() throws Exception {
    var valid = read();
    assertThrows(NullPointerException.class, () -> new CleanupTerminalRepository(null, () -> 1));
    try (var c = locked(db, false)) {
      assertThrows(NullPointerException.class, () -> new CleanupTerminalRepository(c, null));
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      assertThrows(NullPointerException.class, () -> repository.read(null, OBSERVED));
      assertThrows(NullPointerException.class, () -> repository.read(RUN, null));
      c.rollback();
    }
    assertThrows(
        IllegalArgumentException.class, () -> new CleanupTerminalRepository.Snapshot(List.of()));
    var reversed = new ArrayList<>(valid.entries());
    Collections.reverse(reversed);
    assertThrows(
        IllegalArgumentException.class, () -> new CleanupTerminalRepository.Snapshot(reversed));
    var first = valid.entries().getFirst();
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Entry(null, first.endedAt(), first.result()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Entry(first.attempt(), null, first.result()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Entry(first.attempt(), first.endedAt(), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.Entry(
                first.attempt(), first.attempt().startedAt().minusSeconds(1), first.result()));
  }

  @Test
  void cterm004RejectedPartialRowsRemainExactAndMissingIsNotInvented() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.batch_runs where id>=1003");
      sql(
          c,
          "update schubert.batch_runs set status='RUNNING',ended_at=null,target_count=0,success_count=0 where id=1001");
      sql(
          c,
          "update schubert.batch_runs set status='FAILED',error_code='SAFETY_FAILURE',error_summary='batch safety check failed' where id=1002");
    }
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      var actual = repository.readRejected(RUN, OBSERVED);
      assertEquals(RUN, actual.run());
      assertEquals(7, actual.entries().size());
      for (int index = 0; index < 3; index++) {
        var row = actual.entries().get(index).orElseThrow();
        assertEquals(1000 + index, row.attempt().id());
        assertEquals(STEPS[index], row.attempt().step().name());
        assertEquals(1, row.attempt().attempt());
        assertEquals(Instant.parse("2026-09-13T02:00:00Z"), row.attempt().startedAt());
      }
      assertEquals(
          BatchStepResult.Status.SUCCESS,
          actual.entries().get(0).orElseThrow().result().orElseThrow().status());
      assertTrue(actual.entries().get(1).orElseThrow().result().isEmpty());
      assertTrue(actual.entries().get(1).orElseThrow().endedAt().isEmpty());
      var failed = actual.entries().get(2).orElseThrow();
      assertEquals(Optional.of(Instant.parse("2026-09-13T02:00:01Z")), failed.endedAt());
      assertEquals(
          Optional.of(
              new BatchStepResult(
                  BatchStepResult.Status.FAILED,
                  1,
                  1,
                  0,
                  0,
                  BatchStepResult.Reason.SAFETY_FAILURE)),
          failed.result());
      for (int index = 3; index < 7; index++) assertTrue(actual.entries().get(index).isEmpty());
      assertEquals(actual, repository.readRejected(RUN, OBSERVED));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      assertEquals("CleanupRejectedSnapshot[data=<redacted>]", actual.toString());
      assertThrows(UnsupportedOperationException.class, () -> actual.entries().clear());
      assertThrows(BatchRepositoryException.class, () -> repository.read(RUN, OBSERVED));
      c.rollback();
    }
    try (var c = db.admin()) {
      sql(c, "delete from schubert.batch_runs");
    }
    try (var c = locked(db, false)) {
      var empty =
          new CleanupTerminalRepository(c, () -> 10_000_000_000L).readRejected(RUN, OBSERVED);
      assertEquals(Collections.nCopies(7, Optional.empty()), empty.entries());
      try (var s = c.createStatement();
          var rows = s.executeQuery("select count(*) from schubert.batch_runs")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getLong(1));
      }
      c.rollback();
    }
  }

  @Test
  void cterm005RejectedMalformedRunningAndNullFailClosed() throws Exception {
    try (var c = db.admin()) {
      sql(c, "update schubert.batch_runs set status='RUNNING',ended_at=null where id=1001");
    }
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      assertThrows(BatchRepositoryException.class, () -> repository.readRejected(RUN, OBSERVED));
      assertThrows(NullPointerException.class, () -> repository.readRejected(null, OBSERVED));
      assertThrows(NullPointerException.class, () -> repository.readRejected(RUN, null));
      c.rollback();
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupTerminalRepository.RejectedSnapshot(RUN, List.of()));
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupTerminalRepository.RejectedSnapshot(
                null, Collections.nCopies(7, Optional.empty())));
    var attempt =
        new BatchStepAttempt(
            1000,
            RUN,
            BatchStep.CLEAN_NOTIFICATION,
            1,
            Instant.parse("2026-09-13T02:00:00Z"),
            false);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.RejectedEntry(
                attempt, Optional.of(OBSERVED), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.RejectedEntry(
                attempt,
                Optional.empty(),
                Optional.of(
                    new BatchStepResult(
                        BatchStepResult.Status.SUCCESS, 0, 0, 0, 0, BatchStepResult.Reason.NONE))));
  }
}
