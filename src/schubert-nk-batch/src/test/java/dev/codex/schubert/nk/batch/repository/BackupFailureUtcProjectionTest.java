package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
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

  private static void rejects(@Nullable OffsetDateTime start, @Nullable OffsetDateTime end) {
    var fixture = new Fixture(start, end);
    var failure = assertThrows(IOException.class, fixture::verify);
    assertEquals("failed backup observation unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(COMPLETE.subList(0, 4), fixture.closed);
  }

  private static final class Fixture {
    private final @Nullable OffsetDateTime start;
    private final @Nullable OffsetDateTime end;
    private final List<String> closed = new ArrayList<>();
    private int prepared;

    Fixture(@Nullable OffsetDateTime start, @Nullable OffsetDateTime end) {
      this.start = start;
      this.end = end;
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
                case "prepareStatement" -> statement(++prepared, (String) args[0]);
                default -> throw new AssertionError("unexpected operation on borrowed Connection");
              });
    }

    private PreparedStatement statement(int position, String sql) {
      boolean identity = position == 1 || position == 4;
      String table = identity ? "maintenance_read_run_references" : "from schubert.batch_runs";
      assertTrue(sql.contains(table));
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
                  assertEquals(position == 2 ? "BACKUP_DB" : "BACKUP_CONFIG", args[1]);
                  yield null;
                }
                case "executeQuery" -> rows(position, identity);
                case "close" -> {
                  closed.add("stmt-" + position);
                  yield null;
                }
                default -> throw new AssertionError("unexpected statement operation");
              });
    }

    private ResultSet rows(int position, boolean identity) {
      boolean[] advanced = new boolean[1];
      return proxy(
          ResultSet.class,
          (ignored, method, args) ->
              switch (method.getName()) {
                case "next" -> {
                  boolean next = !advanced[0];
                  advanced[0] = true;
                  yield next;
                }
                case "getObject" -> identity ? Boolean.TRUE : field(position, (String) args[0]);
                case "close" -> {
                  closed.add("row-" + position);
                  yield null;
                }
                default -> throw new AssertionError("unexpected result operation " + method);
              });
    }

    private @Nullable Object field(int position, String name) {
      return switch (name) {
        case "id" -> position == 2 ? 7L : 8L;
        case "run_id" -> RUN_ID;
        case "business_date" -> LocalDate.parse("2026-09-13");
        case "step" -> position == 2 ? "BACKUP_DB" : "BACKUP_CONFIG";
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
