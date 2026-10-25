package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * Test-only ownership/config regressions, not Production DB or native acceptance. BUG552/YKT396.
 */
class WebLogDatabaseFixtureTest {
  @TempDir Path root;

  @Test
  void fixture001MissingAndBlankPropertyRejectBeforeAnyResource() throws Exception {
    String original = System.getProperty("nk.pt.repository");
    try {
      for (String value : new String[] {null, "", " "}) {
        if (value == null) System.clearProperty("nk.pt.repository");
        else System.setProperty("nk.pt.repository", value);
        var failure =
            assertThrows(IllegalArgumentException.class, () -> new WebLogDatabaseFixture(root));
        assertEquals("PT repository property is required", failure.getMessage());
        try (var entries = Files.list(root)) {
          assertEquals(0, entries.count());
        }
      }
    } finally {
      if (original == null) System.clearProperty("nk.pt.repository");
      else System.setProperty("nk.pt.repository", original);
    }
  }

  @Test
  void fixture002SetupSqlFailureStopsOnlyConfirmedOwnedDatabase() throws Exception {
    String original = System.getProperty("nk.pt.repository");
    Path repository = Files.createDirectory(root.resolve("repository"));
    Path script =
        repository.resolve("src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql");
    Files.createDirectories(script.getParent());
    Files.writeString(script, "SELECT 1 / 0;\n", StandardCharsets.US_ASCII);
    Path database = Files.createDirectory(root.resolve("database"));
    try {
      System.setProperty("nk.pt.repository", repository.toString());
      var failure = assertThrows(SQLException.class, () -> new WebLogDatabaseFixture(database));
      assertEquals(0, failure.getSuppressed().length);
      assertTrue(Files.isDirectory(database.resolve("data")));
      assertFalse(Files.exists(database.resolve("data/postmaster.pid")));
      assertFalse(Files.exists(database.resolve("data/postmaster.opts.lock")));
    } finally {
      if (original == null) System.clearProperty("nk.pt.repository");
      else System.setProperty("nk.pt.repository", original);
    }
  }

  @Test
  void fixture003OrdinarySuccessAndExplicitStopRemainOwned() throws Exception {
    var fixture = new WebLogDatabaseFixture(root);
    try {
      assertTrue(Files.isRegularFile(root.resolve("data/postmaster.pid")));
      try (var connection = fixture.web();
          var statement = connection.createStatement();
          var rows = statement.executeQuery("SELECT current_user")) {
        assertTrue(rows.next());
        assertEquals("schubert_web_session", rows.getString(1));
        assertFalse(rows.next());
      }
    } finally {
      fixture.stop();
    }
    assertFalse(Files.exists(root.resolve("data/postmaster.pid")));
  }
}
