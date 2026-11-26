package dev.codex.schubert.nk.batch.repository;

import static dev.codex.schubert.nk.batch.repository.BackupTerminalRows.DB;
import static dev.codex.schubert.nk.batch.repository.BackupTerminalRows.END;
import static dev.codex.schubert.nk.batch.repository.BackupTerminalRows.RUN;
import static dev.codex.schubert.nk.batch.repository.BackupTerminalRows.START;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BAT-TERM001 through TERM006; synthetic, borrowed JDBC observations. */
final class BackupTerminalReadTest {
  private static final String ID = "id";
  private static final String RUN_ID = "run_id";
  private static final String BUSINESS_DATE = "business_date";
  private static final String STEP = "step";
  private static final String ATTEMPT = "attempt";
  private static final String STARTED = "started_at";
  private static final String ENDED = "ended_at";
  private static final String STATUS = "status";
  private static final String TARGET = "target_count";
  private static final String SUCCESS = "success_count";
  private static final String FAILURE = "failure_count";
  private static final String BYTES = "byte_count";
  private static final String ERROR_CODE = "error_code";
  private static final String ERROR_SUMMARY = "error_summary";
  private static final String ALREADY_SUCCESSFUL = "ALREADY_SUCCESSFUL";
  private static final String SKIP_SUMMARY = "step already successful for business date";
  private static final String MARKER = "public fixture mismatch";
  private static final Instant OBSERVED = END.plusSeconds(1);

  private record Column(String name, Class<?> type) {}

  private static final List<Column> COLUMNS =
      List.of(
          new Column(ID, Long.class),
          new Column(RUN_ID, UUID.class),
          new Column(BUSINESS_DATE, LocalDate.class),
          new Column(STEP, String.class),
          new Column(ATTEMPT, Integer.class),
          new Column(STARTED, OffsetDateTime.class),
          new Column(ENDED, OffsetDateTime.class),
          new Column(STATUS, String.class),
          new Column(TARGET, Long.class),
          new Column(SUCCESS, Long.class),
          new Column(FAILURE, Long.class),
          new Column(BYTES, Long.class),
          new Column(ERROR_CODE, String.class),
          new Column(ERROR_SUMMARY, String.class));

  @Test
  void term001FixedSuccessRowIsReadInColumnOrderWithoutTakingOwnership() throws SQLException {
    var seen = new ArrayList<Column>();
    var values = BackupTerminalRows.literal();
    ResultSet row =
        (ResultSet)
            Proxy.newProxyInstance(
                ResultSet.class.getClassLoader(),
                new Class<?>[] {ResultSet.class},
                (proxy, method, args) -> {
                  var index = seen.size();
                  assertTrue(index < COLUMNS.size());
                  var expected = COLUMNS.get(index);
                  if (expected.type() == String.class) {
                    assertEquals("getString", method.getName());
                    assertEquals(1, args.length);
                  } else {
                    assertEquals("getObject", method.getName());
                    assertEquals(2, args.length);
                    assertEquals(expected.type(), args[1]);
                  }
                  assertEquals(expected.name(), args[0]);
                  seen.add(expected);
                  return values.get(args[0]);
                });
    var terminal = BackupStepRepository.readTerminal(row, DB, OBSERVED);
    assertEquals(COLUMNS, seen);
    assertEquals(DB, terminal.attempt());
    assertEquals(END, terminal.ended());
    assertEquals(BatchStepResult.Status.SUCCESS, terminal.result().status());
    assertEquals(1L, terminal.result().target());
    assertEquals(1L, terminal.result().success());
    assertEquals(0L, terminal.result().failure());
    assertEquals(26L, terminal.result().bytes());
    assertEquals(BatchStepResult.Reason.NONE, terminal.result().reason());
    assertEquals(Optional.empty(), terminal.errorCode());
    assertEquals(Optional.empty(), terminal.errorSummary());
    assertEquals("BackupTerminal[actual=<redacted>]", terminal.toString());
    var equal = BackupStepRepository.readTerminal(BackupTerminalRows.row(values), DB, OBSERVED);
    assertEquals(terminal, equal);
    var terminals = new HashSet<BackupStepRepository.Terminal>();
    assertTrue(terminals.add(terminal));
    assertTrue(terminals.contains(equal));
  }

  @Test
  void term002SkippedRowKeepsTheFixedReasonAndRequiresASkippedHandle() throws SQLException {
    var values = BackupTerminalRows.literal();
    values.put(STATUS, "SKIPPED");
    values.put(ERROR_CODE, ALREADY_SUCCESSFUL);
    values.put(ERROR_SUMMARY, SKIP_SUMMARY);
    for (String column : List.of(TARGET, SUCCESS, FAILURE, BYTES)) {
      values.put(column, 0L);
    }
    var skipped = new BatchStepAttempt(DB.id(), RUN, BatchStep.BACKUP_DB, 2, START, true);
    var terminal = BackupStepRepository.readTerminal(BackupTerminalRows.row(values), skipped, END);
    assertTrue(terminal.attempt().skipped());
    assertEquals(END, terminal.ended());
    assertEquals(BatchStepResult.Status.SKIPPED, terminal.result().status());
    assertEquals(BatchStepResult.Reason.ALREADY_SUCCESSFUL, terminal.result().reason());
    assertEquals(Optional.of(ALREADY_SUCCESSFUL), terminal.errorCode());
    assertEquals(Optional.of(SKIP_SUMMARY), terminal.errorSummary());
    assertEquals(
        List.of(0L, 0L, 0L, 0L),
        List.of(
            terminal.result().target(),
            terminal.result().success(),
            terminal.result().failure(),
            terminal.result().bytes()));
    assertThrows(
        SQLDataException.class,
        () -> BackupStepRepository.readTerminal(BackupTerminalRows.row(values), DB, END));
  }

  @Test
  void term003EachStoredIdentityAndTheObservationCeilingAreRequired() {
    Map<String, Object> differences =
        Map.of(
            ID,
            9L,
            RUN_ID,
            new UUID(0, 9),
            BUSINESS_DATE,
            LocalDate.of(2026, 9, 14),
            STEP,
            "BACKUP_CONFIG",
            ATTEMPT,
            3,
            STARTED,
            START.plusSeconds(1).atOffset(ZoneOffset.UTC),
            ENDED,
            OBSERVED.plusSeconds(1).atOffset(ZoneOffset.UTC));
    differences.forEach(BackupTerminalReadTest::rejectAlteredColumn);
  }

  @Test
  void term004InvalidTerminalDataDoesNotPublishRawInputOrAResult() {
    rejectAlteredColumn(STATUS, MARKER);
    rejectAlteredColumn(ERROR_CODE, MARKER);
    rejectAlteredColumn(ERROR_SUMMARY, MARKER);
    rejectAlteredColumn(TARGET, -1L);
    rejectAlteredColumn(ENDED, START.minusSeconds(1).atOffset(ZoneOffset.UTC));
  }

  @Test
  void term005RequiredColumnsAndNonNullArgumentsFailClosed() {
    for (var column : COLUMNS.subList(0, 12)) {
      rejectAlteredColumn(column.name(), null);
    }
    var row = BackupTerminalRows.row(BackupTerminalRows.literal());
    assertThrows(
        NullPointerException.class, () -> BackupStepRepository.readTerminal(null, DB, OBSERVED));
    assertThrows(
        NullPointerException.class, () -> BackupStepRepository.readTerminal(row, null, OBSERVED));
    assertThrows(
        NullPointerException.class, () -> BackupStepRepository.readTerminal(row, DB, null));
  }

  @Test
  void term006TerminalValueRechecksStepKindSkipAndClosedErrorCode() {
    var success =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 1, 1, 0, 26, BatchStepResult.Reason.NONE);
    var skipped =
        new BatchStepResult(
            BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.ALREADY_SUCCESSFUL);
    var otherStep = new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 2, START, false);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                otherStep, END, success, Optional.empty(), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                DB, END, skipped, Optional.of(ALREADY_SUCCESSFUL), Optional.of(SKIP_SUMMARY)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupStepRepository.Terminal(
                DB, END, success, Optional.of(MARKER), Optional.empty()));
  }

  private static void rejectAlteredColumn(String column, Object unexpected) {
    var values = BackupTerminalRows.literal();
    values.put(column, unexpected);
    var error =
        assertThrows(
            SQLDataException.class,
            () -> BackupStepRepository.readTerminal(BackupTerminalRows.row(values), DB, OBSERVED));
    assertFalse(error.getMessage().contains(MARKER));
    assertNull(error.getCause());
  }
}
