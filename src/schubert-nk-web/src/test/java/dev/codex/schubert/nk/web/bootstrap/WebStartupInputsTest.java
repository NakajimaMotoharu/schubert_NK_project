package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-WEB-INPUT-001..006; source-to-startup-input composition only. */
final class WebStartupInputsTest {
  private static final String CONFIG_DIRECTORY_ENV = "SCHUBERT_NK_CONFIG_DIR";
  private static final String CREDENTIALS_DIRECTORY_ENV = "CREDENTIALS_DIRECTORY";
  private static final String ROOT = "/run/credentials/schubert-nk-web.service";
  private static final Map<String, String> ENV =
      Map.of(CONFIG_DIRECTORY_ENV, "/etc/schubert-nk", CREDENTIALS_DIRECTORY_ENV, ROOT);

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
                    new WebStartupInputs(source, Map.of(CONFIG_DIRECTORY_ENV, "/etc/schubert-nk")))
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
    var badEnv = Map.of(CONFIG_DIRECTORY_ENV, "/other", CREDENTIALS_DIRECTORY_ENV, ROOT);
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
        Map.of(CONFIG_DIRECTORY_ENV, "/other", CREDENTIALS_DIRECTORY_ENV, ROOT);
    assertEquals(
        "Web non-secret environment unavailable",
        assertThrows(
                IllegalArgumentException.class,
                () -> new WebStartupInputs(unopened, wrongDirectory).validateEnvironment())
            .getMessage());
  }

  @Test
  void opsWebInput006ShowsRedactedValuesWithoutChangingComponentIdentity() throws Exception {
    String fixtureDirectory = "/test-fixture/startup-config-value";
    var location =
        ServiceCredentialLocation.read(Map.of(CREDENTIALS_DIRECTORY_ENV, fixtureDirectory));
    var distinctLocation = ServiceCredentialLocation.read(ENV);
    var config = WebNonSecretConfig.parse("", "");
    var values = new WebStartupInputs.Values(config, location);
    var sameComponents = new WebStartupInputs.Values(config, location);
    var otherLocation = new WebStartupInputs.Values(config, distinctLocation);

    assertEquals(sameComponents, values);
    assertEquals(sameComponents.hashCode(), values.hashCode());
    assertNotEquals(otherLocation, values);

    String diagnostic = values.toString();
    assertTrue(diagnostic.contains("WebNonSecretConfig[REDACTED]"));
    assertTrue(diagnostic.contains("ServiceCredentialLocation[REDACTED]"));
    assertFalse(diagnostic.contains(fixtureDirectory));
  }
}
