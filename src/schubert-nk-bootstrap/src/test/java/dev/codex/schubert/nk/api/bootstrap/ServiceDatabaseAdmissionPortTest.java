package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLNonTransientConnectionException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-OPS-001/SYS002004/DAT001/UI212243253/SS3435.2; PT-OPS-DBPORT-001..015. */
@Timeout(10)
final class ServiceDatabaseAdmissionPortTest {
  private static final String URL = "jdbc:postgresql://127.0.0.1:5432/sample";
  private static final String API_ROLE = "schubert_app";
  private static final String WEB_ROLE = "schubert_web_session";
  private static final String DATABASE = "sample";
  private static final String EFFECTIVE = "effective_role";
  private static final String LOGIN = "login_role";
  private static final String DATABASE_COLUMN = "database_name";
  private static final String RECOVERY_COLUMN = "recovery";
  private static final String FIXTURE_MESSAGE = "independent admission fixture failure";
  private static final String FIXED_MESSAGE = "service database connection unavailable";
  private static final String SECONDARY_MESSAGE = "database admission resource failure";
  private static final String STATE = "08001";
  private static final String SQL =
      "select current_user::text as effective_role,session_user::text as login_role,"
          + "current_database()::text as database_name,pg_is_in_recovery() as recovery";

  private enum Phase {
    AUTO_COMMIT,
    READ_ONLY,
    PREPARE,
    QUERY,
    FIRST_ROW,
    EFFECTIVE_ROLE,
    LOGIN_ROLE,
    DATABASE_NAME,
    RECOVERY,
    EXTRA_ROW,
    ROWS_CLOSE,
    STATEMENT_CLOSE
  }

  private static final List<Phase> SUCCESS = List.of(Phase.values());

  private static final class Fixture {
    private final List<Phase> calls = new ArrayList<>();
    private boolean autoCommit = true;
    private boolean readOnly;
    private boolean firstRow = true;
    private boolean extraRow;
    private boolean nullStatement;
    private boolean nullRows;
    private @Nullable String effectiveRole = API_ROLE;
    private @Nullable String loginRole = API_ROLE;
    private @Nullable String database = DATABASE;
    private @Nullable Boolean recovery = false;
    private @Nullable Phase faultAt;
    private @Nullable Throwable bodyFault;
    private @Nullable Throwable rowCloseFault;
    private @Nullable Throwable statementCloseFault;
    private int nextCalls;
    private final ResultSet rows =
        proxy(
            ResultSet.class,
            (p, method, args) -> {
              return switch (method.getName()) {
                case "next" -> {
                  boolean first = nextCalls == 0;
                  nextCalls++;
                  yield first
                      ? record(Phase.FIRST_ROW, firstRow)
                      : record(Phase.EXTRA_ROW, extraRow);
                }
                case "getString" ->
                    switch ((String) args[0]) {
                      case EFFECTIVE -> record(Phase.EFFECTIVE_ROLE, effectiveRole);
                      case LOGIN -> record(Phase.LOGIN_ROLE, loginRole);
                      case DATABASE_COLUMN -> record(Phase.DATABASE_NAME, database);
                      default -> throw new AssertionError(method.getName());
                    };
                case "getObject" -> {
                  assertEquals(RECOVERY_COLUMN, args[0]);
                  assertSame(Boolean.class, args[1]);
                  yield record(Phase.RECOVERY, recovery);
                }
                case "close" -> close(Phase.ROWS_CLOSE, rowCloseFault);
                default -> throw new AssertionError(method.getName());
              };
            });
    private final PreparedStatement statement =
        proxy(
            PreparedStatement.class,
            (p, method, args) -> {
              return switch (method.getName()) {
                case "executeQuery" -> record(Phase.QUERY, nullRows ? null : rows);
                case "close" -> close(Phase.STATEMENT_CLOSE, statementCloseFault);
                default -> throw new AssertionError(method.getName());
              };
            });
    private final Connection connection =
        proxy(
            Connection.class,
            (p, method, args) -> {
              return switch (method.getName()) {
                case "getAutoCommit" -> record(Phase.AUTO_COMMIT, autoCommit);
                case "isReadOnly" -> record(Phase.READ_ONLY, readOnly);
                case "prepareStatement" -> {
                  assertEquals(SQL, args[0]);
                  yield record(Phase.PREPARE, nullStatement ? null : statement);
                }
                // Caller-owned Connection close/commit/rollback/configuration must never be
                // invoked.
                default -> throw new AssertionError(method.getName());
              };
            });

    private @Nullable Object record(Phase phase, @Nullable Object value) throws Throwable {
      calls.add(phase);
      if (phase == faultAt) throw java.util.Objects.requireNonNull(bodyFault);
      return value;
    }

    private @Nullable Object close(Phase phase, @Nullable Throwable fault) throws Throwable {
      calls.add(phase);
      if (fault != null) throw fault;
      return null;
    }

    private void fault(Phase phase, Throwable failure) {
      faultAt = phase;
      bodyFault = failure;
    }

    private void assertCloses(int rowsCount, int statementsCount) {
      assertEquals(rowsCount, Collections.frequency(calls, Phase.ROWS_CLOSE));
      assertEquals(statementsCount, Collections.frequency(calls, Phase.STATEMENT_CLOSE));
      if (rowsCount == 1 && statementsCount == 1) {
        assertTrue(calls.indexOf(Phase.ROWS_CLOSE) < calls.indexOf(Phase.STATEMENT_CLOSE));
      }
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(
        Proxy.newProxyInstance(
            ClassLoader.getPlatformClassLoader(), new Class<?>[] {type}, handler));
  }

  private static ServiceDatabaseAdmission api() {
    return new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, URL);
  }

  private static void unavailable(ServiceDatabaseAdmission admission, Fixture fixture) {
    var failure =
        assertThrows(
            SQLNonTransientConnectionException.class, () -> admission.verify(fixture.connection));
    assertEquals(FIXED_MESSAGE, failure.getMessage());
    assertEquals(STATE, failure.getSQLState());
    assertEquals(0, failure.getErrorCode());
    assertNull(failure.getCause());
    assertNull(failure.getNextException());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void fixedSecondary(Throwable failure, int count) {
    assertEquals(count, failure.getSuppressed().length);
    for (Throwable secondary : failure.getSuppressed()) {
      var fixed = assertInstanceOf(SQLNonTransientConnectionException.class, secondary);
      assertEquals(SECONDARY_MESSAGE, fixed.getMessage());
      assertEquals(STATE, fixed.getSQLState());
      assertNull(fixed.getCause());
      assertNull(fixed.getNextException());
      assertEquals(0, fixed.getSuppressed().length);
    }
  }

  @Test
  void dbAdmission001UrlBoundsAndBothRoles() throws Exception {
    for (String port : List.of("1", "65535")) {
      for (String name : List.of("a", "_", "a".repeat(63))) {
        for (var service : ServiceConfigFiles.Service.values()) {
          var fixture = new Fixture();
          fixture.database = name;
          fixture.effectiveRole = service == ServiceConfigFiles.Service.API ? API_ROLE : WEB_ROLE;
          fixture.loginRole = fixture.effectiveRole;
          new ServiceDatabaseAdmission(service, "jdbc:postgresql://127.0.0.1:" + port + "/" + name)
              .verify(fixture.connection);
          assertEquals(SUCCESS, fixture.calls);
        }
      }
    }
  }

  @Test
  void dbAdmission002InvalidUrlsAndNullConstructorInputs() {
    for (String url :
        List.of(
            "",
            "jdbc:postgresql://localhost:5432/sample",
            "jdbc:postgresql://127.0.0.1:0/sample",
            "jdbc:postgresql://127.0.0.1:01/sample",
            "jdbc:postgresql://127.0.0.1:65536/sample",
            "jdbc:postgresql://127.0.0.1:99999/sample",
            "jdbc:postgresql://127.0.0.1:100000/sample",
            URL + "?user=fixture",
            URL + "#fixture",
            "jdbc:postgresql://127.0.0.1:5432/1database",
            URL + "-invalid",
            "jdbc:postgresql://127.0.0.1:5432/" + "a".repeat(64))) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, url));
      assertEquals("service database URL is invalid", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertEquals(
        "service",
        assertThrows(NullPointerException.class, () -> new ServiceDatabaseAdmission(null, URL))
            .getMessage());
    assertEquals(
        "database URL",
        assertThrows(
                NullPointerException.class,
                () -> new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, null))
            .getMessage());
  }

  @Test
  void dbAdmission003FixedProjectionAndBorrowedConnection() throws Exception {
    var fixture = new Fixture();
    api().verify(fixture.connection);
    assertEquals(SUCCESS, fixture.calls);
    fixture.assertCloses(1, 1);
  }

  @Test
  void dbAdmission004ConnectionSettingsAndNullContract() {
    var admission = api();
    var transaction = new Fixture();
    transaction.autoCommit = false;
    unavailable(admission, transaction);
    assertEquals(List.of(Phase.AUTO_COMMIT), transaction.calls);
    var readOnly = new Fixture();
    readOnly.readOnly = true;
    unavailable(admission, readOnly);
    assertEquals(List.of(Phase.AUTO_COMMIT, Phase.READ_ONLY), readOnly.calls);
    assertEquals(
        "database connection",
        assertThrows(NullPointerException.class, () -> admission.verify(null)).getMessage());
  }

  @Test
  void dbAdmission005EachProjectionInvariantFailsClosed() {
    List<Consumer<Fixture>> invalid =
        List.of(
            f -> f.firstRow = false,
            f -> f.extraRow = true,
            f -> f.effectiveRole = WEB_ROLE,
            f -> f.effectiveRole = null,
            f -> f.loginRole = WEB_ROLE,
            f -> f.loginRole = null,
            f -> f.database = "different",
            f -> f.database = null,
            f -> f.recovery = true,
            f -> f.recovery = null);
    for (var change : invalid) {
      var fixture = new Fixture();
      change.accept(fixture);
      unavailable(api(), fixture);
      fixture.assertCloses(1, 1);
    }
  }

  @Test
  void dbAdmission006MissingStatementAndRowsCloseOnlyAcquiredPorts() {
    var noStatement = new Fixture();
    noStatement.nullStatement = true;
    unavailable(api(), noStatement);
    noStatement.assertCloses(0, 0);
    var noRows = new Fixture();
    noRows.nullRows = true;
    unavailable(api(), noRows);
    noRows.assertCloses(0, 1);
  }

  @Test
  void dbAdmission007EachSqlFaultIsFixedAndSanitized() {
    for (Phase phase : SUCCESS) {
      if (phase == Phase.ROWS_CLOSE || phase == Phase.STATEMENT_CLOSE) continue;
      var fixture = new Fixture();
      fixture.fault(phase, new SQLException(FIXTURE_MESSAGE, "ZZ999"));
      unavailable(api(), fixture);
      int index = SUCCESS.indexOf(phase);
      fixture.assertCloses(
          index >= SUCCESS.indexOf(Phase.FIRST_ROW) ? 1 : 0,
          index >= SUCCESS.indexOf(Phase.QUERY) ? 1 : 0);
    }
  }

  @Test
  void dbAdmission008SqlCloseFaultCannotReturnSuccess() {
    var rows = new Fixture();
    rows.rowCloseFault = new SQLException(FIXTURE_MESSAGE);
    unavailable(api(), rows);
    rows.assertCloses(1, 1);
    var statement = new Fixture();
    statement.statementCloseFault = new SQLException(FIXTURE_MESSAGE);
    unavailable(api(), statement);
    statement.assertCloses(1, 1);
  }

  @Test
  void dbAdmission009RuntimeFaultIdentityAndCleanup() {
    for (Phase phase :
        List.of(Phase.AUTO_COMMIT, Phase.PREPARE, Phase.QUERY, Phase.FIRST_ROW, Phase.RECOVERY)) {
      var fixture = new Fixture();
      var expected = new IllegalStateException(FIXTURE_MESSAGE);
      fixture.fault(phase, expected);
      assertSame(
          expected,
          assertThrows(IllegalStateException.class, () -> api().verify(fixture.connection)));
      int index = SUCCESS.indexOf(phase);
      fixture.assertCloses(
          index >= SUCCESS.indexOf(Phase.FIRST_ROW) ? 1 : 0,
          index >= SUCCESS.indexOf(Phase.QUERY) ? 1 : 0);
    }
  }

  @Test
  void dbAdmission010ErrorFaultIdentityAndCleanup() {
    for (Phase phase :
        List.of(Phase.AUTO_COMMIT, Phase.PREPARE, Phase.QUERY, Phase.FIRST_ROW, Phase.RECOVERY)) {
      var fixture = new Fixture();
      var expected = new AssertionError(FIXTURE_MESSAGE);
      fixture.fault(phase, expected);
      assertSame(
          expected, assertThrows(AssertionError.class, () -> api().verify(fixture.connection)));
      int index = SUCCESS.indexOf(phase);
      fixture.assertCloses(
          index >= SUCCESS.indexOf(Phase.FIRST_ROW) ? 1 : 0,
          index >= SUCCESS.indexOf(Phase.QUERY) ? 1 : 0);
    }
  }

  @Test
  void dbAdmission011KnownSqlBodyYieldsToUnknownClose() {
    for (boolean rowsClose : List.of(false, true)) {
      var fixture = new Fixture();
      var expected = new IllegalStateException(FIXTURE_MESSAGE);
      fixture.fault(Phase.FIRST_ROW, new SQLException(FIXTURE_MESSAGE));
      if (rowsClose) fixture.rowCloseFault = expected;
      else fixture.statementCloseFault = expected;
      assertSame(
          expected,
          assertThrows(IllegalStateException.class, () -> api().verify(fixture.connection)));
      fixedSecondary(expected, 0);
      fixture.assertCloses(1, 1);
    }
    var sameKnown = new Fixture();
    var primary = new SQLException(FIXTURE_MESSAGE);
    sameKnown.fault(Phase.FIRST_ROW, primary);
    sameKnown.rowCloseFault = primary;
    sameKnown.statementCloseFault = primary;
    unavailable(api(), sameKnown);
    assertEquals(0, primary.getSuppressed().length);
    sameKnown.assertCloses(1, 1);
  }

  @Test
  void dbAdmission012UnknownPrimaryRetainsOnlyFixedSecondary() {
    for (boolean same : List.of(false, true)) {
      var fixture = new Fixture();
      var expected = new IllegalStateException(FIXTURE_MESSAGE);
      fixture.fault(Phase.FIRST_ROW, expected);
      fixture.rowCloseFault = same ? expected : new IllegalArgumentException(FIXTURE_MESSAGE);
      fixture.statementCloseFault = new SQLException(FIXTURE_MESSAGE);
      assertSame(
          expected,
          assertThrows(IllegalStateException.class, () -> api().verify(fixture.connection)));
      fixedSecondary(expected, 2);
      fixture.assertCloses(1, 1);
    }
  }

  @Test
  void dbAdmission013ErrorPrimaryAndBothCloseFaultsRetainIdentity() {
    var fixture = new Fixture();
    var expected = new AssertionError(FIXTURE_MESSAGE);
    fixture.fault(Phase.FIRST_ROW, expected);
    fixture.rowCloseFault = expected;
    fixture.statementCloseFault = new AssertionError(FIXTURE_MESSAGE);
    assertSame(
        expected, assertThrows(AssertionError.class, () -> api().verify(fixture.connection)));
    fixedSecondary(expected, 2);
    fixture.assertCloses(1, 1);
  }

  @Test
  void dbAdmission014TwoCloseFaultsAlwaysAttemptReverseOrder() {
    var fixture = new Fixture();
    var expected = new IllegalStateException(FIXTURE_MESSAGE);
    fixture.rowCloseFault = new SQLException(FIXTURE_MESSAGE);
    fixture.statementCloseFault = expected;
    assertSame(
        expected,
        assertThrows(IllegalStateException.class, () -> api().verify(fixture.connection)));
    fixedSecondary(expected, 0);
    fixture.assertCloses(1, 1);
    var fatal = new Fixture();
    var error = new AssertionError(FIXTURE_MESSAGE);
    fatal.rowCloseFault = error;
    fatal.statementCloseFault = new SQLException(FIXTURE_MESSAGE);
    assertSame(error, assertThrows(AssertionError.class, () -> api().verify(fatal.connection)));
    fixedSecondary(error, 1);
    fatal.assertCloses(1, 1);
  }

  @Test
  void dbAdmission015RepeatAndParallelUseIndependentBorrowedPorts() throws Exception {
    var admission = api();
    var executor = Executors.newVirtualThreadPerTaskExecutor();
    try {
      var tasks = new ArrayList<java.util.concurrent.Future<List<Phase>>>();
      for (int i = 0; i < 8; i++) {
        tasks.add(
            executor.submit(
                () -> {
                  var fixture = new Fixture();
                  admission.verify(fixture.connection);
                  return List.copyOf(fixture.calls);
                }));
      }
      for (var task : tasks) assertEquals(SUCCESS, task.get(5, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
    }
    var after = new Fixture();
    admission.verify(after.connection);
    assertEquals(SUCCESS, after.calls);
    assertFalse(after.calls.isEmpty());
  }

  @Test
  void dbAdmission016FatalNextExceptionSurvivesOrderedRelease() {
    var fixture = new Fixture();
    var fatal = new AssertionError(FIXTURE_MESSAGE);
    var failure = new SQLException(FIXTURE_MESSAGE);
    failure.setNextException(new SQLException(FIXTURE_MESSAGE, fatal));
    fixture.fault(Phase.FIRST_ROW, failure);

    assertSame(fatal, assertThrows(AssertionError.class, () -> api().verify(fixture.connection)));
    fixture.assertCloses(1, 1);
  }
}
