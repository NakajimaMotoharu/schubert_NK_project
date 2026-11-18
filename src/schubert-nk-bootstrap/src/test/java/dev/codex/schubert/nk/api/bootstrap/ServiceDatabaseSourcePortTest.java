package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLFeatureNotSupportedException;
import java.sql.SQLNonTransientConnectionException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-OPS-001/SYS002004/DAT001/UI212243253/SS343/SSC084; PT-OPS-DBSRCPORT-001..014. */
@Timeout(10)
final class ServiceDatabaseSourcePortTest {
  private static final int NULL_SERVICE_CASE = 0;
  private static final int NULL_URL_CASE = 1;
  private static final int NULL_CONNECTOR_CASE = 2;
  private static final int INVALID_URL_CASE = 3;
  private static final int EMPTY_PASSWORD_CASE = 4;
  private static final int OVERLONG_PASSWORD_CASE = 5;
  private static final int FIRST_CONNECTOR_CALL = 1;
  private static final String URL = "jdbc:postgresql://127.0.0.1:5432/sample";
  private static final String API_ROLE = "schubert_app";
  private static final String WEB_ROLE = "schubert_web_session";
  private static final String USER = "user";
  private static final String PASSWORD = "password";
  private static final String TIMEOUT = "connectTimeout";
  private static final String APPLICATION = "ApplicationName";
  private static final String FIXTURE = "independent connector fixture failure";
  private static final String UNAVAILABLE = "service database connection unavailable";
  private static final String UNSUPPORTED = "service database option unavailable";
  private static final String STATE = "08001";
  private static final String UNSUPPORTED_STATE = "0A000";
  private static final String REDACTED = "ServiceDatabaseSource[REDACTED]";
  private static final String SQL =
      "select current_user::text as effective_role,session_user::text as login_role,"
          + "current_database()::text as database_name,pg_is_in_recovery() as recovery";

  private enum FaultKind {
    SQL,
    RUNTIME,
    ERROR;

    Throwable freshFailure() {
      return switch (this) {
        case SQL -> new SQLException(FIXTURE, "ZZ999");
        case RUNTIME -> new IllegalStateException(FIXTURE);
        case ERROR -> new AssertionError(FIXTURE);
      };
    }
  }

  private static final class Fixture {
    private final String role;
    private boolean admitted = true;
    private @Nullable Throwable bodyFault;
    private @Nullable Throwable closeFault;
    private int prepares;
    private int rowCloses;
    private int statementCloses;
    private int connectionCloses;
    private final Connection connection;

    Fixture(String role) {
      this.role = role;
      connection =
          proxy(
              Connection.class,
              (p, method, args) ->
                  switch (method.getName()) {
                    case "getAutoCommit" -> {
                      if (bodyFault != null) throw bodyFault;
                      yield true;
                    }
                    case "isReadOnly" -> false;
                    case "prepareStatement" -> {
                      assertEquals(SQL, args[0]);
                      prepares++;
                      yield statement();
                    }
                    case "close" -> {
                      connectionCloses++;
                      if (closeFault != null) throw closeFault;
                      yield null;
                    }
                    default -> throw new AssertionError(method.getName());
                  });
    }

    private PreparedStatement statement() {
      return proxy(
          PreparedStatement.class,
          (p, method, args) ->
              switch (method.getName()) {
                case "executeQuery" -> rows();
                case "close" -> {
                  statementCloses++;
                  yield null;
                }
                default -> throw new AssertionError(method.getName());
              });
    }

    private ResultSet rows() {
      int[] position = {0};
      return proxy(
          ResultSet.class,
          (p, method, args) ->
              switch (method.getName()) {
                case "next" -> {
                  boolean first = position[0] == 0;
                  position[0]++;
                  yield first;
                }
                case "getString" ->
                    switch ((String) args[0]) {
                      case "effective_role", "login_role" -> admitted ? role : "different_role";
                      case "database_name" -> "sample";
                      default -> throw new AssertionError(method.getName());
                    };
                case "getObject" -> {
                  assertEquals("recovery", args[0]);
                  assertSame(Boolean.class, args[1]);
                  yield false;
                }
                case "close" -> {
                  rowCloses++;
                  yield null;
                }
                default -> throw new AssertionError(method.getName());
              });
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(
        Proxy.newProxyInstance(
            ClassLoader.getPlatformClassLoader(), new Class<?>[] {type}, handler));
  }

  private static char[] material(int length) {
    char[] value = new char[length];
    Arrays.fill(value, 'x');
    return value;
  }

  private static ServiceDatabaseSource source(ServiceDatabaseSource.Connector connector) {
    return new ServiceDatabaseSource(ServiceConfigFiles.Service.API, URL, material(1), connector);
  }

  private static SQLNonTransientConnectionException fixedUnavailable(ServiceDatabaseSource source) {
    var failure = assertThrows(SQLNonTransientConnectionException.class, source::getConnection);
    assertEquals(UNAVAILABLE, failure.getMessage());
    assertEquals(STATE, failure.getSQLState());
    assertNull(failure.getCause());
    assertNull(failure.getNextException());
    assertEquals(0, failure.getSuppressed().length);
    return failure;
  }

  private static void fixedUnsupported(org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(SQLFeatureNotSupportedException.class, operation);
    assertEquals(UNSUPPORTED, failure.getMessage());
    assertEquals(UNSUPPORTED_STATE, failure.getSQLState());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void fixedSecondary(Throwable failure) {
    assertEquals(1, failure.getSuppressed().length);
    var fixed = (SQLNonTransientConnectionException) failure.getSuppressed()[0];
    assertEquals(UNAVAILABLE, fixed.getMessage());
    assertEquals(STATE, fixed.getSQLState());
    assertNull(fixed.getCause());
    assertNull(fixed.getNextException());
    assertEquals(0, fixed.getSuppressed().length);
  }

  @Test
  void dbSource001PublicConstructionErasesInputWithoutConnecting() {
    for (var service : ServiceConfigFiles.Service.values()) {
      char[] owned = material(1);
      var source = new ServiceDatabaseSource(service, URL, owned);
      try {
        assertArrayEquals(new char[1], owned);
        assertEquals(REDACTED, source.toString());
        source.close();
        source.close();
        // The pinned closed gate returns before the default connector is ever invoked.
        fixedUnavailable(source);
      } finally {
        source.close();
      }
    }
  }

  @Test
  void dbSource002BothRolesFixedPropertiesAndEachPhysicalAdmission() throws Exception {
    for (var service : ServiceConfigFiles.Service.values()) {
      String role = service == ServiceConfigFiles.Service.API ? API_ROLE : WEB_ROLE;
      String app =
          service == ServiceConfigFiles.Service.API ? "schubert-nk-api" : "schubert-nk-web";
      var fixtures = new ArrayList<Fixture>();
      var captured = new ArrayList<Properties>();
      var source =
          new ServiceDatabaseSource(
              service,
              URL,
              material(1),
              (url, properties) -> {
                assertEquals(URL, url);
                assertEquals(4, properties.size());
                assertEquals(role, properties.getProperty(USER));
                assertEquals("x", properties.getProperty(PASSWORD));
                assertEquals("3", properties.getProperty(TIMEOUT));
                assertEquals(app, properties.getProperty(APPLICATION));
                captured.add(properties);
                var fixture = new Fixture(role);
                fixtures.add(fixture);
                return fixture.connection;
              });
      try {
        var first = source.getConnection();
        var second = source.getConnection();
        assertNotSame(first, second);
        assertEquals(2, fixtures.size());
        source.close();
        for (var fixture : fixtures) {
          assertEquals(1, fixture.prepares);
          assertEquals(1, fixture.rowCloses);
          assertEquals(1, fixture.statementCloses);
          assertEquals(0, fixture.connectionCloses);
          fixture.connection.close();
          assertEquals(1, fixture.connectionCloses);
        }
        for (var properties : captured) assertTrue(properties.isEmpty());
      } finally {
        source.close();
      }
    }
  }

  @Test
  void dbSource003InvalidConstructionStillConsumesOwnedInput() {
    ServiceDatabaseSource.Connector noConnect =
        (u, p) -> {
          throw new AssertionError(FIXTURE);
        };
    for (int kind : List.of(0, 1, 2, 3, 4, 5)) {
      char[] owned =
          material(kind == EMPTY_PASSWORD_CASE ? 0 : kind == OVERLONG_PASSWORD_CASE ? 65537 : 1);
      if (kind == NULL_SERVICE_CASE)
        assertThrows(
            NullPointerException.class,
            () -> new ServiceDatabaseSource(null, URL, owned, noConnect));
      else if (kind == NULL_URL_CASE)
        assertThrows(
            NullPointerException.class,
            () ->
                new ServiceDatabaseSource(ServiceConfigFiles.Service.API, null, owned, noConnect));
      else if (kind == NULL_CONNECTOR_CASE)
        assertThrows(
            NullPointerException.class,
            () -> new ServiceDatabaseSource(ServiceConfigFiles.Service.API, URL, owned, null));
      else if (kind == INVALID_URL_CASE)
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new ServiceDatabaseSource(
                    ServiceConfigFiles.Service.API, URL + "?bad", owned, noConnect));
      else
        assertThrows(
            IllegalArgumentException.class,
            () -> new ServiceDatabaseSource(ServiceConfigFiles.Service.API, URL, owned, noConnect));
      assertArrayEquals(new char[owned.length], owned);
    }
    assertEquals(
        "owned password",
        assertThrows(
                NullPointerException.class,
                () ->
                    new ServiceDatabaseSource(ServiceConfigFiles.Service.API, URL, null, noConnect))
            .getMessage());
  }

  @Test
  void dbSource004MaterialBoundsAndConstructorCloneAreIndependent() throws Exception {
    for (int length : List.of(1, 65536)) {
      char[] owned = material(length);
      var fixture = new Fixture(API_ROLE);
      var captured = new AtomicReference<Properties>();
      try (var source =
          new ServiceDatabaseSource(
              ServiceConfigFiles.Service.API,
              URL,
              owned,
              (u, p) -> {
                assertEquals("x".repeat(length), p.getProperty(PASSWORD));
                captured.set(p);
                return fixture.connection;
              })) {
        assertArrayEquals(new char[length], owned);
        owned[0] = 'z';
        assertSame(fixture.connection, source.getConnection());
        assertTrue(captured.get().isEmpty());
        fixture.connection.close();
      }
    }
  }

  @Test
  void dbSource005ConnectorFaultsClearPropertiesAndKeepUnknownIdentity() {
    for (var kind : FaultKind.values()) {
      Throwable expected = kind.freshFailure();
      var captured = new AtomicReference<Properties>();
      try (var source =
          source(
              (u, p) -> {
                captured.set(p);
                if (expected instanceof SQLException sql) throw sql;
                if (expected instanceof RuntimeException runtime) throw runtime;
                throw (Error) expected;
              })) {
        if (kind == FaultKind.SQL) fixedUnavailable(source);
        else assertSame(expected, assertThrows(expected.getClass(), source::getConnection));
        assertTrue(captured.get().isEmpty());
      }
    }
  }

  @Test
  void dbSource006NullConnectionCannotEscapeAsSuccess() {
    var captured = new AtomicReference<Properties>();
    try (var source =
        source(
            (u, p) -> {
              captured.set(p);
              return null;
            })) {
      fixedUnavailable(source);
      assertTrue(captured.get().isEmpty());
    }
  }

  @Test
  void dbSource007FailedIdentityAdmissionDiscardsExactlyOnce() {
    var fixture = new Fixture(API_ROLE);
    fixture.admitted = false;
    var captured = new AtomicReference<Properties>();
    try (var source =
        source(
            (u, p) -> {
              captured.set(p);
              return fixture.connection;
            })) {
      fixedUnavailable(source);
      assertEquals(1, fixture.prepares);
      assertEquals(1, fixture.rowCloses);
      assertEquals(1, fixture.statementCloses);
      assertEquals(1, fixture.connectionCloses);
      assertTrue(captured.get().isEmpty());
    }
  }

  @Test
  void dbSource008AdmissionRuntimeAndErrorRetainOriginalIdentity() {
    for (var kind : List.of(FaultKind.RUNTIME, FaultKind.ERROR)) {
      var fixture = new Fixture(API_ROLE);
      Throwable expected = kind.freshFailure();
      fixture.bodyFault = expected;
      var captured = new AtomicReference<Properties>();
      try (var source =
          source(
              (u, p) -> {
                captured.set(p);
                return fixture.connection;
              })) {
        assertSame(expected, assertThrows(expected.getClass(), source::getConnection));
        assertEquals(1, fixture.connectionCloses);
        assertEquals(0, fixture.prepares);
        assertEquals(0, expected.getSuppressed().length);
        assertTrue(captured.get().isEmpty());
      }
    }
  }

  @Test
  void dbSource009DiscardSqlRuntimeErrorMatrixAndSameThrowable() {
    for (var bodyKind : FaultKind.values()) {
      for (var closeKind : FaultKind.values()) {
        var fixture = new Fixture(API_ROLE);
        Throwable body = bodyKind.freshFailure();
        Throwable closing = closeKind.freshFailure();
        fixture.bodyFault = body;
        fixture.closeFault = closing;
        try (var source = source((u, p) -> fixture.connection)) {
          if (bodyKind == FaultKind.SQL && closeKind == FaultKind.SQL) fixedUnavailable(source);
          else {
            Throwable expected = bodyKind == FaultKind.SQL ? closing : body;
            assertSame(expected, assertThrows(expected.getClass(), source::getConnection));
            if (bodyKind == FaultKind.SQL) assertEquals(0, expected.getSuppressed().length);
            else fixedSecondary(expected);
          }
          assertEquals(1, fixture.connectionCloses);
        }
      }
    }
    var same = new Fixture(API_ROLE);
    var expected = new IllegalStateException(FIXTURE);
    same.bodyFault = expected;
    same.closeFault = expected;
    try (var source = source((u, p) -> same.connection)) {
      assertSame(expected, assertThrows(IllegalStateException.class, source::getConnection));
      fixedSecondary(expected);
      assertEquals(1, same.connectionCloses);
    }
  }

  @Test
  void dbSource010UnsupportedOptionsAndMemoryWriterOnly() throws Exception {
    try (var source =
            source(
                (u, p) -> {
                  throw new AssertionError(FIXTURE);
                });
        var writer = new PrintWriter(new StringWriter())) {
      fixedUnsupported(() -> source.getConnection(null, null));
      fixedUnsupported(() -> source.setLogWriter(writer));
      fixedUnsupported(source::getParentLogger);
      assertNull(source.getLogWriter());
      source.setLogWriter(null);
      source.setLoginTimeout(3);
      assertEquals(3, source.getLoginTimeout());
      for (int seconds : List.of(Integer.MIN_VALUE, -1, 0, 2, 4, Integer.MAX_VALUE))
        fixedUnsupported(() -> source.setLoginTimeout(seconds));
      assertEquals(REDACTED, source.toString());
    }
  }

  @Test
  void dbSource011WrapperTypeContractAndNullBoundary() throws Exception {
    try (var source =
        source(
            (u, p) -> {
              throw new AssertionError(FIXTURE);
            })) {
      assertTrue(source.isWrapperFor(ServiceDatabaseSource.class));
      assertTrue(source.isWrapperFor(DataSource.class));
      assertSame(source, source.unwrap(ServiceDatabaseSource.class));
      assertSame(source, source.unwrap(DataSource.class));
      assertSame(source, source.unwrap(AutoCloseable.class));
      assertFalse(source.isWrapperFor(Connection.class));
      fixedUnsupported(() -> source.unwrap(Connection.class));
      assertEquals(
          "wrapper type",
          assertThrows(NullPointerException.class, () -> source.unwrap(null)).getMessage());
      assertEquals(
          "wrapper type",
          assertThrows(NullPointerException.class, () -> source.isWrapperFor(null)).getMessage());
    }
  }

  @Test
  void dbSource012CloseIsIdempotentAndPreservesCallerOwnedConnection() throws Exception {
    var fixture = new Fixture(API_ROLE);
    var connections = new AtomicInteger();
    var source =
        source(
            (u, p) -> {
              connections.incrementAndGet();
              return fixture.connection;
            });
    try {
      assertSame(fixture.connection, source.getConnection());
      source.close();
      source.close();
      assertEquals(0, fixture.connectionCloses);
      fixedUnavailable(source);
      assertEquals(1, connections.get());
      fixture.connection.close();
      assertEquals(1, fixture.connectionCloses);
    } finally {
      source.close();
    }
  }

  @Test
  void dbSource013ParallelIndependentConnectionsAndPropertiesClear() throws Exception {
    var created = new AtomicInteger();
    try (var source =
        source(
            (u, p) -> {
              created.incrementAndGet();
              assertEquals("x", p.getProperty(PASSWORD));
              return new Fixture(API_ROLE).connection;
            })) {
      var executor = Executors.newVirtualThreadPerTaskExecutor();
      try {
        var tasks = new ArrayList<java.util.concurrent.Future<Connection>>();
        for (int i = 0; i < 8; i++)
          tasks.add(
              executor.submit(
                  () -> {
                    return source.getConnection();
                  }));
        var returned = new ArrayList<Connection>();
        for (var task : tasks) {
          var connection = task.get(5, TimeUnit.SECONDS);
          for (var previous : returned) assertNotSame(previous, connection);
          returned.add(connection);
          connection.close();
        }
        assertEquals(8, created.get());
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void dbSource014CloseRaceHasFiniteCallerOwnershipPostcondition() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var created = new AtomicInteger();
    var fixture = new Fixture(API_ROLE);
    var captured = new AtomicReference<Properties>();
    try (var source =
        source(
            (u, p) -> {
              created.incrementAndGet();
              captured.set(p);
              entered.countDown();
              try {
                assertTrue(release.await(5, TimeUnit.SECONDS));
              } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
                throw new SQLException(FIXTURE);
              }
              return fixture.connection;
            })) {
      var executor = Executors.newVirtualThreadPerTaskExecutor();
      try {
        var acquiring =
            executor.submit(
                () -> {
                  return source.getConnection();
                });
        try {
          assertTrue(entered.await(5, TimeUnit.SECONDS));
          var closing = executor.submit(source::close);
          release.countDown();
          assertSame(fixture.connection, acquiring.get(5, TimeUnit.SECONDS));
          closing.get(5, TimeUnit.SECONDS);
        } finally {
          release.countDown();
        }
        fixedUnavailable(source);
        assertEquals(1, created.get());
        assertEquals(0, fixture.connectionCloses);
        assertTrue(captured.get().isEmpty());
        fixture.connection.close();
        assertEquals(1, fixture.connectionCloses);
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void dbSource015FatalConnectorGraphRetainsIdentityAndClearsProperties() {
    var fatal = new AssertionError(FIXTURE);
    var failure = new SQLException(FIXTURE);
    failure.setNextException(new SQLException(FIXTURE, fatal));
    var captured = new AtomicReference<Properties>();
    try (var source =
        source(
            (url, properties) -> {
              captured.set(properties);
              throw failure;
            })) {
      assertSame(fatal, assertThrows(AssertionError.class, source::getConnection));
      assertTrue(captured.get().isEmpty());
    }
  }

  @Test
  void dbSource016ConnectorFailureReleasesTheStateLockForAnotherThread() throws Exception {
    var firstFailure = new IllegalStateException(FIXTURE);
    var captured = new AtomicReference<Properties>();
    var calls = new AtomicInteger();
    var fixture = new Fixture(API_ROLE);
    try (var source =
        source(
            (url, properties) -> {
              if (calls.incrementAndGet() == FIRST_CONNECTOR_CALL) {
                captured.set(properties);
                throw firstFailure;
              }
              return fixture.connection;
            })) {
      assertSame(firstFailure, assertThrows(IllegalStateException.class, source::getConnection));
      assertTrue(captured.get().isEmpty());
      var worker = Executors.newVirtualThreadPerTaskExecutor();
      try {
        var retry =
            worker.submit(
                () -> {
                  return source.getConnection();
                });
        assertSame(fixture.connection, retry.get(5, TimeUnit.SECONDS));
        assertEquals(2, calls.get());
        assertEquals(0, fixture.connectionCloses);
        fixture.connection.close();
        assertEquals(1, fixture.connectionCloses);
      } finally {
        worker.shutdownNow();
        assertTrue(worker.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }
}
