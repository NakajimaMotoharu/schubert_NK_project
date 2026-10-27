package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

/** Source text only, not runtime/render/permission proof. PT-OPS-CONFIG-SUP001..004/spec1556. */
class ConfigurationTemplateContractTest {
  private static final String COMMON_TEMPLATE = "common.yml.template";
  private static final String API_TEMPLATE = "api.yml.template";
  private static final String WEB_TEMPLATE = "web.yml.template";
  private static final String BATCH_TEMPLATE = "batch.yml.template";
  private static final String API_ENV_TEMPLATE = "api.env.template";
  private static final String INSPECTOR_ENV_TEMPLATE = "inbox-inspector.env.template";
  private static final List<String> FILES =
      List.of(
          COMMON_TEMPLATE,
          API_TEMPLATE,
          WEB_TEMPLATE,
          BATCH_TEMPLATE,
          API_ENV_TEMPLATE,
          "web.env.template",
          INSPECTOR_ENV_TEMPLATE);
  private static final Pattern SCALAR =
      Pattern.compile("^\"(nk\\.[a-z0-9.-]+)\": (?:\"([^\"\\\\]*)\"|([0-9]+))$");
  private static final Map<String, String> BATCH_DEFAULTS =
      Map.ofEntries(
          Map.entry("nk.batch.zone", "Asia/Tokyo"),
          Map.entry("nk.batch.schedule", "05:00"),
          Map.entry("nk.batch.backup-root", "/srv/schubert-nk/backup"),
          Map.entry("nk.batch.backup-generations", "7"),
          Map.entry("nk.batch.transfer-cleanup", "enabled"),
          Map.entry("nk.batch.expiry-retention", "7d"),
          Map.entry("nk.batch.log-retention", "90d"),
          Map.entry("nk.batch.run-retention", "400d"),
          Map.entry("nk.batch.chunk-size.notification", "1000"),
          Map.entry("nk.batch.chunk-size.question", "1000"),
          Map.entry("nk.batch.chunk-size.log", "10000"));
  private static final Map<String, String> COMMON =
      Map.of(
          "nk.protocol.version",
          "001",
          "nk.time.display-zone",
          "Asia/Tokyo",
          "nk.monitoring.mode",
          "STANDARD");
  private static final Set<String> API_KEYS =
      Set.of(
          "nk.api.storage.asset-manifest-entries",
          "nk.mq.url",
          "nk.mq.sync-request",
          "nk.mq.sync-reply",
          "nk.mq.async-work",
          "nk.mq.web-log",
          "nk.mq.dlq",
          "nk.mq.expiry",
          "nk.db.url",
          "nk.db.connect-timeout",
          "nk.db.pool.api.max",
          "nk.db.pool.api.min",
          "nk.api.sync-consumers.initial",
          "nk.api.sync-consumers.max",
          "nk.api.async-consumers",
          "nk.api.storage.asset-root",
          "nk.api.storage.transfer-root",
          "nk.inbox.reference-retention",
          "nk.inbox.update-retention",
          "nk.outbox.sent-retention");
  private static final Set<String> WEB_KEYS =
      Set.of(
          "nk.db.url",
          "nk.mq.url",
          "nk.db.pool.web.max",
          "nk.db.pool.web.min",
          "nk.db.connect-timeout",
          "nk.web.http.address",
          "nk.web.http.port",
          "nk.web.management.port",
          "nk.web.mq.reply-timeout",
          "nk.web.mq.wait.initial",
          "nk.web.mq.wait.max",
          "nk.web.session.idle-timeout",
          "nk.web.session.max-per-user",
          "nk.web.storage.asset-root",
          "nk.web.storage.transfer-root",
          "nk.web.media.max-streams",
          "nk.web.media.max-range-bytes");
  private static final String CONFIG_ENV = "SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk\n";
  private static final String INSPECTOR_ENV =
      "NK_INSPECTOR_DB_URL=jdbc:postgresql://127.0.0.1:@PG_PORT@/@PG_DATABASE@\n"
          + "NK_INSPECTOR_FINGERPRINT_VERSIONS=@FINGERPRINT_VERSION_NAMES@\n";

  private record Scalar(boolean quoted, String value) {}

  private static Map<String, String> sources() throws IOException {
    var values = new LinkedHashMap<String, String>();
    for (String name : FILES) {
      try (var stream =
          ConfigurationTemplateContractTest.class.getResourceAsStream("/config/" + name)) {
        assertNotNull(stream, "declared public template");
        values.put(name, new String(stream.readAllBytes(), StandardCharsets.UTF_8));
      }
    }
    return Map.copyOf(values);
  }

  // Deliberately a canonical source-template grammar, not a general YAML or runtime parser.
  private static Map<String, Scalar> yaml(String text) {
    Objects.requireNonNull(text, "public source text");
    assertFalse(text.contains("\r") || text.contains("\t") || text.contains("\0"));
    var values = new LinkedHashMap<String, Scalar>();
    for (String raw : text.lines().toList()) {
      String line = raw.strip();
      if (line.isEmpty() || line.startsWith("#")) continue;
      var match = SCALAR.matcher(line);
      assertTrue(match.matches(), "flat explicit nonsecret source scalar");
      boolean quoted = match.group(2) != null;
      String value = quoted ? match.group(2) : match.group(3);
      assertNull(values.put(match.group(1), new Scalar(quoted, value)), "duplicate source key");
    }
    return Map.copyOf(values);
  }

  private static String quoted(Map<String, Scalar> map, String key) {
    var value = map.get(key);
    assertNotNull(value, "required source key");
    assertTrue(value.quoted(), "do not change canonical source scalar type");
    return value.value();
  }

  private static void exact(Map<String, Scalar> actual, Map<String, String> expected) {
    assertEquals(expected.keySet(), actual.keySet(), "no missing/unknown source key");
    expected.forEach((key, value) -> assertEquals(value, quoted(actual, key), key));
  }

  private static void batch(Map<String, String> files) {
    exact(yaml(files.get(BATCH_TEMPLATE)), BATCH_DEFAULTS);
  }

  private static void cross(Map<String, String> files) {
    exact(yaml(files.get(COMMON_TEMPLATE)), COMMON);
    var api = yaml(files.get(API_TEMPLATE));
    var web = yaml(files.get(WEB_TEMPLATE));
    assertEquals(API_KEYS, api.keySet());
    assertEquals(WEB_KEYS, web.keySet());
    for (String key : API_KEYS) {
      if (key.equals("nk.api.storage.asset-manifest-entries")) {
        assertFalse(api.get(key).quoted());
        assertEquals(
            "59627", api.get(key).value(), "SSC150 initial inventory count, no master data read");
      } else quoted(api, key);
    }
    for (String key : WEB_KEYS) quoted(web, key);
    for (var map : List.of(api, web)) {
      assertEquals("jdbc:postgresql://127.0.0.1:5432/schubert_nk", quoted(map, "nk.db.url"));
      assertEquals("tcp://127.0.0.1:61616", quoted(map, "nk.mq.url"));
    }
    String asset = "/srv/schubert-nk/data/assets";
    String transfer = "/srv/schubert-nk/data/transfer";
    assertEquals(asset, quoted(api, "nk.api.storage.asset-root"));
    assertEquals(asset, quoted(web, "nk.web.storage.asset-root"));
    assertEquals(transfer, quoted(api, "nk.api.storage.transfer-root"));
    assertEquals(transfer, quoted(web, "nk.web.storage.transfer-root"));
    String backup = quoted(yaml(files.get(BATCH_TEMPLATE)), "nk.batch.backup-root");
    var roots = List.of(Path.of(asset), Path.of(transfer), Path.of(backup));
    for (var root : roots) {
      assertTrue(root.isAbsolute());
      assertEquals(root, root.normalize());
    }
    for (int i = 0; i < roots.size(); i++)
      for (int j = i + 1; j < roots.size(); j++)
        assertFalse(roots.get(i).startsWith(roots.get(j)) || roots.get(j).startsWith(roots.get(i)));
  }

  private static void env(Map<String, String> files) {
    assertEquals(CONFIG_ENV, files.get(API_ENV_TEMPLATE));
    assertEquals(CONFIG_ENV, files.get("web.env.template"));
    assertEquals(
        INSPECTOR_ENV,
        files.get(INSPECTOR_ENV_TEMPLATE),
        "source placeholders only, never runtime authority");
  }

  private static void all(Map<String, String> files) {
    assertEquals(Set.copyOf(FILES), files.keySet());
    batch(files);
    cross(files);
    env(files);
  }

  @Test
  void configSup001AllElevenBatchDefaults() throws IOException {
    batch(sources());
  }

  @Test
  void configSup002CommonCrossProcessAndLexicalRootBoundaries() throws IOException {
    cross(sources());
  }

  @Test
  void configSup003DedicatedEnvAndInspectorRenderBoundary() throws IOException {
    all(sources());
  }

  private static void reject(Map<String, String> original, String name, String replacement) {
    var copy = new LinkedHashMap<>(original);
    assertFalse(original.get(name).equals(replacement), "nonvacuous source oracle canary");
    copy.put(name, replacement);
    assertThrows(AssertionError.class, () -> all(copy));
  }

  @Test
  void configSup004IndependentSourceOracleMutationCanaries() throws IOException {
    var files = sources();
    String batch = files.get(BATCH_TEMPLATE);
    reject(
        files,
        BATCH_TEMPLATE,
        batch.replace(
            "\"nk.batch.backup-generations\": \"7\"", "\"nk.batch.backup-generations\": \"6\""));
    reject(files, BATCH_TEMPLATE, batch + "\"nk.batch.secret\": \"SYNTHETIC_PUBLIC_CANARY\"\n");
    reject(files, BATCH_TEMPLATE, batch + "\"nk.batch.zone\": \"Asia/Tokyo\"\n");
    reject(
        files,
        BATCH_TEMPLATE,
        batch.replace(
            "\"nk.batch.backup-generations\": \"7\"", "\"nk.batch.backup-generations\": 7"));
    reject(files, BATCH_TEMPLATE, batch.replace("\"05:00\"", "\"04:00\""));
    reject(files, COMMON_TEMPLATE, files.get(COMMON_TEMPLATE).replace("Asia/Tokyo", "UTC"));
    reject(files, WEB_TEMPLATE, files.get(WEB_TEMPLATE).replace("/data/assets", "/data/transfer"));
    reject(
        files, API_TEMPLATE, files.get(API_TEMPLATE).replace("127.0.0.1:5432", "localhost:5432"));
    reject(
        files,
        API_ENV_TEMPLATE,
        files.get(API_ENV_TEMPLATE) + "JAVA_TOOL_OPTIONS=-Dsynthetic=true\n");
    reject(
        files,
        INSPECTOR_ENV_TEMPLATE,
        files.get(INSPECTOR_ENV_TEMPLATE) + "NK_INSPECTOR_RUN_ID=UNSET\n");
    reject(
        files, BATCH_TEMPLATE, batch.replace("/srv/schubert-nk/backup", "/srv/schubert-nk/data"));
    assertThrows(NullPointerException.class, () -> yaml(null));
  }
}
