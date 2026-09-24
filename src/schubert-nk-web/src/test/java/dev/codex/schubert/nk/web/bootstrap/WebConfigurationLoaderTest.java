package dev.codex.schubert.nk.web.bootstrap;

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

/** PT-OPS-WEB-LOAD-001..004, SS343 Web-only fixed file-to-parser bridge. */
final class WebConfigurationLoaderTest {
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
    WebNonSecretConfig config = new WebConfigurationLoader(source).load();
    assertEquals(1, calls.get());
    assertEquals("DEBUG", config.value("nk.monitoring.mode"));
    assertEquals("8082", config.value("nk.web.http.port"));
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
            });
    assertSame(sourceFailure, assertThrows(StorageIoException.class, failed::load));
    WebConfigurationLoader malformed =
        new WebConfigurationLoader(
            service ->
                new ServiceConfigFiles.Contents(
                    "nk.monitoring.mode: DEBUG\n", "nk.db.pool.api.max: 8\n"));
    assertEquals(
        "Web non-secret configuration unavailable",
        assertThrows(IllegalArgumentException.class, malformed::load).getMessage());
  }

  @Test
  void opsWebLoad003NullContractsAndProductionFactory() {
    assertThrows(NullPointerException.class, () -> new WebConfigurationLoader(null));
    assertThrows(
        NullPointerException.class, () -> new WebConfigurationLoader(service -> null).load());
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
            });
    try (var executor = Executors.newFixedThreadPool(8)) {
      var results = new ArrayList<java.util.concurrent.Future<WebNonSecretConfig>>();
      for (int i = 0; i < 32; i++) results.add(executor.submit(loader::load));
      for (var result : results) {
        assertEquals("STANDARD", result.get().value("nk.monitoring.mode"));
        assertEquals("8080", result.get().value("nk.web.http.port"));
      }
    }
    assertEquals(32, calls.get());
  }
}
