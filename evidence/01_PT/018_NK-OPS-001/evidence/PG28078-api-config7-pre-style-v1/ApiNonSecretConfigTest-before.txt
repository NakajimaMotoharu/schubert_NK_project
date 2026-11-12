package dev.codex.schubert.nk.api.bootstrap;

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

/** PT-OPS-API-CFG-001..006: SS343 literals independent of production map construction. */
final class ApiNonSecretConfigTest {
  private static final String INVALID = "API non-secret configuration unavailable";
  private static final String GOLDEN =
      "nk.api.async-consumers=1\n"
          + "nk.api.storage.asset-manifest-entries=59627\n"
          + "nk.api.storage.asset-root=/srv/schubert-nk/data/assets\n"
          + "nk.api.storage.transfer-root=/srv/schubert-nk/data/transfer\n"
          + "nk.api.sync-consumers.initial=4\n"
          + "nk.api.sync-consumers.max=8\n"
          + "nk.db.connect-timeout=3s\n"
          + "nk.db.pool.api.max=8\n"
          + "nk.db.pool.api.min=2\n"
          + "nk.db.url=jdbc:postgresql://127.0.0.1:5432/schubert_nk\n"
          + "nk.inbox.reference-retention=24h\n"
          + "nk.inbox.update-retention=7d\n"
          + "nk.monitoring.mode=STANDARD\n"
          + "nk.mq.async-work=nk.async.work\n"
          + "nk.mq.dlq=nk.dead.letter\n"
          + "nk.mq.expiry=nk.expiry\n"
          + "nk.mq.sync-reply=nk.sync.reply.web\n"
          + "nk.mq.sync-request=nk.sync.request\n"
          + "nk.mq.url=tcp://127.0.0.1:61616\n"
          + "nk.mq.web-log=nk.web.log\n"
          + "nk.outbox.sent-retention=7d\n"
          + "nk.protocol.version=001\n"
          + "nk.time.display-zone=Asia/Tokyo\n";

  private static IllegalArgumentException rejected(String common, String api) {
    var failure =
        assertThrows(IllegalArgumentException.class, () -> ApiNonSecretConfig.parse(common, api));
    assertEquals(INVALID, failure.getMessage());
    assertEquals(0, failure.getSuppressed().length);
    return failure;
  }

  @Test
  void opsApiCfg007IndependentManifestCountAndCanonicalHash() throws Exception {
    for (String value : List.of("1", "7", "59627")) {
      var actual =
          ApiNonSecretConfig.parse(
              "", "nk.api.storage.asset-manifest-entries: \"" + value + "\"\n");
      assertEquals(value, actual.value("nk.api.storage.asset-manifest-entries"));
      var expected =
          GOLDEN.replace("asset-manifest-entries=59627", "asset-manifest-entries=" + value);
      assertEquals(
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256")
                      .digest(expected.getBytes(StandardCharsets.UTF_8))),
          actual.canonicalSha256());
    }
    for (String value :
        List.of(
            "", "0", "-1", "01", "+1", "1.0", " 7 ", "59628", "99999", "100000", "2147483648", "a"))
      rejected("", "nk.api.storage.asset-manifest-entries: \"" + value + "\"\n");
    rejected("nk.api.storage.asset-manifest-entries: 7\n", "");
  }

  @Test
  void opsApiCfg001IndependentDefaultsAndCanonicalHash() throws Exception {
    var config = ApiNonSecretConfig.parse("", "");
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
    assertEquals("ApiNonSecretConfig[REDACTED]", config.toString());
    assertFalse(config.toString().contains("jdbc:"));
  }

  @Test
  void opsApiCfg002LayeredNonSecretOverridesAndScalarTypes() throws Exception {
    var config =
        ApiNonSecretConfig.parse(
            "nk.monitoring.mode: DEBUG\n",
            "nk.db.url: jdbc:postgresql://127.0.0.1:65535/pgpt_db\n"
                + "nk.mq.url: tcp://127.0.0.1:1\n"
                + "nk.db.pool.api.max: 8\n"
                + "nk.api.storage.asset-root: /var/data/assets\n"
                + "nk.api.storage.transfer-root: /var/data/transfer\n");
    assertEquals("DEBUG", config.value("nk.monitoring.mode"));
    assertEquals("8", config.value("nk.db.pool.api.max"));
    assertEquals("tcp://127.0.0.1:1", config.value("nk.mq.url"));
    assertNotEquals(ApiNonSecretConfig.parse("", "").canonicalSha256(), config.canonicalSha256());
    assertEquals("001", config.value("nk.protocol.version"));
  }

  @Test
  void opsApiCfg003YamlsRejectDuplicateUnknownSecretAndStructures() {
    for (String common :
        List.of(
            "nk.monitoring.mode: DEBUG\nnk.monitoring.mode: STANDARD\n",
            "nk.db.password: private\n",
            "nk.db.url: jdbc:postgresql://127.0.0.1:5432/db\n",
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
    for (String api :
        List.of(
            "nk.db.url: one\nnk.db.url: two\n",
            "nk.db.url: jdbc:postgresql://127.0.0.1:5432/schubert_nk\n---\nnk.db.password: private\n",
            "nk.monitoring.mode: DEBUG\n",
            "nk.db.password: private\n",
            "nk.db.url: {nested: bad}\n",
            "nk.db.url: true\n",
            "nk.inbox.update-retention: &r 7d\nnk.outbox.sent-retention: *r\n",
            "nk.db.url: \"${URL}\"\n")) rejected("", api);
  }

  @Test
  void opsApiCfg004AllFixedKeysUrlsAndRootsFailClosed() {
    for (String pair :
        List.of(
            "nk.protocol.version: 002", "nk.time.display-zone: UTC", "nk.monitoring.mode: TRACE"))
      rejected(pair + "\n", "");
    for (String pair :
        List.of(
            "nk.db.connect-timeout: 4s",
            "nk.db.pool.api.max: 9",
            "nk.db.pool.api.min: 1",
            "nk.api.sync-consumers.initial: 3",
            "nk.api.sync-consumers.max: 9",
            "nk.api.async-consumers: 2",
            "nk.inbox.reference-retention: 23h",
            "nk.inbox.update-retention: 6d",
            "nk.outbox.sent-retention: 6d",
            "nk.mq.sync-request: unknown",
            "nk.mq.sync-reply: unknown",
            "nk.mq.async-work: unknown",
            "nk.mq.web-log: unknown",
            "nk.mq.dlq: unknown",
            "nk.mq.expiry: unknown",
            "nk.db.url: jdbc:postgresql://localhost:5432/schubert_nk",
            "nk.db.url: jdbc:postgresql://127.0.0.1:65536/schubert_nk",
            "nk.db.url: jdbc:postgresql://127.0.0.1:0/schubert_nk",
            "nk.db.url: jdbc:postgresql://127.0.0.1:5432/schubert_nk?password=x",
            "nk.mq.url: amqp://127.0.0.1:61616",
            "nk.mq.url: tcp://127.0.0.1:65536",
            "nk.mq.url: tcp://127.0.0.1:0",
            "nk.api.storage.asset-root: relative/path",
            "nk.api.storage.transfer-root: relative/path",
            "nk.api.storage.asset-root: /srv/schubert-nk/data/transfer",
            "nk.api.storage.asset-root: /srv/schubert-nk/data/transfer/sub",
            "nk.api.storage.transfer-root: /srv/schubert-nk/data/assets/sub",
            "nk.api.storage.asset-root: \"/bad\\u0000path\"")) rejected("", pair + "\n");
  }

  @Test
  void opsApiCfg005NullUnknownAndConcurrentDeterminism() throws Exception {
    assertThrows(NullPointerException.class, () -> ApiNonSecretConfig.parse(null, ""));
    assertThrows(NullPointerException.class, () -> ApiNonSecretConfig.parse("", null));
    var config = ApiNonSecretConfig.parse("", "");
    assertThrows(NullPointerException.class, () -> config.value(null));
    assertEquals(
        INVALID,
        assertThrows(IllegalArgumentException.class, () -> config.value("password")).getMessage());
    var executor = Executors.newFixedThreadPool(8);
    try {
      var jobs = new java.util.ArrayList<java.util.concurrent.Future<String>>();
      for (int i = 0; i < 32; i++)
        jobs.add(executor.submit(() -> ApiNonSecretConfig.parse("", "").canonicalSha256()));
      for (var job : jobs)
        assertEquals(config.canonicalSha256(), job.get(5, java.util.concurrent.TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
    assertTrue(config.canonicalSha256().matches("[0-9a-f]{64}"));
  }

  @Test
  void opsApiCfg006ShippedTemplatesMatchApprovedDefaults() throws Exception {
    Path base = Path.of(System.getProperty("nk.pt.repository")).resolve("src/deployment/config");
    var config =
        ApiNonSecretConfig.parse(
            Files.readString(base.resolve("common.yml.template")),
            Files.readString(base.resolve("api.yml.template")));
    String independentHash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(GOLDEN.getBytes(StandardCharsets.UTF_8)));
    assertEquals(independentHash, config.canonicalSha256());
    assertEquals(
        "schubert_nk",
        config.value("nk.db.url").substring(config.value("nk.db.url").lastIndexOf('/') + 1));
  }
}
