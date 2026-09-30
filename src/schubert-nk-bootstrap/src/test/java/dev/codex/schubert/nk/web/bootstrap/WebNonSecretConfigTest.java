package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** PT-OPS-WEB-CFG-001..006: SS343 literals, independent of production defaults. */
final class WebNonSecretConfigTest {
  private static final String INVALID = "Web non-secret configuration unavailable";
  private static final String GOLDEN =
      "nk.db.connect-timeout=3s\n"
          + "nk.db.pool.web.max=2\n"
          + "nk.db.pool.web.min=1\n"
          + "nk.db.url=jdbc:postgresql://127.0.0.1:5432/schubert_nk\n"
          + "nk.monitoring.mode=STANDARD\n"
          + "nk.mq.url=tcp://127.0.0.1:61616\n"
          + "nk.protocol.version=001\n"
          + "nk.time.display-zone=Asia/Tokyo\n"
          + "nk.web.http.address=127.0.0.1\n"
          + "nk.web.http.port=8080\n"
          + "nk.web.management.port=8081\n"
          + "nk.web.media.max-range-bytes=1048576\n"
          + "nk.web.media.max-streams=20\n"
          + "nk.web.mq.reply-timeout=2s\n"
          + "nk.web.mq.wait.initial=12\n"
          + "nk.web.mq.wait.max=20\n"
          + "nk.web.session.idle-timeout=8h\n"
          + "nk.web.session.max-per-user=2\n"
          + "nk.web.storage.asset-root=/srv/schubert-nk/data/assets\n"
          + "nk.web.storage.transfer-root=/srv/schubert-nk/data/transfer\n";

  private static void rejected(String common, String web) {
    var failure =
        assertThrows(IllegalArgumentException.class, () -> WebNonSecretConfig.parse(common, web));
    assertEquals(INVALID, failure.getMessage());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void opsWebCfg007ExplicitDbMqSourcesAndNegativeBoundaries() throws Exception {
    var config =
        WebNonSecretConfig.parse(
            "", "nk.db.url: jdbc:postgresql://127.0.0.1:1/a\nnk.mq.url: tcp://127.0.0.1:65535\n");
    assertEquals("jdbc:postgresql://127.0.0.1:1/a", config.value("nk.db.url"));
    assertEquals("tcp://127.0.0.1:65535", config.value("nk.mq.url"));
    assertEquals(
        "jdbc:postgresql://127.0.0.1:65535/_" + "a".repeat(62),
        WebNonSecretConfig.parse(
                "", "nk.db.url: jdbc:postgresql://127.0.0.1:65535/_" + "a".repeat(62) + "\n")
            .value("nk.db.url"));
    assertEquals(
        "tcp://127.0.0.1:1",
        WebNonSecretConfig.parse("", "nk.mq.url: tcp://127.0.0.1:1\n").value("nk.mq.url"));
    for (String bad :
        List.of(
            "jdbc:postgresql://localhost:5432/db",
            "jdbc:postgresql://127.0.0.1:0/db",
            "jdbc:postgresql://127.0.0.1:65536/db",
            "jdbc:postgresql://127.0.0.1:05432/db",
            "jdbc:postgresql://127.0.0.1:5432/DB",
            "jdbc:postgresql://127.0.0.1:5432/db?user=other",
            "jdbc:postgresql://u@127.0.0.1:5432/db",
            "jdbc:postgresql://127.0.0.1:5432/" + "x".repeat(64)))
      rejected("", "nk.db.url: " + bad + "\n");
    for (String bad :
        List.of(
            "tcp://localhost:61616",
            "tcp://0.0.0.0:61616",
            "tcp://127.0.0.1:0",
            "tcp://127.0.0.1:65536",
            "tcp://127.0.0.1:061616",
            "tcp://127.0.0.1:61616?user=other",
            "tcp://127.0.0.1:61616#x")) rejected("", "nk.mq.url: " + bad + "\n");
    for (String pair :
        List.of(
            "nk.db.pool.web.max: 3",
            "nk.db.pool.web.min: 2",
            "nk.db.connect-timeout: 4s",
            "nk.db.pool.api.max: 8",
            "nk.db.user: schubert_app")) rejected("", pair + "\n");
    rejected("nk.db.url: jdbc:postgresql://127.0.0.1:5432/db\n", "");
    rejected("nk.mq.url: tcp://127.0.0.1:61616\n", "");
  }

  @Test
  void opsWebCfg001IndependentDefaultsAndCanonicalHash() throws Exception {
    var config = WebNonSecretConfig.parse("", "");
    for (String line : GOLDEN.split("\n")) {
      int equals = line.indexOf('=');
      assertEquals(line.substring(equals + 1), config.value(line.substring(0, equals)));
    }
    String independentHash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(GOLDEN.getBytes(StandardCharsets.UTF_8)));
    assertEquals(independentHash, config.canonicalSha256());
    assertEquals("WebNonSecretConfig[REDACTED]", config.toString());
    assertFalse(config.toString().contains("/srv/"));
  }

  @Test
  void opsWebCfg002LayeredRangesAndScalarTypes() throws Exception {
    var config =
        WebNonSecretConfig.parse(
            "nk.monitoring.mode: DEBUG\n",
            "nk.web.http.port: 1\n"
                + "nk.web.management.port: 65535\n"
                + "nk.web.mq.reply-timeout: 100ms\n"
                + "nk.web.mq.wait.initial: 1\n"
                + "nk.web.mq.wait.max: 20\n"
                + "nk.web.media.max-streams: 1\n"
                + "nk.web.storage.asset-root: /var/data/assets\n"
                + "nk.web.storage.transfer-root: /var/data/transfer\n");
    assertEquals("DEBUG", config.value("nk.monitoring.mode"));
    assertEquals("1", config.value("nk.web.http.port"));
    assertEquals("100ms", config.value("nk.web.mq.reply-timeout"));
    assertNotEquals(WebNonSecretConfig.parse("", "").canonicalSha256(), config.canonicalSha256());
    assertEquals("2", config.value("nk.web.session.max-per-user"));
    assertEquals(
        "1500ms",
        WebNonSecretConfig.parse("", "nk.web.mq.reply-timeout: 1500ms\n")
            .value("nk.web.mq.reply-timeout"));
    assertEquals(
        "1s",
        WebNonSecretConfig.parse("", "nk.web.mq.reply-timeout: 1s\n")
            .value("nk.web.mq.reply-timeout"));
  }

  @Test
  void opsWebCfg003RejectMalformedUnknownSecretAndDecodedValues() {
    for (String common :
        List.of(
            "nk.monitoring.mode: DEBUG\nnk.monitoring.mode: STANDARD\n",
            "nk.web.http.port: 8080\n",
            "nk.db.password: private\n",
            "[one, two]",
            "null",
            "4: value\n",
            "nk.monitoring.mode: [DEBUG]\n",
            "nk.monitoring.mode: null\n",
            "nk.monitoring.mode: \"\"\n",
            "nk.monitoring.mode: \"${MODE}\"\n",
            "nk.monitoring.mode: \"\\u" + "0024{MODE}\"\n",
            "nk.monitoring.mode: &x DEBUG\nnk.protocol.version: *x\n",
            "nk.monitoring.mode: DEBUG\n---\nnk.db.password: private\n",
            "nk.monitoring.mode: *unbound\n",
            "nk.monitoring.mode: DEBUG\r\n",
            "\uFEFFnk.monitoring.mode: DEBUG\n",
            "nk.monitoring.mode: \"DEBUG\\nSTANDARD\"\n",
            " ".repeat(16_385))) rejected(common, "");
    for (String web :
        List.of(
            "nk.web.http.port: 8080\nnk.web.http.port: 8081\n",
            "nk.web.http.port: 8080\n---\nnk.db.password: private\n",
            "nk.monitoring.mode: DEBUG\n",
            "nk.db.password: private\n",
            "nk.web.http.port: {nested: bad}\n",
            "nk.web.http.port: true\n",
            "nk.web.http.port: &p 8080\nnk.web.management.port: *p\n",
            "nk.web.http.port: \"${PORT}\"\n")) rejected("", web);
  }

  @Test
  void opsWebCfg004FixedKeysPortsTimeoutsCountsAndRoots() {
    for (String pair :
        List.of(
            "nk.protocol.version: 002", "nk.time.display-zone: UTC", "nk.monitoring.mode: TRACE"))
      rejected(pair + "\n", "");
    for (String pair :
        List.of(
            "nk.web.http.address: 0.0.0.0",
            "nk.web.session.idle-timeout: 7h",
            "nk.web.session.max-per-user: 3",
            "nk.web.media.max-range-bytes: 1048577",
            "nk.web.http.port: 0",
            "nk.web.http.port: 65536",
            "nk.web.http.port: -1",
            "nk.web.http.port: 8081",
            "nk.web.management.port: 0",
            "nk.web.management.port: 65536",
            "nk.web.management.port: 8080",
            "nk.web.mq.reply-timeout: 99ms",
            "nk.web.mq.reply-timeout: 2001ms",
            "nk.web.mq.reply-timeout: 3s",
            "nk.web.mq.reply-timeout: 0s",
            "nk.web.mq.reply-timeout: 100",
            "nk.web.mq.wait.initial: 0",
            "nk.web.mq.wait.initial: 21",
            "nk.web.mq.wait.initial: 20\nnk.web.mq.wait.max: 19",
            "nk.web.mq.wait.max: 0",
            "nk.web.mq.wait.max: 21",
            "nk.web.media.max-streams: 0",
            "nk.web.media.max-streams: 21",
            "nk.web.storage.asset-root: relative/path",
            "nk.web.storage.transfer-root: relative/path",
            "nk.web.storage.asset-root: /srv/schubert-nk/data/transfer",
            "nk.web.storage.asset-root: /srv/schubert-nk/data/transfer/sub",
            "nk.web.storage.transfer-root: /srv/schubert-nk/data/assets/sub",
            "nk.web.storage.asset-root: \"/bad\\u0000path\"")) rejected("", pair + "\n");
  }

  @Test
  void opsWebCfg005NullUnknownAndConcurrentDeterminism() throws Exception {
    assertThrows(NullPointerException.class, () -> WebNonSecretConfig.parse(null, ""));
    assertThrows(NullPointerException.class, () -> WebNonSecretConfig.parse("", null));
    var config = WebNonSecretConfig.parse("", "");
    assertThrows(NullPointerException.class, () -> config.value(null));
    rejected("", "nk.web.http.port: \"\"\n");
    assertEquals(
        INVALID,
        assertThrows(IllegalArgumentException.class, () -> config.value("password")).getMessage());
    try (var executor = Executors.newFixedThreadPool(8)) {
      var jobs = new java.util.ArrayList<java.util.concurrent.Future<String>>();
      for (int i = 0; i < 32; i++)
        jobs.add(executor.submit(() -> WebNonSecretConfig.parse("", "").canonicalSha256()));
      for (var job : jobs) assertEquals(config.canonicalSha256(), job.get());
    }
    assertTrue(config.canonicalSha256().matches("[0-9a-f]{64}"));
  }

  @Test
  void opsWebCfg006ShippedTemplatesMatchApprovedDefaults() throws Exception {
    Path base = Path.of(System.getProperty("nk.pt.repository")).resolve("src/deployment/config");
    var config =
        WebNonSecretConfig.parse(
            Files.readString(base.resolve("common.yml.template")),
            Files.readString(base.resolve("web.yml.template")));
    String independentHash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(GOLDEN.getBytes(StandardCharsets.UTF_8)));
    assertEquals(independentHash, config.canonicalSha256());
  }
}
