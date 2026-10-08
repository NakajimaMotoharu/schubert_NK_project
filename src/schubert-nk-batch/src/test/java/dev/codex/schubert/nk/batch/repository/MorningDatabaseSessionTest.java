package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.backup.*;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.lang.reflect.*;
import java.nio.file.Path;
import java.sql.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

/** MDB001..011. Literal role/lock oracle; actual isolated DB transaction/lock in MDB007..011. */
final class MorningDatabaseSessionTest {
  static final String URL = "jdbc:postgresql://127.0.0.1:5432/schubert_nk";
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("31100000-2222-4333-8444-555555555555"),
          Instant.parse("2026-09-27T15:00:00Z"));
  static final Instant NOW = Instant.parse("2026-09-28T02:00:00Z");
  @TempDir static Path directory;
  static BatchDatabaseFixture db;
  static String actualUrl;

  @Test
  void mdb019VerificationOnlySchemaCannotMintPermitFactsAndDataCannotEscapeOwner()
      throws Exception {
    MorningDatabaseSession.Schema legacy =
        connection -> fail("inspection must not use a void gate");
    try (var connection = db.open("schubert_batch")) {
      assertThrows(IOException.class, () -> legacy.inspect(connection));
      assertThrows(NullPointerException.class, () -> legacy.inspect(null));
    }
    var probe = new Probe();
    var retained = new AtomicReference<MorningDatabaseSession.Access>();
    probe
        .subject()
        .execute(
            credential(),
            session -> {
              retained.set(session);
              assertThrows(NullPointerException.class, () -> session.inspectPermitDatabase(null));
              assertThrows(
                  IOException.class, () -> session.inspectPermitDatabase(() -> 5_000_000_000L));
              assertThrows(
                  NullPointerException.class,
                  () -> session.recheckPermitDatabase(null, () -> 5_000_000_000L));
              return true;
            });
    assertThrows(
        IOException.class, () -> retained.get().inspectPermitDatabase(() -> 5_000_000_000L));
    var failure = new NullPointerException("PUBLIC_PROGRAMMING");
    var fresh = new Probe();
    assertSame(
        failure,
        assertThrows(
            NullPointerException.class,
            () ->
                fresh
                    .subject()
                    .execute(
                        credential(),
                        session ->
                            session.inspectPermitDatabase(
                                () -> {
                                  throw failure;
                                }))));
    assertEquals(0, fresh.connections);
    assertEquals(0, fresh.statements);
  }

  @BeforeAll
  static void database() throws Exception {
    db = new BatchDatabaseFixture(directory);
    try (var c = db.admin();
        var s = c.createStatement()) {
      actualUrl = c.getMetaData().getURL().replace("/postgres", "/schubert_nk");
      s.execute("create database schubert_nk");
    }
    try (var c = DriverManager.getConnection(actualUrl, "pgpt_admin", "");
        var s = c.createStatement()) {
      s.execute(
          java.nio.file.Files.readString(
              Path.of(System.getProperty("nk.pt.repository"))
                  .resolve(
                      "src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql")));
    }
    Flyway.configure()
        .dataSource(actualUrl, "schubert_migration", "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .locations(
            "filesystem:"
                + Path.of(System.getProperty("nk.pt.repository"))
                    .resolve("src/schubert-nk-api/src/main/resources/db/migration"))
        .validateOnMigrate(true)
        .cleanDisabled(true)
        .load()
        .migrate();
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  static InspectorDbCredential credential() {
    return InspectorDbCredential.consume(
        "PUBLIC_PASSWORD".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
  }

  private static String mdb588Audit(Connection observer, BatchRun run) throws SQLException {
    try (var query = observer.createStatement();
        var role =
            query.executeQuery("select current_database(),session_user::text,current_user::text")) {
      assertTrue(role.next());
      assertEquals("schubert_nk", role.getString(1));
      assertEquals("pgpt_admin", role.getString(2));
      assertEquals("pgpt_admin", role.getString(3));
      assertFalse(role.next());
    }
    try (var statement =
        observer.prepareStatement(
            "select coalesce(jsonb_agg(to_jsonb(t) order by id),'[]'::jsonb)::text from schubert.batch_runs t where run_id=?")) {
      statement.setObject(1, run.id());
      try (var rows = statement.executeQuery()) {
        assertTrue(rows.next());
        String value = rows.getString(1);
        assertNotNull(value);
        assertFalse(rows.next());
        return value;
      }
    }
  }

  @Test
  void mdb590001FailedBackupCleanupSkipAndExpiryTerminalReceiptsMatchIndependentSql()
      throws Exception {
    mdb590Scenarios(0, "", "");
  }

  @Test
  void mdb592001SixReadbackTransitionsRejectEverySqlPortFailureAndPreserveRows() throws Exception {
    int seed = 1;
    for (String phase :
        List.of(
            "failedBackupSnapshot",
            "observeBackup",
            "observeCleanup",
            "cleanupReferences",
            "beginExpiry",
            "observeExpiry")) {
      for (String method : List.of("getAutoCommit", "isReadOnly", "prepareStatement", "rollback")) {
        mdb590Scenarios(seed++, phase, method);
      }
    }
    assertEquals(25, seed);
  }

  private void mdb590Scenarios(int seed, String faultPhase, String faultMethod) throws Exception {
    var zero = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(0);
    var ten = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(10);
    var thirty = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(30);
    var cleanupReceipt =
        dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(0);
    var receipts = List.of(zero, ten, thirty);
    var names =
        List.of(
            "CLEAN_NOTIFICATION",
            "CLEAN_QUESTION",
            "CLEAN_SESSION",
            "CLEAN_INBOX_OUTBOX",
            "CLEAN_LOG",
            "CLEAN_BATCH_RUN",
            "CLEAN_TRANSFER");
    for (int index = 0; index < (seed == 0 ? 6 : 3); index++) {
      int scenario = seed * 6 + index;
      int terminal = index % 3;
      boolean matchingReceipt = index < 3;
      var fixtureDate =
          seed == 0
              ? java.time.LocalDate.of(2026, 9, 20).plusDays(index)
              : java.time.LocalDate.of(2010, 1, 1).plusDays(scenario);
      Instant began = fixtureDate.atStartOfDay(java.time.ZoneOffset.UTC).toInstant();
      var run = new BatchRun(new UUID(590001, scenario + 1), began.minusSeconds(32400));
      var retained = new AtomicReference<Connection>();
      var readBefore = new AtomicReference<String>();
      var phase = new AtomicReference<>("");
      var injected = new AtomicBoolean();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var actual = DriverManager.getConnection(url, properties);
                retained.set(actual);
                if (!faultPhase.isEmpty()) {
                  return (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (proxy, method, args) -> {
                            if (phase.get().equals(faultPhase)
                                && method.getName().equals(faultMethod)
                                && injected.compareAndSet(false, true)) {
                              try (var audit =
                                  DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
                                readBefore.set(mdb588Audit(audit, run));
                              }
                              throw new SQLException("PRIVATE_TRANSITION_SQL_FAULT");
                            }
                            try {
                              return method.invoke(actual, args);
                            } catch (InvocationTargetException failure) {
                              throw failure.getCause();
                            }
                          });
                }
                return actual;
              },
              c -> {});
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner = () -> 5_000_000_000L;
      try (var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
        MorningDatabaseSession.Operation<Boolean> operation =
            session -> {
              assertThrows(IOException.class, () -> session.beginExpiry(run, began, owner));
              assertThrows(IOException.class, () -> session.handoffExpiry(() -> 0));
              var backup = session.beginBackup(run, began, false);
              confirmActualFailedPair(session, backup);
              phase.set("failedBackupSnapshot");
              var failedSnapshot = session.failedBackupSnapshot(backup, owner);
              assertEquals(began.plusSeconds(1), failedSnapshot.endedAt());
              phase.set("observeBackup");
              var backupRows =
                  session.observeBackup(backup, Optional.empty(), began.plusSeconds(1), owner);
              assertEquals(2, backupRows.current().size());
              for (var row : backupRows.current()) {
                assertEquals(BatchStepResult.Status.FAILED, row.result().status());
                assertEquals(BatchStepResult.Reason.COMMAND_FAILURE, row.result().reason());
                assertEquals(began.plusSeconds(1), row.ended());
              }
              phase.set("");
              assertEquals(
                  0,
                  session.handoffCleanup(
                      () -> {
                        try (var child =
                                DriverManager.getConnection(actualUrl, "schubert_batch", "");
                            var sql =
                                child.prepareStatement(
                                    "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values(?,?,?,?,1,?,?,?,0,0,0,0,?,?)")) {
                          assertTrue(advisory(child));
                          child.setAutoCommit(false);
                          for (int step = 0; step < names.size(); step++) {
                            boolean transfer = step == 6;
                            sql.setLong(1, 590000000L + scenario * 100 + step);
                            sql.setObject(2, run.id());
                            sql.setObject(3, fixtureDate);
                            sql.setString(4, names.get(step));
                            sql.setObject(
                                5, began.plusSeconds(2).atOffset(java.time.ZoneOffset.UTC));
                            sql.setObject(
                                6,
                                began
                                    .plusSeconds(transfer ? 3 : 2)
                                    .atOffset(java.time.ZoneOffset.UTC));
                            sql.setString(7, transfer ? "SUCCESS" : "SKIPPED");
                            sql.setString(8, transfer ? null : "BACKUP_UNAVAILABLE");
                            sql.setString(9, transfer ? null : "verified backup unavailable");
                            assertEquals(1, sql.executeUpdate());
                          }
                          child.commit();
                        } catch (SQLException failure) {
                          throw new IOException("fixture cleanup", failure);
                        }
                        return 0;
                      }));
              phase.set("observeCleanup");
              var cleanup = session.observeCleanupBackupUnavailable(run, 0, owner);
              assertEquals(7, cleanup.entries().size());
              for (int step = 0; step < 7; step++) {
                var entry = cleanup.entries().get(step);
                assertEquals(names.get(step), entry.attempt().step().name());
                assertEquals(590000000L + scenario * 100 + step, entry.attempt().id());
                assertEquals(step < 6, entry.attempt().skipped());
                assertEquals(
                    step < 6 ? BatchStepResult.Status.SKIPPED : BatchStepResult.Status.SUCCESS,
                    entry.result().status());
                assertEquals(
                    step < 6
                        ? BatchStepResult.Reason.BACKUP_UNAVAILABLE
                        : BatchStepResult.Reason.NONE,
                    entry.result().reason());
                assertEquals(began.plusSeconds(step < 6 ? 2 : 3), entry.endedAt());
                assertEquals(0, entry.result().target());
                assertEquals(0, entry.result().success());
                assertEquals(0, entry.result().failure());
                assertEquals(0, entry.result().bytes());
              }
              phase.set("cleanupReferences");
              assertEquals(
                  Collections.nCopies(7, Optional.empty()),
                  session.cleanupReferences(cleanup, owner));
              phase.set("");
              assertThrows(NullPointerException.class, () -> session.beginExpiry(run, null, owner));
              assertThrows(NullPointerException.class, () -> session.beginExpiry(run, began, null));
              phase.set("beginExpiry");
              var expiry = session.beginExpiry(run, began.plusSeconds(4), owner);
              phase.set("");
              assertFalse(expiry.current().skipped());
              assertEquals(Optional.empty(), expiry.prior());
              assertThrows(
                  IOException.class,
                  () -> session.observeExpiry(expiry, receipts.get(terminal), owner));
              assertEquals(
                  receipts.get(terminal).exitCode(),
                  session.handoffExpiry(
                      () -> {
                        try (var child =
                                DriverManager.getConnection(actualUrl, "schubert_batch", "");
                            var sql =
                                child.prepareStatement(
                                    "update schubert.batch_runs set status=?,ended_at=?,target_count=1,success_count=?,failure_count=?,byte_count=25,error_code=?,error_summary=?,expiry_cutoff_at=?,expiry_before_count=1,expiry_after_count=? where id=? and run_id=? and step='CLEAN_EXPIRY' and status='RUNNING'")) {
                          assertTrue(advisory(child));
                          sql.setString(1, List.of("SUCCESS", "WARNING", "FAILED").get(terminal));
                          sql.setObject(2, began.plusSeconds(5).atOffset(java.time.ZoneOffset.UTC));
                          sql.setLong(3, terminal == 0 ? 1 : 0);
                          sql.setLong(4, terminal == 0 ? 0 : 1);
                          sql.setString(
                              5,
                              terminal == 0
                                  ? null
                                  : terminal == 1 ? "COMMAND_FAILURE" : "SAFETY_FAILURE");
                          sql.setString(
                              6,
                              terminal == 0
                                  ? null
                                  : terminal == 1
                                      ? "batch command failed"
                                      : "batch safety check failed");
                          sql.setObject(
                              7,
                              run.cutoff().minusSeconds(604800).atOffset(java.time.ZoneOffset.UTC));
                          sql.setLong(8, terminal == 0 ? 0 : 1);
                          sql.setLong(9, expiry.current().id());
                          sql.setObject(10, run.id());
                          assertEquals(1, sql.executeUpdate());
                        } catch (SQLException failure) {
                          throw new IOException("fixture expiry", failure);
                        }
                        return receipts.get(terminal).exitCode();
                      }));
              try {
                readBefore.set(mdb588Audit(observer, run));
              } catch (SQLException failure) {
                throw new IOException("fixture audit", failure);
              }
              assertThrows(
                  IOException.class, () -> session.observeExpiry(expiry, cleanupReceipt, owner));
              phase.set("observeExpiry");
              var actual =
                  session.observeExpiry(
                      expiry,
                      matchingReceipt ? receipts.get(terminal) : terminal == 0 ? thirty : zero,
                      owner);
              assertEquals(expiry, actual.begins());
              assertEquals(began.plusSeconds(5), actual.ended());
              assertEquals(
                  List.of(
                          BatchStepResult.Status.SUCCESS,
                          BatchStepResult.Status.WARNING,
                          BatchStepResult.Status.FAILED)
                      .get(terminal),
                  actual.result().status());
              assertEquals(1, actual.result().target());
              assertEquals(terminal == 0 ? 1 : 0, actual.result().success());
              assertEquals(terminal == 0 ? 0 : 1, actual.result().failure());
              assertEquals(25, actual.result().bytes());
              assertEquals(run.cutoff().minusSeconds(604800), actual.audit().cutoff());
              assertEquals(Long.valueOf(1), actual.audit().before());
              assertEquals(Long.valueOf(terminal == 0 ? 0 : 1), actual.audit().after());
              return Boolean.TRUE;
            };
        if (seed == 0 && index < 3)
          assertEquals(Boolean.TRUE, subject.execute(credential(), operation));
        else
          assertEquals(
              "root batch database unavailable",
              assertThrows(IOException.class, () -> subject.execute(credential(), operation))
                  .getMessage());
        if (seed != 0) assertTrue(injected.get(), faultPhase + ":" + faultMethod);
        assertEquals(readBefore.get(), mdb588Audit(observer, run));
        assertTrue(retained.get().isClosed());
        awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      }
    }
  }

  @Test
  void mdb589001ActualReadbackSqlFailuresCloseConnectionWithoutChangingCommittedRows()
      throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var points =
        List.of(
            "getAutoCommit",
            "isReadOnly",
            "setAutoCommitFalse",
            "prepareStatement",
            "rollback",
            "setAutoCommitTrue",
            "ownerBind");
    for (int index = 0; index < points.size(); index++) {
      String point = points.get(index);
      Instant began = Instant.parse("2026-09-10T00:00:00Z").plusSeconds(index * 86400L);
      var run = new BatchRun(new UUID(589001, index + 1), began.minusSeconds(32400));
      var enabled = new AtomicBoolean();
      var injected = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      var ownerChecks = new AtomicInteger();
      var before = new AtomicReference<String>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var actual = DriverManager.getConnection(url, properties);
                retained.set(actual);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (proxy, method, args) -> {
                          String name = method.getName();
                          boolean hit =
                              name.equals(point)
                                  || (name.equals("setAutoCommit")
                                      && point.equals(
                                          "setAutoCommit"
                                              + ((boolean) args[0] ? "True" : "False")));
                          if (enabled.get() && hit && injected.getAndIncrement() == 0)
                            throw new SQLException("PRIVATE_SQL_FAULT");
                          try {
                            return method.invoke(actual, args);
                          } catch (InvocationTargetException failure) {
                            throw failure.getCause();
                          }
                        });
              },
              c -> {});
      try (var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
        var failure =
            assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          var pair = session.beginBackup(run, began, false);
                          confirmActualFailedPair(session, pair);
                          assertEquals(30, session.handoffCleanup(() -> 30));
                          try {
                            before.set(mdb588Audit(observer, run));
                          } catch (SQLException known) {
                            throw new IOException("fixture audit", known);
                          }
                          enabled.set(true);
                          session.observeCleanupRejected(
                              run,
                              receipt,
                              () -> {
                                if (point.equals("ownerBind")
                                    && ownerChecks.incrementAndGet() == 2) {
                                  injected.incrementAndGet();
                                  throw new IOException("PRIVATE_OWNER_FAULT");
                                }
                                return 5_000_000_000L;
                              });
                          fail("fault must reject readback");
                          return Boolean.TRUE;
                        }),
                point);
        assertEquals("root batch database unavailable", failure.getMessage(), point);
        assertNull(failure.getCause(), point);
        assertEquals(0, failure.getSuppressed().length, point);
        assertTrue(injected.get() >= 1, point);
        assertTrue(retained.get().isClosed(), point);
        assertEquals(before.get(), mdb588Audit(observer, run), point);
        awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      }
    }
  }

  @Test
  void mdb589002ActualCloseFaultPriorityStillReleasesOwnedAdvisory() throws Exception {
    for (boolean bodyFailed : List.of(false, true)) {
      for (Throwable secondary :
          List.of(
              new SQLException("PRIVATE_CLOSE"),
              new IllegalStateException("PRIVATE_CLOSE"),
              new AssertionError("PRIVATE_CLOSE"))) {
        var retained = new AtomicReference<Connection>();
        var closeCount = new AtomicInteger();
        var subject =
            new MorningDatabaseSession(
                actualUrl,
                () -> {},
                (url, properties) -> {
                  var actual = DriverManager.getConnection(url, properties);
                  retained.set(actual);
                  return (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (proxy, method, args) -> {
                            if (method.getName().equals("close")) {
                              closeCount.incrementAndGet();
                              actual.close();
                              throw secondary;
                            }
                            try {
                              return method.invoke(actual, args);
                            } catch (InvocationTargetException failure) {
                              throw failure.getCause();
                            }
                          });
                },
                c -> {});
        Throwable actualFailure =
            assertThrows(
                Throwable.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          session.requireUnused(
                              new BatchRun(
                                  new UUID(589002, 1), Instant.parse("2026-09-01T15:00:00Z")));
                          if (bodyFailed) throw new IOException("PRIVATE_BODY");
                          return Boolean.TRUE;
                        }));
        if (secondary instanceof SQLException) {
          assertInstanceOf(IOException.class, actualFailure);
          assertEquals("root batch database unavailable", actualFailure.getMessage());
          assertNull(actualFailure.getCause());
          assertEquals(0, actualFailure.getSuppressed().length);
        } else assertSame(secondary, actualFailure);
        assertEquals(1, closeCount.get());
        assertTrue(retained.get().isClosed());
        try (var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
          awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
        }
      }
    }
  }

  /** MDB588001..003 / P017-01.03 / OPS009,DAT009/UI251/SS341343/SSC199200. */
  @Test
  void mdb588001TypedCleanup30EmptyReadbackDoesNotFabricateRowsOrReleaseParent() throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var foreign = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(30);
    var normal = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(0);
    var run =
        new BatchRun(
            UUID.fromString("58800000-2222-4333-8444-555555555551"),
            Instant.parse("2026-10-07T15:00:00Z"));
    Instant began = Instant.parse("2026-10-08T00:00:00Z");
    var connection = new AtomicReference<Connection>();
    var retained = new AtomicReference<MorningDatabaseSession.Access>();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var value = DriverManager.getConnection(url, properties);
              connection.set(value);
              return value;
            },
            c -> {});
    try (var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
      subject.execute(
          credential(),
          session -> {
            retained.set(session);
            dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner =
                () -> 5_000_000_000L;
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            var pair = session.beginBackup(run, began, false);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            confirmActualFailedPair(session, pair);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            assertEquals(30, session.handoffCleanup(() -> 30));
            try {
              String before = mdb588Audit(observer, run);
              var actual = session.observeCleanupRejected(run, receipt, owner);
              assertEquals(run, actual.run());
              assertEquals(
                  List.of(
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty()),
                  actual.entries());
              assertEquals("CleanupRejectedSnapshot[data=<redacted>]", actual.toString());
              assertEquals(before, mdb588Audit(observer, run));
              assertNotNull(connection.get());
              assertTrue(connection.get().getAutoCommit());
              assertFalse(connection.get().isReadOnly());
              assertFalse(advisory(observer));
              assertThrows(
                  IOException.class, () -> session.observeCleanupRejected(run, foreign, owner));
              assertThrows(
                  IOException.class, () -> session.observeCleanupRejected(run, normal, owner));
              var failure = new IOException("PUBLIC_OWNER_DEADLINE");
              assertSame(
                  failure,
                  assertThrows(
                      IOException.class,
                      () ->
                          session.observeCleanupRejected(
                              run,
                              receipt,
                              () -> {
                                throw failure;
                              })));
              assertEquals(before, mdb588Audit(observer, run));
            } catch (SQLException failure) {
              throw new IOException("isolated DB assertion", failure);
            }
            return Boolean.TRUE;
          });
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      assertTrue(connection.get().isClosed());
      assertThrows(
          IOException.class,
          () -> retained.get().observeCleanupRejected(run, receipt, () -> 5_000_000_000L));
    }
  }

  @Test
  void mdb588002Typed30PartialRunningAndFailedSlotsStayExactAndUnmodified() throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var run =
        new BatchRun(
            UUID.fromString("58800000-2222-4333-8444-555555555552"),
            Instant.parse("2026-10-06T15:00:00Z"));
    Instant began = Instant.parse("2026-10-07T00:00:10Z");
    var subject =
        new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
    try (var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
      subject.execute(
          credential(),
          session -> {
            var pair = session.beginBackup(run, began, false);
            confirmActualFailedPair(session, pair);
            assertEquals(
                30,
                session.handoffCleanup(
                    () -> {
                      try (var child =
                              DriverManager.getConnection(actualUrl, "schubert_batch", "");
                          var statement =
                              child.prepareStatement(
                                  "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values (588201,?,'2026-10-07','CLEAN_NOTIFICATION',1,'2026-10-07T00:00:11Z',null,'RUNNING',0,0,0,0,null,null),(588202,?,'2026-10-07','CLEAN_QUESTION',1,'2026-10-07T00:00:11Z','2026-10-07T00:00:12Z','FAILED',1,0,1,0,'COMMAND_FAILURE','batch command failed')")) {
                        assertTrue(advisory(child));
                        statement.setObject(1, run.id());
                        statement.setObject(2, run.id());
                        assertEquals(2, statement.executeUpdate());
                      } catch (SQLException failure) {
                        throw new IOException("isolated partial fixture", failure);
                      }
                      return 30;
                    }));
            try {
              String before = mdb588Audit(observer, run);
              var actual = session.observeCleanupRejected(run, receipt, () -> 5_000_000_000L);
              var first =
                  new CleanupTerminalRepository.RejectedEntry(
                      new BatchStepAttempt(
                          588201,
                          run,
                          BatchStep.CLEAN_NOTIFICATION,
                          1,
                          began.plusSeconds(1),
                          false),
                      Optional.empty(),
                      Optional.empty());
              var second =
                  new CleanupTerminalRepository.RejectedEntry(
                      new BatchStepAttempt(
                          588202, run, BatchStep.CLEAN_QUESTION, 1, began.plusSeconds(1), false),
                      Optional.of(began.plusSeconds(2)),
                      Optional.of(
                          new BatchStepResult(
                              BatchStepResult.Status.FAILED,
                              1,
                              0,
                              1,
                              0,
                              BatchStepResult.Reason.COMMAND_FAILURE)));
              assertEquals(
                  List.of(
                      Optional.of(first),
                      Optional.of(second),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty()),
                  actual.entries());
              assertEquals(before, mdb588Audit(observer, run));
              assertFalse(advisory(observer));
            } catch (SQLException failure) {
              throw new IOException("isolated partial readback", failure);
            }
            return Boolean.TRUE;
          });
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  @Test
  void mdb588003UnexpectedTransactionOrReadOnlyCannotEnterRejectedReadback() throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var run =
        new BatchRun(
            UUID.fromString("58800000-2222-4333-8444-555555555553"),
            Instant.parse("2026-10-05T15:00:00Z"));
    var retained = new AtomicReference<Connection>();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var c = DriverManager.getConnection(url, properties);
              retained.set(c);
              return c;
            },
            c -> {});
    subject.execute(
        credential(),
        session -> {
          var pair = session.beginBackup(run, Instant.parse("2026-10-06T00:00:20Z"), false);
          confirmActualFailedPair(session, pair);
          assertEquals(30, session.handoffCleanup(() -> 30));
          dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner = () -> 5_000_000_000L;
          try {
            var c = retained.get();
            assertNotNull(c);
            c.setAutoCommit(false);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            assertFalse(c.getAutoCommit());
            c.rollback();
            c.setAutoCommit(true);
            c.setReadOnly(true);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            assertTrue(c.isReadOnly());
            c.setReadOnly(false);
            assertThrows(
                NullPointerException.class,
                () -> session.observeCleanupRejected(null, receipt, owner));
            assertThrows(
                NullPointerException.class, () -> session.observeCleanupRejected(run, null, owner));
            assertThrows(
                NullPointerException.class,
                () -> session.observeCleanupRejected(run, receipt, null));
          } catch (SQLException failure) {
            throw new IOException("isolated transaction fixture", failure);
          }
          return Boolean.TRUE;
        });
    assertTrue(retained.get().isClosed());
  }

  @Test
  void bresume001GenuinePriorPairAndCurrentSkipAreSeparateCommittedRows() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("38700000-2222-4333-8444-555555555555"),
            Instant.parse("2026-11-27T15:00:00Z"));
    var started = Instant.parse("2026-11-28T02:00:00Z");
    var observed = Instant.parse("2026-11-28T03:00:00Z");
    try (var admin = DriverManager.getConnection(actualUrl, "pgpt_admin", "");
        var s = admin.createStatement()) {
      s.execute(
          "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,byte_count) values"
              + "(670001,'38700000-2222-4333-8444-555555555555','2026-11-28','BACKUP_DB',1,'2026-11-28T02:00:00Z','2026-11-28T02:00:03Z','SUCCESS',1,1,26),"
              + "(670002,'38700000-2222-4333-8444-555555555555','2026-11-28','BACKUP_CONFIG',1,'2026-11-28T02:00:00Z','2026-11-28T02:00:03Z','SUCCESS',2,2,67)");
    }
    var prior =
        new MorningDatabaseSession.BackupBegins(
            new BatchStepAttempt(670001, run, BatchStep.BACKUP_DB, 1, started, false),
            new BatchStepAttempt(670002, run, BatchStep.BACKUP_CONFIG, 1, started, false));
    var manifest =
        new BackupManifest(
            prior.database(),
            prior.configuration(),
            started,
            started.plusSeconds(2),
            new BackupVersions(
                "public-host", "1.0", "023", "ubuntu-26.04", "25.0.4", "18.6", "2.56.0", "1.2.1"),
            "0".repeat(64),
            new BackupFileDigest(26, "1".repeat(64)),
            new BackupFileDigest(35, "2".repeat(64)),
            new BackupFileDigest(32, "3".repeat(64)));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    var current =
        subject.execute(
            credential(),
            session -> {
              assertEquals(Optional.of(prior), session.successfulBackup(run, observed));
              var skipped = session.beginResumeBackup(manifest, observed);
              assertTrue(skipped.database().skipped());
              assertTrue(skipped.configuration().skipped());
              assertNotEquals(prior.database().id(), skipped.database().id());
              assertEquals(2, skipped.database().attempt());
              assertEquals(2, skipped.configuration().attempt());
              assertThrows(
                  IOException.class, () -> session.completeReusedBackup(prior, manifest, observed));
              session.completeReusedBackup(skipped, manifest, observed.plusSeconds(1));
              var observedPair =
                  session.observeBackup(
                      skipped,
                      Optional.of(manifest),
                      observed.plusSeconds(1),
                      () -> 10_000_000_000L);
              assertEquals(
                  List.of(skipped.database(), skipped.configuration()),
                  observedPair.current().stream()
                      .map(BackupStepRepository.Terminal::attempt)
                      .toList());
              assertEquals(
                  List.of(prior.database(), prior.configuration()),
                  observedPair.prior().stream()
                      .map(BackupStepRepository.Terminal::attempt)
                      .toList());
              assertEquals(26, observedPair.prior().get(0).result().bytes());
              assertEquals(67, observedPair.prior().get(1).result().bytes());
              assertEquals(Optional.empty(), observedPair.prior().get(0).errorCode());
              assertThrows(
                  IOException.class,
                  () ->
                      session.observeBackup(
                          prior,
                          Optional.of(manifest),
                          observed.plusSeconds(1),
                          () -> 10_000_000_000L));
              assertTrue(session.retainedBackupSuccessful(manifest, observed.plusSeconds(1)));
              assertThrows(
                  NullPointerException.class,
                  () -> session.retainedBackupSuccessful(null, observed));
              assertThrows(
                  IOException.class, () -> session.retainedBackupSuccessful(manifest, started));
              session.recheckConsistent(run);
              assertThrows(
                  IOException.class,
                  () -> session.completeReusedBackup(skipped, manifest, observed.plusSeconds(1)));
              assertThrows(IOException.class, () -> session.successfulBackup(run, observed));
              return skipped;
            });
    try (var connection = DriverManager.getConnection(actualUrl, "schubert_batch", "")) {
      awaitReleased(connection, TimeUnit.SECONDS.toNanos(5));
      connection.setAutoCommit(false);
      var repository = new BatchRunRepository(connection);
      repository.verifyAlreadySuccessful(current.database());
      repository.verifyAlreadySuccessful(current.configuration());
      assertEquals(
          Optional.of(started.plusSeconds(3)),
          new BackupStepRepository(connection).inspect(manifest, observed));
      try (var s = connection.createStatement();
          var rows =
              s.executeQuery(
                  "select string_agg(step||':'||attempt||':'||status||':'||target_count||':'||success_count||':'||failure_count||':'||byte_count,',' order by step,attempt) from schubert.batch_runs where run_id='38700000-2222-4333-8444-555555555555'")) {
        assertTrue(rows.next());
        assertEquals(
            "BACKUP_CONFIG:1:SUCCESS:2:2:0:67,BACKUP_CONFIG:2:SKIPPED:0:0:0:0,BACKUP_DB:1:SUCCESS:1:1:0:26,BACKUP_DB:2:SKIPPED:0:0:0:0",
            rows.getString(1));
        assertFalse(rows.next());
      }
    }
  }

  @Test
  void mdb015SameConnectionAtomicFailedPairAndReadbackWithoutMutation() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("37900000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(40L * 86400));
    Instant started = NOW.plusSeconds(40L * 86400);
    Instant ended = started.plusSeconds(2);
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    var success =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 1, 1, 0, 1, BatchStepResult.Reason.NONE);
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    var held = new AtomicReference<MorningDatabaseSession.Access>();
    var attempts = new AtomicReference<MorningDatabaseSession.BackupBegins>();
    subject.execute(
        credential(),
        session -> {
          held.set(session);
          var begins = session.beginBackup(run, started, false);
          attempts.set(begins);
          assertThrows(IOException.class, () -> session.failBackup(begins, ended, success, failed));
          assertThrows(IOException.class, () -> session.failBackup(begins, ended, failed, success));
          assertThrows(
              NullPointerException.class, () -> session.failBackup(null, ended, failed, failed));
          var wrong =
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(
                      begins.database().id() + 100, run, BatchStep.BACKUP_DB, 1, started, false),
                  begins.configuration());
          assertThrows(IOException.class, () -> session.failBackup(wrong, ended, failed, failed));
          session.failBackup(begins, ended, failed, failed);
          var pair = session.observeBackup(begins, Optional.empty(), ended, () -> 10_000_000_000L);
          assertTrue(pair.prior().isEmpty());
          assertEquals(2, pair.current().size());
          for (var row : pair.current()) {
            assertEquals(ended, row.ended());
            assertEquals(failed, row.result());
            assertEquals(Optional.of("COMMAND_FAILURE"), row.errorCode());
            assertEquals(Optional.of("batch command failed"), row.errorSummary());
          }
          assertThrows(
              IOException.class,
              () -> session.observeBackup(wrong, Optional.empty(), ended, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(null, Optional.empty(), ended, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(begins, null, ended, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(begins, Optional.empty(), null, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(begins, Optional.empty(), ended, null));
          assertThrows(IOException.class, () -> session.failBackup(begins, ended, failed, failed));
          var observed = session.failedBackupSnapshot(begins, () -> 10_000_000_000L);
          assertEquals(begins.database(), observed.database());
          assertEquals(begins.configuration(), observed.configuration());
          assertEquals(ended, observed.endedAt());
          assertThrows(
              IOException.class, () -> session.failedBackupSnapshot(wrong, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class, () -> session.failedBackupSnapshot(null, () -> 1));
          assertThrows(
              NullPointerException.class, () -> session.failedBackupSnapshot(begins, null));
          return true;
        });
    assertThrows(
        IOException.class, () -> held.get().failBackup(attempts.get(), ended, failed, failed));
    assertThrows(
        IOException.class,
        () -> held.get().failedBackupSnapshot(attempts.get(), () -> 10_000_000_000L));
    try (var observer = DriverManager.getConnection(actualUrl, "schubert_batch", "")) {
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      observer.setAutoCommit(false);
      var repository = new BatchRunRepository(observer);
      repository.verifyFinished(attempts.get().database(), ended, failed);
      repository.verifyFinished(attempts.get().configuration(), ended, failed);
      assertThrows(
          BatchRepositoryException.class,
          () -> repository.verifyFinished(attempts.get().database(), ended.plusSeconds(1), failed));
      try (var statement =
          observer.prepareStatement(
              "select step,status,target_count,success_count,failure_count,byte_count,error_code"
                  + " from schubert.batch_runs where run_id=? order by step")) {
        statement.setObject(1, run.id());
        try (var rows = statement.executeQuery()) {
          for (String step : List.of("BACKUP_CONFIG", "BACKUP_DB")) {
            assertTrue(rows.next());
            assertEquals(step, rows.getString(1));
            assertEquals("FAILED", rows.getString(2));
            assertEquals(1, rows.getLong(3));
            assertEquals(0, rows.getLong(4));
            assertEquals(1, rows.getLong(5));
            assertEquals(0, rows.getLong(6));
            assertEquals("COMMAND_FAILURE", rows.getString(7));
          }
          assertFalse(rows.next());
        }
      }
    }
  }

  @Test
  void bresume002PartialMismatchedAndMissingPriorPairsCannotPublishSkipProof() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("38710000-2222-4333-8444-555555555555"),
            Instant.parse("2026-11-29T15:00:00Z"));
    var observed = Instant.parse("2026-11-30T03:00:00Z");
    var subject =
        new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
    assertTrue(subject.execute(credential(), s -> s.successfulBackup(run, observed)).isEmpty());
    try (var admin = DriverManager.getConnection(actualUrl, "pgpt_admin", "");
        var statement = admin.createStatement()) {
      String row =
          "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,byte_count) values";
      statement.execute(
          row
              + "(670101,'38710000-2222-4333-8444-555555555555','2026-11-30','BACKUP_DB',1,'2026-11-30T02:00:00Z','2026-11-30T02:00:03Z','SUCCESS',1,1,26)");
      assertThrows(
          IOException.class,
          () -> subject.execute(credential(), s -> s.successfulBackup(run, observed)));
      statement.execute(
          row
              + "(670102,'38710000-2222-4333-8444-555555555555','2026-11-30','BACKUP_CONFIG',1,'2026-11-30T02:00:00Z','2026-11-30T02:00:03Z','SUCCESS',2,2,67)");
      for (String change :
          List.of(
              "started_at='2026-11-30T02:00:01Z'",
              "ended_at='2026-11-30T02:00:04Z'",
              "attempt=2",
              "target_count=3",
              "success_count=1",
              "byte_count=0")) {
        statement.execute("update schubert.batch_runs set " + change + " where id=670102");
        assertThrows(
            IOException.class,
            () -> subject.execute(credential(), s -> s.successfulBackup(run, observed)));
        statement.execute(
            "update schubert.batch_runs set started_at='2026-11-30T02:00:00Z',ended_at='2026-11-30T02:00:03Z',attempt=1,target_count=2,success_count=2,byte_count=67 where id=670102");
      }
      assertTrue(subject.execute(credential(), s -> s.successfulBackup(run, observed)).isPresent());
      assertThrows(
          IOException.class,
          () ->
              subject.execute(
                  credential(),
                  s -> s.successfulBackup(run, Instant.parse("2026-11-30T02:00:02Z"))));
      assertThrows(
          NullPointerException.class,
          () -> subject.execute(credential(), s -> s.successfulBackup(null, observed)));
      assertThrows(
          NullPointerException.class,
          () -> subject.execute(credential(), s -> s.successfulBackup(run, null)));
      assertThrows(
          NullPointerException.class,
          () -> subject.execute(credential(), s -> s.beginResumeBackup(null, observed)));
      try (var rows =
          statement.executeQuery(
              "select count(*) from schubert.batch_runs where run_id='38710000-2222-4333-8444-555555555555' and status='SKIPPED'")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getInt(1));
        assertFalse(rows.next());
      }
    }
  }

  @Test
  void mdb016ActualAbandonedPairAndPostBeginOriginalProofAreDistinctFromAdmission()
      throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("38500000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(85L * 86400));
    Instant oldStart = NOW.plusSeconds(85L * 86400);
    Instant newStart = oldStart.plusSeconds(10);
    var previous = new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(run.id(), oldStart);
    var subject =
        new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
    subject.execute(
        credential(),
        s -> {
          assertThrows(IOException.class, () -> s.recheckConsistent(run));
          assertThrows(IOException.class, () -> s.requireAbandonedRequest(previous));
          s.beginBackup(run, oldStart, false);
          s.recheckConsistent(run);
          return true;
        });
    var held = new AtomicReference<MorningDatabaseSession.Access>();
    subject.execute(
        credential(),
        s -> {
          held.set(s);
          s.requireConsistent(run);
          var begins = s.beginBackup(run, newStart, true);
          assertEquals(2, begins.database().attempt());
          assertEquals(2, begins.configuration().attempt());
          assertThrows(IOException.class, () -> s.requireConsistent(run));
          assertThrows(NullPointerException.class, () -> s.recheckConsistent(null));
          assertThrows(NullPointerException.class, () -> s.requireAbandonedRequest(null));
          assertThrows(
              IOException.class,
              () ->
                  s.requireAbandonedRequest(
                      new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                          UUID.fromString("38500001-2222-4333-8444-555555555555"), oldStart)));
          assertThrows(
              IOException.class,
              () ->
                  s.requireAbandonedRequest(
                      new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                          run.id(), newStart)));
          s.requireAbandonedRequest(previous);
          s.recheckConsistent(run);
          var failed =
              new BatchStepResult(
                  BatchStepResult.Status.FAILED,
                  1,
                  0,
                  1,
                  0,
                  BatchStepResult.Reason.COMMAND_FAILURE);
          s.failBackup(begins, newStart.plusSeconds(2), failed, failed);
          s.recheckConsistent(run);
          assertThrows(IOException.class, () -> s.requireAbandonedRequest(previous));
          return true;
        });
    assertThrows(IOException.class, () -> held.get().recheckConsistent(run));
    assertThrows(IOException.class, () -> held.get().requireAbandonedRequest(previous));
    try (var c = DriverManager.getConnection(actualUrl, "pgpt_admin", "");
        var s = c.createStatement();
        var rows =
            s.executeQuery(
                "select string_agg(step||':'||attempt||':'||status||':'||error_code,',' order by step,attempt) from schubert.batch_runs where run_id='38500000-2222-4333-8444-555555555555'")) {
      assertTrue(rows.next());
      assertEquals(
          "BACKUP_CONFIG:1:FAILED:ABANDONED,BACKUP_CONFIG:2:FAILED:COMMAND_FAILURE,BACKUP_DB:1:FAILED:ABANDONED,BACKUP_DB:2:FAILED:COMMAND_FAILURE",
          rows.getString(1));
      assertFalse(rows.next());
    }
  }

  static final class Probe {
    final List<String> events = new ArrayList<>();
    final Map<String, Integer> counts = new HashMap<>();
    final Map<String, Throwable> faults = new HashMap<>();
    final Map<String, Integer> rowCounts = new HashMap<>();
    final Map<String, Object> role =
        new HashMap<>(
            Map.of(
                "effective_role",
                "schubert_batch",
                "login_role",
                "schubert_batch",
                "database_name",
                "schubert_nk",
                "recovery",
                false));
    boolean auto = true,
        readonly,
        lock = true,
        nullLock,
        held = true,
        any,
        identityConsistent = true,
        nullConnection,
        nullStatement,
        nullRows;
    int isolation = Connection.TRANSACTION_READ_COMMITTED,
        rowCount = 1,
        connections,
        statements,
        rows;
    Properties retained;
    String faultAt = "";
    Throwable failure = new SQLException("PRIVATE");

    void event(String name) throws Throwable {
      String point = name + "#" + counts.merge(name, 1, Integer::sum);
      events.add(point);
      if (faults.containsKey(name)) throw faults.get(name);
      if (point.equals(faultAt)) throw failure;
    }

    MorningDatabaseSession subject() {
      return new MorningDatabaseSession(
          URL,
          this::gate,
          (url, properties) -> open(url, properties, "schubert-nk-morning-controller"),
          this::schema);
    }

    CleanupDatabaseSession cleanupSubject() {
      return new CleanupDatabaseSession(
          URL,
          this::gate,
          (url, properties) -> open(url, properties, "schubert-nk-cleanup"),
          this::schema);
    }

    void gate() throws IOException {
      try {
        event("gate");
      } catch (IOException | RuntimeException | Error failure) {
        throw failure;
      } catch (Throwable failure) {
        throw new AssertionError(failure);
      }
    }

    void schema(Connection connection) throws SQLException, IOException {
      // Explicit synthetic schema port; this fixture does NOT mint root release authority.
      try {
        event("schema");
      } catch (SQLException | IOException | RuntimeException | Error failure) {
        throw failure;
      } catch (Throwable failure) {
        throw new AssertionError(failure);
      }
    }

    Connection open(String url, Properties properties, String application) throws SQLException {
      assertEquals(URL, url);
      assertEquals(
          Set.of("user", "password", "connectTimeout", "ApplicationName"),
          properties.stringPropertyNames());
      assertEquals("schubert_batch", properties.getProperty("user"));
      assertEquals("PUBLIC_PASSWORD", properties.getProperty("password"));
      assertEquals("3", properties.getProperty("connectTimeout"));
      assertEquals(application, properties.getProperty("ApplicationName"));
      retained = properties;
      try {
        event("connect");
      } catch (SQLException | RuntimeException | Error e) {
        throw e;
      } catch (Throwable e) {
        throw new AssertionError(e);
      }
      if (nullConnection) return null;
      connections++;
      return proxy(
          Connection.class,
          (m, a) -> {
            if (m.equals("close")) {
              connections--;
              event("connection.close");
              return null;
            }
            event("connection." + m);
            return switch (m) {
              case "getAutoCommit" -> auto;
              case "isReadOnly" -> readonly;
              case "getTransactionIsolation" -> isolation;
              case "setAutoCommit" -> {
                auto = (boolean) a[0];
                yield null;
              }
              case "prepareStatement" -> statement((String) a[0]);
              case "commit", "rollback" -> null;
              default -> throw new AssertionError(m);
            };
          });
    }

    PreparedStatement statement(String sql) {
      if (nullStatement) return null;
      String kind =
          sql.contains("current_user")
              ? "ROLE"
              : sql.contains("pg_try_advisory")
                  ? "LOCK"
                  : sql.contains("pg_locks")
                      ? "HELD"
                      : sql.contains("maintenance_read_run_references") ? "REF" : "HISTORY";
      statements++;
      return proxy(
          PreparedStatement.class,
          (m, a) -> {
            if (m.equals("close")) {
              statements--;
              event(kind + ".statement.close");
              return null;
            }
            event(kind + ".statement." + m);
            if (m.equals("setQueryTimeout")) {
              assertEquals(5, a[0]);
              return null;
            }
            if (m.equals("setObject") || m.equals("setString")) return null;
            if (!m.equals("executeQuery")) throw new AssertionError(m);
            if (kind.equals("HISTORY")) throw new SQLException("PRIVATE");
            if (nullRows) return null;
            rows++;
            int[] index = {0};
            return proxy(
                ResultSet.class,
                (method, args) -> {
                  if (method.equals("close")) {
                    rows--;
                    event(kind + ".row.close");
                    return null;
                  }
                  event(kind + ".row." + method);
                  return switch (method) {
                    case "next" -> ++index[0] <= rowCounts.getOrDefault(kind, rowCount);
                    case "getString" -> role.get((String) args[0]);
                    case "getObject" -> {
                      String name = (String) args[0];
                      if (kind.equals("LOCK") && nullLock) yield null;
                      yield kind.equals("ROLE")
                          ? role.get(name)
                          : kind.equals("LOCK")
                              ? lock
                              : kind.equals("HELD")
                                  ? held
                                  : name.equals("identity_consistent")
                                      ? identityConsistent
                                      : name.equals("has_batch_history") ? any : false;
                    }
                    default -> throw new AssertionError(method);
                  };
                });
          });
    }

    void released() {
      assertEquals(0, connections);
      assertEquals(0, statements);
      assertEquals(0, rows);
      if (retained != null) assertTrue(retained.isEmpty());
    }
  }

  interface Invocation {
    Object call(String method, Object[] args) throws Throwable;
  }

  @SuppressWarnings("unchecked")
  static <T> T proxy(Class<T> type, Invocation invocation) {
    return (T)
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (p, m, a) -> invocation.call(m.getName(), a));
  }

  @Test
  void fixedUrlRootConstructorAndNullContracts() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession(URL, () -> {}, (url, properties) -> null, null));
    for (String url :
        List.of(
            "",
            "jdbc:postgresql://localhost:5432/schubert_nk",
            URL + "?user=root",
            "jdbc:postgresql://127.0.0.1:0/schubert_nk",
            "jdbc:postgresql://127.0.0.1:65536/schubert_nk",
            URL.replace("schubert_nk", "postgres")))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningDatabaseSession(url, () -> {}, (u, p) -> null));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession(null, () -> {}, (u, p) -> null));
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession(URL, null, (u, p) -> null));
    assertThrows(NullPointerException.class, () -> new MorningDatabaseSession(URL, () -> {}, null));
    var context = RootStartupContext.create();
    var snapshot =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.MORNING, "PUBLIC", "PUBLIC", 2, 1, 1, "PUBLIC");
    assertThrows(NullPointerException.class, () -> new MorningDatabaseSession(URL, null, snapshot));
    assertThrows(NullPointerException.class, () -> new MorningDatabaseSession(URL, context, null));
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession(URL, context, snapshot, null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession(
                URL,
                context,
                new RootStartupContext.Snapshot(
                    RootStartupContext.Service.API, "P", "P", 2, 1, 1, "P")));
    assertThrows(
        IOException.class,
        () -> new MorningDatabaseSession(URL, context, snapshot).execute(credential(), s -> true));
    var p = new Probe();
    assertThrows(NullPointerException.class, () -> p.subject().execute(null, s -> true));
    var c = credential();
    assertThrows(NullPointerException.class, () -> p.subject().execute(c, null));
    assertThrows(IllegalStateException.class, c::copyPassword);
    p.released();
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession.BackupBegins(null, null));
    var a = new BatchStepAttempt(1, RUN, BatchStep.BACKUP_DB, 1, NOW, false);
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession.BackupBegins(a, null));
  }

  @Test
  void literalAdmissionAndSessionLifetime() throws Exception {
    var p = new Probe();
    var holder = new AtomicReference<MorningDatabaseSession.Session>();
    var c = credential();
    assertEquals(
        "PUBLIC",
        p.subject()
            .execute(
                c,
                s -> {
                  holder.set(s);
                  s.requireUnused(RUN);
                  return "PUBLIC";
                }));
    assertFalse(p.auto);
    assertThrows(IllegalStateException.class, c::copyPassword);
    p.released();
    int calls = p.events.size();
    assertThrows(IOException.class, () -> holder.get().requireUnused(RUN));
    assertEquals(calls, p.events.size());
    var current = new Probe();
    assertThrows(
        NullPointerException.class, () -> current.subject().execute(credential(), s -> null));
    current.released();
  }

  @Test
  void mdb013ResumeKeepsSameCutoffWithExistingReferences() throws Exception {
    var p = new Probe();
    p.any = true;
    var escaped = new AtomicReference<MorningDatabaseSession.Session>();
    assertEquals(
        "consistent",
        p.subject()
            .execute(
                credential(),
                session -> {
                  escaped.set(session);
                  session.requireConsistent(RUN);
                  assertThrows(IOException.class, () -> session.requireUnused(RUN));
                  return "consistent";
                }));
    assertTrue(p.events.stream().anyMatch(event -> event.startsWith("REF.statement.executeQuery")));
    p.released();
    assertThrows(IOException.class, () -> escaped.get().requireConsistent(RUN));

    var wrong = new Probe();
    wrong.any = true;
    wrong.identityConsistent = false;
    assertThrows(
        IOException.class,
        () ->
            wrong
                .subject()
                .execute(
                    credential(),
                    session -> {
                      session.requireConsistent(RUN);
                      return true;
                    }));
    wrong.released();

    var nullRun = new Probe();
    assertThrows(
        NullPointerException.class,
        () ->
            nullRun
                .subject()
                .execute(
                    credential(),
                    session -> {
                      session.requireConsistent(null);
                      return true;
                    }));
    nullRun.released();
  }

  @Test
  void mdb014RealResumeReferenceProjectionRejectsDifferentCutoff() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("34500000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(100L * 86400));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    subject.execute(
        credential(),
        session -> {
          session.requireUnused(run);
          session.beginBackup(run, NOW.plusSeconds(100L * 86400), false);
          return true;
        });
    boolean consistent =
        subject.execute(
            credential(),
            session -> {
              session.requireConsistent(run);
              return true;
            });
    assertTrue(consistent);
    var sameBusinessDay = new BatchRun(run.id(), run.cutoff().plusSeconds(1));
    boolean sameDateAccepted =
        subject.execute(
            credential(),
            session -> {
              session.requireConsistent(sameBusinessDay);
              return true;
            });
    assertTrue(sameDateAccepted);
    // SS331 §3.12: batch history has only JST business_date, not the original instant.
    // Exact same-run cutoff is owned by the durable original; this SQL rejects a different day.
    var wrongCutoff = new BatchRun(run.id(), run.cutoff().plusSeconds(86400));
    assertThrows(
        IOException.class,
        () ->
            subject.execute(
                credential(),
                session -> {
                  session.requireConsistent(wrongCutoff);
                  return true;
                }));
  }

  @Test
  void roleRecoveryNullAndLockRejections() throws Exception {
    for (String kind : List.of("LOCK", "HELD"))
      for (int count : List.of(0, 2)) {
        var probe = new Probe();
        probe.rowCounts.put(kind, count);
        assertThrows(IOException.class, () -> probe.subject().execute(credential(), s -> true));
        probe.released();
      }
    for (String key : List.of("effective_role", "login_role", "database_name", "recovery"))
      for (boolean missing : List.of(false, true)) {
        var p = new Probe();
        if (missing) p.role.remove(key);
        else p.role.put(key, key.equals("recovery") ? true : "wrong");
        assertThrows(IOException.class, () -> p.subject().execute(credential(), s -> true), key);
        p.released();
      }
    for (String kind :
        List.of(
            "auto",
            "readonly",
            "isolation",
            "lock",
            "held",
            "connection",
            "statement",
            "rows",
            "none",
            "many")) {
      var p = new Probe();
      switch (kind) {
        case "auto" -> p.auto = false;
        case "readonly" -> p.readonly = true;
        case "isolation" -> p.isolation = 8;
        case "lock" -> p.lock = false;
        case "held" -> p.held = false;
        case "connection" -> p.nullConnection = true;
        case "statement" -> p.nullStatement = true;
        case "rows" -> p.nullRows = true;
        case "none" -> p.rowCount = 0;
        default -> p.rowCount = 2;
      }
      assertThrows(IOException.class, () -> p.subject().execute(credential(), s -> true), kind);
      p.released();
    }
  }

  @Test
  void allAdmissionResourceFailuresAndUnknownIdentity() throws Exception {
    var good = new Probe();
    good.subject()
        .execute(
            credential(),
            s -> {
              s.requireUnused(RUN);
              return true;
            });
    List<String> points = List.copyOf(good.events);
    for (String point : points)
      for (Throwable failure :
          List.of(
              point.startsWith("gate") ? new IOException("PRIVATE") : new SQLException("PRIVATE"),
              new IllegalStateException("PRIVATE"),
              new AssertionError("PRIVATE"))) {
        var p = new Probe();
        p.faultAt = point;
        p.failure = failure;
        Throwable actual =
            assertThrows(
                Throwable.class,
                () ->
                    p.subject()
                        .execute(
                            credential(),
                            s -> {
                              s.requireUnused(RUN);
                              return true;
                            }),
                point);
        if (failure instanceof RuntimeException || failure instanceof Error)
          assertSame(failure, actual, point);
        else assertEquals("root batch database unavailable", actual.getMessage());
        p.released();
      }
    var p = new Probe();
    p.any = true;
    assertThrows(
        IOException.class,
        () ->
            p.subject()
                .execute(
                    credential(),
                    s -> {
                      s.requireUnused(RUN);
                      return true;
                    }));
    p.released();
  }

  @Test
  void compoundUnknownAndNullMethodBoundaries() throws Exception {
    for (Throwable body :
        List.of(
            new SQLException("PRIVATE"),
            new IOException("PRIVATE"),
            new BatchRepositoryException()))
      for (Throwable close :
          List.of(
              new SQLException("PRIVATE"),
              new IllegalStateException("PRIVATE"),
              new AssertionError("PRIVATE"))) {
        var probe = new Probe();
        if (body instanceof SQLException) probe.faults.put("ROLE.row.next", body);
        probe.faults.put("connection.close", close);
        Throwable actual =
            assertThrows(
                Throwable.class,
                () ->
                    probe
                        .subject()
                        .execute(
                            credential(),
                            s -> {
                              if (body instanceof IOException io) throw io;
                              if (body instanceof BatchRepositoryException known) throw known;
                              return true;
                            }));
        if (close instanceof SQLException)
          assertEquals("root batch database unavailable", actual.getMessage());
        else assertSame(close, actual);
        probe.released();
      }
    for (Throwable secondary :
        List.of(
            new SQLException("PRIVATE"),
            new IllegalStateException("PRIVATE"),
            new AssertionError("PRIVATE"))) {
      var p = new Probe();
      var primary = new IllegalStateException("PRIVATE");
      p.faults.put("ROLE.row.next", primary);
      p.faults.put("ROLE.row.close", secondary);
      p.faults.put("ROLE.statement.close", secondary);
      p.faults.put("connection.close", secondary);
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class, () -> p.subject().execute(credential(), s -> true)));
      assertEquals(3, primary.getSuppressed().length);
      for (var f : primary.getSuppressed())
        assertEquals("batch repository operation failed", f.getMessage());
      p.released();
    }
    var p = new Probe();
    assertEquals(
        Boolean.TRUE,
        p.subject()
            .execute(
                credential(),
                s -> {
                  assertThrows(NullPointerException.class, () -> s.requireUnused(null));
                  assertThrows(NullPointerException.class, () -> s.beginBackup(null, NOW, false));
                  assertThrows(NullPointerException.class, () -> s.beginBackup(RUN, null, false));
                  assertThrows(
                      BatchRepositoryException.class, () -> s.beginBackup(RUN, NOW, false));
                  return true;
                }));
    p.released();
    var other = new Probe();
    var primary = new SQLException("PRIVATE");
    var unknown = new AssertionError("PRIVATE");
    other.faults.put("ROLE.row.next", primary);
    other.faults.put("ROLE.row.close", unknown);
    var current = other;
    assertSame(
        unknown,
        assertThrows(
            AssertionError.class, () -> current.subject().execute(credential(), s -> true)));
    other.released();
  }

  @Test
  void interruptionAndForeignThreadCannotUseBorrowedSession() throws Exception {
    for (Throwable failure :
        List.of(
            new SQLException("PRIVATE"),
            new IOException("PRIVATE"),
            new IllegalStateException("PRIVATE"),
            new AssertionError("PRIVATE"))) {
      var blocked = new Probe();
      blocked.faults.put("schema", failure);
      Throwable actual =
          assertThrows(
              Throwable.class,
              () -> blocked.subject().execute(credential(), s -> s.beginBackup(RUN, NOW, false)));
      if (failure instanceof RuntimeException || failure instanceof Error)
        assertSame(failure, actual);
      else assertInstanceOf(IOException.class, actual);
      assertEquals(1, blocked.counts.get("schema"));
      assertTrue(blocked.events.stream().noneMatch(e -> e.startsWith("HISTORY.")));
      assertTrue(blocked.events.stream().noneMatch(e -> e.startsWith("connection.commit")));
      blocked.released();
    }
    var p = new Probe();
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, () -> p.subject().execute(credential(), s -> true));
    } finally {
      Thread.interrupted();
    }
    assertTrue(p.events.isEmpty());
    p.released();
    var q = new Probe();
    assertThrows(
        IOException.class,
        () ->
            q.subject()
                .execute(
                    credential(),
                    s -> {
                      Thread.currentThread().interrupt();
                      return true;
                    }));
    Thread.interrupted();
    q.released();
    var r = new Probe();
    try (var executor = Executors.newSingleThreadExecutor()) {
      assertEquals(
          Boolean.TRUE,
          r.subject()
              .execute(
                  credential(),
                  s -> {
                    try {
                      assertEquals(
                          "root batch database unavailable",
                          executor
                              .submit(
                                  () ->
                                      assertThrows(IOException.class, () -> s.requireUnused(RUN))
                                          .getMessage())
                              .get(5, TimeUnit.SECONDS));
                    } catch (Exception e) {
                      throw new AssertionError(e);
                    }
                    return true;
                  }));
    }
    r.released();
  }

  @Test
  void actualBothBackupBeginsAreCommittedTogether() throws Exception {
    var unverified = new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection);
    var absent =
        new BatchRun(
            UUID.fromString("31400000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(1728000));
    assertThrows(
        IOException.class,
        () ->
            unverified.execute(
                credential(),
                session -> session.beginBackup(absent, NOW.plusSeconds(1728000), false)));
    try (var connection = DriverManager.getConnection(actualUrl, "pgpt_admin", "");
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select count(*) from schubert.batch_runs where run_id='31400000-2222-4333-8444-555555555555'")) {
      assertTrue(rows.next());
      assertEquals(0, rows.getInt(1));
      assertFalse(rows.next());
    }
    var schemaCalls = new AtomicInteger();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            DriverManager::getConnection,
            connection -> {
              assertFalse(connection.isClosed());
              schemaCalls.incrementAndGet();
            });
    var begins =
        subject.execute(
            credential(),
            s -> {
              s.requireUnused(RUN);
              return s.beginBackup(RUN, NOW, false);
            });
    assertEquals(BatchStep.BACKUP_DB, begins.database().step());
    assertEquals(BatchStep.BACKUP_CONFIG, begins.configuration().step());
    assertEquals(RUN, begins.database().run());
    assertEquals(RUN, begins.configuration().run());
    assertNotEquals(begins.database().id(), begins.configuration().id());
    assertEquals(1, schemaCalls.get());
    try (var c = DriverManager.getConnection(actualUrl, "pgpt_admin", "");
        var s = c.createStatement();
        var rows =
            s.executeQuery(
                "select string_agg(step||':'||status||':'||attempt,',' order by step) from schubert.batch_runs where run_id='31100000-2222-4333-8444-555555555555'")) {
      assertTrue(rows.next());
      assertEquals("BACKUP_CONFIG:RUNNING:1,BACKUP_DB:RUNNING:1", rows.getString(1));
      assertFalse(rows.next());
    }
  }

  @Test
  void actualCommitAmbiguityNeverReturnsHandles() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("31100001-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(864000));
    for (boolean afterCommit : List.of(false, true)) {
      AtomicReference<Connection> owned = new AtomicReference<>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, props) -> {
                var c = DriverManager.getConnection(url, props);
                owned.set(c);
                return proxy(
                    Connection.class,
                    (name, args) -> {
                      if (name.equals("commit")) {
                        if (afterCommit) c.commit();
                        throw new SQLException("PRIVATE");
                      }
                      try {
                        return Connection.class
                            .getMethod(name, parameterTypes(name, args))
                            .invoke(c, args);
                      } catch (InvocationTargetException e) {
                        throw e.getCause();
                      }
                    });
              },
              connection -> assertFalse(connection.isClosed()));
      assertThrows(
          IOException.class,
          () ->
              subject.execute(
                  credential(),
                  s -> {
                    s.requireUnused(run);
                    return s.beginBackup(run, NOW.plusSeconds(864000), false);
                  }));
      assertTrue(owned.get().isClosed());
      try (var c = DriverManager.getConnection(actualUrl, "pgpt_admin", "");
          var s = c.createStatement();
          var rows =
              s.executeQuery(
                  "select count(*) from schubert.batch_runs where run_id='31100001-2222-4333-8444-555555555555'")) {
        assertTrue(rows.next());
        assertEquals(afterCommit ? 2 : 0, rows.getInt(1));
      }
    }
  }

  @Test
  void mdb009NoHandoffBeforeConfirmedBackupCommit() throws Exception {
    var p = new Probe();
    var calls = new AtomicInteger();
    assertEquals(
        Boolean.TRUE,
        p.subject()
            .execute(
                credential(),
                session -> {
                  assertThrows(NullPointerException.class, () -> session.handoffCleanup(null));
                  assertEquals(
                      "root batch database unavailable",
                      assertThrows(
                              IOException.class,
                              () ->
                                  session.handoffCleanup(
                                      () -> {
                                        calls.incrementAndGet();
                                        return true;
                                      }))
                          .getMessage());
                  return true;
                }));
    assertEquals(0, calls.get());
    p.released();
  }

  @Test
  void mdb010RealSeparateChildAdvisoryHandoffAndParentReacquire() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("32600000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(2592000));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    try (var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
      assertEquals(
          "CHILD",
          subject.execute(
              credential(),
              session -> {
                session.requireUnused(run);
                var begins = session.beginBackup(run, NOW.plusSeconds(2592000), false);
                assertThrows(IOException.class, () -> session.handoffCleanup(() -> "PREMATURE"));
                confirmActualFailedPair(session, begins);
                assertThrows(
                    IOException.class,
                    () -> session.beginBackup(run, NOW.plusSeconds(2592000), false));
                try (var otherThread = Executors.newSingleThreadExecutor()) {
                  assertEquals(
                      "root batch database unavailable",
                      otherThread
                          .submit(
                              () ->
                                  assertThrows(
                                          IOException.class,
                                          () -> session.handoffCleanup(() -> "WRONG_THREAD"))
                                      .getMessage())
                          .get(5, TimeUnit.SECONDS));
                } catch (InterruptedException failure) {
                  Thread.currentThread().interrupt();
                  throw new IOException("thread check interrupted");
                } catch (ExecutionException | TimeoutException failure) {
                  throw new IOException("thread check failed");
                }
                String result =
                    session.handoffCleanup(
                        () -> {
                          assertThrows(IOException.class, () -> session.requireUnused(run));
                          assertThrows(
                              IOException.class, () -> session.handoffCleanup(() -> "REENTER"));
                          try (var child =
                              DriverManager.getConnection(actualUrl, "schubert_batch", "")) {
                            assertTrue(advisory(child));
                            assertFalse(advisory(observer));
                            return "CHILD";
                          } catch (SQLException failure) {
                            throw new IOException("child database unavailable");
                          }
                        });
                try {
                  assertFalse(advisory(observer));
                } catch (SQLException failure) {
                  throw new IOException("observer database unavailable");
                }
                assertThrows(IOException.class, () -> session.handoffCleanup(() -> "SECOND"));
                assertThrows(IOException.class, () -> session.requireUnused(run));
                return result;
              }));
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  @Test
  void mdb011ChildFailureCannotBecomeSuccessOrRetainParentConnection() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("32600001-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(2678400));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    var callback = new AtomicInteger();
    assertEquals(
        "root batch database unavailable",
        assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          session.requireUnused(run);
                          var begins = session.beginBackup(run, NOW.plusSeconds(2678400), false);
                          confirmActualFailedPair(session, begins);
                          return session.handoffCleanup(
                              () -> {
                                callback.incrementAndGet();
                                throw new IOException("PRIVATE child failure");
                              });
                        }))
            .getMessage());
    assertEquals(1, callback.get());
    try (var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  @Test
  void mdb012AutocommitDriftAfterCommitRefusesChildWithoutCallback() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("32600002-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(2764800));
    var restored = new AtomicBoolean();
    var borrowed = new AtomicReference<Connection>();
    var calls = new AtomicInteger();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var real = DriverManager.getConnection(url, properties);
              borrowed.set(real);
              return proxy(
                  Connection.class,
                  (name, args) -> {
                    if (name.equals("getAutoCommit") && restored.get()) return false;
                    try {
                      return Connection.class
                          .getMethod(name, parameterTypes(name, args))
                          .invoke(real, args);
                    } catch (InvocationTargetException e) {
                      throw e.getCause();
                    }
                  });
            },
            connection -> {});
    assertEquals(
        "root batch database unavailable",
        assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          session.requireUnused(run);
                          var begins = session.beginBackup(run, NOW.plusSeconds(2764800), false);
                          confirmActualFailedPair(session, begins);
                          restored.set(
                              true); // Inject drift only after genuine terminal completion.
                          return session.handoffCleanup(
                              () -> {
                                calls.incrementAndGet();
                                return true;
                              });
                        }))
            .getMessage());
    assertEquals(0, calls.get());
    assertTrue(borrowed.get().isClosed());
  }

  @Test
  void mdb020ReleaseObservationHasFiniteDeadlineAndCannotUnlockAnotherOwner() throws Exception {
    try (var holder = DriverManager.getConnection(actualUrl, "schubert_batch", "");
        var observer = DriverManager.getConnection(actualUrl, "pgpt_admin", "")) {
      assertTrue(advisory(holder));
      assertThrows(
          AssertionError.class, () -> awaitReleased(observer, TimeUnit.MILLISECONDS.toNanos(30)));
      assertFalse(advisory(observer));
      try (var unlock = holder.prepareStatement("select pg_advisory_unlock(71419602)")) {
        try (var result = unlock.executeQuery()) {
          assertTrue(result.next());
          assertTrue(result.getBoolean(1));
        }
      }
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  private static void awaitReleased(Connection observer, long budgetNanos) throws Exception {
    long deadline = System.nanoTime() + budgetNanos;
    while (!advisory(observer)) {
      if (System.nanoTime() >= deadline) fail("server advisory release deadline exceeded");
      TimeUnit.MILLISECONDS.sleep(5);
    }
  }

  private static boolean advisory(Connection connection) throws SQLException {
    try (var statement = connection.prepareStatement("select pg_try_advisory_lock(71419602)")) {
      try (var rows = statement.executeQuery()) {
        assertTrue(rows.next());
        boolean result = rows.getBoolean(1);
        assertFalse(rows.next());
        return result;
      }
    }
  }

  private static void confirmActualFailedPair(
      MorningDatabaseSession.Access session, MorningDatabaseSession.BackupBegins begins)
      throws IOException {
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    session.failBackup(begins, begins.database().startedAt().plusSeconds(1), failed, failed);
  }

  private static Class<?>[] parameterTypes(String name, Object[] args) {
    if (args == null) return new Class<?>[0];
    if (name.equals("prepareStatement")) return new Class<?>[] {String.class};
    if (name.equals("setAutoCommit")) return new Class<?>[] {boolean.class};
    throw new AssertionError(name);
  }
}
