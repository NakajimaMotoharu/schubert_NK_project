package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-WEB-LOAD-001..005, SS343 Web-only fixed file-to-parser bridge. */
final class WebConfigurationLoaderTest {
  private static final String FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484 = "SCHUBERT_NK_CONFIG_DIR";
  private static final String FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED = "/etc/schubert-nk";
  private static final String FIXTURE_NK_WEB_HTTP_PORT_F1BB508F = "nk.web.http.port";
  private static final Map<String, String> ENV =
      Map.of(FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484, FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED);

  @Test
  void opsWebLoad001FixedServiceAndLayerOrder() throws Exception {
    AtomicInteger calls = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          assertEquals(ServiceConfigFiles.Service.WEB, service);
          calls.incrementAndGet();
          return new ServiceConfigFiles.Contents(
              "nk.monitoring.mode: DEBUG\n", "nk.web.http.port: '8082'\n");
        };
    WebNonSecretConfig config = new WebConfigurationLoader(source, ENV).load();
    assertEquals(1, calls.get());
    assertEquals("DEBUG", config.value("nk.monitoring.mode"));
    assertEquals("8082", config.value(FIXTURE_NK_WEB_HTTP_PORT_F1BB508F));
    assertEquals("001", config.value("nk.protocol.version"));
  }

  @Test
  void opsWebLoad002SourceAndParserFailuresStayDistinct() {
    StorageIoException sourceFailure =
        new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    WebConfigurationLoader failed =
        new WebConfigurationLoader(
            service -> {
              throw sourceFailure;
            },
            ENV);
    assertSame(sourceFailure, assertThrows(StorageIoException.class, failed::load));
    WebConfigurationLoader malformed =
        new WebConfigurationLoader(
            service ->
                new ServiceConfigFiles.Contents(
                    "nk.monitoring.mode: DEBUG\n", "nk.db.pool.api.max: 8\n"),
            ENV);
    assertEquals(
        "Web non-secret configuration unavailable",
        assertThrows(IllegalArgumentException.class, malformed::load).getMessage());
  }

  @Test
  void opsWebLoad003NullContractsAndProductionFactory() {
    assertThrows(NullPointerException.class, () -> new WebConfigurationLoader(null, ENV));
    assertThrows(
        NullPointerException.class, () -> new WebConfigurationLoader(service -> null, ENV).load());
    assertNotNull(WebConfigurationLoader.production());
  }

  @Test
  void opsWebLoad004ConcurrentFreshReads() throws Exception {
    AtomicInteger calls = new AtomicInteger();
    WebConfigurationLoader loader =
        new WebConfigurationLoader(
            service -> {
              assertEquals(ServiceConfigFiles.Service.WEB, service);
              calls.incrementAndGet();
              return new ServiceConfigFiles.Contents(
                  "nk.monitoring.mode: STANDARD\n", "nk.web.http.port: '8080'\n");
            },
            ENV);
    try (var executor = Executors.newFixedThreadPool(8)) {
      var results = new ArrayList<java.util.concurrent.Future<WebNonSecretConfig>>();
      for (int i = 0; i < 32; i++) results.add(executor.submit(loader::load));
      for (var result : results) {
        assertEquals("STANDARD", result.get().value("nk.monitoring.mode"));
        assertEquals("8080", result.get().value(FIXTURE_NK_WEB_HTTP_PORT_F1BB508F));
      }
    }
    assertEquals(32, calls.get());
  }

  @Test
  void opsWebLoad005EnvironmentIsExactBeforeFileRead() throws Exception {
    AtomicInteger calls = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          calls.incrementAndGet();
          return new ServiceConfigFiles.Contents(
              "nk.monitoring.mode: STANDARD\n", "nk.web.http.port: '8080'\n");
        };
    for (Map<String, String> invalid :
        java.util.List.of(
            Map.<String, String>of(),
            Map.of(FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484, "/tmp/config"),
            Map.of("schubert_nk_config_dir", FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED),
            Map.of(
                FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484,
                FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED,
                "SCHUBERT_NK_PASSWORD",
                "not-a-secret"))) {
      assertEquals(
          "Web non-secret environment unavailable",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new WebConfigurationLoader(source, invalid).load())
              .getMessage());
    }
    assertEquals(0, calls.get());
    assertThrows(NullPointerException.class, () -> new WebConfigurationLoader(source, null));
    assertEquals(
        "8080",
        new WebConfigurationLoader(
                source,
                Map.of(
                    FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484,
                    FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED,
                    "PATH",
                    "/usr/bin"))
            .load()
            .value(FIXTURE_NK_WEB_HTTP_PORT_F1BB508F));
    assertEquals(1, calls.get());
    // BUG268: fixed names do not certify supplied FD values or readiness.
    for (String key :
        java.util.List.of("SCHUBERT_NK_STARTUP_ADMISSION_FD", "SCHUBERT_NK_STARTUP_PROOF_FD")) {
      var approved = new java.util.HashMap<>(ENV);
      approved.put(key, "not-an-admitted-descriptor");
      assertEquals(
          "8080",
          new WebConfigurationLoader(source, approved)
              .load()
              .value(FIXTURE_NK_WEB_HTTP_PORT_F1BB508F));
      for (String alias :
          java.util.List.of(key.toLowerCase(java.util.Locale.ROOT), key + "_OTHER")) {
        var invalid = new java.util.HashMap<>(ENV);
        invalid.put(alias, "128");
        assertThrows(
            IllegalArgumentException.class,
            () -> new WebConfigurationLoader(source, invalid).load());
      }
    }
    assertEquals(3, calls.get());
  }
}
