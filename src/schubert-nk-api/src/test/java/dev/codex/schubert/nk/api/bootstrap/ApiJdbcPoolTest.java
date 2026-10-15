package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.zaxxer.hikari.pool.HikariPool.PoolInitializationException;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.SQLTransientConnectionException;
import java.util.ArrayList;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.postgresql.ds.PGSimpleDataSource;

/** PT-OPS-DBPOOL-001..003: independent PostgreSQL role and bounded-pool postconditions. */
final class ApiJdbcPoolTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static String url;

  @BeforeAll
  static void startDatabase() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    try (var admin = database.admin()) {
      url = admin.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stopDatabase() throws Exception {
    if (database != null) database.stop();
  }

  private static PGSimpleDataSource source(String jdbcUrl) {
    var source = new PGSimpleDataSource();
    source.setURL(jdbcUrl);
    source.setUser("schubert_app");
    return source;
  }

  @Test
  void opsDbpool001RealRoleAndFixedConfiguration() throws Exception {
    try (var pool = new ApiJdbcPool().open(source(url));
        var connection = pool.getConnection();
        var query = connection.createStatement();
        var row = query.executeQuery("select current_user::text, current_database()::text")) {
      assertTrue(row.next());
      assertEquals("schubert_app", row.getString(1));
      assertEquals("postgres", row.getString(2));
      assertFalse(row.next());
      assertEquals("schubert-nk-api", pool.getPoolName());
      assertEquals(8, pool.getMaximumPoolSize());
      assertEquals(2, pool.getMinimumIdle());
      assertEquals(3_000, pool.getConnectionTimeout());
      assertEquals(2_000, pool.getValidationTimeout());
      assertEquals(1, pool.getInitializationFailTimeout());
      assertTrue(pool.isAutoCommit());
      assertFalse(pool.isReadOnly());
      assertFalse(pool.isRegisterMbeans());
      try (var denied = connection.createStatement()) {
        assertEquals(
            "42501",
            assertThrows(
                    SQLException.class,
                    () ->
                        denied.executeQuery(
                            "select count(*) from schubert_web_session.web_http_sessions"))
                .getSQLState());
      }
    }
  }

  @Test
  void opsDbpool002EightBorrowersAndNinthTimeout() throws Exception {
    try (var pool = new ApiJdbcPool().open(source(url))) {
      var borrowed = new ArrayList<Connection>();
      try {
        for (int i = 0; i < 8; i++) borrowed.add(pool.getConnection());
        assertEquals(8, pool.getHikariPoolMXBean().getActiveConnections());
        assertThrows(SQLTransientConnectionException.class, pool::getConnection);
      } finally {
        for (var connection : borrowed) connection.close();
      }
      try (var recovered = pool.getConnection()) {
        assertFalse(recovered.isClosed());
      }
    }
  }

  @Test
  void opsDbpool003NullAndUnavailableFailBeforeReady() {
    assertThrows(NullPointerException.class, () -> new ApiJdbcPool().open(null));
    String missing = url.substring(0, url.lastIndexOf('/') + 1) + "nk_missing_fixture";
    assertThrows(PoolInitializationException.class, () -> new ApiJdbcPool().open(source(missing)));
  }
}
