package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-CREDLOC-001..005; independent SS343/systemd location boundary. */
final class ServiceCredentialLocationTest {
  private static final String KEY = "CREDENTIALS_DIRECTORY";
  private static final String ROOT = "/run/credentials/schubert-nk-api.service";

  @Test
  void opsCredloc001AcceptsPrivateAbsoluteLocationWithoutOtherEnvironmentRetention() {
    var location = ServiceCredentialLocation.read(Map.of(KEY, ROOT, "PATH", "/usr/bin"));
    assertEquals(Path.of(ROOT), location.directory());
    assertEquals("ServiceCredentialLocation[REDACTED]", location.toString());
  }

  @Test
  void opsCredloc002RejectsMissingEmptyRelativeAndRoot() {
    for (Map<String, String> environment :
        java.util.List.of(
            Map.<String, String>of(), Map.of(KEY, ""), Map.of(KEY, "relative"), Map.of(KEY, "/")))
      assertInvalid(environment);
  }

  @Test
  void opsCredloc003RejectsAliasTraversalAndControlBytes() {
    for (Map<String, String> environment :
        java.util.List.of(
            Map.of("credentials_directory", ROOT),
            Map.of(KEY, ROOT, "Credentials_Directory", "/other"),
            Map.of(KEY, ROOT + "/../other"),
            Map.of(KEY, ROOT + "\0"),
            Map.of(KEY, ROOT + "\r"),
            Map.of(KEY, ROOT + "\n"))) assertInvalid(environment);
  }

  @Test
  void opsCredloc004BoundsAndNullContracts() {
    assertInvalid(Map.of(KEY, "/" + "a".repeat(4096)));
    assertEquals(
        4096,
        ServiceCredentialLocation.read(Map.of(KEY, "/" + "a".repeat(4095)))
            .directory()
            .toString()
            .length());
    var nullKey = new HashMap<String, String>();
    nullKey.put(null, "x");
    nullKey.put(KEY, ROOT);
    assertInvalid(nullKey);
    var nullValue = new HashMap<String, String>();
    nullValue.put(KEY, null);
    assertInvalid(nullValue);
    assertThrows(NullPointerException.class, () -> ServiceCredentialLocation.read(null));
  }

  @Test
  void opsCredloc005ConcurrentFreshMapsDoNotChangeSnapshot() throws Exception {
    Path expected = Path.of(ROOT);
    try (var pool = Executors.newFixedThreadPool(8)) {
      var tasks = new java.util.ArrayList<java.util.concurrent.Future<Path>>();
      for (int i = 0; i < 32; i++)
        tasks.add(pool.submit(() -> ServiceCredentialLocation.read(Map.of(KEY, ROOT)).directory()));
      for (var task : tasks) assertEquals(expected, task.get(10, TimeUnit.SECONDS));
    }
  }

  private static void assertInvalid(Map<String, String> environment) {
    assertEquals(
        "service credential location unavailable",
        assertThrows(
                IllegalArgumentException.class, () -> ServiceCredentialLocation.read(environment))
            .getMessage());
  }
}
