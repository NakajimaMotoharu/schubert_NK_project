package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.StringJoiner;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SS343 literal source grammar and independent boundary construction; PT-OPS-CFG-001..006. */
final class InspectorStaticEnvironmentTest {
  private static final String URL = "jdbc:postgresql://127.0.0.1:5432/schubert_nk";
  private static final String GOLDEN =
      "NK_INSPECTOR_DB_URL=jdbc:postgresql://127.0.0.1:5432/schubert_nk\n"
          + "NK_INSPECTOR_FINGERPRINT_VERSIONS=current,previous\n";

  @Test
  void canonicalFixtures() throws Exception {
    accept(bytes(GOLDEN));
    String template =
        java.nio.file.Files.readString(
            java.nio.file.Path.of(
                System.getProperty("nk.pt.repository"),
                "src/deployment/config/inbox-inspector.env.template"));
    String rendered =
        template
            .replace("@PG_PORT@", "5432")
            .replace("@PG_DATABASE@", "schubert_nk")
            .replace("@FINGERPRINT_VERSION_NAMES@", "current,previous");
    assertEquals(GOLDEN, rendered);
    accept(bytes(rendered));
    reject(bytes(template));
    for (String url :
        List.of(
            "jdbc:postgresql://127.0.0.1:1/a",
            "jdbc:postgresql://127.0.0.1:65535/" + "_".repeat(63))) {
      for (String names : List.of("1", "A".repeat(16), "a,A,a_1,A.2,9-v3")) {
        accept(config(url, names));
      }
    }
  }

  @Test
  void sourceAndSyntaxRejection() {
    for (String wrong :
        List.of(
            "",
            GOLDEN + GOLDEN,
            GOLDEN + "\n",
            GOLDEN.replace("\n", "\r\n"),
            GOLDEN.replace("DB_URL", "db_url"),
            GOLDEN.replace("DB_URL", "RUN_ID"),
            GOLDEN.replace("DB_URL", "CUTOFF"),
            GOLDEN.replace("NK_INSPECTOR_DB_URL", "CREDENTIALS_DIRECTORY"),
            GOLDEN.replace("NK_INSPECTOR_DB_URL", "UNKNOWN"),
            GOLDEN.replace("NK_INSPECTOR_FINGERPRINT_VERSIONS", "NK_INSPECTOR_DB_URL"),
            GOLDEN.replace("=jdbc", "=\"jdbc"),
            GOLDEN.replace("=jdbc", "= jdbc"),
            GOLDEN.replace("=jdbc", "=\\jdbc"),
            GOLDEN.replace("current", "$(id)"),
            "#comment\n" + GOLDEN,
            GOLDEN.replace("current", "current #comment"),
            "NK_INSPECTOR_FINGERPRINT_VERSIONS=current,previous\n"
                + "NK_INSPECTOR_DB_URL="
                + URL
                + "\n")) reject(bytes(wrong));
    byte[] golden = bytes(GOLDEN);
    for (int at = 0; at < golden.length; at++) {
      for (int value = 0; value <= 255; value++) {
        if ((value >= 32 && value < 127) || value == golden[at]) continue;
        byte[] changed = golden.clone();
        changed[at] = (byte) value;
        reject(changed);
      }
    }
    reject(GOLDEN.replace("current", "あ").getBytes(StandardCharsets.UTF_8));
  }

  @Test
  void urlBoundaries() {
    for (String port : List.of("0", "00", "01", "65536", "99999", "100000", "-1", "+1", ""))
      reject(config("jdbc:postgresql://127.0.0.1:" + port + "/schubert_nk", "v1"));
    for (String db : List.of("", "a".repeat(64), "A", "1a", "a-b", "a/b", "a?user=x", "a#x"))
      reject(config("jdbc:postgresql://127.0.0.1:5432/" + db, "v1"));
    for (String host : List.of("localhost", "[::1]", "127.0.0.2", "192.0.2.1", "u:p@127.0.0.1"))
      reject(config("jdbc:postgresql://" + host + ":5432/schubert_nk", "v1"));
    reject(config(URL + "?password=not-a-real-secret", "v1"));
    reject(config("", "v1"));
  }

  @Test
  void versionBoundaries() {
    // Fixed-length distinct elements make the aggregate boundary independent of production parsing.
    StringJoiner prefix = new StringJoiner(",");
    for (int i = 0; i < 4095; i++) prefix.add(String.format(Locale.ROOT, "v%014d", i));
    // Each element is 15 bytes: 4095*15 + 4094 separators = 65519.
    assertEquals(65519, prefix.length());
    String at65535 = prefix + "," + "Z".repeat(15);
    String at65536 = prefix + "," + "Z".repeat(16);
    assertEquals(65535, at65535.length());
    assertEquals(65536, at65536.length());
    accept(config(URL, at65535));
    accept(config(URL, at65536));
    reject(config(URL, at65536 + "X"));
    for (String names :
        List.of(
            "",
            ",",
            "v1,",
            ",v1",
            "v1,,v2",
            "v1,v1",
            "v1,v2,v1",
            "_v",
            ".v",
            "-v",
            "v".repeat(17),
            "v1 v2",
            "v1/v2")) reject(config(URL, names));
    accept(config(URL, "v1,V1"));
  }

  @Test
  void sizeNullAndRedaction() {
    assertThrows(NullPointerException.class, () -> InspectorStaticEnvironment.requireValid(null));
    for (int length : List.of(0, 65848, 65849)) reject(new byte[length]);
    byte[] golden = bytes(GOLDEN);
    for (int size = 0; size < golden.length; size++) reject(Arrays.copyOf(golden, size));
    reject(config(URL, "password=not-a-real-secret"));
    assertEquals(65848, InspectorStaticEnvironment.MAXIMUM_BYTES);
  }

  @Test
  void concurrentValidation() throws Exception {
    byte[] golden = bytes(GOLDEN);
    byte[] bad = config(URL, "v1,v1");
    var pool = Executors.newFixedThreadPool(8);
    try {
      List<Callable<Integer>> work = new ArrayList<>();
      for (int i = 0; i < 64; i++)
        work.add(
            () -> {
              accept(golden);
              reject(bad);
              return 1;
            });
      int finished = 0;
      for (var future : pool.invokeAll(work, 5, TimeUnit.SECONDS))
        finished += future.get(5, TimeUnit.SECONDS);
      assertEquals(64, finished);
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS), "fixture workers not stopped");
    }
    assertArrayEquals(bytes(GOLDEN), golden);
  }

  private static byte[] config(String url, String versions) {
    return bytes(
        "NK_INSPECTOR_DB_URL=" + url + "\nNK_INSPECTOR_FINGERPRINT_VERSIONS=" + versions + "\n");
  }

  private static byte[] bytes(String literal) {
    return literal.getBytes(StandardCharsets.US_ASCII);
  }

  private static void accept(byte[] value) {
    byte[] before = value.clone();
    assertDoesNotThrow(() -> InspectorStaticEnvironment.requireValid(value));
    assertArrayEquals(before, value);
  }

  private static void reject(byte[] value) {
    byte[] before = value.clone();
    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> InspectorStaticEnvironment.requireValid(value));
    assertEquals("inspector static environment is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertArrayEquals(before, value);
  }
}
