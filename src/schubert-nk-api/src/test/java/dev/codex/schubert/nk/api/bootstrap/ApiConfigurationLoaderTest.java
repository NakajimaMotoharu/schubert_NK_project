package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-API-LOAD-001..004, SS343 API-only fixed file-to-parser bridge. */
final class ApiConfigurationLoaderTest {
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
    ApiNonSecretConfig config = new ApiConfigurationLoader(source).load();
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
            });
    assertSame(sourceFailure, assertThrows(StorageIoException.class, failed::load));
    ApiConfigurationLoader malformed =
        new ApiConfigurationLoader(
            service ->
                new ServiceConfigFiles.Contents(
                    "nk.monitoring.mode: DEBUG\n", "nk.web.http.port: 8080\n"));
    assertEquals(
        "API non-secret configuration unavailable",
        assertThrows(IllegalArgumentException.class, malformed::load).getMessage());
  }

  @Test
  void opsApiLoad003NullContractsAndProductionFactory() {
    assertThrows(NullPointerException.class, () -> new ApiConfigurationLoader(null));
    assertThrows(
        NullPointerException.class, () -> new ApiConfigurationLoader(service -> null).load());
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
            });
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
}
