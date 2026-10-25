package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Literal test-only JSON builder; no production serialization/DB/file observation for expected. */
final class ReleaseInventoryTest {
  private static final String SHA = "b".repeat(64);
  private static final String COMMIT = "a".repeat(40);
  private static final String SCHEMA =
      "{\"installedRank\":0,\"version\":null,\"type\":\"SCHEMA\",\"script\":\"\\\"schubert_meta\\\"\",\"checksum\":null,\"success\":true}";
  private static final String SQL =
      "{\"installedRank\":1,\"version\":\"001\",\"type\":\"SQL\",\"script\":\"V001__first.sql\",\"checksum\":0,\"success\":true}";

  private static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.UTF_8);
  }

  private static String artifact(String path, String size, String hash) {
    return "{\"path\":\"" + path + "\",\"size\":" + size + ",\"sha256\":\"" + hash + "\"}";
  }

  private static String dependency(String coordinate, List<String> paths) {
    return "{\"coordinate\":\""
        + coordinate
        + "\",\"paths\":["
        + String.join(",", paths.stream().map(p -> "\"" + p + "\"").toList())
        + "]}";
  }

  static final class Fixture {
    final TreeMap<String, String> files = new TreeMap<>();
    final TreeMap<String, String> deps = new TreeMap<>();
    final List<String> migrations = new ArrayList<>(List.of(SCHEMA, SQL));
    String schema = "001";

    Fixture() {
      for (String path :
          List.of(
              "VERSION",
              "api/api.jar",
              "web/web.jar",
              "operations/batch.jar",
              "db/migration/V001__first.sql")) files.put(path, artifact(path, "16", SHA));
      for (String name : List.of("bootstrap", "protocol", "storage")) {
        var paths = new ArrayList<String>();
        for (String role :
            name.equals("protocol") ? List.of("api", "web") : List.of("api", "operations", "web")) {
          String path = role + "/lib/" + name + ".jar";
          paths.add(path);
          files.put(path, artifact(path, "16", SHA));
        }
        String coordinate = "dev.codex.schubert:schubert-nk-" + name + ":0.1.0";
        deps.put(coordinate, dependency(coordinate, paths));
      }
    }

    String text() {
      return "{\"format\":\"NKRELEASE1\",\"release\":\"1.2.3-PG313\",\"versions\":{\"app\":\"0.1.0\",\"protocol\":\"0.1.0\",\"storage\":\"0.1.0\",\"bootstrap\":\"0.1.0\",\"schema\":\""
          + schema
          + "\",\"config\":\"1\"},\"source\":{\"commit\":\""
          + COMMIT
          + "\",\"tag\":\"PG313\"},\"build\":{\"jdkVendor\":\"PUBLIC VENDOR\",\"jdkVersion\":\"25.0.4\",\"mavenVersion\":\"3.9.12\"},\"platform\":{\"osId\":\"ubuntu\",\"osVersion\":\"26.04\",\"architecture\":\"x86_64\",\"javaFeature\":25},\"dependencies\":["
          + String.join(",", deps.values())
          + "],\"artifacts\":["
          + String.join(",", files.values())
          + "],\"migrations\":["
          + String.join(",", migrations)
          + "]}";
    }
  }

  private static String golden() {
    return new Fixture().text();
  }

  private static void refused(String value) {
    assertThrows(IOException.class, () -> ReleaseInventory.parse(bytes(value)));
  }

  @Test
  void bomProfile001IndependentLiteralClaims() throws Exception {
    var value = ReleaseInventory.parse(bytes(golden()));
    assertEquals("1.2.3-PG313", value.release());
    assertEquals("001", value.versions().get("schema"));
    assertEquals(COMMIT, value.source().get("commit"));
    assertEquals("25.0.4", value.build().get("jdkVersion"));
    assertEquals("25", value.platform().get("javaFeature"));
    assertEquals(13, value.artifacts().size());
    assertEquals(3, value.dependencies().size());
    assertEquals(2, value.migrations().size());
    assertNull(value.migrations().getFirst().version());
    assertNull(value.migrations().getFirst().checksum());
    assertEquals("\"schubert_meta\"", value.migrations().getFirst().script());
    assertEquals(0, value.migrations().getLast().checksum());
  }

  @Test
  void bomProfile002FixedKeysTypesAndOrder() {
    for (String name :
        List.of(
            "format",
            "release",
            "versions",
            "source",
            "build",
            "platform",
            "dependencies",
            "artifacts",
            "migrations",
            "app",
            "protocol",
            "storage",
            "bootstrap",
            "schema",
            "config",
            "commit",
            "tag",
            "jdkVendor",
            "jdkVersion",
            "mavenVersion",
            "osId",
            "osVersion",
            "architecture",
            "javaFeature",
            "coordinate",
            "paths",
            "path",
            "size",
            "sha256",
            "installedRank",
            "version",
            "type",
            "script",
            "checksum",
            "success")) {
      refused(golden().replaceFirst("\"" + name + "\":", "\"unknown\":"));
      refused(
          golden().replaceFirst("\"" + name + "\":", "\"" + name + "\":null,\"" + name + "\":"));
    }
    refused(golden().replace("\"release\":\"1.2.3-PG313\"", "\"release\":null"));
    refused(golden().replace("\"format\":\"NKRELEASE1\"", "\"format\":1"));
    refused(golden().replace("\"format\":\"NKRELEASE1\"", "\"format\":\"NKRELEASE2\""));
    refused(golden().replace("\"success\":true", "\"success\":\"true\""));
    refused(golden().replace("\"source\":{", "\"source\":[] ,\"unexpected\":{"));
    refused(golden() + " {}");
  }

  @Test
  void bomProfile003ByteUtf8AndDocumentBounds() throws Exception {
    assertThrows(NullPointerException.class, () -> ReleaseInventory.parse(null));
    assertThrows(IllegalArgumentException.class, () -> ReleaseInventory.parse(new byte[0]));
    assertThrows(IllegalArgumentException.class, () -> ReleaseInventory.parse(new byte[1_048_577]));
    assertThrows(IOException.class, () -> ReleaseInventory.parse(new byte[] {(byte) 0xff}));
    refused("\ufeff" + golden());
    refused("[]");
    refused(golden().substring(0, 30));
    String padded = golden() + " ".repeat(1_048_576 - bytes(golden()).length);
    assertEquals("1.2.3-PG313", ReleaseInventory.parse(bytes(padded)).release());
  }

  @Test
  void bomProfile004StrictNumbersAndBoundaryValues() throws Exception {
    var f = new Fixture();
    for (String number : List.of("0", Long.toString(Long.MAX_VALUE))) {
      f.files.put("api/api.jar", artifact("api/api.jar", number, SHA));
      assertEquals(
          Long.parseLong(number),
          ReleaseInventory.parse(bytes(f.text())).artifacts().stream()
              .filter(a -> a.path().equals("api/api.jar"))
              .findFirst()
              .orElseThrow()
              .size());
    }
    for (String number :
        List.of("-1", "-0", "01", "1.0", "1e0", "9223372036854775808", "\"16\"", "null")) {
      f.files.put("api/api.jar", artifact("api/api.jar", number, SHA));
      refused(f.text());
    }
    for (String number : List.of("24", "26", "25.0", "\"25\"", "null"))
      refused(golden().replace("\"javaFeature\":25", "\"javaFeature\":" + number));
  }

  @Test
  void bomProfile005ArtifactLexicalAndNullContracts() {
    for (String path :
        List.of(
            "",
            "/api/api.jar",
            "a//b",
            "a/../b",
            "a/./b",
            "a\\b",
            "é",
            "a\0",
            "a".repeat(202),
            "a/".repeat(8) + "a"))
      assertThrows(
          IllegalArgumentException.class, () -> new ReleaseInventory.Artifact(path, 1, SHA));
    assertThrows(NullPointerException.class, () -> new ReleaseInventory.Artifact(null, 1, SHA));
    assertThrows(NullPointerException.class, () -> new ReleaseInventory.Artifact("a", 1, null));
    for (String hash : List.of("", "B".repeat(64), "b".repeat(63), "b".repeat(65)))
      assertThrows(
          IllegalArgumentException.class, () -> new ReleaseInventory.Artifact("a", 1, hash));
    assertEquals("a".repeat(201), new ReleaseInventory.Artifact("a".repeat(201), 0, SHA).path());
  }

  @Test
  void bomProfile006DependencyContractsAndCopies() {
    for (String coordinate : List.of("", "g:a", "g:a:v:x", "g:a:v\n", "g:é:v"))
      assertThrows(
          IllegalArgumentException.class,
          () -> new ReleaseInventory.Dependency(coordinate, List.of("api/lib/a.jar")));
    assertThrows(
        NullPointerException.class,
        () -> new ReleaseInventory.Dependency(null, List.of("api/lib/a.jar")));
    assertThrows(NullPointerException.class, () -> new ReleaseInventory.Dependency("g:a:v", null));
    for (List<String> paths :
        List.of(
            List.<String>of(),
            List.of("api/lib/a.jar", "api/lib/a.jar"),
            List.of("web/lib/a.jar", "api/lib/a.jar"),
            List.of("api/lib/a.txt"),
            List.of("api/a.jar"),
            List.of("api/lib/a.jar", "api/lib/b.jar", "api/lib/c.jar", "api/lib/d.jar")))
      assertThrows(
          IllegalArgumentException.class, () -> new ReleaseInventory.Dependency("g:a:v", paths));
    var paths = new ArrayList<>(List.of("api/lib/a.jar"));
    var value = new ReleaseInventory.Dependency("g:a:v", paths);
    paths.clear();
    assertEquals(List.of("api/lib/a.jar"), value.paths());
    assertThrows(UnsupportedOperationException.class, () -> value.paths().clear());
  }

  @Test
  void bomProfile007RequiredPayloadAndOrdering() {
    for (String path : List.of("VERSION", "api/api.jar", "web/web.jar", "operations/batch.jar")) {
      var f = new Fixture();
      f.files.remove(path);
      refused(f.text());
    }
    var f = new Fixture();
    f.files.put("VERSION", artifact("VERSION", "16", SHA) + "," + artifact("VERSION", "16", SHA));
    refused(f.text());
    refused(
        golden().replace("\"artifacts\":[", "\"artifacts\":[" + artifact("zz", "16", SHA) + ","));
    refused(
        golden()
            .replace(
                "\"dependencies\":[",
                "\"dependencies\":[" + dependency("zz:a:v", List.of("api/lib/z.jar")) + ","));
  }

  @Test
  void bomProfile008ManagementSelfHashAndAncestorConflicts() {
    for (String path :
        List.of("RELEASE-MANIFEST.json", "SHA256SUMS", "api", "api/lib", "db/migration")) {
      var f = new Fixture();
      f.files.put(path, artifact(path, "1", SHA));
      refused(f.text());
    }
  }

  @Test
  void bomProfile009RegisteredLibCompleteSetAndCommonBytes() {
    var f = new Fixture();
    f.files.put("api/lib/unknown.jar", artifact("api/lib/unknown.jar", "16", SHA));
    refused(f.text());
    f = new Fixture();
    f.files.put("api/lib/unknown.txt", artifact("api/lib/unknown.txt", "16", SHA));
    refused(f.text());
    f = new Fixture();
    f.files.remove("api/lib/storage.jar");
    refused(f.text());
    for (String size : List.of("15", "17")) {
      f = new Fixture();
      f.files.put("api/lib/storage.jar", artifact("api/lib/storage.jar", size, SHA));
      refused(f.text());
    }
    f = new Fixture();
    f.files.put("api/lib/storage.jar", artifact("api/lib/storage.jar", "16", "a".repeat(64)));
    refused(f.text());
    f = new Fixture();
    f.deps.put("z:a:v", dependency("z:a:v", List.of("api/lib/storage.jar")));
    refused(f.text());
  }

  @Test
  void bomProfile010SharedVersionsAndRequiredRoles() {
    for (String shared : List.of("bootstrap", "protocol", "storage")) {
      // BUG291: the expected GAV remains; the extra GAV must not shadow its runtime classes.
      var shadow = new Fixture();
      String extra = "dev.codex.schubert:schubert-nk-" + shared + ":0.2.0";
      shadow.deps.put(extra, dependency(extra, List.of("api/lib/extra.jar")));
      shadow.files.put("api/lib/extra.jar", artifact("api/lib/extra.jar", "16", SHA));
      refused(shadow.text());
      var f = new Fixture();
      String c = "dev.codex.schubert:schubert-nk-" + shared + ":0.1.0";
      f.deps.remove(c);
      refused(f.text());
      refused(golden().replace("\"" + shared + "\":\"0.1.0\"", "\"" + shared + "\":\"0.2.0\""));
    }
    var f = new Fixture();
    String c = "dev.codex.schubert:schubert-nk-storage:0.1.0";
    f.deps.put(c, dependency(c, List.of("api/lib/storage.jar", "web/lib/storage.jar")));
    f.files.remove("operations/lib/storage.jar");
    refused(f.text());
    f = new Fixture();
    c = "dev.codex.schubert:schubert-nk-protocol:0.1.0";
    f.deps.put(
        c,
        dependency(
            c, List.of("api/lib/protocol.jar", "api/lib/zprotocol.jar", "web/lib/protocol.jar")));
    f.files.put("api/lib/zprotocol.jar", artifact("api/lib/zprotocol.jar", "16", SHA));
    refused(f.text());
    f = new Fixture();
    for (String version : List.of("0.1", "0.2")) {
      String path = "api/lib/external-" + version + ".jar";
      String gav = "org.example:external:" + version;
      f.files.put(path, artifact(path, "16", SHA));
      f.deps.put(gav, dependency(gav, List.of(path)));
    }
    refused(f.text());
  }

  @Test
  void bomProfile011SqlNamesRanksAndSchemaVersion() {
    var f = new Fixture();
    f.files.remove("db/migration/V001__first.sql");
    refused(f.text());
    f = new Fixture();
    f.files.put("db/migration/V002__extra.sql", artifact("db/migration/V002__extra.sql", "1", SHA));
    refused(f.text());
    refused(golden().replace("\"schema\":\"001\"", "\"schema\":\"002\""));
    refused(golden().replace(SQL, SQL.replace("\"installedRank\":1", "\"installedRank\":2")));
    refused(golden().replace(SQL, SQL.replace("\"success\":true", "\"success\":false")));
    refused(golden().replace(SQL, SQL.replace("\"checksum\":0", "\"checksum\":null")));
    refused(golden().replace(SCHEMA, SCHEMA.replace("\"version\":null", "\"version\":\"001\"")));
    var empty = new Fixture();
    empty.migrations.clear();
    refused(empty.text());
    var schemaOnly = new Fixture();
    schemaOnly.migrations.removeLast();
    refused(schemaOnly.text());
  }

  @Test
  void bomProfile012IntegerNullableAndColumnContracts() throws Exception {
    for (String value : List.of("-2147483649", "2147483648", "1.0", "\"1\""))
      refused(golden().replace("\"checksum\":0", "\"checksum\":" + value));
    for (String value : List.of("-2147483648", "2147483647"))
      assertEquals(
          Integer.parseInt(value),
          ReleaseInventory.parse(bytes(golden().replace("\"checksum\":0", "\"checksum\":" + value)))
              .migrations()
              .getLast()
              .checksum());
    refused(golden().replace("\"version\":null", "\"version\":1"));
    refused(golden().replace("\"checksum\":null", "\"checksum\":\"0\""));
    refused(golden().replace("\"installedRank\":0", "\"installedRank\":null"));
    refused(golden().replace("\"script\":\"V001__first.sql\"", "\"script\":null"));
  }

  @Test
  void bomProfile013DefensiveInputAndCollections() throws Exception {
    byte[] input = bytes(golden());
    byte[] saved = input.clone();
    var value = ReleaseInventory.parse(input);
    assertArrayEquals(saved, input);
    Arrays.fill(input, (byte) 0);
    for (Map<String, String> map :
        List.of(value.versions(), value.source(), value.build(), value.platform()))
      assertThrows(UnsupportedOperationException.class, map::clear);
    assertThrows(UnsupportedOperationException.class, () -> value.artifacts().clear());
    assertThrows(UnsupportedOperationException.class, () -> value.dependencies().clear());
    assertThrows(UnsupportedOperationException.class, () -> value.migrations().clear());
    assertEquals("1.2.3-PG313", value.release());
  }

  @Test
  void bomProfile014CollectionCapsAndExactPositiveBoundaries() throws Exception {
    for (int count : List.of(2048, 2049)) {
      var f = new Fixture();
      for (int i = f.files.size(); i < count; i++) {
        String path = "operations/runbooks/x" + String.format(Locale.ROOT, "%04d", i) + ".md";
        f.files.put(path, artifact(path, "0", SHA));
      }
      if (count == 2048)
        assertEquals(count, ReleaseInventory.parse(bytes(f.text())).artifacts().size());
      else refused(f.text());
    }
    for (int count : List.of(512, 513)) {
      var f = new Fixture();
      for (int i = f.deps.size(); i < count; i++) {
        String n = String.format(Locale.ROOT, "%04d", i);
        String path = "api/lib/x" + n + ".jar";
        String c = "z:x" + n + ":1";
        f.files.put(path, artifact(path, "16", SHA));
        f.deps.put(c, dependency(c, List.of(path)));
      }
      if (count == 512)
        assertEquals(count, ReleaseInventory.parse(bytes(f.text())).dependencies().size());
      else refused(f.text());
    }
    var f = new Fixture();
    for (int i = 2; i <= 999; i++) {
      String v = String.format(Locale.ROOT, "%03d", i);
      String script = "V" + v + "__m.sql";
      String path = "db/migration/" + script;
      f.files.put(path, artifact(path, "0", SHA));
      f.migrations.add(
          "{\"installedRank\":"
              + i
              + ",\"version\":\""
              + v
              + "\",\"type\":\"SQL\",\"script\":\""
              + script
              + "\",\"checksum\":0,\"success\":true}");
    }
    f.schema = "999";
    assertEquals(1000, ReleaseInventory.parse(bytes(f.text())).migrations().size());
    f.migrations.add(SQL);
    refused(f.text());
    f = new Fixture();
    String c = f.deps.firstKey();
    f.deps.put(
        c,
        dependency(c, List.of("api/lib/a.jar", "api/lib/b.jar", "api/lib/c.jar", "api/lib/d.jar")));
    refused(f.text());
  }

  @Test
  void bomProfile015AllMetadataScalarContracts() {
    for (String field :
        List.of("release", "app", "protocol", "storage", "bootstrap", "schema", "config"))
      refused(golden().replaceFirst("\"" + field + "\":\"[^\"]*\"", "\"" + field + "\":\"\""));
    refused(golden().replace(COMMIT, "b".repeat(39)));
    refused(golden().replace(COMMIT, "A".repeat(40)));
    for (String text : List.of("", "P".repeat(129), "é", "P\\nQ"))
      refused(golden().replace("PUBLIC VENDOR", text));
    refused(golden().replace("\"tag\":\"PG313\"", "\"tag\":null"));
    refused(golden().replace("\"paths\":[", "\"paths\":[null,"));
  }

  @Test
  void bomProfile016IndependentConcurrentParsers() throws Exception {
    var barrier = new CyclicBarrier(4);
    try (var pool = Executors.newFixedThreadPool(4)) {
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < 4; i++)
        futures.add(
            pool.submit(
                () -> {
                  barrier.await(5, TimeUnit.SECONDS);
                  return ReleaseInventory.parse(bytes(golden())).release();
                }));
      for (var future : futures) assertEquals("1.2.3-PG313", future.get(5, TimeUnit.SECONDS));
    }
  }
}
