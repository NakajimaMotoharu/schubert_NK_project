package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.junit.jupiter.api.Test;

/** Public text only, never execute a directive. PT-OPS-UNIT-SUP001..005/spec1553. */
class SupplementaryUnitTemplateTest {
  private static final String DIRECTIVE_TRUE = "true";
  private static final String SERVICE_SECTION = "Service";
  private static final String STOP_TIMEOUT_KEY = "TimeoutStopSec";
  private static final String THIRTY_SECONDS = "30s";
  private static final String UNIT_SECTION = "Unit";
  private static final String MINIMUM_HEAP_OPTION = "-Xms";
  private static final String MAXIMUM_HEAP_OPTION = "-Xmx";

  private static final String BACKUP = "schubert-nk-backup.service.template";
  private static final String ADMIN = "schubert-nk-bootstrap-admin.service.template";
  private static final String START = "caddy.service.d/schubert-nk-startup-policy.conf";
  private static final String STOP = "caddy.service.d/schubert-nk-stop-policy.conf";
  private static final Map<String, String> HARDENING =
      Map.ofEntries(
          Map.entry("NoNewPrivileges", DIRECTIVE_TRUE),
          Map.entry("CapabilityBoundingSet", ""),
          Map.entry("AmbientCapabilities", ""),
          Map.entry("UMask", "0077"),
          Map.entry("PrivateTmp", DIRECTIVE_TRUE),
          Map.entry("PrivateDevices", DIRECTIVE_TRUE),
          Map.entry("ProtectSystem", "strict"),
          Map.entry("ProtectHome", DIRECTIVE_TRUE),
          Map.entry("ProtectKernelTunables", DIRECTIVE_TRUE),
          Map.entry("ProtectKernelModules", DIRECTIVE_TRUE),
          Map.entry("ProtectControlGroups", DIRECTIVE_TRUE),
          Map.entry("ProtectKernelLogs", DIRECTIVE_TRUE),
          Map.entry("ProtectClock", DIRECTIVE_TRUE),
          Map.entry("ProtectHostname", DIRECTIVE_TRUE),
          Map.entry("RestrictSUIDSGID", DIRECTIVE_TRUE),
          Map.entry("LockPersonality", DIRECTIVE_TRUE),
          Map.entry("RestrictNamespaces", DIRECTIVE_TRUE),
          Map.entry("RestrictRealtime", DIRECTIVE_TRUE),
          Map.entry("RestrictAddressFamilies", "AF_UNIX AF_INET AF_INET6"),
          Map.entry("StandardOutput", "journal"),
          Map.entry("StandardError", "journal"));

  private record Template(List<String> sections, Map<String, List<String>> directives) {}

  private static String source(String name) throws IOException {
    try (var stream = SupplementaryUnitTemplateTest.class.getResourceAsStream("/systemd/" + name)) {
      assertNotNull(stream, "explicit public template resource");
      return new String(stream.readAllBytes(), StandardCharsets.UTF_8);
    }
  }

  private static Template parse(String text) {
    Objects.requireNonNull(text, "public template text");
    assertFalse(text.contains("\r"));
    assertFalse(text.contains("\t"));
    var sections = new ArrayList<String>();
    var directives = new LinkedHashMap<String, List<String>>();
    String section = "";
    for (String raw : text.lines().toList()) {
      String line = raw.strip();
      if (line.isEmpty() || line.startsWith("#") || line.startsWith(";")) continue;
      assertTrue(line.chars().allMatch(c -> c >= 32 && c <= 126), "ASCII directive");
      if (line.startsWith("[") && line.endsWith("]")) {
        section = line.substring(1, line.length() - 1);
        sections.add(section);
        continue;
      }
      int equals = line.indexOf('=');
      assertTrue(!section.isEmpty() && equals > 0, "section/key/value required");
      String key = section + "." + line.substring(0, equals);
      directives.computeIfAbsent(key, ignored -> new ArrayList<>()).add(line.substring(equals + 1));
    }
    var immutable = new LinkedHashMap<String, List<String>>();
    directives.forEach((k, v) -> immutable.put(k, List.copyOf(v)));
    return new Template(List.copyOf(sections), Map.copyOf(immutable));
  }

  private static void put(Map<String, List<String>> map, String section, String key, String value) {
    assertNull(map.put(section + "." + key, List.of(value)), "unique independent oracle key");
  }

  private static Map<String, List<String>> expected(String name) {
    var m = new LinkedHashMap<String, List<String>>();
    if (name.equals(STOP)) {
      put(m, SERVICE_SECTION, STOP_TIMEOUT_KEY, THIRTY_SECONDS);
      put(m, SERVICE_SECTION, "SendSIGKILL", "no");
      return m;
    }
    if (name.equals(START)) {
      for (var entry :
          Map.ofEntries(
                  Map.entry("User", "caddy"),
                  Map.entry("Group", "caddy"),
                  Map.entry("SupplementaryGroups", ""),
                  Map.entry("Type", "notify"),
                  Map.entry("Restart", "no"),
                  Map.entry("TimeoutStartSec", THIRTY_SECONDS),
                  Map.entry(STOP_TIMEOUT_KEY, THIRTY_SECONDS),
                  Map.entry("SendSIGKILL", "no"),
                  Map.entry("KillMode", "control-group"),
                  Map.entry("NoNewPrivileges", "yes"),
                  Map.entry("CapabilityBoundingSet", ""),
                  Map.entry("AmbientCapabilities", ""),
                  Map.entry("UMask", "0027"),
                  Map.entry("ProtectSystem", "strict"),
                  Map.entry("ProtectHome", DIRECTIVE_TRUE),
                  Map.entry("PrivateTmp", DIRECTIVE_TRUE),
                  Map.entry("ReadWritePaths", "/var/lib/caddy"))
              .entrySet()) put(m, SERVICE_SECTION, entry.getKey(), entry.getValue());
      m.put(
          "Service.ExecStartPre",
          List.of("", "/usr/bin/caddy validate --config /etc/caddy/Caddyfile"));
      m.put("Service.ExecStart", List.of("", "/usr/bin/caddy run --config /etc/caddy/Caddyfile"));
      m.put("Service.ExecReload", List.of(""));
      return m;
    }
    assertTrue(name.equals(BACKUP) || name.equals(ADMIN), "only declared public source");
    HARDENING.forEach((key, value) -> put(m, SERVICE_SECTION, key, value));
    put(m, UNIT_SECTION, "Description", "@description");
    put(m, UNIT_SECTION, "After", "postgresql.service");
    put(m, UNIT_SECTION, "Requires", "postgresql.service");
    put(m, SERVICE_SECTION, "Type", "oneshot");
    put(
        m,
        SERVICE_SECTION,
        "UnsetEnvironment",
        "JAVA_TOOL_OPTIONS JDK_JAVA_OPTIONS _JAVA_OPTIONS CLASSPATH LD_PRELOAD LD_LIBRARY_PATH");
    put(m, SERVICE_SECTION, "ExecStart", "@java-abi");
    put(m, SERVICE_SECTION, "Restart", "no");
    put(m, SERVICE_SECTION, "SendSIGKILL", "no");
    put(m, SERVICE_SECTION, "MemoryMax", "@resource-budget");
    if (name.equals(BACKUP)) {
      put(
          m,
          UNIT_SECTION,
          "Before",
          "schubert-nk-api.service schubert-nk-web.service caddy.service");
      put(m, SERVICE_SECTION, "User", "schubert-backup");
      put(m, SERVICE_SECTION, "Group", "schubert-backup");
      put(m, SERVICE_SECTION, "SupplementaryGroups", "schubert");
      put(m, SERVICE_SECTION, "WorkingDirectory", "/opt/schubert-nk/current/operations");
      m.put(
          "Service.LoadCredential",
          List.of(
              "backup-request:/run/schubert-nk/backup-request/backup-request",
              "backup-pgpass:/etc/schubert-nk/credentials/backup-pgpass"));
      put(m, SERVICE_SECTION, "RemainAfterExit", "yes");
      put(m, SERVICE_SECTION, "TimeoutStartSec", "30min");
      put(m, SERVICE_SECTION, STOP_TIMEOUT_KEY, "60s");
      put(m, SERVICE_SECTION, "KillMode", "control-group");
      put(m, SERVICE_SECTION, "RuntimeDirectory", "schubert-nk-backup");
      put(m, SERVICE_SECTION, "RuntimeDirectoryMode", "0700");
      put(m, SERVICE_SECTION, "RuntimeDirectoryPreserve", "yes");
      put(m, SERVICE_SECTION, "ReadWritePaths", "/srv/schubert-nk/backup");
      put(m, SERVICE_SECTION, "LimitNOFILE", "65536");
    } else {
      put(m, SERVICE_SECTION, "User", "schubert-api");
      put(m, SERVICE_SECTION, "Group", "schubert-api");
      put(m, SERVICE_SECTION, "SupplementaryGroups", "schubert schubert-read schubert-web");
      put(m, SERVICE_SECTION, "WorkingDirectory", "/opt/schubert-nk/current/api");
      put(m, SERVICE_SECTION, "EnvironmentFile", "/etc/schubert-nk/api.env");
      m.put(
          "Service.LoadCredential",
          List.of(
              "db-api:/etc/schubert-nk/credentials/db-api",
              "bootstrap-admin-username:/etc/schubert-nk/credentials/bootstrap-admin-username",
              "bootstrap-admin-password:/etc/schubert-nk/credentials/bootstrap-admin-password"));
      put(m, SERVICE_SECTION, "SuccessExitStatus", "20");
      put(m, SERVICE_SECTION, "TimeoutStartSec", THIRTY_SECONDS);
      put(m, SERVICE_SECTION, STOP_TIMEOUT_KEY, THIRTY_SECONDS);
    }
    return m;
  }

  private static long positiveMiB(String value, char unit) {
    assertTrue(value.matches("[1-9][0-9]{0,6}" + unit), "bounded positive memory");
    return Long.parseLong(value.substring(0, value.length() - 1));
  }

  private static void javaAbi(String name, Map<String, List<String>> actual) {
    String text = actual.get("Service.ExecStart").getFirst();
    var args = List.of(text.split(" "));
    assertEquals(
        List.of(
            "/usr/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-Dfile.encoding=UTF-8",
            "-Duser.timezone=UTC",
            "-XX:+ExitOnOutOfMemoryError"),
        args.subList(0, 5));
    String area = name.equals(BACKUP) ? "operations" : "api";
    String main =
        name.equals(BACKUP)
            ? "dev.codex.schubert.nk.batch.file.BackupDatabaseWorker"
            : "dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain";
    String jar = name.equals(BACKUP) ? "batch" : "api";
    assertEquals(
        List.of(
            "-cp",
            "/opt/schubert-nk/current/"
                + area
                + "/"
                + jar
                + ".jar:/opt/schubert-nk/current/"
                + area
                + "/lib/*",
            main),
        args.subList(args.size() - 3, args.size()));
    var memory = new HashMap<String, Long>();
    for (String arg : args.subList(5, args.size() - 3)) {
      String key;
      String value;
      if (arg.startsWith(MINIMUM_HEAP_OPTION) || arg.startsWith(MAXIMUM_HEAP_OPTION)) {
        key = arg.substring(0, 4);
        value = arg.substring(4);
      } else {
        int split = arg.indexOf('=');
        assertTrue(split > 0, "explicit bounded JVM limit");
        key = arg.substring(0, split);
        value = arg.substring(split + 1);
      }
      assertNull(memory.put(key, positiveMiB(value, 'm')), "one limit per category");
    }
    var expectedKeys =
        name.equals(BACKUP)
            ? java.util.Set.of(
                MINIMUM_HEAP_OPTION,
                MAXIMUM_HEAP_OPTION,
                "-XX:MaxDirectMemorySize",
                "-XX:MaxMetaspaceSize",
                "-XX:ReservedCodeCacheSize")
            : java.util.Set.of(MAXIMUM_HEAP_OPTION);
    assertEquals(expectedKeys, memory.keySet());
    long limit = positiveMiB(actual.get("Service.MemoryMax").getFirst(), 'M');
    assertTrue(
        limit <= (name.equals(BACKUP) ? 1536 : 2048), "within approved aggregate process budget");
    long maximum = memory.get(MAXIMUM_HEAP_OPTION);
    for (String key : expectedKeys) {
      assertTrue(memory.get(key) < limit);
      if (!key.equals(MINIMUM_HEAP_OPTION) && !key.equals(MAXIMUM_HEAP_OPTION))
        maximum += memory.get(key);
    }
    if (memory.containsKey(MINIMUM_HEAP_OPTION))
      assertTrue(memory.get(MINIMUM_HEAP_OPTION) <= memory.get(MAXIMUM_HEAP_OPTION));
    assertTrue(maximum < limit, "positive native headroom, no heap dump or arbitrary JVM option");
  }

  private static void verify(String name, String text) {
    var actual = parse(text);
    var expected = expected(name);
    assertEquals(
        name.equals(START) || name.equals(STOP)
            ? List.of(SERVICE_SECTION)
            : List.of(UNIT_SECTION, SERVICE_SECTION),
        actual.sections());
    assertEquals(
        expected.keySet(),
        actual.directives().keySet(),
        "no unknown directive or automatic enable");
    for (var entry : expected.entrySet()) {
      var values = actual.directives().get(entry.getKey());
      if (entry.getValue().getFirst().startsWith("@")) {
        assertEquals(1, values.size(), "single typed directive");
        if (entry.getKey().equals("Unit.Description"))
          assertTrue(!values.getFirst().isBlank() && values.getFirst().length() <= 256);
      } else assertEquals(entry.getValue(), values, entry.getKey());
    }
    if (name.equals(BACKUP) || name.equals(ADMIN)) javaAbi(name, actual.directives());
  }

  @Test
  void unitSup001BackupAllDeclaredContracts() throws IOException {
    verify(BACKUP, source(BACKUP));
  }

  @Test
  void unitSup002AdminDisabledAndDedicatedAllDeclaredContracts() throws IOException {
    verify(ADMIN, source(ADMIN));
  }

  @Test
  void unitSup003CaddyStartupResetsAndFixedDaemonAbi() throws IOException {
    verify(START, source(START));
  }

  @Test
  void unitSup004CaddyStopOnlyDeclaredOverrides() throws IOException {
    verify(STOP, source(STOP));
  }

  private static void rejected(String name, String original, String mutated) {
    assertFalse(original.equals(mutated), "nonvacuous oracle canary");
    assertThrows(AssertionError.class, () -> verify(name, mutated));
  }

  @Test
  void unitSup005IndependentOracleMutationCanaries() throws IOException {
    String backup = source(BACKUP);
    rejected(BACKUP, backup, backup.replace("backup-request:/run/", "backup-request:/tmp/"));
    rejected(BACKUP, backup, backup.replace("ExecStart=/usr/bin/java", "ExecStart=+/usr/bin/java"));
    rejected(BACKUP, backup, backup + "ExecStartPost=/bin/true\n");
    rejected(BACKUP, backup, backup + "MemoryMax=1024M\n");
    rejected(BACKUP, backup, backup.replace("-Xmx512m", "-Xmx2048m"));
    String admin = source(ADMIN);
    rejected(ADMIN, admin, admin + "[Install]\nWantedBy=multi-user.target\n");
    String start = source(START);
    rejected(START, start, start.replace("TimeoutStopSec=30s", "TimeoutStopSec=1s"));
    rejected(START, start, start.replace("ExecStartPre=\n", ""));
    rejected(
        START,
        start,
        start.replace(
            "ExecStart=\nExecStart=/usr/bin/caddy run --config /etc/caddy/Caddyfile",
            "ExecStart=/usr/bin/caddy run --config /etc/caddy/Caddyfile\nExecStart="));
    rejected(STOP, source(STOP), "");
    rejected(STOP, source(STOP), "not-a-directive\n");
    rejected(STOP, source(STOP), "[Unknown]\nTimeoutStopSec=30s\nSendSIGKILL=no\n");
    assertThrows(NullPointerException.class, () -> parse(null));
  }
}
