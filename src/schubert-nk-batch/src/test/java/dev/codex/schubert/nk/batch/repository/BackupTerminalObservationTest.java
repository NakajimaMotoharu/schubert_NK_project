package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SSC134/ISSCOMP001..003: hand-written 14-column literal, never production expected. */
final class BackupTerminalObservationTest {
  private static final String FIXTURE_COMMAND_FAILURE_38148BF2 = "COMMAND_FAILURE";
  private static final String FIXTURE_BATCH_COMMAND_FAILED_7D52C711 = "batch command failed";
  private static final String FIXTURE_ALREADY_SUCCESSFUL_0E316429 = "ALREADY_SUCCESSFUL";
  private static final String FIXTURE_STEP_ALREADY_SUCCESSFUL_FOR_BUSINESS_DAT_B0F7DC85 =
      "step already successful for business date";
  private static final String FIXTURE_ENDED_AT_E151E393 = "ended_at";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_TARGET_COUNT_5B6567D4 = "target_count";
  private static final String FIXTURE_SUCCESS_COUNT_716E5185 = "success_count";
  private static final String FIXTURE_FAILURE_COUNT_C7E67F21 = "failure_count";
  private static final String FIXTURE_BYTE_COUNT_6D76E237 = "byte_count";
  private static final String FIXTURE_ERROR_CODE_B886CCEF = "error_code";
  private static final String FIXTURE_ERROR_SUMMARY_3F58BF23 = "error_summary";

  @Test
  void isscomp003PairInvariantsAndOriginalReferencesCannotAliasOrDrift() {
    var success =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 1, 1, 0, 26, BatchStepResult.Reason.NONE);
    var config = new BatchStepAttempt(2, RUN, BatchStep.BACKUP_CONFIG, 2, START, false);
    var d = new BackupStepRepository.Terminal(DB, END, success, Optional.empty(), Optional.empty());
    var c =
        new BackupStepRepository.Terminal(config, END, success, Optional.empty(), Optional.empty());
    var mutable = new ArrayList<>(List.of(d, c));
    var observed = new MorningDatabaseSession.BackupObservation(mutable, List.of());
    mutable.clear();
    assertEquals(List.of(d, c), observed.current());
    assertThrows(UnsupportedOperationException.class, () -> observed.current().clear());
    assertFalse(observed.toString().contains(RUN.id().toString()));
    for (List<BackupStepRepository.Terminal> invalid :
        List.of(List.<BackupStepRepository.Terminal>of(), List.of(d), List.of(d, c, d)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningDatabaseSession.BackupObservation(invalid, List.of()));
    for (List<BackupStepRepository.Terminal> invalid : List.of(List.of(d), List.of(d, c, d)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningDatabaseSession.BackupObservation(List.of(d, c), invalid));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.BackupObservation(null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(d, c), null));
    assertThrows(
        NullPointerException.class,
        () ->
            new BackupStepRepository.Terminal(
                null, END, success, Optional.empty(), Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () ->
            new BackupStepRepository.Terminal(
                DB, null, success, Optional.empty(), Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new BackupStepRepository.Terminal(DB, END, null, Optional.empty(), Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new BackupStepRepository.Terminal(DB, END, success, null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new BackupStepRepository.Terminal(DB, END, success, Optional.empty(), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 2, START, false),
                END,
                success,
                Optional.empty(),
                Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                DB, START.minusNanos(1000), success, Optional.empty(), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                new BatchStepAttempt(1, RUN, BatchStep.BACKUP_DB, 2, START, true),
                END,
                success,
                Optional.empty(),
                Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                DB, END, success, Optional.of(FIXTURE_COMMAND_FAILURE_38148BF2), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                DB, END, success, Optional.empty(), Optional.of("altered")));
    var otherRun = new BatchRun(new UUID(0, 99), RUN.cutoff());
    for (var wrong :
        List.of(
            new BatchStepAttempt(1, RUN, BatchStep.BACKUP_CONFIG, 2, START, false),
            new BatchStepAttempt(2, RUN, BatchStep.BACKUP_DB, 2, START, false),
            new BatchStepAttempt(2, otherRun, BatchStep.BACKUP_CONFIG, 2, START, false),
            new BatchStepAttempt(
                2, RUN, BatchStep.BACKUP_CONFIG, 2, START.plusSeconds(1), false))) {
      var row =
          new BackupStepRepository.Terminal(
              wrong, END, success, Optional.empty(), Optional.empty());
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningDatabaseSession.BackupObservation(List.of(d, row), List.of()));
    }
    var endChanged =
        new BackupStepRepository.Terminal(
            config, END.plusSeconds(1), success, Optional.empty(), Optional.empty());
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(d, endChanged), List.of()));
    var duplicate =
        new BackupStepRepository.Terminal(
            new BatchStepAttempt(1, RUN, BatchStep.BACKUP_CONFIG, 2, START, false),
            END,
            success,
            Optional.empty(),
            Optional.empty());
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(d, duplicate), List.of()));
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    var failure =
        new BackupStepRepository.Terminal(
            config,
            END,
            failed,
            Optional.of(FIXTURE_COMMAND_FAILURE_38148BF2),
            Optional.of(FIXTURE_BATCH_COMMAND_FAILED_7D52C711));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(d, failure), List.of()));
    var currentStart = END.plusSeconds(2);
    var skipped =
        new BatchStepResult(
            BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.ALREADY_SUCCESSFUL);
    var sd =
        new BackupStepRepository.Terminal(
            new BatchStepAttempt(11, RUN, BatchStep.BACKUP_DB, 3, currentStart, true),
            currentStart,
            skipped,
            Optional.of(FIXTURE_ALREADY_SUCCESSFUL_0E316429),
            Optional.of(FIXTURE_STEP_ALREADY_SUCCESSFUL_FOR_BUSINESS_DAT_B0F7DC85));
    var sc =
        new BackupStepRepository.Terminal(
            new BatchStepAttempt(12, RUN, BatchStep.BACKUP_CONFIG, 3, currentStart, true),
            currentStart,
            skipped,
            Optional.of(FIXTURE_ALREADY_SUCCESSFUL_0E316429),
            Optional.of(FIXTURE_STEP_ALREADY_SUCCESSFUL_FOR_BUSINESS_DAT_B0F7DC85));
    assertEquals(
        List.of(d, c),
        new MorningDatabaseSession.BackupObservation(List.of(sd, sc), List.of(d, c)).prior());
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(sd, sc), List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(d, c), List.of(d, c)));
    for (var wrong :
        List.of(
            new BatchStepAttempt(11, RUN, BatchStep.BACKUP_DB, 2, START, false),
            new BatchStepAttempt(1, RUN, BatchStep.BACKUP_CONFIG, 2, START, false),
            new BatchStepAttempt(1, otherRun, BatchStep.BACKUP_DB, 2, START, false),
            new BatchStepAttempt(1, RUN, BatchStep.BACKUP_DB, 3, START, false))) {
      var row =
          new BackupStepRepository.Terminal(
              wrong, END, success, Optional.empty(), Optional.empty());
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningDatabaseSession.BackupObservation(List.of(sd, sc), List.of(row, c)));
    }
    var late =
        new BackupStepRepository.Terminal(
            DB, currentStart.plusSeconds(1), success, Optional.empty(), Optional.empty());
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(sd, sc), List.of(late, c)));
    var priorFailure =
        new BackupStepRepository.Terminal(
            DB,
            END,
            failed,
            Optional.of(FIXTURE_COMMAND_FAILURE_38148BF2),
            Optional.of(FIXTURE_BATCH_COMMAND_FAILED_7D52C711));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.BackupObservation(
                List.of(sd, sc), List.of(priorFailure, c)));
    var unavailable =
        new BatchStepResult(
            BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.BACKUP_UNAVAILABLE);
    var wrongSkip =
        new BackupStepRepository.Terminal(
            sd.attempt(),
            currentStart,
            unavailable,
            Optional.of("BACKUP_UNAVAILABLE"),
            Optional.of("verified backup unavailable"));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.BackupObservation(List.of(wrongSkip, sc), List.of(d, c)));
    var wrongEnd =
        new BackupStepRepository.Terminal(
            sd.attempt(), currentStart.plusSeconds(1), skipped, sd.errorCode(), sd.errorSummary());
    var wrongEndConfig =
        new BackupStepRepository.Terminal(
            sc.attempt(), currentStart.plusSeconds(1), skipped, sc.errorCode(), sc.errorSummary());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.BackupObservation(
                List.of(wrongEnd, wrongEndConfig), List.of(d, c)));
  }

  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  static final Instant END = Instant.parse("2026-09-13T02:00:01Z");
  static final BatchStepAttempt DB =
      new BatchStepAttempt(1, RUN, BatchStep.BACKUP_DB, 2, START, false);

  static Map<String, Object> literal() {
    var m = new HashMap<String, Object>();
    m.put("id", 1L);
    m.put("run_id", RUN.id());
    m.put("business_date", LocalDate.of(2026, 9, 13));
    m.put("step", "BACKUP_DB");
    m.put("attempt", 2);
    m.put("started_at", START.atOffset(ZoneOffset.UTC));
    m.put(FIXTURE_ENDED_AT_E151E393, END.atOffset(ZoneOffset.UTC));
    m.put(FIXTURE_STATUS_CFC31BCC, "SUCCESS");
    m.put(FIXTURE_TARGET_COUNT_5B6567D4, 1L);
    m.put(FIXTURE_SUCCESS_COUNT_716E5185, 1L);
    m.put(FIXTURE_FAILURE_COUNT_C7E67F21, 0L);
    m.put(FIXTURE_BYTE_COUNT_6D76E237, 26L);
    m.put(FIXTURE_ERROR_CODE_B886CCEF, null);
    m.put(FIXTURE_ERROR_SUMMARY_3F58BF23, null);
    return m;
  }

  static ResultSet row(Map<String, Object> input) {
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, m, args) -> {
              if (m.getName().equals("getObject") || m.getName().equals("getString"))
                return input.get(args[0]);
              throw new AssertionError("unexpected JDBC operation " + m.getName());
            });
  }

  @Test
  void isscomp001RetainsEveryTerminalValueForSuccessFailureAndSkip() throws Exception {
    var actual = BackupStepRepository.readTerminal(row(literal()), DB, END);
    assertEquals(DB, actual.attempt());
    assertEquals(END, actual.ended());
    assertEquals(BatchStepResult.Status.SUCCESS, actual.result().status());
    assertEquals(26, actual.result().bytes());
    assertEquals(Optional.empty(), actual.errorCode());
    assertEquals(Optional.empty(), actual.errorSummary());
    assertFalse(actual.toString().contains(RUN.id().toString()));
    var failed = literal();
    failed.put(FIXTURE_STATUS_CFC31BCC, "FAILED");
    failed.put(FIXTURE_SUCCESS_COUNT_716E5185, 0L);
    failed.put(FIXTURE_FAILURE_COUNT_C7E67F21, 1L);
    failed.put(FIXTURE_BYTE_COUNT_6D76E237, 0L);
    failed.put(FIXTURE_ERROR_CODE_B886CCEF, FIXTURE_COMMAND_FAILURE_38148BF2);
    failed.put(FIXTURE_ERROR_SUMMARY_3F58BF23, FIXTURE_BATCH_COMMAND_FAILED_7D52C711);
    var f = BackupStepRepository.readTerminal(row(failed), DB, END);
    assertEquals(FIXTURE_COMMAND_FAILURE_38148BF2, f.errorCode().orElseThrow());
    assertEquals(FIXTURE_BATCH_COMMAND_FAILED_7D52C711, f.errorSummary().orElseThrow());
    assertEquals(1, f.result().failure());
    var skipped = literal();
    skipped.put(FIXTURE_STATUS_CFC31BCC, "SKIPPED");
    skipped.put(FIXTURE_ENDED_AT_E151E393, START.atOffset(ZoneOffset.UTC));
    for (String key :
        List.of(
            FIXTURE_TARGET_COUNT_5B6567D4,
            FIXTURE_SUCCESS_COUNT_716E5185,
            FIXTURE_FAILURE_COUNT_C7E67F21,
            FIXTURE_BYTE_COUNT_6D76E237)) skipped.put(key, 0L);
    skipped.put(FIXTURE_ERROR_CODE_B886CCEF, FIXTURE_ALREADY_SUCCESSFUL_0E316429);
    skipped.put(
        FIXTURE_ERROR_SUMMARY_3F58BF23, FIXTURE_STEP_ALREADY_SUCCESSFUL_FOR_BUSINESS_DAT_B0F7DC85);
    var s =
        BackupStepRepository.readTerminal(
            row(skipped), new BatchStepAttempt(1, RUN, BatchStep.BACKUP_DB, 2, START, true), END);
    assertEquals(START, s.ended());
    assertTrue(s.attempt().skipped());
    assertEquals(0, s.result().target());
  }

  @Test
  void isscomp002MissingOrAlteredColumnAndUnknownJdbcAreNotNormal() throws Exception {
    for (String key : literal().keySet()) {
      if (key.equals(FIXTURE_ERROR_CODE_B886CCEF) || key.equals(FIXTURE_ERROR_SUMMARY_3F58BF23))
        continue;
      var input = literal();
      input.put(key, null);
      assertThrows(
          SQLException.class, () -> BackupStepRepository.readTerminal(row(input), DB, END), key);
    }
    Map<String, Object> changes =
        Map.ofEntries(
            Map.entry("id", 2L),
            Map.entry("run_id", new UUID(0, 1)),
            Map.entry("business_date", LocalDate.of(2026, 9, 14)),
            Map.entry("step", "BACKUP_CONFIG"),
            Map.entry("attempt", 3),
            Map.entry("started_at", START.plusSeconds(1).atOffset(ZoneOffset.UTC)),
            Map.entry(FIXTURE_ENDED_AT_E151E393, END.plusSeconds(1).atOffset(ZoneOffset.UTC)),
            Map.entry(FIXTURE_STATUS_CFC31BCC, "RUNNING"),
            Map.entry(FIXTURE_TARGET_COUNT_5B6567D4, -1L),
            Map.entry(FIXTURE_SUCCESS_COUNT_716E5185, -1L),
            Map.entry(FIXTURE_FAILURE_COUNT_C7E67F21, 1L),
            Map.entry(FIXTURE_BYTE_COUNT_6D76E237, -1L),
            Map.entry(FIXTURE_ERROR_CODE_B886CCEF, "UNKNOWN"),
            Map.entry(FIXTURE_ERROR_SUMMARY_3F58BF23, "altered"));
    for (var entry : changes.entrySet()) {
      var input = literal();
      input.put(entry.getKey(), entry.getValue());
      assertThrows(
          SQLException.class,
          () -> BackupStepRepository.readTerminal(row(input), DB, END),
          entry.getKey());
    }
    var reverse = literal();
    reverse.put(FIXTURE_ENDED_AT_E151E393, START.minusNanos(1000).atOffset(ZoneOffset.UTC));
    assertThrows(
        SQLException.class, () -> BackupStepRepository.readTerminal(row(reverse), DB, END));
    var skipped = literal();
    skipped.put(FIXTURE_STATUS_CFC31BCC, "SKIPPED");
    skipped.put(FIXTURE_ERROR_CODE_B886CCEF, FIXTURE_ALREADY_SUCCESSFUL_0E316429);
    skipped.put(
        FIXTURE_ERROR_SUMMARY_3F58BF23, FIXTURE_STEP_ALREADY_SUCCESSFUL_FOR_BUSINESS_DAT_B0F7DC85);
    for (String key :
        List.of(
            FIXTURE_TARGET_COUNT_5B6567D4,
            FIXTURE_SUCCESS_COUNT_716E5185,
            FIXTURE_FAILURE_COUNT_C7E67F21,
            FIXTURE_BYTE_COUNT_6D76E237)) skipped.put(key, 0L);
    assertThrows(
        SQLException.class, () -> BackupStepRepository.readTerminal(row(skipped), DB, END));
    var unknown = new IllegalArgumentException("private driver failure");
    var driver =
        (ResultSet)
            Proxy.newProxyInstance(
                ResultSet.class.getClassLoader(),
                new Class<?>[] {ResultSet.class},
                (p, m, a) -> {
                  throw unknown;
                });
    assertSame(
        unknown,
        assertThrows(
            IllegalArgumentException.class,
            () -> BackupStepRepository.readTerminal(driver, DB, END)));
    assertThrows(
        NullPointerException.class, () -> BackupStepRepository.readTerminal(null, DB, END));
    assertThrows(
        NullPointerException.class,
        () -> BackupStepRepository.readTerminal(row(literal()), null, END));
    assertThrows(
        NullPointerException.class,
        () -> BackupStepRepository.readTerminal(row(literal()), DB, null));
  }
}
