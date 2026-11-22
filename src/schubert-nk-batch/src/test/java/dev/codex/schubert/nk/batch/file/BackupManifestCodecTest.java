package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.manifest;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.versionTokens;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HexFormat;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

/** BAK/BKO/UI251/SS341 6.4/343 5.3; SSC058/PG165; BAT186..193 in method order. */
final class BackupManifestCodecTest {
  @Test
  void independentCanonicalGolden() throws IOException, NoSuchAlgorithmException {
    byte[] golden = golden();
    assertEquals(965, golden.length);
    assertEquals(
        "733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e",
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(golden)));
    byte[] encoded = BackupManifestCodec.encode(manifest());
    assertArrayEquals(golden, encoded);
    Path traces = Path.of("target", "backup-manifest-traces");
    Files.createDirectories(traces);
    Files.write(traces.resolve("PT-BAT-186-manifest.json"), encoded);
    var actual = BackupManifestCodec.decode(golden);
    assertEquals(manifest(), actual);
    assertEquals(713, actual.totalBytes());
    assertEquals("20260913-000002-12345678-9abc-def0-8123-456789abcdef", actual.directoryName());
  }

  @Test
  void allFieldsAndMaximumLengths() throws IOException {
    String input =
        text()
            .replace("12345678-9abc-def0-8123-456789abcdef", "00000000-0000-0000-0000-000000000000")
            .replace("2026-09-12T15:00:00.000000Z", "1900-01-01T00:00:00.000001Z")
            .replace("2026-09-12T15:00:01.000000Z", "1900-01-01T00:00:01.000002Z")
            .replace("2026-09-12T15:00:02.123456Z", "1900-01-01T00:00:02.000003Z")
            .replace("2026-09-12T15:00:03.654321Z", "9999-12-31T23:59:59.999999Z")
            .replace("\"id\":90000,\"attempt\":1", "\"id\":999999999999,\"attempt\":99")
            .replace("\"id\":90001,\"attempt\":1", "\"id\":999999999998,\"attempt\":98")
            .replace("\"size\":1,", "\"size\":3074457345618258602,")
            .replace("\"size\":512,", "\"size\":3074457345618258602,")
            .replace("\"size\":200,", "\"size\":3074457345618258603,")
            .replace("0".repeat(64), "d".repeat(64))
            .replace("a".repeat(64), "e".repeat(64))
            .replace("b".repeat(64), "f".repeat(64))
            .replace("c".repeat(64), "1".repeat(64));
    var expectedVersions = versionTokens();
    for (int i = 0; i < expectedVersions.size(); i++)
      input =
          input.replace(
              "\"" + expectedVersions.get(i) + "\"",
              "\"" + (i == 2 ? "999" : String.valueOf((char) ('A' + i)).repeat(128)) + "\"");
    byte[] expected = ascii(input);
    var actual = BackupManifestCodec.decode(expected);
    assertEquals(new UUID(0, 0), actual.run().id());
    assertEquals(Instant.parse("1900-01-01T00:00:00.000001Z"), actual.run().cutoff());
    assertEquals(Instant.parse("1900-01-01T00:00:02.000003Z"), actual.startedAt());
    assertEquals(Instant.parse("9999-12-31T23:59:59.999999Z"), actual.contentFinishedAt());
    assertEquals(999999999999L, actual.databaseStep().id());
    assertEquals(999999999998L, actual.configurationStep().id());
    assertEquals(99, actual.databaseStep().attempt());
    assertEquals(98, actual.configurationStep().attempt());
    assertEquals(Instant.parse("1900-01-01T00:00:00.000001Z"), actual.databaseStep().startedAt());
    assertEquals(
        Instant.parse("1900-01-01T00:00:01.000002Z"), actual.configurationStep().startedAt());
    assertEquals("999", actual.versions().schema());
    assertEquals(
        List.of(
            "A".repeat(128),
            "B".repeat(128),
            "D".repeat(128),
            "E".repeat(128),
            "F".repeat(128),
            "G".repeat(128),
            "H".repeat(128)),
        List.of(
            actual.versions().host(),
            actual.versions().app(),
            actual.versions().os(),
            actual.versions().jdk(),
            actual.versions().postgresql(),
            actual.versions().artemis(),
            actual.versions().age()));
    assertEquals("d".repeat(64), actual.recipientSha256());
    assertEquals("e".repeat(64), actual.dump().sha256());
    assertEquals("f".repeat(64), actual.configuration().sha256());
    assertEquals("1".repeat(64), actual.credentials().sha256());
    assertEquals(3074457345618258602L, actual.dump().size());
    assertEquals(3074457345618258602L, actual.configuration().size());
    assertEquals(3074457345618258603L, actual.credentials().size());
    assertEquals(6148914691236517205L, actual.configurationBytes());
    assertEquals(Long.MAX_VALUE, actual.totalBytes());
    assertEquals(1873, expected.length); // All three positive counts occupy nineteen digits.
    assertTrue(expected.length < 4096);
    assertArrayEquals(expected, BackupManifestCodec.encode(actual));
  }

  @Test
  void structuralByteMutation() throws IOException {
    byte[] original = golden();
    for (int i = 0; i < original.length; i++)
      for (byte replacement : new byte[] {'~', 0, (byte) 0xff}) {
        byte[] changed = original.clone();
        changed[i] = replacement;
        rejected(changed);
      }
    for (String s :
        List.of(
            "\ufeff" + text(),
            text().replace("\n", "\r\n"),
            text().replace("nk-pt", "日本"),
            text() + "\n",
            text().stripTrailing())) rejected(s.getBytes(StandardCharsets.UTF_8));
  }

  @Test
  void noncanonicalScalarsAndDates() throws IOException {
    String source = text();
    for (String bad :
        List.of(
            "0",
            "-1",
            "+1",
            "01",
            "1.0",
            "1e0",
            "9223372036854775808",
            "999999999999999999999999999999999999999999999999999"))
      rejected(ascii(source.replace("\"size\":1,", "\"size\":" + bad + ",")));
    for (String bad :
        List.of(
            "1-1-1-1-1",
            "12345678-9ABC-DEF0-8123-456789ABCDEF",
            "123456789-9abc-def0-8123-456789abcdef",
            "unknown"))
      rejected(ascii(source.replace("12345678-9abc-def0-8123-456789abcdef", bad)));
    for (String bad :
        List.of(
            "2026-09-12T15:00:03Z",
            "2026-09-12T15:00:03.654321+00:00",
            "2026-09-12t15:00:03.654321z",
            "2026-09-12T15:00:03.654321000Z",
            "2026-09-12T15:00:03.654321001Z",
            "2026-02-30T15:00:03.654321Z",
            "2026-09-12T23:59:60.000000Z",
            "2026-09-12T24:00:00.000000Z",
            "+10000-01-01T00:00:00.000000Z",
            "0000-01-01T00:00:00.000000Z",
            "1900-01-01T00:00:00.000000Z",
            "not-a-time")) rejected(ascii(source.replace("2026-09-12T15:00:03.654321Z", bad)));
    for (String part : List.of("a", "b", "c"))
      rejected(ascii(source.replace(part.repeat(64), part.toUpperCase(Locale.ROOT).repeat(64))));
    for (String bad : List.of("0", "100", "2147483648", "01"))
      rejected(ascii(source.replace("\"attempt\":1", "\"attempt\":" + bad)));
    rejected(ascii(source.replace("\"id\":90001", "\"id\":90000")));
    rejected(ascii(source.replace("\"id\":90001", "\"id\":1000000000000")));
    rejected(ascii(source.replace("\"schema\":\"020\"", "\"schema\":\"000\"")));
  }

  @Test
  void missingUnknownDuplicateAndOrder() throws IOException {
    String source = text();
    for (String bad :
        List.of(
            source.replace("\"database\":\"schubert_nk\",", ""),
            source.replace("\"database\":", "\"unknown\":"),
            source.replace("\"database\":", "\"database\":\"schubert_nk\",\"database\":"),
            source.replace(
                "\"format\":\"NKBACKUP1\",\"database\":\"schubert_nk\"",
                "\"database\":\"schubert_nk\",\"format\":\"NKBACKUP1\""),
            source.replace("\"host\":\"nk-pt\"", "\"host\":null"),
            source.replace("\"host\":\"nk-pt\"", "\"host\":\"\""),
            source.replace("nk-pt", "nk\\u002dpt"),
            source.replace(":", ": "),
            source.replace(",", ", "),
            source.replace("NKBACKUP1", "NKBACKUP2"),
            source + "{}")) rejected(ascii(bad));
    // Each variable field independently missing/null: fixed schema must not silently default.
    String[] fields = {
      "runId",
      "cutoff",
      "startedAt",
      "contentFinishedAt",
      "id",
      "attempt",
      "host",
      "app",
      "schema",
      "os",
      "jdk",
      "postgresql",
      "artemis",
      "age",
      "recipientSha256",
      "size",
      "sha256"
    };
    for (String field : fields) {
      String pattern = "\"" + field + "\":(\"[^\"]*\"|[0-9]+)";
      rejected(ascii(source.replaceAll(pattern, "\"" + field + "\":null")));
    }
  }

  @Test
  void sizeAndNullBoundaries() throws IOException {
    rejected(new byte[0]);
    for (int size : new int[] {1, 4095, 4096, 4097}) {
      byte[] input = Arrays.copyOf(golden(), size);
      rejected(input);
    }
    assertThrows(NullPointerException.class, () -> BackupManifestCodec.decode(null));
    assertThrows(NullPointerException.class, () -> BackupManifestCodec.encode(null));
    rejected(ascii(text().replace("nk-pt", "a".repeat(129))));
  }

  @Test
  void inputOutputOwnership() throws IOException {
    byte[] source = golden();
    var value = BackupManifestCodec.decode(source);
    Arrays.fill(source, (byte) 'x');
    assertEquals(manifest(), value);
    byte[] first = BackupManifestCodec.encode(value);
    byte[] second = BackupManifestCodec.encode(value);
    assertNotSame(first, second);
    first[0] = 'x';
    assertArrayEquals(golden(), second);
    assertArrayEquals(golden(), BackupManifestCodec.encode(value));
  }

  @Test
  void concurrentCanonicalRoundTrips()
      throws IOException, InterruptedException, ExecutionException, TimeoutException {
    byte[] expected = golden();
    var value = manifest();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Future<byte[]>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            pool.submit(
                () -> {
                  assertEquals(value, BackupManifestCodec.decode(expected));
                  return BackupManifestCodec.encode(value);
                }));
      Set<byte[]> identities = Collections.newSetFromMap(new IdentityHashMap<>());
      for (var task : tasks) {
        byte[] actual = task.get(5, java.util.concurrent.TimeUnit.SECONDS);
        assertArrayEquals(expected, actual);
        assertTrue(identities.add(actual));
      }
      assertEquals(64, identities.size());
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
  }

  private static byte[] golden() throws IOException {
    try (var input =
        Objects.requireNonNull(
            BackupManifestCodecTest.class.getResourceAsStream("/backup/manifest-golden.json"))) {
      return input.readAllBytes();
    }
  }

  private static String text() throws IOException {
    return new String(golden(), StandardCharsets.US_ASCII);
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void rejected(byte[] value) {
    var error =
        assertThrows(IllegalArgumentException.class, () -> BackupManifestCodec.decode(value));
    assertEquals("invalid backup manifest", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
