package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupKind;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.UUID;
import java.util.function.LongSupplier;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

final class StepCleanupTransactionPortTest {
  private static final String BEGIN = "begin";
  private static final String COMMIT = "commit";
  private static final String RESTORE = "restore";
  private static final String ROLLBACK = "rollback";
  private static final String STOPS = "cleanup did not complete";
  private static final String FIXTURE = "synthetic failure";
  private static final String REFERENCES =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final String CHUNK =
      "select target_count,deleted_count,skipped_count,step_target_count,step_success_count,complete,reason_code"
          + " from schubert.maintenance_execute_cleanup_step(?,?,?,?,?,?,?)";
  private static final UUID ID = new UUID(0, 57);
  private static final BatchStepAttempt ATTEMPT =
      new BatchStepAttempt(
          31,
          new BatchRun(ID, Instant.parse("2026-11-18T00:00:00Z")),
          BatchStep.CLEAN_QUESTION,
          2,
          Instant.parse("2026-11-18T00:01:00Z"),
          false);
  private static final OffsetDateTime CUTOFF = OffsetDateTime.parse("2026-11-18T00:00:00Z");
  private static final OffsetDateTime START = OffsetDateTime.parse("2026-11-18T00:01:00Z");
  private static final String DB = "DATABASE_FAILURE";
  private static final long LIMIT = 1_800_000_000_000L;

  @Test
  void steptx461001ContinuationUsesOnlyConfirmedChunksAndKeepsFkDeferred() {
    for (boolean deferred : List.of(false, true)) {
      var f = new Fixture();
      f.chunks.add(new Projection(1, 5L, false, "OK"));
      f.chunks.add(new Projection(0, 5L, !deferred, deferred ? "FOREIGN_KEY_CONFLICT" : "OK"));
      StepCleanupSummary result = run(f);
      assertEquals(new CleanupCounts(4, 4, 0), result.before());
      assertEquals(new CleanupCounts(5, 5, 0), result.after());
      assertEquals(new CleanupCounts(1, 1, 0), result.callCounts());
      assertEquals(!deferred, result.complete());
      assertEquals(List.of(BEGIN, COMMIT, RESTORE, BEGIN, COMMIT, RESTORE), f.events);
      assertTrue(f.autoCommit);
      f.closedExactly(6);
    }
  }

  @Test
  void steptx461002KnownRefusalAndDriftCannotGuessSuccess() {
    for (String reason : List.of("LOCK_BUSY", "BACKUP_GATE")) {
      var f = new Fixture();
      f.chunks.add(new Projection(0, null, false, reason));
      assertStop(reason, f);
      assertEquals(List.of(BEGIN, ROLLBACK, RESTORE), f.events);
      f.closedExactly(3);
    }
    var drift = new Fixture();
    drift.chunks.add(new Projection(1, 5L, false, "OK"));
    drift.chunks.add(new Projection(0, 6L, true, "OK"));
    assertStop(DB, drift);
    assertEquals(List.of(BEGIN, COMMIT, RESTORE, BEGIN, ROLLBACK, RESTORE), drift.events);
    drift.closedExactly(6);
  }

  @Test
  void steptx461003InvalidArgumentsAndSessionStateRejectBeforeBegin() {
    var f = new Fixture();
    var service = new StepCleanupService(() -> 0);
    assertThrows(
        NullPointerException.class, () -> service.execute(null, ATTEMPT, CleanupKind.QUESTIONS));
    assertThrows(
        NullPointerException.class, () -> service.execute(f.borrowed, null, CleanupKind.QUESTIONS));
    assertThrows(NullPointerException.class, () -> service.execute(f.borrowed, ATTEMPT, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> service.execute(f.borrowed, ATTEMPT, CleanupKind.SESSIONS));
    for (int refusal = 0; refusal < 3; refusal++) {
      f.autoCommit = refusal != 0;
      f.readOnly = refusal == 1;
      f.isolation = refusal == 2 ? 8 : 2;
      assertThrows(IllegalArgumentException.class, () -> run(f));
    }
    assertTrue(f.events.isEmpty());
    f.closedExactly(0);
  }

  @Test
  void steptx461004OuterKnownGraphRoutesPreserveFatalIdentity() {
    for (int edge = 0; edge < 3; edge++) {
      for (boolean stopped : List.of(false, true)) {
        var f = new Fixture();
        var fatal = new AssertionError(FIXTURE);
        SQLException sql = graph(edge, fatal);
        if (stopped) {
          var signal = new CleanupStoppedException(CleanupStopReason.TIME_LIMIT);
          signal.initCause(sql);
          f.beforeBeginFailure = signal;
        } else f.beforeBeginFailure = sql;
        assertSame(fatal, assertThrows(AssertionError.class, () -> run(f)));
        assertTrue(f.events.isEmpty());
        f.closedExactly(0);
      }
    }
    var f = new Fixture();
    f.beforeBeginFailure = new SQLException(FIXTURE);
    assertStop(DB, f);
    assertTrue(f.events.isEmpty());
    f.closedExactly(0);
  }

  @Test
  void steptx461005BeginRecoveryKeepsOriginalFaultAndFixedSecondary() {
    for (int edge = 0; edge < 3; edge++) {
      for (boolean onBegin : List.of(false, true)) {
        var f = new Fixture();
        var fatal = new AssertionError(FIXTURE);
        f.beginFailure = onBegin ? graph(edge, fatal) : new SQLException(FIXTURE);
        f.rollbackFailure = onBegin ? new SQLException(FIXTURE) : graph(edge, fatal);
        assertSame(fatal, assertThrows(AssertionError.class, () -> run(f)));
        assertEquals(List.of(BEGIN, ROLLBACK), f.events);
        f.closedExactly(0);
      }
    }
    var f = new Fixture();
    var original = new IllegalStateException(FIXTURE);
    f.beginFailure = original;
    f.rollbackFailure = original;
    assertSame(original, assertThrows(IllegalStateException.class, () -> run(f)));
    assertEquals(1, original.getSuppressed().length);
    assertEquals(STOPS, original.getSuppressed()[0].getMessage());
    assertNull(original.getSuppressed()[0].getCause());
    assertEquals(List.of(BEGIN, ROLLBACK), f.events);
    f.closedExactly(0);

    for (Throwable secondary :
        List.of(new IllegalStateException(FIXTURE), new AssertionError(FIXTURE))) {
      var known = new Fixture();
      known.beginFailure = new SQLException(FIXTURE);
      known.rollbackFailure = secondary;
      assertSame(secondary, assertThrows(secondary.getClass(), () -> run(known)));
      assertEquals(List.of(BEGIN, ROLLBACK), known.events);
      known.closedExactly(0);
    }
  }

  @Test
  void steptx461006DeadlinesAndConfirmedCommitAreKeptSeparate() {
    for (long invalid : new long[] {-1, LIMIT}) {
      var f = new Fixture();
      Deque<Long> ticks = new ArrayDeque<>(List.of(0L, invalid));
      LongSupplier clock = ticks::removeFirst;
      CleanupStoppedException stop =
          assertThrows(
              CleanupStoppedException.class,
              () ->
                  new StepCleanupService(clock)
                      .execute(f.borrowed, ATTEMPT, CleanupKind.QUESTIONS));
      assertEquals("TIME_LIMIT", stop.reason().name());
      assertTrue(f.events.isEmpty());
      f.closedExactly(0);
    }
    var interrupted = new Fixture();
    try {
      Thread.currentThread().interrupt();
      assertStop("INTERRUPTED", interrupted);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    interrupted.closedExactly(0);

    var committed = new Fixture();
    committed.chunks.add(new Projection(0, 5L, true, "OK"));
    committed.restoreFailure = new SQLException(FIXTURE);
    assertStop(DB, committed);
    assertEquals(List.of(BEGIN, COMMIT, RESTORE), committed.events);
    assertFalse(committed.autoCommit);
    committed.closedExactly(3);
  }

  private static StepCleanupSummary run(Fixture f) {
    return new StepCleanupService(() -> 0).execute(f.borrowed, ATTEMPT, CleanupKind.QUESTIONS);
  }

  private static void assertStop(String reason, Fixture fixture) {
    var failure = assertThrows(CleanupStoppedException.class, () -> run(fixture));
    assertEquals(reason, failure.reason().name());
    assertEquals(STOPS, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static SQLException graph(int edge, Error fatal) {
    var sql = new SQLException(FIXTURE);
    switch (edge) {
      case 0 -> sql.initCause(fatal);
      case 1 -> sql.addSuppressed(fatal);
      case 2 -> sql.setNextException(new SQLException(FIXTURE, fatal));
      default -> throw new AssertionError("invalid fixture");
    }
    return sql;
  }

  private static <T> T proxy(Class<T> type, InvocationHandler callback) {
    return type.cast(
        Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, callback));
  }

  private record Projection(long delta, @Nullable Long total, boolean complete, String reason) {
    @Nullable Object read(String column) {
      return switch (column) {
        case "target_count", "deleted_count" -> delta;
        case "skipped_count" -> 0L;
        case "step_target_count", "step_success_count" -> total;
        case "complete" -> complete;
        case "reason_code" -> reason;
        default -> throw new AssertionError(column);
      };
    }
  }

  private static final class Fixture {
    private final Deque<Projection> chunks = new ArrayDeque<>();
    private final List<String> events = new ArrayList<>();
    private boolean autoCommit = true;
    private boolean readOnly;
    private int isolation = 2;
    private int closedStatements;
    private int closedRows;
    @Nullable private Throwable beforeBeginFailure;
    @Nullable private Throwable beginFailure;
    @Nullable private Throwable rollbackFailure;
    @Nullable private Throwable restoreFailure;
    private final Connection borrowed =
        proxy(
            Connection.class,
            (ignored, call, args) -> {
              switch (call.getName()) {
                case "getAutoCommit":
                  if (autoCommit && beforeBeginFailure != null) throw beforeBeginFailure;
                  return autoCommit;
                case "isReadOnly":
                  return readOnly;
                case "getTransactionIsolation":
                  return isolation;
                case "setAutoCommit":
                  boolean setting = (boolean) args[0];
                  events.add(setting ? RESTORE : BEGIN);
                  Throwable fault = setting ? restoreFailure : beginFailure;
                  if (fault != null) throw fault;
                  autoCommit = setting;
                  return null;
                case COMMIT:
                  assertFalse(autoCommit);
                  events.add(COMMIT);
                  return null;
                case ROLLBACK:
                  events.add(ROLLBACK);
                  if (rollbackFailure != null) throw rollbackFailure;
                  return null;
                case "prepareStatement":
                  assertFalse(autoCommit);
                  return statement((String) args[0]);
                default:
                  throw new AssertionError(call.getName());
              }
            });

    private PreparedStatement statement(String sql) {
      boolean lookup = REFERENCES.equals(sql);
      if (!lookup) assertEquals(CHUNK, sql);
      List<Object> binds = new ArrayList<>();
      return proxy(
          PreparedStatement.class,
          (ignored, call, args) -> {
            switch (call.getName()) {
              case "setQueryTimeout":
                assertEquals(5, args[0]);
                return null;
              case "setObject", "setInt", "setLong", "setString":
                assertEquals(binds.size() + 1, args[0]);
                binds.add(args[1]);
                return null;
              case "executeQuery":
                assertEquals(
                    lookup
                        ? List.of(ID, CUTOFF)
                        : List.of(ID, CUTOFF, 31L, 2, START, "QUESTIONS", 1000),
                    binds);
                return rows(lookup ? null : chunks.removeFirst());
              case "close":
                closedStatements++;
                return null;
              default:
                throw new AssertionError(call.getName());
            }
          });
    }

    private ResultSet rows(@Nullable Projection projection) {
      int[] next = {0};
      return proxy(
          ResultSet.class,
          (ignored, call, args) -> {
            switch (call.getName()) {
              case "next":
                next[0]++;
                return next[0] == 1;
              case "getObject", "getString":
                assertEquals(1, next[0]);
                String column = (String) args[0];
                if (projection != null) return projection.read(column);
                return switch (column) {
                  case "has_batch_history", "identity_consistent" -> true;
                  case "has_inbox_progress", "has_log_progress" -> false;
                  default -> throw new AssertionError(column);
                };
              case "close":
                closedRows++;
                return null;
              default:
                throw new AssertionError(call.getName());
            }
          });
    }

    private void closedExactly(int expected) {
      assertEquals(expected, closedStatements);
      assertEquals(expected, closedRows);
      assertTrue(chunks.isEmpty());
    }
  }
}
