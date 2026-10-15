package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.zaxxer.hikari.pool.HikariPool.PoolInitializationException;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
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

/** PT-OPS-DBPOOL-004..006: real isolated Web-role and two-connection ceiling. */
final class WebJdbcPoolTest {
  @TempDir static Path root;
  private static WebLogDatabaseFixture database;
  private static String url;

  @BeforeAll
  static void startDatabase() throws Exception {
    database = new WebLogDatabaseFixture(root);
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
    source.setUser("schubert_web_session");
    return source;
  }

  @Test
  void opsDbpool004RealRoleAndFixedConfiguration() throws Exception {
    try (var pool = new WebJdbcPool().open(source(url));
        var connection = pool.getConnection();
        var query = connection.createStatement();
        var row = query.executeQuery("select current_user::text, current_database()::text")) {
      assertTrue(row.next());
      assertEquals("schubert_web_session", row.getString(1));
      assertEquals("postgres", row.getString(2));
      assertFalse(row.next());
      assertEquals("schubert-nk-web", pool.getPoolName());
      assertEquals(2, pool.getMaximumPoolSize());
      assertEquals(1, pool.getMinimumIdle());
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
                    () -> denied.executeQuery("select count(*) from schubert.app_logs"))
                .getSQLState());
      }
    }
  }

  @Test
  void opsDbpool005TwoBorrowersAndThirdTimeout() throws Exception {
    try (var pool = new WebJdbcPool().open(source(url))) {
      var borrowed = new ArrayList<Connection>();
      try {
        for (int i = 0; i < 2; i++) borrowed.add(pool.getConnection());
        assertEquals(2, pool.getHikariPoolMXBean().getActiveConnections());
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
  void opsDbpool006NullAndUnavailableFailBeforeReady() {
    assertThrows(NullPointerException.class, () -> new WebJdbcPool().open(null));
    String missing = url.substring(0, url.lastIndexOf('/') + 1) + "nk_missing_fixture";
    assertThrows(PoolInitializationException.class, () -> new WebJdbcPool().open(source(missing)));
  }
}
