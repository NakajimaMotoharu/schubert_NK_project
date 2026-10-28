package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmissionTest;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** CDB001..009. Literal role/lock vectors, injected JDBC failures and independent actual PG. */
final class CleanupDatabaseSessionTest {
  private static final String FIXTURE_PGPT_ADMIN_F5D1227C = "pgpt_admin";
  private static final String FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A =
      "root cleanup database unavailable";
  private static final String FIXTURE_AUTO_634635A2 = "auto";
  private static final String FIXTURE_READONLY_C4A495E7 = "readonly";
  private static final String FIXTURE_ISOLATION_AB1E8569 = "isolation";
  private static final String FIXTURE_PRIVATE_D45CA6F9 = "PRIVATE";
  private static final String FIXTURE_KNOWN_BADD3000 = "known";
  private static final String FIXTURE_UNKNOWN_EB8BF0D8 = "unknown";
  @TempDir static Path directory;
  static BatchDatabaseFixture db;
  static String actualUrl;

  @BeforeAll
  static void database() throws Exception {
    db = new BatchDatabaseFixture(directory);
    try (var connection = db.admin();
        var statement = connection.createStatement()) {
      actualUrl = connection.getMetaData().getURL().replace("/postgres", "/schubert_nk");
      statement.execute("create database schubert_nk");
    }
    Path sql =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db");
    try (var connection = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement = connection.createStatement()) {
      statement.execute(Files.readString(sql.resolve("provisioning/001_roles.sql")));
    }
    Flyway.configure()
        .dataSource(actualUrl, "schubert_migration", "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .locations("filesystem:" + sql.resolve("migration"))
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
    return InspectorDbCredential.consume("PUBLIC_PASSWORD".getBytes(StandardCharsets.US_ASCII));
  }

  @Test
  void cdb001FixedUrlNullAndRootActorContract() throws Exception {
    for (String url :
        List.of(
            "",
            "jdbc:postgresql://localhost:5432/schubert_nk",
            MorningDatabaseSessionTest.URL + "?user=other",
            "jdbc:postgresql://127.0.0.1:0/schubert_nk",
            "jdbc:postgresql://127.0.0.1:65536/schubert_nk",
            MorningDatabaseSessionTest.URL.replace("schubert_nk", "postgres")))
      assertThrows(
          IllegalArgumentException.class,
          () -> new CleanupDatabaseSession(url, () -> {}, (u, p) -> null, c -> {}));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupDatabaseSession(null, () -> {}, (u, p) -> null, c -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupDatabaseSession(
                MorningDatabaseSessionTest.URL, null, (u, p) -> null, c -> {}));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupDatabaseSession(MorningDatabaseSessionTest.URL, () -> {}, null, c -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupDatabaseSession(
                MorningDatabaseSessionTest.URL, () -> {}, (u, p) -> null, null));
    var root = RootStartupContext.create();
    var morning =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.MORNING, "PUBLIC", "PUBLIC", 2, 1, 1, "PUBLIC");
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupDatabaseSession(MorningDatabaseSessionTest.URL, root, morning, null));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupDatabaseSession(MorningDatabaseSessionTest.URL, null, morning, null));
    var child = RootReleaseAdmissionTest.syntheticCleanup();
    assertEquals(1, child.reads().get());
    assertThrows(
        NullPointerException.class,
        () -> new CleanupDatabaseSession(actualUrl, child.context(), null, child.release()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupDatabaseSession(actualUrl, child.context(), child.snapshot(), null));
    var actual =
        new CleanupDatabaseSession(actualUrl, child.context(), child.snapshot(), child.release());
    assertEquals(1, child.reads().get()); // Construction is not a fresh child admission.
    var calls = new AtomicInteger();
    assertEquals(
        FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A,
        assertThrows(
                IOException.class,
                () ->
                    actual.execute(
                        credential(),
                        connection -> {
                          calls.incrementAndGet();
                          return true;
                        }))
            .getMessage());
    assertEquals(0, calls.get());
    assertEquals(2, child.reads().get()); // create + child fresh schema read; no fixture success.
  }

  @Test
  void cdb002LiteralRoleSchemaBeforeLockAndAllOwnerClose() throws Exception {
    var p = new MorningDatabaseSessionTest.Probe();
    var owner = credential();
    assertEquals(
        "OK",
        p.cleanupSubject()
            .execute(
                owner,
                connection -> {
                  assertEquals(1, p.connections);
                  assertTrue(p.auto);
                  return "OK";
                }));
    assertEquals(1, p.counts.get("schema"));
    assertEquals(1, p.counts.get("LOCK.statement.executeQuery"));
    assertEquals(2, p.counts.get("HELD.statement.executeQuery"));
    assertTrue(p.events.indexOf("schema#1") < p.events.indexOf("LOCK.statement.executeQuery#1"));
    assertThrows(IllegalStateException.class, owner::copyPassword);
    p.released();
  }

  @Test
  void cdb003RoleStateRowsAndNullJdbcObjectsFailClosed() throws Exception {
    for (String kind :
        List.of(
            FIXTURE_AUTO_634635A2,
            FIXTURE_READONLY_C4A495E7,
            FIXTURE_ISOLATION_AB1E8569,
            "role",
            "recovery",
            "nullRole",
            "connection",
            "statement",
            "rows",
            "none",
            "many")) {
      var p = new MorningDatabaseSessionTest.Probe();
      switch (kind) {
        case FIXTURE_AUTO_634635A2 -> p.auto = false;
        case FIXTURE_READONLY_C4A495E7 -> p.readonly = true;
        case FIXTURE_ISOLATION_AB1E8569 -> p.isolation = Connection.TRANSACTION_SERIALIZABLE;
        case "role" -> p.role.put("effective_role", "wrong");
        case "recovery" -> p.role.put("recovery", true);
        case "nullRole" -> p.role.remove("login_role");
        case "connection" -> p.nullConnection = true;
        case "statement" -> p.nullStatement = true;
        case "rows" -> p.nullRows = true;
        case "none" -> p.rowCount = 0;
        default -> p.rowCount = 2;
      }
      var calls = new AtomicInteger();
      assertThrows(
          IOException.class,
          () ->
              p.cleanupSubject()
                  .execute(
                      credential(),
                      c -> {
                        calls.incrementAndGet();
                        return true;
                      }),
          kind);
      assertEquals(0, calls.get(), kind);
      p.released();
    }
  }

  @Test
  void cdb004SchemaAndRootGateMustPrecedeLockAndCallback() throws Exception {
    for (Throwable failure :
        List.of(
            new IOException(FIXTURE_PRIVATE_D45CA6F9),
            new SQLException(FIXTURE_PRIVATE_D45CA6F9),
            new AssertionError(FIXTURE_PRIVATE_D45CA6F9))) {
      var p = new MorningDatabaseSessionTest.Probe();
      p.faults.put("schema", failure);
      var calls = new AtomicInteger();
      Throwable actual =
          assertThrows(
              Throwable.class,
              () ->
                  p.cleanupSubject()
                      .execute(
                          credential(),
                          c -> {
                            calls.incrementAndGet();
                            return true;
                          }));
      if (failure instanceof Error) assertSame(failure, actual);
      else assertEquals(FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A, actual.getMessage());
      assertEquals(0, calls.get());
      assertFalse(p.events.stream().anyMatch(e -> e.startsWith("LOCK.")));
      p.released();
    }
    var blocked = new MorningDatabaseSessionTest.Probe();
    blocked.faults.put("gate", new IOException(FIXTURE_PRIVATE_D45CA6F9));
    assertThrows(
        IOException.class, () -> blocked.cleanupSubject().execute(credential(), c -> true));
    assertTrue(blocked.events.stream().noneMatch(e -> e.startsWith("connect")));
    blocked.released();
  }

  @Test
  void cdb005BusyMissingAndAmbiguousAdvisoryNeverCallBody() throws Exception {
    for (String kind : List.of("lockFalse", "heldFalse", "lockMissing", "heldMany", "lockNull")) {
      var p = new MorningDatabaseSessionTest.Probe();
      switch (kind) {
        case "lockFalse" -> p.lock = false;
        case "heldFalse" -> p.held = false;
        case "lockMissing" -> p.rowCounts.put("LOCK", 0);
        case "heldMany" -> p.rowCounts.put("HELD", 2);
        default -> p.nullLock = true;
      }
      var calls = new AtomicInteger();
      assertThrows(
          IOException.class,
          () ->
              p.cleanupSubject()
                  .execute(
                      credential(),
                      c -> {
                        calls.incrementAndGet();
                        return true;
                      }),
          kind);
      assertEquals(0, calls.get());
      p.released();
    }
  }

  @Test
  void cdb006CallbackNullKnownUnknownAndPostStateRefusal() throws Exception {
    var p = new MorningDatabaseSessionTest.Probe();
    assertThrows(NullPointerException.class, () -> p.cleanupSubject().execute(null, c -> true));
    var c = credential();
    assertThrows(NullPointerException.class, () -> p.cleanupSubject().execute(c, null));
    assertThrows(IllegalStateException.class, c::copyPassword);
    p.released();
    for (String kind :
        List.of(
            "null",
            FIXTURE_KNOWN_BADD3000,
            FIXTURE_UNKNOWN_EB8BF0D8,
            FIXTURE_AUTO_634635A2,
            FIXTURE_READONLY_C4A495E7,
            FIXTURE_ISOLATION_AB1E8569,
            "held")) {
      var current = new MorningDatabaseSessionTest.Probe();
      var unknown = new IllegalStateException("PUBLIC unknown");
      Throwable actual =
          assertThrows(
              Throwable.class,
              () ->
                  current
                      .cleanupSubject()
                      .execute(
                          credential(),
                          connection -> {
                            return switch (kind) {
                              case "null" -> null;
                              case FIXTURE_KNOWN_BADD3000 ->
                                  throw new IOException(FIXTURE_PRIVATE_D45CA6F9);
                              case FIXTURE_UNKNOWN_EB8BF0D8 -> throw unknown;
                              case FIXTURE_AUTO_634635A2 -> {
                                current.auto = false;
                                yield true;
                              }
                              case FIXTURE_READONLY_C4A495E7 -> {
                                current.readonly = true;
                                yield true;
                              }
                              case FIXTURE_ISOLATION_AB1E8569 -> {
                                current.isolation = Connection.TRANSACTION_SERIALIZABLE;
                                yield true;
                              }
                              default -> {
                                current.held = false;
                                yield true;
                              }
                            };
                          }));
      if (kind.equals(FIXTURE_UNKNOWN_EB8BF0D8)) assertSame(unknown, actual);
      else if (kind.equals("null")) assertInstanceOf(NullPointerException.class, actual);
      else assertEquals(FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A, actual.getMessage());
      current.released();
    }
  }

  @Test
  void cdb007ActualSeparateRoleConnectionAndParallelLockContention() throws Exception {
    var subject =
        new CleanupDatabaseSession(
            actualUrl,
            () -> {},
            DriverManager::getConnection,
            connection -> assertFalse(connection.isClosed()));
    var childCalls = new AtomicInteger();
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var executor = Executors.newSingleThreadExecutor()) {
      assertEquals(
          "DONE",
          subject.execute(
              credential(),
              child -> {
                try (var statement = child.createStatement();
                    var rows = statement.executeQuery("select current_user::text")) {
                  assertTrue(rows.next());
                  assertEquals("schubert_batch", rows.getString(1));
                  assertFalse(rows.next());
                } catch (SQLException failure) {
                  throw new IOException("child role observation unavailable");
                }
                try {
                  assertFalse(advisory(observer));
                  assertEquals(
                      FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A,
                      executor
                          .submit(
                              () ->
                                  assertThrows(
                                          IOException.class,
                                          () ->
                                              subject.execute(
                                                  credential(),
                                                  concurrent -> {
                                                    childCalls.incrementAndGet();
                                                    return "WRONG";
                                                  }))
                                      .getMessage())
                          .get(5, TimeUnit.SECONDS));
                } catch (SQLException
                    | InterruptedException
                    | ExecutionException
                    | TimeoutException failure) {
                  throw new IOException("parallel advisory observation unavailable");
                }
                return "DONE";
              }));
      assertEquals(0, childCalls.get());
      long releaseDeadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
      while (!advisory(observer)) {
        if (System.nanoTime() >= releaseDeadline) fail("server advisory release deadline exceeded");
        TimeUnit.MILLISECONDS.sleep(5);
      }
    }
  }

  @Test
  void cdb008InterruptAndCloseFailuresDoNotReturnSuccess() throws Exception {
    var interrupted = new MorningDatabaseSessionTest.Probe();
    Thread.currentThread().interrupt();
    try {
      assertThrows(
          IOException.class,
          () -> interrupted.cleanupSubject().execute(credential(), connection -> true));
    } finally {
      Thread.interrupted();
    }
    assertTrue(interrupted.events.isEmpty());
    interrupted.released();
    var close = new MorningDatabaseSessionTest.Probe();
    close.faults.put("connection.close", new SQLException("PRIVATE close"));
    assertEquals(
        FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A,
        assertThrows(
                IOException.class,
                () -> close.cleanupSubject().execute(credential(), connection -> true))
            .getMessage());
    close.released();

    var good = new MorningDatabaseSessionTest.Probe();
    good.cleanupSubject().execute(credential(), connection -> true);
    for (String point : List.copyOf(good.events)) {
      if (!(point.startsWith("connect")
          || point.startsWith("connection.")
          || point.startsWith("ROLE.")
          || point.startsWith("LOCK.")
          || point.startsWith("HELD."))) continue;
      var faulted = new MorningDatabaseSessionTest.Probe();
      faulted.faultAt = point;
      faulted.failure = new SQLException(FIXTURE_PRIVATE_D45CA6F9);
      assertEquals(
          FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A,
          assertThrows(
                  IOException.class,
                  () -> faulted.cleanupSubject().execute(credential(), connection -> true),
                  point)
              .getMessage());
      faulted.released();
    }
    good.released();

    for (String first :
        List.of("success", FIXTURE_KNOWN_BADD3000, "batch", FIXTURE_UNKNOWN_EB8BF0D8))
      for (String second : List.of("sql", "runtime", "error")) {
        var combined = new MorningDatabaseSessionTest.Probe();
        Throwable secondary =
            switch (second) {
              case "sql" -> new SQLException("PRIVATE close");
              case "runtime" -> new IllegalStateException("PUBLIC close");
              default -> new AssertionError("PUBLIC close");
            };
        combined.faults.put("connection.close", secondary);
        var unknown = new IllegalStateException("PUBLIC callback");
        Throwable actual =
            assertThrows(
                Throwable.class,
                () ->
                    combined
                        .cleanupSubject()
                        .execute(
                            credential(),
                            connection -> {
                              return switch (first) {
                                case FIXTURE_KNOWN_BADD3000 ->
                                    throw new IOException("PRIVATE callback");
                                case "batch" -> throw new BatchRepositoryException();
                                case FIXTURE_UNKNOWN_EB8BF0D8 -> throw unknown;
                                default -> true;
                              };
                            }));
        if (first.equals(FIXTURE_UNKNOWN_EB8BF0D8)) {
          assertSame(unknown, actual);
          assertEquals(1, unknown.getSuppressed().length);
          assertEquals(
              "batch repository operation failed", unknown.getSuppressed()[0].getMessage());
        } else if (second.equals("sql"))
          assertEquals(FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A, actual.getMessage());
        else assertSame(secondary, actual);
        combined.released();
      }

    var nested = new MorningDatabaseSessionTest.Probe();
    nested.faultAt = "ROLE.row.next#1";
    nested.failure = new SQLException("PRIVATE primary");
    nested.faults.put("ROLE.row.close", new SQLException("PRIVATE row close"));
    nested.faults.put("ROLE.statement.close", new SQLException("PRIVATE statement close"));
    nested.faults.put("connection.close", new SQLException("PRIVATE connection close"));
    assertEquals(
        FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A,
        assertThrows(
                IOException.class,
                () -> nested.cleanupSubject().execute(credential(), connection -> true))
            .getMessage());
    nested.released();
  }

  @Test
  void cdb009PublicChildAdmissionSucceedsOnlyWithFreshMatchingRelease() throws Exception {
    var rows = migrationRows();
    var child = RootReleaseAdmissionTest.syntheticCleanup(rows);
    assertEquals(1, child.reads().get());
    var subject =
        new CleanupDatabaseSession(actualUrl, child.context(), child.snapshot(), child.release());
    assertEquals(1, child.reads().get());
    assertEquals("ACCEPTED", subject.execute(credential(), connection -> "ACCEPTED"));
    assertEquals(2, child.reads().get()); // New read during the child's borrowed DB session.
  }

  /** PT-OPS-CDB3200001 / SS343 child role and fresh schema, before deletion authority. */
  @Test
  void cdb3200001ExpiryFactoryRetainsRoleFreshSchemaAndClosesEveryOwner() throws Exception {
    var wrong = RootReleaseAdmissionTest.syntheticExpiry();
    var owner = credential();
    var calls = new AtomicInteger();
    var refused =
        CleanupDatabaseSession.forExpiry(
            actualUrl, wrong.context(), wrong.snapshot(), wrong.release());
    assertEquals(1, wrong.reads().get());
    assertEquals(
        FIXTURE_ROOT_CLEANUP_DATABASE_UNAVAILABLE_6B76238A,
        assertThrows(
                IOException.class,
                () -> refused.execute(owner, connection -> calls.incrementAndGet()))
            .getMessage());
    assertEquals(0, calls.get());
    assertEquals(2, wrong.reads().get());
    assertThrows(IllegalStateException.class, owner::copyPassword);

    var child = RootReleaseAdmissionTest.syntheticExpiry(migrationRows());
    assertEquals(RootStartupContext.Service.EXPIRY, child.snapshot().service());
    var subject =
        CleanupDatabaseSession.forExpiry(
            actualUrl, child.context(), child.snapshot(), child.release());
    assertEquals(1, child.reads().get());
    var borrowed = new ArrayList<Connection>();
    var validOwner = credential();
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
      assertEquals(
          "EXPIRY-OWNED",
          subject.execute(
              validOwner,
              connection -> {
                borrowed.add(connection);
                try (var statement = connection.createStatement();
                    var rows = statement.executeQuery("select current_user::text")) {
                  assertTrue(rows.next());
                  assertEquals("schubert_batch", rows.getString(1));
                  assertFalse(rows.next());
                  assertTrue(connection.getAutoCommit());
                  assertFalse(connection.isReadOnly());
                  assertFalse(advisory(observer));
                } catch (SQLException failure) {
                  throw new IOException("test Expiry role/lock observation unavailable");
                }
                return "EXPIRY-OWNED";
              }));
      assertEquals(1, borrowed.size());
      assertTrue(borrowed.getFirst().isClosed());
      assertTrue(advisory(observer));
    }
    assertEquals(2, child.reads().get());
    assertThrows(IllegalStateException.class, validOwner::copyPassword);
    var cleanup = RootReleaseAdmissionTest.syntheticCleanup();
    assertThrows(
        IllegalArgumentException.class,
        () ->
            CleanupDatabaseSession.forExpiry(
                actualUrl, cleanup.context(), cleanup.snapshot(), child.release()));
    assertThrows(
        NullPointerException.class,
        () -> CleanupDatabaseSession.forExpiry(actualUrl, child.context(), child.snapshot(), null));
    assertThrows(
        NullPointerException.class,
        () -> CleanupDatabaseSession.forExpiry(actualUrl, null, child.snapshot(), child.release()));
    assertThrows(
        NullPointerException.class,
        () -> CleanupDatabaseSession.forExpiry(actualUrl, child.context(), null, child.release()));
  }

  private static List<SchemaHistoryAdmission.Row> migrationRows() throws Exception {
    List<SchemaHistoryAdmission.Row> rows = new ArrayList<>();
    try (var connection = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement =
            connection.prepareStatement(
                "select installed_rank,version,type,script,checksum,success"
                    + " from schubert_meta.startup_schema_history() order by installed_rank");
        var result = statement.executeQuery()) {
      while (result.next())
        rows.add(
            new SchemaHistoryAdmission.Row(
                result.getInt("installed_rank"),
                result.getString("version"),
                result.getString("type"),
                result.getString("script"),
                result.getObject("checksum", Integer.class),
                result.getBoolean("success")));
    }
    assertEquals(29, rows.size()); // SCHEMA + independently approved V001..V028 (SSC201).
    assertEquals("028", rows.getLast().version());
    return rows;
  }

  private static boolean advisory(Connection connection) throws SQLException {
    try (var statement = connection.prepareStatement("select pg_try_advisory_lock(71419602)");
        var rows = statement.executeQuery()) {
      assertTrue(rows.next());
      boolean actual = rows.getBoolean(1);
      assertFalse(rows.next());
      return actual;
    }
  }
}
