package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.lang.reflect.*;
import java.nio.file.Path;
import java.sql.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

/** MDB001..008. Literal role/lock oracle; actual isolated DB transaction in MDB007/008. */
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
        held = true,
        any,
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
          () -> {
            try {
              event("gate");
            } catch (IOException | RuntimeException | Error e) {
              throw e;
            } catch (Throwable e) {
              throw new AssertionError(e);
            }
          },
          (url, properties) -> {
            assertEquals(URL, url);
            assertEquals(
                Set.of("user", "password", "connectTimeout", "ApplicationName"),
                properties.stringPropertyNames());
            assertEquals("schubert_batch", properties.getProperty("user"));
            assertEquals("PUBLIC_PASSWORD", properties.getProperty("password"));
            assertEquals("3", properties.getProperty("connectTimeout"));
            assertEquals(
                "schubert-nk-morning-controller", properties.getProperty("ApplicationName"));
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
          },
          connection -> {
            // Explicit synthetic schema port; this fixture does NOT mint root release authority.
            try {
              event("schema");
            } catch (SQLException | IOException | RuntimeException | Error failure) {
              throw failure;
            } catch (Throwable failure) {
              throw new AssertionError(failure);
            }
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
                      yield kind.equals("ROLE")
                          ? role.get(name)
                          : kind.equals("LOCK")
                              ? lock
                              : kind.equals("HELD")
                                  ? held
                                  : name.equals("identity_consistent")
                                      ? true
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

  private static Class<?>[] parameterTypes(String name, Object[] args) {
    if (args == null) return new Class<?>[0];
    if (name.equals("prepareStatement")) return new Class<?>[] {String.class};
    if (name.equals("setAutoCommit")) return new Class<?>[] {boolean.class};
    throw new AssertionError(name);
  }
}
