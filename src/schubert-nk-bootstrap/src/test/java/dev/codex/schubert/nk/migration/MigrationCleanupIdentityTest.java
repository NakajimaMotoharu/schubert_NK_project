package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-CLEANID001..010; original-primary and suppressed identity are independent oracles. */
final class MigrationCleanupIdentityTest {
  private static final int SUBJECTS = 5;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String CALL_AUTO = "auto";
  private static final String CALL_CREATE = "create";
  private static final String CALL_TIMEOUT = "timeout";
  private static final String CALL_QUERY = "query";
  private static final String CALL_NEXT = "next";
  private static final String CALL_LONG = "long";
  private static final String CALL_WAS_NULL = "wasNull";
  private static final String CALL_RESULT_CLOSE = "result.close";
  private static final String CALL_STATEMENT_CLOSE = "statement.close";
  private static final List<String> FIRST_SQL =
      List.of(
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT COALESCE(MAX(id),0) FROM schubert.speakers",
          "SELECT count(*) FROM schubert.speakers");
  private static final List<String> READ_FAILURE_CALLS =
      List.of(
          CALL_AUTO,
          CALL_CREATE,
          CALL_TIMEOUT,
          CALL_QUERY,
          CALL_NEXT,
          CALL_LONG,
          CALL_RESULT_CLOSE,
          CALL_STATEMENT_CLOSE);
  private static final List<String> CLOSE_FAILURE_CALLS =
      List.of(
          CALL_AUTO,
          CALL_CREATE,
          CALL_TIMEOUT,
          CALL_QUERY,
          CALL_NEXT,
          CALL_LONG,
          CALL_WAS_NULL,
          CALL_NEXT,
          CALL_RESULT_CLOSE,
          CALL_STATEMENT_CLOSE);

  @Test
  void cleanupId001SpeakerKeepsSamePrimaryForAllThreeFaultKinds() throws Exception {
    self(0);
  }

  @Test
  void cleanupId002ScenarioKeepsSamePrimaryForAllThreeFaultKinds() throws Exception {
    self(1);
  }

  @Test
  void cleanupId003AssetKeepsSamePrimaryForAllThreeFaultKinds() throws Exception {
    self(2);
  }

  @Test
  void cleanupId004FinalizerKeepsSamePrimaryForAllThreeFaultKinds() throws Exception {
    self(3);
  }

  @Test
  void cleanupId005ReferenceKeepsSamePrimaryForAllThreeFaultKinds() throws Exception {
    self(4);
  }

  @Test
  void cleanupId006EqualValuedDifferentObjectsStillBecomeSuppressed() throws Exception {
    for (int subject = 0; subject < SUBJECTS; subject++) {
      var primary = new EqualFailure();
      var cleanup = new EqualFailure();
      assertTrue(primary.equals(cleanup));
      var f = new Fixture(primary, cleanup, cleanup, false);
      assertPrimary(subject, f, primary, List.of(cleanup, cleanup));
    }
  }

  @Test
  void cleanupId007SameInnerOrSameOuterCannotMaskDifferentPeerCleanup() throws Exception {
    for (int subject = 0; subject < SUBJECTS; subject++) {
      for (int p = 0; p < 3; p++) {
        for (int c = 0; c < 3; c++) {
          for (boolean sameInner : List.of(true, false)) {
            Throwable primary = failures().get(p);
            Throwable cleanup = failures().get(c);
            var f =
                new Fixture(
                    primary, sameInner ? primary : cleanup, sameInner ? cleanup : primary, false);
            assertPrimary(subject, f, primary, List.of(cleanup));
          }
        }
      }
    }
  }

  @Test
  void cleanupId008SameCleanupFromTwoResourcesRetainsBothAttemptsInOrder() throws Exception {
    for (int subject = 0; subject < SUBJECTS; subject++) {
      for (int p = 0; p < 3; p++) {
        for (int c = 0; c < 3; c++) {
          Throwable primary = failures().get(p);
          Throwable cleanup = failures().get(c);
          var f = new Fixture(primary, cleanup, cleanup, false);
          assertPrimary(subject, f, primary, List.of(cleanup, cleanup));
        }
      }
    }
  }

  @Test
  void cleanupId009FirstResultCloseFailureRemainsPrimaryAtSameStatementFailure() throws Exception {
    for (int subject = 0; subject < SUBJECTS; subject++) {
      for (Throwable primary : failures()) {
        var f = new Fixture(primary, primary, primary, true);
        assertPrimary(subject, f, primary, List.of());
      }
    }
  }

  @Test
  void cleanupId010FiniteWorkersKeepFaultIdentitiesAndResourcesPerCall() throws Exception {
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        int subject = index % SUBJECTS;
        futures.add(
            executor.submit(
                () -> {
                  var primary = new SQLException("synthetic primary");
                  var f = new Fixture(primary, primary, primary, false);
                  assertPrimary(subject, f, primary, List.of());
                  return f.statementCloses;
                }));
      }
      for (var future : futures) assertEquals(1, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static void self(int subject) throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture(primary, primary, primary, false);
      assertPrimary(subject, f, primary, List.of());
    }
  }

  private static void assertPrimary(
      int subject, Fixture f, Throwable primary, List<Throwable> suppressed) throws Exception {
    var declared = emptyMaster();
    assertSame(
        primary, assertThrows(primary.getClass(), () -> act(subject, f.connection(), declared)));
    assertEquals(suppressed.size(), primary.getSuppressed().length);
    for (int index = 0; index < suppressed.size(); index++)
      assertSame(suppressed.get(index), primary.getSuppressed()[index]);
    assertEquals(List.of(FIRST_SQL.get(subject)), f.sql);
    assertEquals(f.closeOrigin ? CLOSE_FAILURE_CALLS : READ_FAILURE_CALLS, f.calls);
    assertEquals(1, f.resultCloses);
    assertEquals(1, f.statementCloses);
  }

  private static void act(int subject, Connection connection, MigrationMasterCopyDataset declared)
      throws SQLException {
    switch (subject) {
      case 0 -> new SpeakerStagingTable().transfer(connection, 0);
      case 1 -> new ScenarioStagingTables().transfer(connection, 0, 0);
      case 2 -> new AssetStagingTables().transfer(connection, 0, 0, 0);
      case 3 -> new MigrationMasterFinalizer().finish(connection, declared);
      default -> new MigrationMasterReferenceVerifier().verify(connection, declared);
    }
  }

  private static MigrationMasterCopyDataset emptyMaster() {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries = new ScenarioEntryMigrationMap(List.of());
    var scenario =
        new ScenarioCopyDataset(
            new ScenarioFileCopyBatch(files, List.of()),
            new ScenarioEntryCopyBatch(
                new ScenarioEntryPlacementMap(files, entries, List.of()), List.of()));
    var media = new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of());
    var content = new MigrationCopyDataset(scenario, List.of(), List.of(), media);
    return new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), content);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static final class EqualFailure extends SQLException {
    private static final long serialVersionUID = 1L;

    private EqualFailure() {
      super("synthetic equal-valued failures");
    }

    @Override
    public boolean equals(@Nullable Object other) {
      return other instanceof EqualFailure;
    }

    @Override
    public int hashCode() {
      return 1;
    }
  }

  private static final class Fixture {
    private final Throwable primary;
    private final @Nullable Throwable resultFailure;
    private final @Nullable Throwable statementFailure;
    private final boolean closeOrigin;
    private final List<String> calls = new ArrayList<>();
    private final List<String> sql = new ArrayList<>();
    private int resultCloses;
    private int statementCloses;
    private boolean row;

    private Fixture(
        Throwable primary,
        @Nullable Throwable resultFailure,
        @Nullable Throwable statementFailure,
        boolean closeOrigin) {
      this.primary = primary;
      this.resultFailure = resultFailure;
      this.statementFailure = statementFailure;
      this.closeOrigin = closeOrigin;
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getAutoCommit" -> {
                    calls.add(CALL_AUTO);
                    return false;
                  }
                  case "createStatement" -> {
                    calls.add(CALL_CREATE);
                    return statement();
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected connection operation " + method.getName());
                }
              });
    }

    private Statement statement() {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout" -> {
                    calls.add(CALL_TIMEOUT);
                    assertEquals(30, args[0]);
                    return null;
                  }
                  case "executeQuery" -> {
                    calls.add(CALL_QUERY);
                    sql.add((String) args[0]);
                    return result();
                  }
                  case "close" -> {
                    statementCloses++;
                    calls.add(CALL_STATEMENT_CLOSE);
                    if (statementFailure != null) throw statementFailure;
                    return null;
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected statement operation " + method.getName());
                }
              });
    }

    private ResultSet result() {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "next" -> {
                    calls.add(CALL_NEXT);
                    boolean next = !row;
                    row = true;
                    return next;
                  }
                  case "getLong" -> {
                    calls.add(CALL_LONG);
                    assertEquals(1, args[0]);
                    if (!closeOrigin) throw primary;
                    return 0L;
                  }
                  case "wasNull" -> {
                    calls.add(CALL_WAS_NULL);
                    return false;
                  }
                  case "close" -> {
                    resultCloses++;
                    calls.add(CALL_RESULT_CLOSE);
                    if (resultFailure != null) throw resultFailure;
                    return null;
                  }
                  default ->
                      throw new AssertionError("unexpected result operation " + method.getName());
                }
              });
    }
  }
}
