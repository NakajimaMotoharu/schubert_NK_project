package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/OPS009/DAT009/UI251/SS331,341/SSC337; BUG2317/YKT2062; spec709. */
final class LogCleanupTransactionPortTest {
  private static final BatchRun RUN =
      new BatchRun(new UUID(0, 337), Instant.parse("2026-11-06T00:00:00Z"));
  private static final long LIMIT = 1_800_000_000_000L;
  private static final Plan EMPTY = new Plan(0, 0, 0, 0, 0, 0, true, "OK");

  @Test
  void boundariesAndDeadline() {
    assertThrows(NullPointerException.class, () -> new LogCleanupService((LongSupplier) null));
    assertThrows(NullPointerException.class, () -> LogCleanupService.withOwner(null));
    assertThrows(NullPointerException.class, () -> new LogCleanupService().execute(null, RUN));
    var f = new Fixture();
    assertThrows(NullPointerException.class, () -> service().execute(f.connection, null));
    f.autoCommit = false;
    assertThrows(IllegalArgumentException.class, () -> service().execute(f.connection, RUN));
    for (long elapsed : new long[] {-1, LIMIT, LIMIT + 1}) {
      var calls = new AtomicInteger();
      stopped(
          CleanupStopReason.TIME_LIMIT,
          () ->
              new LogCleanupService(() -> calls.incrementAndGet() == 1 ? 0 : elapsed)
                  .execute(new Fixture().connection, RUN));
    }
    assertFalse(Thread.currentThread().isInterrupted());
    Thread.currentThread().interrupt();
    try {
      stopped(CleanupStopReason.INTERRUPTED, () -> service().execute(f.connection, RUN));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    var calls = new AtomicInteger();
    try {
      stopped(
          CleanupStopReason.INTERRUPTED,
          () ->
              new LogCleanupService(
                      () -> {
                        if (calls.incrementAndGet() == 2) Thread.currentThread().interrupt();
                        return 0;
                      })
                  .execute(new Fixture().connection, RUN));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    f.assertBorrowed();
  }

  @Test
  void emptyAndLoop() {
    var empty = new Fixture();
    var result = new LogCleanupService().execute(empty.connection, RUN);
    counts(result.before(), 0, 0, 0);
    counts(result.after().counts(), 0, 0, 0);
    assertEquals(0, result.exitCode());
    assertEquals(1, empty.commits);
    assertEquals(0, empty.rollbacks);
    assertTrue(empty.autoCommit);
    empty.assertBorrowed();
    var f = new Fixture();
    f.plans =
        List.of(new Plan(0, 0, 0, 0, 0, 0, false, "OK"), new Plan(2, 1, 1, 2, 1, 1, true, "OK"));
    result = service().execute(f.connection, RUN);
    counts(result.attemptCounts(), 2, 1, 1);
    assertEquals(10, result.exitCode());
    assertEquals(2, f.commits);
    assertEquals(0, f.rollbacks);
    assertEquals(10000, f.maximumRows);
    assertEquals(1, f.hits.getOrDefault("unlock.execute", 0));
    f.assertBorrowed();
  }

  @Test
  void knownStops() {
    for (String reason : List.of("LOCK_BUSY", "BACKUP_GATE")) {
      var f = new Fixture();
      f.plans = List.of(new Plan(0, 0, 0, 0, 0, 0, false, reason));
      stopped(CleanupStopReason.valueOf(reason), () -> service().execute(f.connection, RUN));
      assertEquals(1, f.rollbacks);
      assertEquals(1, f.restores);
      assertEquals(0, f.commits);
      f.assertBorrowed();
    }
  }

  @Test
  void cumulativeDeltas() {
    for (var plans :
        List.of(
            List.of(new Plan(1, 1, 0, 0, 0, 0, true, "OK")),
            List.of(
                new Plan(0, 0, 0, 0, 0, 0, false, "OK"), new Plan(1, 1, 0, 2, 2, 0, true, "OK")))) {
      var f = new Fixture();
      f.plans = plans;
      stopped(CleanupStopReason.DATABASE_FAILURE, () -> service().execute(f.connection, RUN));
      assertEquals(plans.size() - 1, f.commits);
      assertEquals(1, f.rollbacks);
      f.assertBorrowed();
    }
  }

  @Test
  void lockRows() {
    for (String mode : List.of("NONE", "NULL", "FALSE", "MANY")) {
      var f = new Fixture();
      f.modes.put("lock", mode);
      stopped(
          mode.equals("FALSE") ? CleanupStopReason.LOCK_BUSY : CleanupStopReason.DATABASE_FAILURE,
          () -> service().execute(f.connection, RUN));
      assertEquals(0, f.begins);
      assertEquals(0, f.commits);
      f.assertBorrowed();
    }
  }

  @Test
  void unlockRows() {
    for (String mode : List.of("NONE", "NULL", "FALSE", "MANY")) {
      var f = new Fixture();
      f.modes.put("unlock", mode);
      stopped(CleanupStopReason.DATABASE_FAILURE, () -> service().execute(f.connection, RUN));
      assertEquals(1, f.commits);
      assertEquals(0, f.rollbacks);
      f.assertBorrowed();
    }
  }

  @Test
  void bodyFaultsWithCleanRecovery() {
    for (int kind = 0; kind < 6; kind++) {
      var f = new Fixture();
      var primary = fault(kind, false);
      f.failures.put("body", primary);
      Throwable actual = assertThrows(Throwable.class, () -> service().execute(f.connection, RUN));
      if (kind >= 3) {
        assertSame(primary, actual);
        assertEquals(0, actual.getSuppressed().length);
      } else
        fixed(
            actual, kind == 2 ? CleanupStopReason.TIME_LIMIT : CleanupStopReason.DATABASE_FAILURE);
      assertEquals(1, f.rollbacks);
      assertEquals(1, f.restores);
      assertEquals(0, f.commits);
      assertTrue(f.autoCommit);
      assertEquals(List.of("LOCK", "BEGIN", "BODY", "ROLLBACK", "RESTORE", "UNLOCK"), f.events);
      f.assertBorrowed();
    }
  }

  @Test
  void rollbackMatrix() {
    matrix("rollback");
  }

  @Test
  void restoreMatrix() {
    matrix("restore");
  }

  @Test
  void sameFailureIdentity() {
    for (String phase : List.of("rollback", "restore")) {
      for (int kind = 3; kind < 6; kind++) {
        var f = new Fixture();
        var same = fault(kind, false);
        f.failures.put("body", same);
        f.failures.put(phase, same);
        Throwable actual =
            assertThrows(Throwable.class, () -> service().execute(f.connection, RUN));
        assertSame(same, actual);
        fixedSecondaries(actual, 2);
        assertEquals(1, f.rollbacks);
        assertEquals(phase.equals("rollback") ? 0 : 1, f.restores);
        f.assertBorrowed();
      }
    }
  }

  @Test
  void rollbackGatesRestore() {
    var f = new Fixture();
    f.failures.put("body", new SQLException("SYNTHETIC_BODY"));
    f.failures.put("rollback", new SQLException("SYNTHETIC_ROLLBACK"));
    stopped(CleanupStopReason.DATABASE_FAILURE, () -> service().execute(f.connection, RUN));
    assertEquals(List.of("LOCK", "BEGIN", "BODY", "ROLLBACK"), f.events);
    assertFalse(f.autoCommit);
    assertEquals(0, f.restores);
    assertEquals(0, f.commits);
    f.assertBorrowed();
  }

  @Test
  void allResourceBoundaries() {
    var pairs =
        List.of(
            List.of("lock.next", "lock.resultClose"),
            List.of("lock.execute", "lock.statementClose"),
            List.of("unlock.next", "unlock.resultClose"),
            List.of("unlock.execute", "unlock.statementClose"),
            List.of("clock", "unlock.prepare"));
    for (var pair : pairs) {
      for (int first = -1; first < 6; first++) {
        for (int second = 0; second < 6; second++) resource(pair, first, second, false);
        if (first >= 3) resource(pair, first, first, true);
      }
    }
  }

  @Test
  void postcommitOwnerFailure() {
    for (boolean fatal : List.of(false, true)) {
      var f = new Fixture();
      var unknown = new AssertionError("SYNTHETIC_POSTCOMMIT");
      var service =
          LogCleanupService.withOwner(
              () -> {
                if (f.commits > 0) {
                  if (fatal) throw unknown;
                  throw new java.io.IOException("SYNTHETIC_OWNER_DEADLINE");
                }
                return 10_000_000_000L;
              });
      Throwable actual = assertThrows(Throwable.class, () -> service.execute(f.connection, RUN));
      if (fatal) {
        assertSame(unknown, actual);
        fixedSecondaries(actual, 1);
      } else fixed(actual, CleanupStopReason.TIME_LIMIT);
      assertEquals(1, f.commits);
      assertEquals(0, f.rollbacks);
      assertEquals(0, f.restores);
      assertFalse(f.autoCommit);
      f.assertBorrowed();
    }
  }

  @Test
  void successfulCommitRestoreFailure() {
    for (int kind = 0; kind < 6; kind++) {
      var f = new Fixture();
      var secondary = fault(kind, false);
      f.failures.put("restore", secondary);
      Throwable actual = assertThrows(Throwable.class, () -> service().execute(f.connection, RUN));
      if (kind >= 3) {
        assertSame(secondary, actual);
        fixedSecondaries(actual, 1);
      } else
        fixed(
            actual, kind == 2 ? CleanupStopReason.TIME_LIMIT : CleanupStopReason.DATABASE_FAILURE);
      assertEquals(1, f.commits);
      assertEquals(0, f.rollbacks);
      assertEquals(1, f.restores);
      f.assertBorrowed();
    }
  }

  @Test
  void beginFailure() {
    for (int kind = 0; kind < 6; kind++) {
      var f = new Fixture();
      var failure = fault(kind, false);
      f.failures.put("begin", failure);
      Throwable actual = assertThrows(Throwable.class, () -> service().execute(f.connection, RUN));
      if (kind >= 3) assertSame(failure, actual);
      else
        fixed(
            actual, kind == 2 ? CleanupStopReason.TIME_LIMIT : CleanupStopReason.DATABASE_FAILURE);
      assertEquals(0, f.rollbacks);
      assertEquals(0, f.restores);
      assertEquals(0, f.commits);
      assertTrue(f.autoCommit);
      f.assertBorrowed();
    }
  }

  @Test
  void ownerTimeoutBinding() {
    var f = new Fixture();
    var result = LogCleanupService.withOwner(() -> 10_000_000_000L).execute(f.connection, RUN);
    assertEquals(0, result.exitCode());
    assertEquals("5000", f.timeoutValue);
    assertEquals(5, f.timeoutSeconds);
    f.assertBorrowed();
  }

  @Test
  void providerNullResources() {
    for (String stage : List.of("statement", "result")) {
      var f = new Fixture();
      if (stage.equals("statement")) f.nullStatements.add("lock");
      else f.nullResults.add("lock");
      assertThrows(NullPointerException.class, () -> service().execute(f.connection, RUN));
      assertEquals(0, f.commits);
      assertEquals(0, f.rollbacks);
      f.assertBorrowed();
    }
  }

  @Test
  void independentConnectionsInParallel() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var futures = new ArrayList<java.util.concurrent.Future<Fixture>>();
      for (int i = 0; i < 20; i++)
        futures.add(
            workers.submit(
                () -> {
                  var f = new Fixture();
                  assertEquals(0, service().execute(f.connection, RUN).exitCode());
                  return f;
                }));
      for (var future : futures) {
        var f = future.get(3, TimeUnit.SECONDS);
        assertEquals(1, f.commits);
        assertEquals(0, f.rollbacks);
        f.assertBorrowed();
      }
    }
  }

  @Test
  void suppressionDisabledPrimary() {
    for (String phase : List.of("rollback", "restore")) {
      var f = new Fixture();
      var primary = new SuppressionDisabled();
      f.failures.put("body", primary);
      f.failures.put(phase, new SQLException("SYNTHETIC_SECONDARY"));
      assertSame(
          primary, assertThrows(Throwable.class, () -> service().execute(f.connection, RUN)));
      assertEquals(0, primary.getSuppressed().length);
      assertEquals(1, f.rollbacks);
      assertEquals(phase.equals("rollback") ? 0 : 1, f.restores);
      f.assertBorrowed();
    }
  }

  private static LogCleanupService service() {
    return new LogCleanupService(() -> 0);
  }

  private static void counts(CleanupCounts actual, long target, long deleted, long skipped) {
    assertEquals(target, actual.target());
    assertEquals(deleted, actual.deleted());
    assertEquals(skipped, actual.skipped());
  }

  private static void stopped(CleanupStopReason reason, Runnable call) {
    fixed(assertThrows(CleanupStoppedException.class, call::run), reason);
  }

  private static void fixed(Throwable actual, CleanupStopReason reason) {
    var value = assertInstanceOf(CleanupStoppedException.class, actual);
    assertEquals(reason, value.reason());
    assertEquals("cleanup did not complete", value.getMessage());
    assertNull(value.getCause());
    assertEquals(0, value.getSuppressed().length);
  }

  private static void fixedSecondaries(Throwable actual, int count) {
    assertEquals(count, actual.getSuppressed().length);
    var identities =
        java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<Throwable, Boolean>());
    for (var secondary : actual.getSuppressed()) {
      assertNotSame(actual, secondary);
      assertTrue(identities.add(secondary));
      fixed(secondary, CleanupStopReason.DATABASE_FAILURE);
    }
  }

  private static Throwable fault(int kind, boolean clock) {
    return switch (kind) {
      case 0 -> clock ? new BatchRepositoryException() : new SQLException("SYNTHETIC_SQL");
      case 1 -> new BatchRepositoryException();
      case 2 -> new CleanupStoppedException(CleanupStopReason.TIME_LIMIT);
      case 3 -> new IllegalStateException("SYNTHETIC_RUNTIME");
      case 4 -> new NullPointerException("SYNTHETIC_NULL_CONTRACT");
      case 5 -> new AssertionError("SYNTHETIC_ERROR");
      default -> throw new IllegalArgumentException("unknown fixture kind");
    };
  }

  private static void matrix(String phase) {
    for (int first = 0; first < 6; first++)
      for (int second = 0; second < 6; second++) {
        var f = new Fixture();
        var primary = fault(first, false);
        var cleanup = fault(second, false);
        f.failures.put("body", primary);
        f.failures.put(phase, cleanup);
        Throwable actual =
            assertThrows(Throwable.class, () -> service().execute(f.connection, RUN));
        // Independent literal K={0,1,2}, U={3,4,5}, as specified in SS341 SSC337.
        if (first >= 3) {
          assertSame(primary, actual);
          fixedSecondaries(actual, 2); // transaction recovery, then retained lease disposal.
        } else if (second >= 3) {
          assertSame(cleanup, actual);
          fixedSecondaries(actual, 1); // only lease disposal remains after cleanup selection.
        } else fixed(actual, CleanupStopReason.DATABASE_FAILURE);
        assertEquals(1, f.rollbacks);
        assertEquals(phase.equals("rollback") ? 0 : 1, f.restores);
        assertEquals(0, f.commits);
        assertFalse(f.autoCommit);
        f.assertBorrowed();
      }
  }

  private static void resource(List<String> pair, int first, int second, boolean same) {
    var f = new Fixture();
    boolean clockBody = pair.getFirst().equals("clock");
    Throwable primary = first < 0 ? null : fault(first, clockBody);
    Throwable secondary = same ? primary : fault(second, false);
    if (primary != null && !clockBody) f.failures.put(pair.getFirst(), primary);
    f.failures.put(pair.getLast(), secondary);
    var ticks = new AtomicInteger();
    var clockThrows = new AtomicInteger();
    var service =
        new LogCleanupService(
            () -> {
              if (ticks.incrementAndGet() == 3 && clockBody && primary != null) {
                clockThrows.incrementAndGet();
                if (primary instanceof RuntimeException runtime) throw runtime;
                throw (Error) primary;
              }
              return 0;
            });
    Throwable actual = assertThrows(Throwable.class, () -> service.execute(f.connection, RUN));
    if (first >= 3 || second >= 3) {
      assertSame(first >= 3 ? primary : secondary, actual);
      fixedSecondaries(actual, first >= 3 ? 1 : 0);
    } else {
      int retained = first < 0 ? second : first;
      fixed(
          actual,
          retained == 2 ? CleanupStopReason.TIME_LIMIT : CleanupStopReason.DATABASE_FAILURE);
    }
    assertEquals(first < 0 || clockBody ? 1 : 2, f.injected);
    assertEquals(clockBody && primary != null ? 1 : 0, clockThrows.get());
    f.assertBorrowed();
  }

  private static final class SuppressionDisabled extends RuntimeException {
    private static final long serialVersionUID = 1L;

    SuppressionDisabled() {
      super("SYNTHETIC_NO_SUPPRESSION", null, false, false);
    }
  }

  private record Plan(
      long target,
      long deleted,
      long skipped,
      long totalTarget,
      long totalDeleted,
      long totalSkipped,
      boolean complete,
      String reason) {}

  /** Fixed SS331 row vectors only; no JDBC driver, actual SQL or external lifecycle. */
  private static final class Fixture {
    final Map<String, Throwable> failures = new HashMap<>();
    final Map<String, Integer> hits = new HashMap<>();
    final Map<String, String> modes = new HashMap<>();
    final Set<String> nullStatements = new HashSet<>();
    final Set<String> nullResults = new HashSet<>();
    final List<String> events = new ArrayList<>();
    final List<String> unexpected = new ArrayList<>();
    final Connection connection = proxy(Connection.class, this::connection);
    List<Plan> plans = List.of(EMPTY);
    boolean autoCommit = true;
    int transaction = -1;
    int begins;
    int rollbacks;
    int restores;
    int commits;
    int closes;
    int injected;
    int maximumRows;
    int timeoutSeconds;
    String timeoutValue;

    void hit(String point) throws Throwable {
      hits.merge(point, 1, Integer::sum);
      if (failures.containsKey(point)) {
        injected++;
        throw failures.get(point);
      }
    }

    Object connection(Object ignored, java.lang.reflect.Method method, Object[] args)
        throws Throwable {
      return switch (method.getName()) {
        case "getAutoCommit" -> autoCommit;
        case "isReadOnly", "isClosed" -> false;
        case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
        case "setAutoCommit" -> {
          if ((Boolean) args[0]) {
            events.add("RESTORE");
            restores++;
            hit("restore");
            autoCommit = true;
          } else {
            events.add("BEGIN");
            begins++;
            hit("begin");
            autoCommit = false;
            transaction++;
          }
          yield null;
        }
        case "prepareStatement" -> prepare((String) args[0]);
        case "rollback" -> {
          events.add("ROLLBACK");
          rollbacks++;
          hit("rollback");
          yield null;
        }
        case "commit" -> {
          events.add("COMMIT");
          commits++;
          hit("commit");
          yield null;
        }
        case "close" -> {
          closes++;
          throw new AssertionError("borrowed Connection was closed");
        }
        case "toString" -> "OWNED_MEMORY_JDBC";
        default -> throw unexpected(method.getName());
      };
    }

    Object prepare(String sql) throws Throwable {
      final String role;
      if (sql.equals("select pg_try_advisory_lock(71419602) as held")) {
        role = "lock";
        events.add("LOCK");
      } else if (sql.equals("select pg_advisory_unlock(71419602) as released")) {
        role = "unlock";
        events.add("UNLOCK");
      } else if (sql.equals(
          "select target_count,deleted_count,skipped_count,reason_code from"
              + " schubert.maintenance_cleanup_logs(?,?,?)")) {
        role = "chunk";
        events.add("BODY");
        hit("body");
      } else if (sql.equals(
          "select target_count,deleted_count,skipped_count,complete from"
              + " schubert.maintenance_read_log_cleanup_progress(?,?)"))
        role = "progress";
      else if (sql.equals(
          "select pg_catalog.set_config('statement_timeout', ?, true) as bound_timeout"))
        role = "timeout";
      else throw unexpected("unknown SQL fixture");
      hit(role + ".prepare");
      if (nullStatements.contains(role)) return null;
      return proxy(
          PreparedStatement.class,
          (p, m, a) ->
              switch (m.getName()) {
                case "executeQuery" -> {
                  hit(role + ".execute");
                  yield nullResults.contains(role) ? null : rows(role);
                }
                case "close" -> {
                  hit(role + ".statementClose");
                  yield null;
                }
                case "setObject", "setLong" -> null;
                case "setInt" -> {
                  maximumRows = (Integer) a[1];
                  yield null;
                }
                case "setQueryTimeout" -> {
                  timeoutSeconds = (Integer) a[0];
                  yield null;
                }
                case "setString" -> {
                  timeoutValue = (String) a[1];
                  yield null;
                }
                default -> throw unexpected("statement." + m.getName());
              });
    }

    ResultSet rows(String role) {
      var index = new AtomicInteger();
      return proxy(
          ResultSet.class,
          (p, m, a) ->
              switch (m.getName()) {
                case "next" -> {
                  hit(role + ".next");
                  int n = index.incrementAndGet();
                  String mode = modes.getOrDefault(role, "ONE");
                  yield !mode.equals("NONE") && n <= (mode.equals("MANY") ? 2 : 1);
                }
                case "getObject" -> {
                  String column = (String) a[0];
                  String mode = modes.getOrDefault(role, "ONE");
                  if (role.equals("lock") || role.equals("unlock"))
                    yield mode.equals("NULL") ? null : !mode.equals("FALSE");
                  Plan plan = plans.get(Math.min(transaction, plans.size() - 1));
                  yield switch (column) {
                    case "target_count" ->
                        role.equals("chunk") ? plan.target() : plan.totalTarget();
                    case "deleted_count" ->
                        role.equals("chunk") ? plan.deleted() : plan.totalDeleted();
                    case "skipped_count" ->
                        role.equals("chunk") ? plan.skipped() : plan.totalSkipped();
                    case "complete" -> plan.complete();
                    default -> throw unexpected("unknown column");
                  };
                }
                case "getString" ->
                    role.equals("timeout")
                        ? "5s"
                        : plans.get(Math.min(transaction, plans.size() - 1)).reason();
                case "close" -> {
                  hit(role + ".resultClose");
                  yield null;
                }
                default -> throw unexpected("rows." + m.getName());
              });
    }

    AssertionError unexpected(String method) {
      unexpected.add(method);
      return new AssertionError("unexpected memory fixture method: " + method);
    }

    void assertBorrowed() {
      assertEquals(0, closes);
      assertEquals(List.of(), unexpected);
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
