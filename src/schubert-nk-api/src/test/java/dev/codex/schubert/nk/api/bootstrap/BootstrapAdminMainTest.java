package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext.Observed;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity.Value;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * Actual PG transaction/independent identity literals; SSC188/PT-ADM-BOOT007, not native success.
 */
class BootstrapAdminMainTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static final Value FIXED = new Value(900, 900, List.of(800L, 900L));
  static final Observed GOLDEN =
      new Observed(
          "11111111-2222-4333-8444-555555555555",
          123,
          456,
          900,
          900,
          List.of(800L, 900L),
          "0::/system.slice/schubert-nk-bootstrap-admin.service\n",
          true,
          true);

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  /** PT-ADM-BOOT707001: actual public entry, fixed70 without credentials/OS admission. */
  @Test
  void boot707001ExternalMainRejectsMissingNamespaceAndArgvWithoutSecretDiagnostics()
      throws Exception {
    for (var arguments : List.of(List.<String>of(), List.of("override"))) {
      var command = new ArrayList<String>();
      command.add(Path.of(System.getProperty("java.home"), "bin/java").toString());
      ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
          .filter(arg -> arg.startsWith("-javaagent:") && arg.contains("jacoco"))
          .forEach(command::add);
      command.addAll(
          List.of(
              "--enable-native-access=ALL-UNNAMED",
              "-cp",
              System.getProperty("java.class.path"),
              BootstrapAdminMain.class.getName()));
      command.addAll(arguments);
      var builder = new ProcessBuilder(command);
      builder.environment().clear();
      var stdout = Files.createTempFile(root, "boot707-out-", ".txt");
      var stderr = Files.createTempFile(root, "boot707-err-", ".txt");
      builder.redirectOutput(stdout.toFile()).redirectError(stderr.toFile());
      var process = builder.start();
      try {
        assertTrue(process.waitFor(15, TimeUnit.SECONDS));
        assertEquals(70, process.exitValue());
      } finally {
        if (process.isAlive()) {
          process.destroy();
          assertTrue(process.waitFor(5, TimeUnit.SECONDS));
        }
      }
      assertEquals("", Files.readString(stdout));
      assertEquals("Initial ADMIN bootstrap finished\n", Files.readString(stderr));
    }
  }

  @Test
  void boot007ArgumentAndNamespaceDenyBeforeAnyIo() throws Exception {
    var main = new BootstrapAdminMain();
    assertEquals(70, main.run(new String[] {"override"}, Map.of()));
    for (Map<String, String> env :
        List.of(
            Map.<String, String>of(),
            Map.of("CREDENTIALS_DIRECTORY", "relative"),
            Map.of("CREDENTIALS_DIRECTORY", "/run/credentials/other"),
            Map.of(
                "credentials_directory", "/run/credentials/schubert-nk-bootstrap-admin.service")))
      assertEquals(70, main.run(new String[0], env));
    assertThrows(NullPointerException.class, () -> main.run(null, Map.of()));
    assertThrows(NullPointerException.class, () -> main.run(new String[0], null));
  }

  @Test
  void boot007EveryActorFieldAndSameGenerationMustMatch() throws Exception {
    BootstrapAdminMain.requireActor(GOLDEN, FIXED);
    BootstrapAdminMain.requireSame(GOLDEN, GOLDEN, FIXED);
    var invalid =
        List.of(
            new Observed(
                GOLDEN.boot(), 123, 456, 901, 900, FIXED.groups(), GOLDEN.cgroup(), true, true),
            new Observed(
                GOLDEN.boot(), 123, 456, 900, 901, FIXED.groups(), GOLDEN.cgroup(), true, true),
            new Observed(
                GOLDEN.boot(), 123, 456, 900, 900, List.of(900L), GOLDEN.cgroup(), true, true),
            new Observed(
                GOLDEN.boot(), 123, 456, 900, 900, FIXED.groups(), GOLDEN.cgroup(), false, true),
            new Observed(
                GOLDEN.boot(), 123, 456, 900, 900, FIXED.groups(), GOLDEN.cgroup(), true, false),
            new Observed(
                GOLDEN.boot(),
                123,
                456,
                900,
                900,
                FIXED.groups(),
                "0::/system.slice/schubert-nk-api.service\n",
                true,
                true));
    for (var actor : invalid)
      assertThrows(IOException.class, () -> BootstrapAdminMain.requireActor(actor, FIXED));
    for (var actor :
        List.of(
            new Observed(
                "22222222-2222-4333-8444-555555555555",
                123,
                456,
                900,
                900,
                FIXED.groups(),
                GOLDEN.cgroup(),
                true,
                true),
            new Observed(
                GOLDEN.boot(), 124, 456, 900, 900, FIXED.groups(), GOLDEN.cgroup(), true, true),
            new Observed(
                GOLDEN.boot(), 123, 457, 900, 900, FIXED.groups(), GOLDEN.cgroup(), true, true)))
      assertThrows(IOException.class, () -> BootstrapAdminMain.requireSame(GOLDEN, actor, FIXED));
    assertThrows(NullPointerException.class, () -> BootstrapAdminMain.requireActor(null, FIXED));
    assertThrows(NullPointerException.class, () -> BootstrapAdminMain.requireActor(GOLDEN, null));
  }

  @Test
  void boot007NormalCommitAndRepeat20ConsumeInputsAndLeaveCallerOwnership() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_users,schubert.app_logs restart identity cascade");
    }
    for (int expected : List.of(0, 20)) {
      char[] input = "synthetic-credential".toCharArray();
      try (var c = db.api()) {
        assertEquals(expected, BootstrapAdminMain.createAndCommit(c, "Initial.Admin", input));
        assertFalse(c.isClosed());
        assertArrayEquals(new char[input.length], input);
      }
    }
    try (var c = db.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select (select count(*) from schubert.app_users),(select count(*) from schubert.app_logs)")) {
      assertTrue(r.next());
      assertEquals(1, r.getLong(1));
      assertEquals(2, r.getLong(2));
      assertFalse(r.next());
    }
    char[] input = "synthetic-credential".toCharArray();
    assertThrows(
        NullPointerException.class, () -> BootstrapAdminMain.createAndCommit(null, "admin", input));
    assertArrayEquals(new char[input.length], input);
    try (var c = db.api()) {
      assertThrows(
          NullPointerException.class, () -> BootstrapAdminMain.createAndCommit(c, "admin", null));
    }
  }

  @Test
  void boot007CommitUnknownCannotBecomeSuccessAndRepeatCannotDuplicate() throws Exception {
    for (boolean committed : List.of(false, true)) {
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute("truncate schubert.app_users,schubert.app_logs restart identity cascade");
      }
      char[] input = "synthetic-credential".toCharArray();
      try (var actual = db.api()) {
        var fault =
            (Connection)
                java.lang.reflect.Proxy.newProxyInstance(
                    Connection.class.getClassLoader(),
                    new Class<?>[] {Connection.class},
                    (p, m, a) -> {
                      if (m.getName().equals("commit")) {
                        if (committed) actual.commit();
                        throw new SQLException("synthetic unknown commit");
                      }
                      try {
                        return m.invoke(actual, a);
                      } catch (java.lang.reflect.InvocationTargetException e) {
                        throw e.getCause();
                      }
                    });
        assertThrows(
            SQLException.class, () -> BootstrapAdminMain.createAndCommit(fault, "admin", input));
        assertArrayEquals(new char[input.length], input);
      }
      try (var c = db.api();
          var s = c.createStatement();
          var r =
              s.executeQuery(
                  "select (select count(*) from schubert.app_users),(select count(*) from schubert.app_logs)")) {
        assertTrue(r.next());
        assertEquals(committed ? 1 : 0, r.getLong(1));
        assertEquals(committed ? 2 : 0, r.getLong(2));
      }
      try (var c = db.api()) {
        assertEquals(
            committed ? 20 : 0,
            BootstrapAdminMain.createAndCommit(c, "admin", "synthetic-credential".toCharArray()));
      }
    }
  }
}
