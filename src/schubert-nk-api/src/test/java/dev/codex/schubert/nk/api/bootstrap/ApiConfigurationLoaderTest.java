package dev.codex.schubert.nk.api.bootstrap;

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

/** PT-OPS-API-LOAD-001..005, SS343 API-only fixed file-to-parser bridge. */
final class ApiConfigurationLoaderTest {
  private static final String FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484 = "SCHUBERT_NK_CONFIG_DIR";
  private static final String FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED = "/etc/schubert-nk";
  private static final Map<String, String> ENV =
      Map.of(FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484, FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED);

  @Test
  void opsApiLoad001FixedServiceAndLayerOrder() throws Exception {
    AtomicInteger calls = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          assertEquals(ServiceConfigFiles.Service.API, service);
          calls.incrementAndGet();
          return new ServiceConfigFiles.Contents(
              "nk.monitoring.mode: DEBUG\n", "nk.mq.url: tcp://127.0.0.1:61617\n");
        };
    ApiNonSecretConfig config = new ApiConfigurationLoader(source, ENV).load();
    assertEquals(1, calls.get());
    assertEquals("DEBUG", config.value("nk.monitoring.mode"));
    assertEquals("tcp://127.0.0.1:61617", config.value("nk.mq.url"));
    assertEquals("001", config.value("nk.protocol.version"));
  }

  @Test
  void opsApiLoad002SourceAndParserFailuresStayDistinct() {
    StorageIoException sourceFailure =
        new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    ApiConfigurationLoader failed =
        new ApiConfigurationLoader(
            service -> {
              throw sourceFailure;
            },
            ENV);
    assertSame(sourceFailure, assertThrows(StorageIoException.class, failed::load));
    ApiConfigurationLoader malformed =
        new ApiConfigurationLoader(
            service ->
                new ServiceConfigFiles.Contents(
                    "nk.monitoring.mode: DEBUG\n", "nk.web.http.port: 8080\n"),
            ENV);
    assertEquals(
        "API non-secret configuration unavailable",
        assertThrows(IllegalArgumentException.class, malformed::load).getMessage());
  }

  @Test
  void opsApiLoad003NullContractsAndProductionFactory() {
    assertThrows(NullPointerException.class, () -> new ApiConfigurationLoader(null, ENV));
    assertThrows(
        NullPointerException.class, () -> new ApiConfigurationLoader(service -> null, ENV).load());
    assertNotNull(ApiConfigurationLoader.production());
  }

  @Test
  void opsApiLoad004ConcurrentFreshReads() throws Exception {
    AtomicInteger calls = new AtomicInteger();
    ApiConfigurationLoader loader =
        new ApiConfigurationLoader(
            service -> {
              assertEquals(ServiceConfigFiles.Service.API, service);
              calls.incrementAndGet();
              return new ServiceConfigFiles.Contents(
                  "nk.monitoring.mode: STANDARD\n", "nk.db.pool.api.max: '8'\n");
            },
            ENV);
    try (var executor = Executors.newFixedThreadPool(8)) {
      var results = new ArrayList<java.util.concurrent.Future<ApiNonSecretConfig>>();
      for (int i = 0; i < 32; i++) results.add(executor.submit(loader::load));
      for (var result : results) {
        assertEquals("STANDARD", result.get().value("nk.monitoring.mode"));
        assertEquals("8", result.get().value("nk.db.pool.api.max"));
      }
    }
    assertEquals(32, calls.get());
  }

  @Test
  void opsApiLoad005EnvironmentIsExactBeforeFileRead() throws Exception {
    AtomicInteger calls = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          calls.incrementAndGet();
          return new ServiceConfigFiles.Contents(
              "nk.monitoring.mode: STANDARD\n", "nk.db.pool.api.max: '8'\n");
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
          "API non-secret environment unavailable",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new ApiConfigurationLoader(source, invalid).load())
              .getMessage());
    }
    assertEquals(0, calls.get());
    assertThrows(NullPointerException.class, () -> new ApiConfigurationLoader(source, null));
    assertEquals(
        "8",
        new ApiConfigurationLoader(
                source,
                Map.of(
                    FIXTURE_SCHUBERT_NK_CONFIG_DIR_DBE4C484,
                    FIXTURE_ETC_SCHUBERT_NK_AB7CF1ED,
                    "PATH",
                    "/usr/bin"))
            .load()
            .value("nk.db.pool.api.max"));
    assertEquals(1, calls.get());
    // BUG268: recognize names, not authority or descriptor values. Native gate is separate.
    for (String key :
        java.util.List.of("SCHUBERT_NK_STARTUP_ADMISSION_FD", "SCHUBERT_NK_STARTUP_PROOF_FD")) {
      var approved = new java.util.HashMap<>(ENV);
      approved.put(key, "not-an-admitted-descriptor");
      assertEquals(
          "8", new ApiConfigurationLoader(source, approved).load().value("nk.db.pool.api.max"));
      for (String alias :
          java.util.List.of(key.toLowerCase(java.util.Locale.ROOT), key + "_OTHER")) {
        var invalid = new java.util.HashMap<>(ENV);
        invalid.put(alias, "128");
        assertThrows(
            IllegalArgumentException.class,
            () -> new ApiConfigurationLoader(source, invalid).load());
      }
    }
    assertEquals(3, calls.get());
  }
}
