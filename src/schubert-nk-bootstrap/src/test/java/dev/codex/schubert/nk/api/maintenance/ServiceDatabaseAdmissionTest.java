package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseAdmission;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.nio.file.Path;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-DBADMIT-001..004; isolated real PG and public JDBC fault probes, no deployed secret. */
final class ServiceDatabaseAdmissionTest {
  private static final String FIXTURE_PRIVATE_D45CA6F9 = "PRIVATE";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var admin = db.admin()) {
      url = admin.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void opsDbadmit001ExactApiAndWebRolesOnIsolatedPg() throws Exception {
    try (var api = db.api();
        var web = DriverManager.getConnection(url, "schubert_web_session", "")) {
      new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, url).verify(api);
      new ServiceDatabaseAdmission(ServiceConfigFiles.Service.WEB, url).verify(web);
      assertFalse(api.isClosed());
      assertFalse(web.isClosed());
    }
  }

  @Test
  void opsDbadmit002WrongRoleTransactionAndReadonlyRejectWithoutOwningConnection()
      throws Exception {
    var apiAdmission = new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, url);
    try (var admin = db.admin()) {
      failure(() -> apiAdmission.verify(admin));
      assertFalse(admin.isClosed());
    }
    try (var api = db.api()) {
      failure(() -> new ServiceDatabaseAdmission(ServiceConfigFiles.Service.WEB, url).verify(api));
      api.setAutoCommit(false);
      failure(() -> apiAdmission.verify(api));
      api.setAutoCommit(true);
      api.setReadOnly(true);
      failure(() -> apiAdmission.verify(api));
      assertFalse(api.isClosed());
    }
  }

  @Test
  void opsDbadmit003RowsNullMismatchDuplicateAndSqlFaultsFailClosed() throws Exception {
    var admission = new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, url);
    // BUG283/YKT216: known body + unknown statement-close must not become fixed success/failure.
    for (Throwable closeFailure :
        List.of(
            new IllegalStateException(FIXTURE_PRIVATE_D45CA6F9),
            new SQLException(FIXTURE_PRIVATE_D45CA6F9))) {
      int[] statementCloses = {0};
      var closeProbe =
          (java.sql.Connection)
              java.lang.reflect.Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {java.sql.Connection.class},
                  (p, m, a) ->
                      switch (m.getName()) {
                        case "getAutoCommit" -> true;
                        case "isReadOnly" -> false;
                        case "prepareStatement" ->
                            java.lang.reflect.Proxy.newProxyInstance(
                                getClass().getClassLoader(),
                                new Class<?>[] {java.sql.PreparedStatement.class},
                                (sp, sm, sa) -> {
                                  if (sm.getName().equals("executeQuery"))
                                    throw new SQLException(FIXTURE_PRIVATE_D45CA6F9);
                                  if (sm.getName().equals(FIXTURE_CLOSE_97959247)) {
                                    statementCloses[0]++;
                                    throw closeFailure;
                                  }
                                  throw new AssertionError(sm.getName());
                                });
                        default -> throw new AssertionError(m.getName());
                      });
      if (closeFailure instanceof SQLException) failure(() -> admission.verify(closeProbe));
      else
        org.junit.jupiter.api.Assertions.assertSame(
            closeFailure,
            assertThrows(IllegalStateException.class, () -> admission.verify(closeProbe)));
      assertEquals(1, statementCloses[0]);
    }
    org.junit.jupiter.api.Assertions.assertAll(
        List.of("statement", "rows", "sameThrowable").stream()
            .map(
                kind ->
                    (org.junit.jupiter.api.function.Executable)
                        () -> {
                          int[] closed = new int[3];
                          var primary = new IllegalStateException(FIXTURE_PRIVATE_D45CA6F9);
                          java.sql.ResultSet rows =
                              (java.sql.ResultSet)
                                  java.lang.reflect.Proxy.newProxyInstance(
                                      getClass().getClassLoader(),
                                      new Class<?>[] {java.sql.ResultSet.class},
                                      (p, m, a) -> {
                                        if (m.getName().equals(FIXTURE_CLOSE_97959247)) {
                                          closed[0]++;
                                          throw primary;
                                        }
                                        if (m.getName().equals("next")) throw primary;
                                        throw new AssertionError(m.getName());
                                      });
                          var statement =
                              (java.sql.PreparedStatement)
                                  java.lang.reflect.Proxy.newProxyInstance(
                                      getClass().getClassLoader(),
                                      new Class<?>[] {java.sql.PreparedStatement.class},
                                      (p, m, a) ->
                                          switch (m.getName()) {
                                            case "executeQuery" ->
                                                kind.equals("rows") ? null : rows;
                                            case FIXTURE_CLOSE_97959247 -> {
                                              closed[1]++;
                                              yield null;
                                            }
                                            default -> throw new AssertionError(m.getName());
                                          });
                          var connection =
                              (java.sql.Connection)
                                  java.lang.reflect.Proxy.newProxyInstance(
                                      getClass().getClassLoader(),
                                      new Class<?>[] {java.sql.Connection.class},
                                      (p, m, a) ->
                                          switch (m.getName()) {
                                            case "getAutoCommit" -> true;
                                            case "isReadOnly" -> false;
                                            case "prepareStatement" ->
                                                kind.equals("statement") ? null : statement;
                                            case FIXTURE_CLOSE_97959247 -> {
                                              closed[2]++;
                                              yield null;
                                            }
                                            default -> throw new AssertionError(m.getName());
                                          });
                          if (kind.equals("sameThrowable"))
                            org.junit.jupiter.api.Assertions.assertSame(
                                primary,
                                assertThrows(
                                    RuntimeException.class, () -> admission.verify(connection)));
                          else failure(() -> admission.verify(connection));
                          assertEquals(kind.equals("sameThrowable") ? 1 : 0, closed[0]);
                          assertEquals(kind.equals("statement") ? 0 : 1, closed[1]);
                          assertEquals(0, closed[2]);
                        }));
    for (String column : List.of("effective_role", "login_role", "database_name", "recovery")) {
      for (Object wrong : Arrays.asList(null, column.equals("recovery") ? Boolean.TRUE : "wrong")) {
        var probe = new MaintenanceJdbcProbe();
        probe.selectedSql = "current_user";
        probe.columns.put(column, wrong);
        try (var connection = probe.wrap(db.api())) {
          failure(() -> admission.verify(connection));
          assertFalse(connection.isClosed());
        }
      }
    }
    for (boolean empty : List.of(true, false)) {
      var probe = new MaintenanceJdbcProbe();
      probe.selectedSql = "current_user";
      probe.empty = empty;
      probe.duplicate = !empty;
      try (var connection = probe.wrap(db.api())) {
        failure(() -> admission.verify(connection));
      }
    }
    for (String fault :
        List.of(
            "getAutoCommit",
            "isReadOnly",
            "prepareStatement",
            "executeQuery",
            "resultClose",
            "statementClose")) {
      var probe = new MaintenanceJdbcProbe();
      probe.selectedSql = "current_user";
      probe.fault = fault;
      try (var connection = probe.wrap(db.api())) {
        failure(() -> admission.verify(connection));
      }
    }
  }

  @Test
  void opsDbadmit004StrictUrlAndNullContracts() throws Exception {
    assertThrows(NullPointerException.class, () -> new ServiceDatabaseAdmission(null, url));
    assertThrows(
        NullPointerException.class,
        () -> new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, null));
    var admission = new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, url);
    assertThrows(NullPointerException.class, () -> admission.verify(null));
    for (String bad :
        List.of(
            "",
            "jdbc:postgresql://localhost:5432/db",
            "jdbc:postgresql://127.0.0.1:0/db",
            "jdbc:postgresql://127.0.0.1:65536/db",
            "jdbc:postgresql://127.0.0.1:05432/db",
            "jdbc:postgresql://127.0.0.1:5432/DB",
            url + "?user=other",
            url + "#x",
            "jdbc:postgresql://u@127.0.0.1:5432/db",
            "jdbc:postgresql://127.0.0.1:5432/" + "x".repeat(64))) {
      var error =
          assertThrows(
              IllegalArgumentException.class,
              () -> new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, bad));
      assertEquals("service database URL is invalid", error.getMessage());
      assertNull(error.getCause());
    }
    new ServiceDatabaseAdmission(ServiceConfigFiles.Service.API, "jdbc:postgresql://127.0.0.1:1/a");
    new ServiceDatabaseAdmission(
        ServiceConfigFiles.Service.WEB, "jdbc:postgresql://127.0.0.1:65535/_" + "a".repeat(62));
  }

  private static void failure(org.junit.jupiter.api.function.Executable action) {
    SQLException error = assertThrows(SQLException.class, action);
    assertEquals("08001", error.getSQLState());
    assertEquals("service database connection unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
