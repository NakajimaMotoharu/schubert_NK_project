package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-DBSOURCE-001..006; real isolated PG roles plus public JDBC fault/ownership probes. */
final class ServiceDatabaseSourceTest {
  private static final String FIXTURE_UNTRUSTED_6FC6869D = "UNTRUSTED";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static String url;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    try (var admin = database.admin()) {
      url = admin.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  private static char[] fixturePassword() {
    return "pt-public-password".toCharArray();
  }

  @Test
  void opsDbsource001BothFixedRolesAndInputErasure() throws Exception {
    for (var service : ServiceConfigFiles.Service.values()) {
      char[] owned = fixturePassword();
      try (var source = new ServiceDatabaseSource(service, url, owned)) {
        assertArrayEquals(new char[owned.length], owned);
        try (var connection = source.getConnection();
            var statement = connection.createStatement();
            var rows =
                statement.executeQuery("select current_user::text,current_database()::text")) {
          assertTrue(rows.next());
          assertEquals(
              service == ServiceConfigFiles.Service.API ? "schubert_app" : "schubert_web_session",
              rows.getString(1));
          assertEquals("postgres", rows.getString(2));
          assertFalse(rows.next());
          closeOwnedSource(source);
          closeOwnedSource(source);
          assertFalse(connection.isClosed());
          fixedFailure(source::getConnection);
        }
        assertEquals("ServiceDatabaseSource[REDACTED]", source.toString());
      }
    }
  }

  @Test
  void opsDbsource002EveryPhysicalPoolConnectionIsAdmitted() throws Exception {
    AtomicInteger created = new AtomicInteger();
    AtomicInteger admitted = new AtomicInteger();
    AtomicReference<Properties> supplied = new AtomicReference<>();
    var connector =
        (ServiceDatabaseSource.Connector)
            (target, properties) -> {
              assertEquals(url, target);
              assertEquals("schubert_app", properties.getProperty("user"));
              assertEquals("pt-public-password", properties.getProperty("password"));
              assertEquals("3", properties.getProperty("connectTimeout"));
              assertEquals("schubert-nk-api", properties.getProperty("ApplicationName"));
              assertEquals(4, properties.size());
              supplied.set(properties);
              created.incrementAndGet();
              return probe(
                  DriverManager.getConnection(target, properties),
                  null,
                  null,
                  admitted,
                  new AtomicInteger());
            };
    try (var source =
            new ServiceDatabaseSource(
                ServiceConfigFiles.Service.API, url, fixturePassword(), connector);
        var pool = physicalPool(source)) {
      var held = new ArrayList<Connection>();
      try {
        for (int i = 0; i < 8; i++) held.add(pool.getConnection());
        assertEquals(8, created.get());
        assertEquals(created.get(), admitted.get());
        assertTrue(supplied.get().isEmpty());
      } finally {
        for (var connection : held) connection.close();
      }
    }
    assertEquals(created.get(), admitted.get());
  }

  private static com.zaxxer.hikari.HikariDataSource physicalPool(javax.sql.DataSource source) {
    // Independent real pool fixture. The Production API/Web pool configuration is tested there.
    var config = new com.zaxxer.hikari.HikariConfig();
    config.setDataSource(source);
    config.setMaximumPoolSize(8);
    config.setMinimumIdle(2);
    config.setConnectionTimeout(3_000);
    return new com.zaxxer.hikari.HikariDataSource(config);
  }

  @Test
  void opsDbsource003NullProviderWrongRoleAndSqlFailuresCloseBeforeRefusal() throws Exception {
    AtomicReference<Properties> properties = new AtomicReference<>();
    for (boolean nullResult : List.of(true, false)) {
      try (var source =
          new ServiceDatabaseSource(
              ServiceConfigFiles.Service.API,
              url,
              fixturePassword(),
              (target, p) -> {
                properties.set(p);
                if (nullResult) return null;
                throw new SQLException(FIXTURE_UNTRUSTED_6FC6869D, "99999");
              })) {
        fixedFailure(source::getConnection);
        assertTrue(properties.get().isEmpty());
      }
    }
    AtomicInteger closed = new AtomicInteger();
    try (var source =
        new ServiceDatabaseSource(
            ServiceConfigFiles.Service.API,
            url,
            fixturePassword(),
            (target, p) -> probe(database.admin(), null, null, new AtomicInteger(), closed))) {
      fixedFailure(source::getConnection);
      assertEquals(1, closed.get());
    }
    try (var source =
        new ServiceDatabaseSource(
            ServiceConfigFiles.Service.API,
            url,
            fixturePassword(),
            (target, p) ->
                probe(
                    database.api(),
                    new SQLException(FIXTURE_UNTRUSTED_6FC6869D),
                    new SQLException(FIXTURE_UNTRUSTED_6FC6869D),
                    new AtomicInteger(),
                    closed))) {
      fixedFailure(source::getConnection);
      assertEquals(2, closed.get());
    }
  }

  @Test
  void opsDbsource004UnknownAndCompoundFailuresPreserveIdentity() throws Exception {
    for (Throwable primary :
        List.of(
            new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D),
            new NullPointerException(FIXTURE_UNTRUSTED_6FC6869D),
            new AssertionError(FIXTURE_UNTRUSTED_6FC6869D))) {
      for (Throwable cleanup :
          Arrays.asList(
              null,
              new SQLException(FIXTURE_UNTRUSTED_6FC6869D),
              primary,
              new AssertionError(FIXTURE_UNTRUSTED_6FC6869D))) {
        AtomicInteger closed = new AtomicInteger();
        AtomicReference<Properties> properties = new AtomicReference<>();
        try (var source =
            new ServiceDatabaseSource(
                ServiceConfigFiles.Service.API,
                url,
                fixturePassword(),
                (target, p) -> {
                  properties.set(p);
                  return probe(database.api(), primary, cleanup, new AtomicInteger(), closed);
                })) {
          assertSame(primary, assertThrows(primary.getClass(), source::getConnection));
          assertEquals(1, closed.get());
          assertTrue(properties.get().isEmpty());
          for (Throwable secondary : primary.getSuppressed()) {
            assertEquals("service database connection unavailable", secondary.getMessage());
            assertNull(secondary.getCause());
          }
        }
      }
    }
    for (Throwable cleanup :
        List.of(
            new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D),
            new AssertionError(FIXTURE_UNTRUSTED_6FC6869D))) {
      AtomicInteger closed = new AtomicInteger();
      try (var source =
          new ServiceDatabaseSource(
              ServiceConfigFiles.Service.API,
              url,
              fixturePassword(),
              (target, p) ->
                  probe(
                      database.api(),
                      new SQLException(FIXTURE_UNTRUSTED_6FC6869D),
                      cleanup,
                      new AtomicInteger(),
                      closed))) {
        assertSame(cleanup, assertThrows(cleanup.getClass(), source::getConnection));
        assertEquals(1, closed.get());
      }
    }
    IllegalStateException connectorFailure = new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D);
    AtomicReference<Properties> properties = new AtomicReference<>();
    try (var source =
        new ServiceDatabaseSource(
            ServiceConfigFiles.Service.API,
            url,
            fixturePassword(),
            (target, p) -> {
              properties.set(p);
              throw connectorFailure;
            })) {
      assertSame(
          connectorFailure, assertThrows(IllegalStateException.class, source::getConnection));
      assertTrue(properties.get().isEmpty());
    }
  }

  @Test
  void opsDbsource005OptionsNullUrlSizeAndConstructorFailureErasure() throws Exception {
    for (int mode = 0; mode < 5; mode++) {
      char[] owned = fixturePassword();
      int condition = mode;
      Class<? extends RuntimeException> expected =
          condition < 3 ? NullPointerException.class : IllegalArgumentException.class;
      assertThrows(
          expected,
          () ->
              new ServiceDatabaseSource(
                  condition == 0 ? null : ServiceConfigFiles.Service.API,
                  condition == 1
                      ? null
                      : condition == 3 ? "jdbc:postgresql://localhost:5432/db" : url,
                  condition == 4 ? new char[0] : owned,
                  condition == 2 ? null : DriverManager::getConnection));
      if (mode != 4) assertArrayEquals(new char[owned.length], owned);
    }
    char[] tooLarge = new char[65537];
    Arrays.fill(tooLarge, 'x');
    assertThrows(
        IllegalArgumentException.class,
        () -> new ServiceDatabaseSource(ServiceConfigFiles.Service.API, url, tooLarge));
    assertArrayEquals(new char[65537], tooLarge);
    assertThrows(
        NullPointerException.class,
        () -> new ServiceDatabaseSource(ServiceConfigFiles.Service.API, url, null));
    try (var boundary =
            new ServiceDatabaseSource(ServiceConfigFiles.Service.API, url, new char[65536]);
        var source =
            new ServiceDatabaseSource(ServiceConfigFiles.Service.API, url, fixturePassword())) {
      assertEquals(3, boundary.getLoginTimeout());
      assertEquals(3, source.getLoginTimeout());
      source.setLoginTimeout(3);
      assertThrows(SQLException.class, () -> source.setLoginTimeout(0));
      assertNull(source.getLogWriter());
      source.setLogWriter(null);
      assertThrows(
          SQLException.class, () -> source.setLogWriter(new PrintWriter(new StringWriter())));
      assertThrows(SQLException.class, source::getParentLogger);
      assertThrows(SQLException.class, () -> source.getConnection("arbitrary", "arbitrary"));
      assertThrows(SQLException.class, () -> source.getConnection(null, null));
      assertTrue(source.isWrapperFor(DataSource.class));
      assertFalse(source.isWrapperFor(String.class));
      assertSame(source, source.unwrap(DataSource.class));
      assertThrows(SQLException.class, () -> source.unwrap(String.class));
      assertThrows(NullPointerException.class, () -> source.unwrap(null));
      assertThrows(NullPointerException.class, () -> source.isWrapperFor(null));
    }
  }

  @Test
  void opsDbsource006ConcurrentConnectionsAndPrivateMonitor() throws Exception {
    try (var source =
            new ServiceDatabaseSource(ServiceConfigFiles.Service.WEB, url, fixturePassword());
        var workers = Executors.newFixedThreadPool(8)) {
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 32; i++)
        work.add(
            () -> {
              try (var connection = source.getConnection()) {
                return !connection.isClosed();
              }
            });
      for (var result : workers.invokeAll(work)) assertTrue(result.get(5, TimeUnit.SECONDS));
      synchronized (source) {
        assertTrue(
            workers
                .submit(
                    () -> {
                      try (var connection = source.getConnection()) {
                        closeOwnedSource(source);
                        return !connection.isClosed();
                      }
                    })
                .get(5, TimeUnit.SECONDS));
      }
      fixedFailure(source::getConnection);
    }
  }

  private static Connection probe(
      Connection actual,
      Throwable primary,
      Throwable cleanup,
      AtomicInteger admissions,
      AtomicInteger closes) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (ignored, method, arguments) -> {
              if (method.getName().equals("getAutoCommit") && primary != null) throw primary;
              if (method.getName().equals("prepareStatement")
                  && ((String) arguments[0]).startsWith("select current_user"))
                admissions.incrementAndGet();
              try {
                Object result = method.invoke(actual, arguments);
                if (method.getName().equals("close")) {
                  closes.incrementAndGet();
                  if (cleanup != null) throw cleanup;
                }
                return result;
              } catch (InvocationTargetException failure) {
                throw failure.getCause();
              }
            });
  }

  private static void fixedFailure(org.junit.jupiter.api.function.Executable action) {
    SQLException failure = assertThrows(SQLException.class, action);
    assertEquals("08001", failure.getSQLState());
    assertEquals("service database connection unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void closeOwnedSource(ServiceDatabaseSource source) {
    source.close();
  }
}
