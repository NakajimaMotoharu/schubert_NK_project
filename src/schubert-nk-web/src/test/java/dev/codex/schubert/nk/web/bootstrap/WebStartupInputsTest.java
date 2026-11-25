package dev.codex.schubert.nk.web.bootstrap;

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

/** PT-OPS-WEB-INPUT-001..005; source-to-startup-input composition only. */
final class WebStartupInputsTest {
  private static final String ROOT = "/run/credentials/schubert-nk-web.service";
  private static final Map<String, String> ENV =
      Map.of("SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk", "CREDENTIALS_DIRECTORY", ROOT);

  @Test
  void opsWebInput001CombinesIndependentFixedInputs() throws Exception {
    AtomicInteger reads = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          assertEquals(ServiceConfigFiles.Service.WEB, service);
          reads.incrementAndGet();
          return new ServiceConfigFiles.Contents(
              "nk.monitoring.mode: DEBUG\n", "nk.web.http.port: '8080'\n");
        };
    var result = new WebStartupInputs(source, ENV).load();
    assertEquals("DEBUG", result.config().value("nk.monitoring.mode"));
    assertEquals("8080", result.config().value("nk.web.http.port"));
    assertEquals(Path.of(ROOT), result.credentials().directory());
    assertEquals(1, reads.get());
  }

  @Test
  void opsWebInput002MissingPrivateLocationStopsBeforeSourceRead() {
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
                    new WebStartupInputs(
                        source, Map.of("SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk")))
            .getMessage());
    assertEquals(0, reads.get());
  }

  @Test
  void opsWebInput003SourceFailureAndConfigAdmissionStayDistinct() {
    StorageIoException failure = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    assertSame(
        failure,
        assertThrows(
            StorageIoException.class,
            () ->
                new WebStartupInputs(
                        service -> {
                          throw failure;
                        },
                        ENV)
                    .load()));
    var badEnv = Map.of("SCHUBERT_NK_CONFIG_DIR", "/other", "CREDENTIALS_DIRECTORY", ROOT);
    assertEquals(
        "Web non-secret environment unavailable",
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new WebStartupInputs(
                            service -> {
                              throw new AssertionError("source must not run");
                            },
                            badEnv)
                        .load())
            .getMessage());
  }

  @Test
  void opsWebInput004NullContracts() throws Exception {
    assertThrows(NullPointerException.class, () -> new WebStartupInputs(null, ENV));
    assertThrows(NullPointerException.class, () -> new WebStartupInputs(service -> null, null));
    var credentials = ServiceCredentialLocation.read(ENV);
    var config = WebNonSecretConfig.parse("", "");
    assertThrows(NullPointerException.class, () -> new WebStartupInputs.Values(null, credentials));
    assertThrows(NullPointerException.class, () -> new WebStartupInputs.Values(config, null));
  }

  @Test
  void opsWebInput005ChecksEnvironmentBeforeOpeningConfigSource() {
    NonSecretConfigSource unopened =
        service -> {
          throw new AssertionError("environment validation must not read the source");
        };
    new WebStartupInputs(unopened, ENV).validateEnvironment();

    Map<String, String> wrongDirectory =
        Map.of("SCHUBERT_NK_CONFIG_DIR", "/other", "CREDENTIALS_DIRECTORY", ROOT);
    assertEquals(
        "Web non-secret environment unavailable",
        assertThrows(
                IllegalArgumentException.class,
                () -> new WebStartupInputs(unopened, wrongDirectory).validateEnvironment())
            .getMessage());
  }
}
