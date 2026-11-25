package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-API-INPUT-001..005; source-to-startup-input composition only. */
final class ApiStartupInputsTest {
  private static final String ROOT = "/run/credentials/schubert-nk-api.service";
  private static final Map<String, String> ENV =
      Map.of("SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk", "CREDENTIALS_DIRECTORY", ROOT);

  @Test
  void opsApiInput001CombinesIndependentFixedInputs() throws Exception {
    AtomicInteger reads = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          assertEquals(ServiceConfigFiles.Service.API, service);
          reads.incrementAndGet();
          return new ServiceConfigFiles.Contents(
              "nk.monitoring.mode: DEBUG\n", "nk.db.pool.api.max: '8'\n");
        };
    var result = new ApiStartupInputs(source, ENV).load();
    assertEquals("DEBUG", result.config().value("nk.monitoring.mode"));
    assertEquals("8", result.config().value("nk.db.pool.api.max"));
    assertEquals(Path.of(ROOT), result.credentials().directory());
    assertEquals(1, reads.get());
  }

  @Test
  void opsApiInput002MissingPrivateLocationStopsBeforeSourceRead() {
    AtomicInteger reads = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          reads.incrementAndGet();
          throw new AssertionError("source must not run");
        };
    assertEquals(
        "service credential location unavailable",
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new ApiStartupInputs(
                        source, Map.of("SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk")))
            .getMessage());
    assertEquals(0, reads.get());
  }

  @Test
  void opsApiInput003SourceFailureAndConfigAdmissionStayDistinct() {
    StorageIoException failure = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    assertSame(
        failure,
        assertThrows(
            StorageIoException.class,
            () ->
                new ApiStartupInputs(
                        service -> {
                          throw failure;
                        },
                        ENV)
                    .load()));
    var badEnv = Map.of("SCHUBERT_NK_CONFIG_DIR", "/other", "CREDENTIALS_DIRECTORY", ROOT);
    assertEquals(
        "API non-secret environment unavailable",
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new ApiStartupInputs(
                            service -> {
                              throw new AssertionError("source must not run");
                            },
                            badEnv)
                        .load())
            .getMessage());
  }

  @Test
  void opsApiInput004NullContracts() throws Exception {
    assertThrows(NullPointerException.class, () -> new ApiStartupInputs(null, ENV));
    assertThrows(NullPointerException.class, () -> new ApiStartupInputs(service -> null, null));
    var credentials = ServiceCredentialLocation.read(ENV);
    var config = ApiNonSecretConfig.parse("", "");
    assertThrows(NullPointerException.class, () -> new ApiStartupInputs.Values(null, credentials));
    assertThrows(NullPointerException.class, () -> new ApiStartupInputs.Values(config, null));
  }

  @Test
  void opsApiInput005ChecksEnvironmentBeforeOpeningConfigSource() {
    NonSecretConfigSource unopened =
        service -> {
          throw new AssertionError("environment validation must not read the source");
        };
    new ApiStartupInputs(unopened, ENV).validateEnvironment();

    Map<String, String> wrongDirectory =
        Map.of("SCHUBERT_NK_CONFIG_DIR", "/other", "CREDENTIALS_DIRECTORY", ROOT);
    assertEquals(
        "API non-secret environment unavailable",
        assertThrows(
                IllegalArgumentException.class,
                () -> new ApiStartupInputs(unopened, wrongDirectory).validateEnvironment())
            .getMessage());
  }
}
