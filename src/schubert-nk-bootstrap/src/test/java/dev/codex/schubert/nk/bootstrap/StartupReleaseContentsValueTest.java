package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;
import org.junit.jupiter.api.Test;

/**
 * NK-OPS-001/SYS002004/OPS009/UI251/SS342343/3678; PT-OPS-RELEASE-CONTENTS001..008. Public value
 * metadata only; never calls an outer release reader or grants startup authority.
 */
final class StartupReleaseContentsValueTest {
  private static final String KEY_COMMIT = "commit";
  private static final String PUBLIC_VALUE = "public";
  private static final String PLATFORM_LINUX = "linux";
  private static final String VERSION = "PG2802";
  private static final String DIGEST = "0".repeat(64);
  private static final SchemaHistoryAdmission.Row SCHEMA =
      new SchemaHistoryAdmission.Row(0, null, "SCHEMA", "\"schubert_meta\"", null, true);
  private static final SchemaHistoryAdmission.Row MIGRATION =
      new SchemaHistoryAdmission.Row(1, "001", "SQL", "V001__fixture.sql", 42, true);

  @Test
  void contents001FiveArgumentDefaultsKeepIndependentLiteralMetadata() {
    var value =
        new StartupReleaseManifest.Contents(
            VERSION,
            DIGEST,
            List.of(SCHEMA),
            Map.of(KEY_COMMIT, PUBLIC_VALUE),
            Map.of("os", PLATFORM_LINUX));
    assertEquals("PG2802", value.version());
    assertEquals("0".repeat(64), value.sha256());
    assertEquals(List.of(SCHEMA), value.migrations());
    assertEquals(Map.of(KEY_COMMIT, PUBLIC_VALUE), value.build());
    assertEquals(Map.of("os", PLATFORM_LINUX), value.platform());
    assertEquals(Map.of(), value.versions());
    assertEquals(Map.of(), value.artifactHashes());
  }

  @Test
  void contents002SevenArgumentCopiesDetachAllOriginalCollections() {
    var rows = new ArrayList<>(List.of(SCHEMA, MIGRATION));
    var build = new LinkedHashMap<>(Map.of(KEY_COMMIT, PUBLIC_VALUE));
    var platform = new LinkedHashMap<>(Map.of("os", PLATFORM_LINUX));
    var versions = new LinkedHashMap<>(Map.of("java", "25"));
    var artifacts = new LinkedHashMap<>(Map.of("app.jar", DIGEST));
    var value =
        new StartupReleaseManifest.Contents(
            VERSION, DIGEST, rows, build, platform, versions, artifacts);
    rows.clear();
    build.clear();
    platform.clear();
    versions.clear();
    artifacts.clear();
    assertEquals(List.of(SCHEMA, MIGRATION), value.migrations());
    assertEquals(Map.of(KEY_COMMIT, PUBLIC_VALUE), value.build());
    assertEquals(Map.of("os", PLATFORM_LINUX), value.platform());
    assertEquals(Map.of("java", "25"), value.versions());
    assertEquals(Map.of("app.jar", DIGEST), value.artifactHashes());
  }

  @Test
  void contents003BothConstructorScalarNullContractsReject() {
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents(null, DIGEST, List.of(), Map.of(), Map.of()));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents(VERSION, null, List.of(), Map.of(), Map.of()));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupReleaseManifest.Contents(
                null, DIGEST, List.of(), Map.of(), Map.of(), Map.of(), Map.of()));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupReleaseManifest.Contents(
                VERSION, null, List.of(), Map.of(), Map.of(), Map.of(), Map.of()));
  }

  @Test
  void contents004EveryMissingCollectionRejectsBeforePublication() {
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupReleaseManifest.Contents(
                VERSION, DIGEST, null, Map.of(), Map.of(), Map.of(), Map.of()));
    for (var factory : mapFactories())
      assertThrows(NullPointerException.class, () -> factory.apply(null));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents(VERSION, DIGEST, null, Map.of(), Map.of()));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents(VERSION, DIGEST, List.of(), null, Map.of()));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents(VERSION, DIGEST, List.of(), Map.of(), null));
  }

  @Test
  void contents005NullElementsKeysAndValuesCannotEnterSnapshot() {
    var rows = new ArrayList<SchemaHistoryAdmission.Row>();
    rows.add(null);
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents(VERSION, DIGEST, rows, Map.of(), Map.of()));
    for (var factory : mapFactories()) {
      Map<String, String> missingKey = new HashMap<>();
      missingKey.put(null, PUBLIC_VALUE);
      Map<String, String> missingValue = new HashMap<>();
      missingValue.put(PUBLIC_VALUE, null);
      assertThrows(NullPointerException.class, () -> factory.apply(missingKey));
      assertThrows(NullPointerException.class, () -> factory.apply(missingValue));
    }
  }

  @Test
  void contents006EveryReturnedCollectionIsImmutable() {
    var value =
        new StartupReleaseManifest.Contents(
            VERSION,
            DIGEST,
            List.of(SCHEMA),
            Map.of(KEY_COMMIT, PUBLIC_VALUE),
            Map.of("os", PLATFORM_LINUX),
            Map.of("java", "25"),
            Map.of("app.jar", DIGEST));
    assertThrows(UnsupportedOperationException.class, () -> value.migrations().add(MIGRATION));
    assertThrows(
        UnsupportedOperationException.class, () -> value.build().put("other", PUBLIC_VALUE));
    assertThrows(
        UnsupportedOperationException.class, () -> value.platform().put("other", PUBLIC_VALUE));
    assertThrows(
        UnsupportedOperationException.class, () -> value.versions().put("other", PUBLIC_VALUE));
    assertThrows(
        UnsupportedOperationException.class, () -> value.artifactHashes().put("other.jar", DIGEST));
    assertEquals(List.of(SCHEMA), value.migrations());
    assertEquals(Map.of(KEY_COMMIT, PUBLIC_VALUE), value.build());
  }

  @Test
  void contents007MigrationOrderAndEmptyBoundariesRemainCapturedValues() {
    var rows = new ArrayList<>(List.of(SCHEMA, MIGRATION));
    var value =
        new StartupReleaseManifest.Contents(
            VERSION, DIGEST, rows, Map.of(), Map.of(), Map.of(), Map.of());
    rows.set(0, MIGRATION);
    rows.removeLast();
    assertEquals(List.of(SCHEMA, MIGRATION), value.migrations());
    assertEquals(0, value.migrations().getFirst().installedRank());
    assertEquals(1, value.migrations().getLast().installedRank());
    var empty =
        new StartupReleaseManifest.Contents(
            VERSION, DIGEST, List.of(), Map.of(), Map.of(), Map.of(), Map.of());
    assertEquals(List.of(), empty.migrations());
    assertEquals(Map.of(), empty.build());
    assertEquals(Map.of(), empty.platform());
    assertEquals(Map.of(), empty.versions());
    assertEquals(Map.of(), empty.artifactHashes());
  }

  @Test
  void contents008ConcurrentCopiesKeepOnlyEachWorkersOriginalMap() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<String>>();
      for (int index = 0; index < 32; index++) {
        String expected = "public-" + index;
        jobs.add(
            workers.submit(
                () -> {
                  var original = new LinkedHashMap<>(Map.of(KEY_COMMIT, expected));
                  var value =
                      new StartupReleaseManifest.Contents(
                          VERSION, DIGEST, List.of(SCHEMA, MIGRATION), original, Map.of());
                  original.put(KEY_COMMIT, "changed");
                  assertEquals(Map.of(KEY_COMMIT, expected), value.build());
                  assertEquals(List.of(SCHEMA, MIGRATION), value.migrations());
                  return value.build().get(KEY_COMMIT);
                }));
      }
      for (int index = 0; index < jobs.size(); index++)
        assertEquals("public-" + index, jobs.get(index).get(5, TimeUnit.SECONDS));
    }
  }

  private static List<Function<Map<String, String>, StartupReleaseManifest.Contents>>
      mapFactories() {
    return List.of(
        map ->
            new StartupReleaseManifest.Contents(
                VERSION, DIGEST, List.of(), map, Map.of(), Map.of(), Map.of()),
        map ->
            new StartupReleaseManifest.Contents(
                VERSION, DIGEST, List.of(), Map.of(), map, Map.of(), Map.of()),
        map ->
            new StartupReleaseManifest.Contents(
                VERSION, DIGEST, List.of(), Map.of(), Map.of(), map, Map.of()),
        map ->
            new StartupReleaseManifest.Contents(
                VERSION, DIGEST, List.of(), Map.of(), Map.of(), Map.of(), map));
  }
}
