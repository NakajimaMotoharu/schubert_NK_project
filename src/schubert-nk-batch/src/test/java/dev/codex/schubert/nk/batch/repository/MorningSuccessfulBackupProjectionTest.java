package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * MDB-PROJ-1737-001..006 / OPS009/DAT009/UI251/SS331332343354. Independent JDBC projection vectors:
 * no VM, no ownership grant, no production-generated oracle.
 */
final class MorningSuccessfulBackupProjectionTest {
  private static final String FIXTURE_BACKUP_DB_6C03A087 = "BACKUP_DB";
  private static final String FIXTURE_ATTEMPT_7FD8A755 = "attempt";
  private static final String FIXTURE_STARTED_AT_D1210657 = "started_at";
  private static final String FIXTURE_ENDED_AT_E151E393 = "ended_at";
  private static final String FIXTURE_BYTE_COUNT_6D76E237 = "byte_count";
  private static final String FIXTURE_BACKUP_CONFIG_8386D7E7 = "BACKUP_CONFIG";
  private static final Instant OBSERVED = Instant.parse("2026-09-28T03:00:00Z");

  private static Map<String, Object> row(String step) {
    var value = new HashMap<String, Object>();
    boolean database = step.equals(FIXTURE_BACKUP_DB_6C03A087);
    value.put("id", database ? 1737001L : 1737002L);
    value.put("business_date", LocalDate.of(2026, 9, 28));
    value.put("step", step);
    value.put(FIXTURE_ATTEMPT_7FD8A755, 1);
    value.put(FIXTURE_STARTED_AT_D1210657, OffsetDateTime.parse("2026-09-28T02:00:00Z"));
    value.put(FIXTURE_ENDED_AT_E151E393, OffsetDateTime.parse("2026-09-28T02:00:03Z"));
    value.put("target_count", database ? 1L : 2L);
    value.put("success_count", database ? 1L : 2L);
    value.put("failure_count", 0L);
    value.put(FIXTURE_BYTE_COUNT_6D76E237, database ? 26L : 67L);
    value.put("error_code", null);
    value.put("error_summary", null);
    return value;
  }

  private static void rejected(List<Map<String, Object>> rows) throws Exception {
    var probe = new MorningDatabaseSessionTest.Probe();
    probe.successfulRows = rows;
    assertThrows(
        IOException.class,
        () ->
            probe
                .subject()
                .execute(
                    MorningDatabaseSessionTest.credential(),
                    session -> session.successfulBackup(MorningDatabaseSessionTest.RUN, OBSERVED)));
    probe.released();
    assertEquals(0, probe.counts.getOrDefault("connection.commit", 0));
    assertFalse(probe.events.stream().anyMatch(v -> v.startsWith("connection.rollback")));
  }

  @Test
  void mdbProj1737001BothSqlOrdersReturnLiteralIdsAndNoMutation() throws Exception {
    for (boolean reversed : new boolean[] {false, true}) {
      var probe = new MorningDatabaseSessionTest.Probe();
      probe.successfulRows =
          reversed
              ? List.of(row(FIXTURE_BACKUP_CONFIG_8386D7E7), row(FIXTURE_BACKUP_DB_6C03A087))
              : List.of(row(FIXTURE_BACKUP_DB_6C03A087), row(FIXTURE_BACKUP_CONFIG_8386D7E7));
      var result =
          probe
              .subject()
              .execute(
                  MorningDatabaseSessionTest.credential(),
                  session -> session.successfulBackup(MorningDatabaseSessionTest.RUN, OBSERVED));
      assertTrue(result.isPresent());
      assertEquals(1737001L, result.get().database().id());
      assertEquals(1737002L, result.get().configuration().id());
      assertEquals(BatchStep.BACKUP_DB, result.get().database().step());
      assertEquals(BatchStep.BACKUP_CONFIG, result.get().configuration().step());
      assertEquals(1, result.get().database().attempt());
      assertEquals(Instant.parse("2026-09-28T02:00:00Z"), result.get().database().startedAt());
      probe.released();
      assertEquals(0, probe.counts.getOrDefault("connection.commit", 0));
    }
  }

  @Test
  void mdbProj1737002EmptyMeansNoReusablePairAndIncompleteOrExtraRowsReject() throws Exception {
    var probe = new MorningDatabaseSessionTest.Probe();
    probe.successfulRows = List.of();
    assertTrue(
        probe
            .subject()
            .execute(
                MorningDatabaseSessionTest.credential(),
                session -> session.successfulBackup(MorningDatabaseSessionTest.RUN, OBSERVED))
            .isEmpty());
    probe.released();
    rejected(List.of(row(FIXTURE_BACKUP_DB_6C03A087)));
    rejected(
        List.of(
            row(FIXTURE_BACKUP_DB_6C03A087),
            row(FIXTURE_BACKUP_CONFIG_8386D7E7),
            row(FIXTURE_BACKUP_DB_6C03A087)));
    rejected(List.of(row(FIXTURE_BACKUP_DB_6C03A087), row(FIXTURE_BACKUP_DB_6C03A087)));
  }

  @Test
  void mdbProj1737003EveryRequiredProjectionNullRejectsWithoutNpeOrLeak() throws Exception {
    for (String field :
        List.of(
            "step",
            "business_date",
            FIXTURE_STARTED_AT_D1210657,
            FIXTURE_ENDED_AT_E151E393,
            "target_count",
            "success_count",
            "failure_count",
            FIXTURE_BYTE_COUNT_6D76E237,
            "id",
            FIXTURE_ATTEMPT_7FD8A755)) {
      for (int which : new int[] {0, 1}) {
        var rows =
            new ArrayList<>(
                List.of(row(FIXTURE_BACKUP_DB_6C03A087), row(FIXTURE_BACKUP_CONFIG_8386D7E7)));
        rows.get(which).put(field, null);
        rejected(rows);
      }
    }
  }

  @Test
  void mdbProj1737004EachSemanticFieldCounterexampleRejects() throws Exception {
    var invalid = new HashMap<String, Object>();
    invalid.put("business_date", LocalDate.of(2026, 9, 27));
    invalid.put(FIXTURE_ENDED_AT_E151E393, OffsetDateTime.parse("2026-09-28T01:59:59Z"));
    invalid.put("target_count", 3L);
    invalid.put("success_count", 0L);
    invalid.put("failure_count", 1L);
    invalid.put(FIXTURE_BYTE_COUNT_6D76E237, 0L);
    invalid.put("error_code", "FIXED_FAULT");
    invalid.put("error_summary", "PUBLIC_FIXTURE");
    invalid.put("step", "CLEAN_LOG");
    for (var mutation : invalid.entrySet()) {
      for (int which : new int[] {0, 1}) {
        var rows =
            new ArrayList<>(
                List.of(row(FIXTURE_BACKUP_DB_6C03A087), row(FIXTURE_BACKUP_CONFIG_8386D7E7)));
        rows.get(which).put(mutation.getKey(), mutation.getValue());
        rejected(rows);
      }
    }
    for (String timestamp :
        List.of("2026-09-28T03:00:00.000001Z", "2026-09-28T02:00:03.000000001Z")) {
      var bad = row(FIXTURE_BACKUP_DB_6C03A087);
      bad.put(FIXTURE_ENDED_AT_E151E393, OffsetDateTime.parse(timestamp));
      rejected(List.of(bad, row(FIXTURE_BACKUP_CONFIG_8386D7E7)));
    }
  }

  @Test
  void mdbProj1737005PairAttemptStartAndEndMustBeOneBundle() throws Exception {
    for (String field :
        List.of(FIXTURE_ATTEMPT_7FD8A755, FIXTURE_STARTED_AT_D1210657, FIXTURE_ENDED_AT_E151E393)) {
      var bad = row(FIXTURE_BACKUP_CONFIG_8386D7E7);
      bad.put(
          field,
          field.equals(FIXTURE_ATTEMPT_7FD8A755)
              ? 2
              : OffsetDateTime.parse(
                  field.equals(FIXTURE_STARTED_AT_D1210657)
                      ? "2026-09-28T02:00:01Z"
                      : "2026-09-28T02:00:04Z"));
      rejected(List.of(row(FIXTURE_BACKUP_DB_6C03A087), bad));
    }
  }

  @Test
  void mdbProj1737006EndAtObservationAndPositiveByteBoundaryRemainEligible() throws Exception {
    var probe = new MorningDatabaseSessionTest.Probe();
    var db = row(FIXTURE_BACKUP_DB_6C03A087);
    var config = row(FIXTURE_BACKUP_CONFIG_8386D7E7);
    for (var row : List.of(db, config)) {
      row.put(FIXTURE_ENDED_AT_E151E393, OBSERVED.atOffset(java.time.ZoneOffset.UTC));
      row.put(FIXTURE_BYTE_COUNT_6D76E237, 1L);
    }
    probe.successfulRows = List.of(db, config);
    var result =
        probe
            .subject()
            .execute(
                MorningDatabaseSessionTest.credential(),
                session -> session.successfulBackup(MorningDatabaseSessionTest.RUN, OBSERVED));
    assertTrue(result.isPresent());
    assertEquals(1737001L, result.get().database().id());
    probe.released();
  }

  @Test
  void mdbProj1737007AllowedJdbcFailuresAndUnknownProviderIdentityCloseEveryResource()
      throws Exception {
    for (String point :
        List.of(
            "HISTORY.statement.executeQuery",
            "HISTORY.row.next",
            "HISTORY.row.getString",
            "HISTORY.row.getObject",
            "HISTORY.row.close",
            "HISTORY.statement.close")) {
      for (int kind : new int[] {0, 1, 2}) {
        var probe = new MorningDatabaseSessionTest.Probe();
        probe.successfulRows =
            List.of(row(FIXTURE_BACKUP_DB_6C03A087), row(FIXTURE_BACKUP_CONFIG_8386D7E7));
        Throwable failure =
            switch (kind) {
              case 0 -> new java.sql.SQLException("PRIVATE_PROVIDER_DIAGNOSTIC");
              case 1 -> new IllegalStateException("PUBLIC_UNKNOWN_IDENTITY");
              default -> new AssertionError("PUBLIC_FATAL_IDENTITY");
            };
        probe.faults.put(point, failure);
        org.junit.jupiter.api.function.Executable work =
            () ->
                probe
                    .subject()
                    .execute(
                        MorningDatabaseSessionTest.credential(),
                        session ->
                            session.successfulBackup(MorningDatabaseSessionTest.RUN, OBSERVED));
        if (kind == 0) {
          var actual = assertThrows(IOException.class, work);
          assertEquals("root batch database unavailable", actual.getMessage());
          assertNull(actual.getCause());
          assertEquals(0, actual.getSuppressed().length);
        } else if (kind == 1) {
          assertSame(failure, assertThrows(IllegalStateException.class, work));
        } else {
          assertSame(failure, assertThrows(AssertionError.class, work));
        }
        probe.released();
        assertEquals(0, probe.counts.getOrDefault("connection.commit", 0));
      }
    }
  }
}
