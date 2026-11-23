package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** SS332 SSC-056. Supplied row values and borrowed JDBC interfaces only. */
final class BackupFailureUtcProjectionTest {
  private static final UUID RUN_ID = new UUID(19, 24);
  private static final Instant CUTOFF = Instant.parse("2026-09-12T15:00:00Z");
  private static final Instant STARTED = Instant.parse("2026-09-13T02:00:00.123456Z");
  private static final Instant ENDED = Instant.parse("2026-09-13T02:00:03.654321Z");
  private static final OffsetDateTime DISPLAY_START =
      OffsetDateTime.parse("2026-09-13T11:00:00.123456+09:00");
  private static final OffsetDateTime DISPLAY_END =
      OffsetDateTime.parse("2026-09-12T21:00:03.654321-05:00");
  private static final List<String> COMPLETE =
      List.of("row-1", "stmt-1", "row-2", "stmt-2", "row-3", "stmt-3", "row-4", "stmt-4");
  private static final int FIRST_BACKUP_QUERY = 2;
  private static final String FIRST_BACKUP_STATEMENT = "stmt-2";

  private enum ReadFault {
    NONE,
    MISSING_STATEMENT,
    MISSING_RESULT_SET,
    EMPTY_RESULT_SET,
    EXTRA_RESULT_ROW,
    BOTH_CLOSES_AFTER_REJECTION,
    REPEATED_ROW_FAILURE,
    REPEATED_STATEMENT_FAILURE,
    DISTINCT_CLOSES_AFTER_RUNTIME,
    ROW_CLOSE_ONLY,
    STATEMENT_CLOSE_ONLY,
    INITIAL_INCONSISTENT_RUN,
    FINAL_INCONSISTENT_RUN
  }

  /** PT-BAT-BACKUP-UTC001. */
  @Test
  void utc001SameInstantsAtDifferentOffsetsCompleteBothRowsAndRecheck() {
    var fixture = new Fixture(DISPLAY_START, DISPLAY_END);
    assertDoesNotThrow(fixture::verify);
    assertEquals(COMPLETE, fixture.closed);
  }

  /** PT-BAT-BACKUP-UTC002. */
  @Test
  void utc002SameWallTimeAtDifferentOffsetAndOneMicrosecondDriftStillFail() {
    rejects(OffsetDateTime.parse("2026-09-13T02:00:00.123456+09:00"), DISPLAY_END);
    rejects(DISPLAY_START, OffsetDateTime.parse("2026-09-12T21:00:03.654322-05:00"));
  }

  /** PT-BAT-BACKUP-UTC003. */
  @Test
  void utc003MissingEitherRequiredTimeFailsWithFixedDiagnosticAndOwnedClose() {
    rejects(null, DISPLAY_END);
    rejects(DISPLAY_START, null);
  }

  /** PT-BAT-BACKUP-UTC004. */
  @Test
  void utc004EveryOtherRequiredProjectionColumnRejectsNullIndependently() {
    for (String name :
        List.of(
            "id",
            "run_id",
            "business_date",
            "step",
            "attempt",
            "status",
            "target_count",
            "success_count",
            "failure_count",
            "byte_count",
            "error_code",
            "error_summary")) {
      var fixture = new Fixture(DISPLAY_START, DISPLAY_END, ReadFault.NONE, name);
      rejectsProjection(fixture, COMPLETE.subList(0, 4));
    }
  }

  /** PT-BAT-BACKUP-UTC005. */
  @Test
  void utc005MissingHandlesAndUnexpectedRowCountsRetainOnlyOwnedCloses() {
    rejectsProjection(fixture(ReadFault.MISSING_STATEMENT), COMPLETE.subList(0, 2));
    rejectsProjection(
        fixture(ReadFault.MISSING_RESULT_SET), List.of("row-1", "stmt-1", FIRST_BACKUP_STATEMENT));
    for (ReadFault fault : List.of(ReadFault.EMPTY_RESULT_SET, ReadFault.EXTRA_RESULT_ROW)) {
      rejectsProjection(fixture(fault), COMPLETE.subList(0, 4));
    }
  }

  /** PT-BAT-BACKUP-UTC006. */
  @Test
  void utc006RunIdentityMustRemainConsistentBeforeAndAfterBothRows() {
    var initial = fixture(ReadFault.INITIAL_INCONSISTENT_RUN);
    var end = fixture(ReadFault.FINAL_INCONSISTENT_RUN);
    for (var fixture : List.of(initial, end)) {
      var failure = assertThrows(IOException.class, fixture::verify);
      assertEquals("failed backup run identity unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    assertEquals(COMPLETE.subList(0, 2), initial.closed);
    assertEquals(COMPLETE, end.closed);
  }

  /** PT-BAT-BACKUP-UTC007. */
  @Test
  void utc007ProjectionAndBothOwnedCloseFailuresKeepOneFixedDiagnostic() {
    rejectsProjection(fixture(ReadFault.BOTH_CLOSES_AFTER_REJECTION), COMPLETE.subList(0, 4));
  }

  /** PT-BAT-BACKUP-UTC008. */
  @Test
  void utc008SameProviderExceptionFromUseAndReleaseKeepsFixedDiagnostic() {
    var row = fixture(ReadFault.REPEATED_ROW_FAILURE);
    rejectsProjection(row, COMPLETE.subList(0, 4));
    assertEquals(0, row.repeated.getSuppressed().length);
    var statement = fixture(ReadFault.REPEATED_STATEMENT_FAILURE);
    rejectsProjection(statement, List.of("row-1", "stmt-1", FIRST_BACKUP_STATEMENT));
    assertEquals(0, statement.repeated.getSuppressed().length);
  }

  /** PT-BAT-BACKUP-UTC009. */
  @Test
  void utc009DistinctCloseFailuresRemainOrderedOnTheOriginalRuntimeFailure() {
    var fixture = fixture(ReadFault.DISTINCT_CLOSES_AFTER_RUNTIME);
    var actual = assertThrows(IllegalStateException.class, fixture::verify);
    assertSame(fixture.primaryRuntime, actual);
    assertEquals(List.of(fixture.rowClose, fixture.statementClose), List.of(actual.getSuppressed()));
    assertEquals(COMPLETE.subList(0, 4), fixture.closed);
  }

  /** PT-BAT-BACKUP-UTC010. */
  @Test
  void utc010EachCloseOnlyFailureUsesTheFixedDiagnosticAfterBothReleases() {
    for (ReadFault fault : List.of(ReadFault.ROW_CLOSE_ONLY, ReadFault.STATEMENT_CLOSE_ONLY)) {
      rejectsProjection(fixture(fault), COMPLETE.subList(0, 4));
    }
  }

  private static Fixture fixture(ReadFault fault) {
    return new Fixture(DISPLAY_START, DISPLAY_END, fault, null);
  }

  private static void rejects(@Nullable OffsetDateTime start, @Nullable OffsetDateTime end) {
    rejectsProjection(new Fixture(start, end), COMPLETE.subList(0, 4));
  }

  private static void rejectsProjection(Fixture fixture, List<String> expectedCloses) {
    var failure = assertThrows(IOException.class, fixture::verify);
    assertEquals("failed backup observation unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(expectedCloses, fixture.closed);
  }

  private static final class Fixture {
    private final @Nullable OffsetDateTime start;
    private final @Nullable OffsetDateTime end;
    private final ReadFault fault;
    private final @Nullable String missingColumn;
    private final List<String> closed = new ArrayList<>();
    private final SQLException repeated = new SQLException("synthetic repeat failure");
    private final SQLException rowClose = new SQLException("synthetic result close failure");
    private final SQLException statementClose = new SQLException("synthetic statement close failure");
    private final IllegalStateException primaryRuntime =
        new IllegalStateException("synthetic row read failure");
    private int prepared;

    Fixture(@Nullable OffsetDateTime start, @Nullable OffsetDateTime end) {
      this(start, end, ReadFault.NONE, null);
    }

    Fixture(
        @Nullable OffsetDateTime start,
        @Nullable OffsetDateTime end,
        ReadFault fault,
        @Nullable String missingColumn) {
      this.start = start;
      this.end = end;
      this.fault = fault;
      this.missingColumn = missingColumn;
    }

    void verify() throws IOException {
      var run = new BatchRun(RUN_ID, CUTOFF);
      var db = new BatchStepAttempt(7, run, BatchStep.BACKUP_DB, 4, STARTED, false);
      var config = new BatchStepAttempt(8, run, BatchStep.BACKUP_CONFIG, 4, STARTED, false);
      new BackupFailureSnapshot(db, config, ENDED).verifyLatest(connection(), () -> 5_000_000_000L);
    }

    private Connection connection() {
      return proxy(
          Connection.class,
          (ignored, method, args) ->
              switch (method.getName()) {
                case "getAutoCommit", "isReadOnly" -> false;
                case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                case "prepareStatement" -> {
                  prepared++;
                  yield statement(prepared, (String) args[0]);
                }
                default -> throw new AssertionError("unexpected operation on borrowed Connection");
              });
    }

    private @Nullable PreparedStatement statement(int position, String sql) {
      boolean identity = position == 1 || position == 4;
      String table = identity ? "maintenance_read_run_references" : "from schubert.batch_runs";
      assertTrue(sql.contains(table));
      if (position == FIRST_BACKUP_QUERY && fault == ReadFault.MISSING_STATEMENT) return null;
      return proxy(
          PreparedStatement.class,
          (ignored, method, args) ->
              switch (method.getName()) {
                case "setQueryTimeout" -> {
                  assertEquals(5, args[0]);
                  yield null;
                }
                case "setObject" -> {
                  if (Integer.valueOf(1).equals(args[0])) assertEquals(RUN_ID, args[1]);
                  else assertEquals(OffsetDateTime.parse("2026-09-12T15:00:00Z"), args[1]);
                  yield null;
                }
                case "setString" -> {
                  assertEquals(2, args[0]);
                  assertEquals(
                      position == FIRST_BACKUP_QUERY ? "BACKUP_DB" : "BACKUP_CONFIG", args[1]);
                  yield null;
                }
                case "executeQuery" -> {
                  if (position == FIRST_BACKUP_QUERY && fault == ReadFault.REPEATED_STATEMENT_FAILURE)
                    throw repeated;
                  yield position == FIRST_BACKUP_QUERY && fault == ReadFault.MISSING_RESULT_SET
                      ? null
                      : rows(position, identity);
                }
                case "close" -> {
                  closed.add("stmt-" + position);
                  if (position == FIRST_BACKUP_QUERY) checkStatementClose();
                  yield null;
                }
                default -> throw new AssertionError("unexpected statement operation");
              });
    }

    private ResultSet rows(int position, boolean identity) {
      int rowCount = 1;
      if (position == FIRST_BACKUP_QUERY) {
        if (fault == ReadFault.EMPTY_RESULT_SET || fault == ReadFault.BOTH_CLOSES_AFTER_REJECTION)
          rowCount = 0;
        if (fault == ReadFault.EXTRA_RESULT_ROW) rowCount = 2;
      }
      final int expectedRows = rowCount;
      int[] advanced = new int[1];
      return proxy(
          ResultSet.class,
          (ignored, method, args) ->
              switch (method.getName()) {
                case "next" -> {
                  if (position == FIRST_BACKUP_QUERY) checkRowRead();
                  advanced[0]++;
                  yield advanced[0] <= expectedRows;
                }
                case "getObject" ->
                    identity
                        ? identityValue(position, (String) args[0])
                        : field(position, (String) args[0]);
                case "close" -> {
                  closed.add("row-" + position);
                  if (position == FIRST_BACKUP_QUERY) checkRowClose();
                  yield null;
                }
                default -> throw new AssertionError("unexpected result operation " + method);
              });
    }

    private void checkStatementClose() throws SQLException {
      switch (fault) {
        case REPEATED_STATEMENT_FAILURE -> throw repeated;
        case BOTH_CLOSES_AFTER_REJECTION, DISTINCT_CLOSES_AFTER_RUNTIME, STATEMENT_CLOSE_ONLY ->
            throw statementClose;
        default -> {}
      }
    }

    private void checkRowRead() throws SQLException {
      switch (fault) {
        case REPEATED_ROW_FAILURE -> throw repeated;
        case DISTINCT_CLOSES_AFTER_RUNTIME -> throw primaryRuntime;
        default -> {}
      }
    }

    private void checkRowClose() throws SQLException {
      switch (fault) {
        case REPEATED_ROW_FAILURE -> throw repeated;
        case BOTH_CLOSES_AFTER_REJECTION, DISTINCT_CLOSES_AFTER_RUNTIME, ROW_CLOSE_ONLY ->
            throw rowClose;
        default -> {}
      }
    }

    private boolean identityValue(int position, String name) {
      if (!"identity_consistent".equals(name)) return true;
      return !(position == 1 && fault == ReadFault.INITIAL_INCONSISTENT_RUN)
          && !(position == 4 && fault == ReadFault.FINAL_INCONSISTENT_RUN);
    }

    private @Nullable Object field(int position, String name) {
      if (name.equals(missingColumn)) return null;
      return switch (name) {
        case "id" -> position == FIRST_BACKUP_QUERY ? 7L : 8L;
        case "run_id" -> RUN_ID;
        case "business_date" -> LocalDate.parse("2026-09-13");
        case "step" -> position == FIRST_BACKUP_QUERY ? "BACKUP_DB" : "BACKUP_CONFIG";
        case "attempt" -> 4;
        case "started_at" -> start;
        case "ended_at" -> end;
        case "status" -> "FAILED";
        case "target_count", "failure_count" -> 1L;
        case "success_count", "byte_count" -> 0L;
        case "error_code" -> "COMMAND_FAILURE";
        case "error_summary" -> "batch command failed";
        default -> throw new AssertionError("unexpected projection column " + name);
      };
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
