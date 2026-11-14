package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.migration.AssetMigrationManifest.Comparison;
import dev.codex.schubert.nk.migration.AssetMigrationManifest.Entry;
import dev.codex.schubert.nk.migration.AssetMigrationManifest.Kind;
import dev.codex.schubert.nk.migration.AssetMigrationManifest.Observation;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-MIG-ASSET001..012, SS343 SSC342: only synthetic metadata, no file/DB/authority. */
final class AssetMigrationManifestTest {
  private static final String ABC =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String EMPTY =
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
  private static final String SOURCE = "input/a.txt";
  private static final String TARGET = "assets/a.txt";
  private static final String OTHER = "assets/b.bin";
  private static final String GOLDEN =
      """
      NKMIGASSET1
      SCENARIO\tinput/a.txt\tassets/a.txt\t3\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
      AUDIO\tinput/b.bin\tassets/b.bin\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      """;

  private static Entry first() {
    return new Entry(Kind.SCENARIO, SOURCE, TARGET, 3, ABC);
  }

  private static Entry second() {
    return new Entry(Kind.AUDIO, "input/b.bin", OTHER, 0, EMPTY);
  }

  private static AssetMigrationManifest manifest() {
    return new AssetMigrationManifest(List.of(second(), first()));
  }

  private static void invalid(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(IllegalArgumentException.class, action);
    assertEquals("migration asset metadata is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void comparison(
      Comparison actual,
      long missing,
      long unexpected,
      long size,
      long hash,
      long files,
      long bytes,
      boolean matches) {
    assertEquals(missing, actual.missingFiles());
    assertEquals(unexpected, actual.unexpectedFiles());
    assertEquals(size, actual.sizeMismatches());
    assertEquals(hash, actual.hashMismatches());
    assertEquals(files, actual.observedFiles());
    assertEquals(bytes, actual.observedBytes());
    assertEquals(matches, actual.metadataMatches());
  }

  @Test
  void asset001CanonicalGolden() {
    var value = manifest();
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), value.canonicalBytes());
    assertEquals(List.of(first(), second()), value.entries());
    assertEquals(3, value.totalBytes());
    assertEquals("AssetMigrationManifest[REDACTED]", value.toString());
    assertEquals("MigrationAssetEntry[REDACTED]", first().toString());
  }

  @Test
  void asset002ValidPathsAndKinds() {
    assertEquals(
        List.of(Kind.SCENARIO, Kind.AUDIO, Kind.VIDEO, Kind.MUSIC), List.of(Kind.values()));
    for (var kind : Kind.values())
      for (String path : List.of("a", "é/名前.txt", "\ud7ff/\ue000/😀", "a:b/with space")) {
        var entry = new Entry(kind, path, path, Long.MAX_VALUE, EMPTY);
        var value = new AssetMigrationManifest(List.of(entry));
        assertEquals(Long.MAX_VALUE, value.totalBytes());
        assertEquals(kind, entry.kind());
        assertEquals(path, entry.currentPath());
        assertEquals(path, entry.targetPath());
      }
    var empty = new AssetMigrationManifest(List.of());
    assertEquals(0, empty.totalBytes());
    assertArrayEquals("NKMIGASSET1\n".getBytes(StandardCharsets.UTF_8), empty.canonicalBytes());
    comparison(empty.compareClaims(List.of()), 0, 0, 0, 0, 0, 0, true);
  }

  @Test
  void asset003InvalidPaths() {
    var paths =
        new ArrayList<>(
            List.of(
                "", "/a", "a\\b", "a//b", "a/", ".", "..", "a/./b", "a/../b", "e\u0301", "x\ud800",
                "x\udfff"));
    for (int point : List.of(0, 9, 10, 13, 31, 127, 128, 159))
      paths.add("a" + Character.toString(point));
    for (String path : paths) {
      invalid(() -> new Entry(Kind.AUDIO, path, TARGET, 0, EMPTY));
      invalid(() -> new Entry(Kind.AUDIO, SOURCE, path, 0, EMPTY));
      invalid(() -> new Observation(path, 0, EMPTY));
    }
  }

  @Test
  void asset004NullContracts() {
    assertThrows(NullPointerException.class, () -> new AssetMigrationManifest(null));
    assertThrows(
        NullPointerException.class, () -> new AssetMigrationManifest(Arrays.asList(first(), null)));
    assertThrows(NullPointerException.class, () -> new Entry(null, SOURCE, TARGET, 0, EMPTY));
    assertThrows(NullPointerException.class, () -> new Entry(Kind.AUDIO, null, TARGET, 0, EMPTY));
    assertThrows(NullPointerException.class, () -> new Entry(Kind.AUDIO, SOURCE, null, 0, EMPTY));
    assertThrows(NullPointerException.class, () -> new Entry(Kind.AUDIO, SOURCE, TARGET, 0, null));
    assertThrows(NullPointerException.class, () -> new Observation(null, 0, EMPTY));
    assertThrows(NullPointerException.class, () -> new Observation(TARGET, 0, null));
    assertThrows(NullPointerException.class, () -> manifest().compareClaims(null));
    assertThrows(
        NullPointerException.class,
        () -> manifest().compareClaims(Arrays.asList((Observation) null)));
  }

  @Test
  void asset005InvalidSizesAndHashes() {
    invalid(() -> new Entry(Kind.AUDIO, SOURCE, TARGET, -1, EMPTY));
    invalid(() -> new Observation(TARGET, -1, EMPTY));
    for (String hash :
        List.of("", "a".repeat(63), "a".repeat(65), "A".repeat(64), "g".repeat(64))) {
      invalid(() -> new Entry(Kind.AUDIO, SOURCE, TARGET, 0, hash));
      invalid(() -> new Observation(TARGET, 0, hash));
    }
    assertEquals("0".repeat(64), new Entry(Kind.MUSIC, SOURCE, TARGET, 0, "0".repeat(64)).sha256());
  }

  @Test
  void asset006DuplicatePaths() {
    var original = new ArrayList<>(List.of(first(), first()));
    invalid(() -> new AssetMigrationManifest(original));
    assertEquals(List.of(first(), first()), original);
    invalid(
        () ->
            new AssetMigrationManifest(
                List.of(first(), new Entry(Kind.AUDIO, "different", TARGET, 0, EMPTY))));
    invalid(
        () ->
            manifest()
                .compareClaims(
                    List.of(new Observation(TARGET, 0, EMPTY), new Observation(TARGET, 3, ABC))));
  }

  @Test
  void asset007CheckedAggregateOverflow() {
    var huge = new Entry(Kind.AUDIO, SOURCE, TARGET, Long.MAX_VALUE, ABC);
    var one = new Entry(Kind.MUSIC, "other", OTHER, 1, EMPTY);
    invalid(() -> new AssetMigrationManifest(List.of(huge, one)));
    var maximum = new AssetMigrationManifest(List.of(huge, second()));
    assertEquals(Long.MAX_VALUE, maximum.totalBytes());
    invalid(
        () ->
            maximum.compareClaims(
                List.of(
                    new Observation(TARGET, Long.MAX_VALUE, ABC),
                    new Observation(OTHER, 1, EMPTY))));
    comparison(
        maximum.compareClaims(
            List.of(
                new Observation(TARGET, Long.MAX_VALUE, ABC), new Observation(OTHER, 0, EMPTY))),
        0,
        0,
        0,
        0,
        2,
        Long.MAX_VALUE,
        true);
  }

  @Test
  void asset008ImmutableOwnership() {
    var input = new ArrayList<>(List.of(second(), first()));
    var value = new AssetMigrationManifest(input);
    input.clear();
    assertEquals(2, value.entries().size());
    assertThrows(UnsupportedOperationException.class, () -> value.entries().clear());
    byte[] bytes = value.canonicalBytes();
    Arrays.fill(bytes, (byte) 0);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), value.canonicalBytes());
  }

  @Test
  void asset009IdenticalClaims() {
    var observations =
        new ArrayList<>(List.of(new Observation(OTHER, 0, EMPTY), new Observation(TARGET, 3, ABC)));
    var result = manifest().compareClaims(observations);
    comparison(result, 0, 0, 0, 0, 2, 3, true);
    observations.clear();
    comparison(result, 0, 0, 0, 0, 2, 3, true);
    assertEquals("MigrationAssetObservation[REDACTED]", new Observation(TARGET, 3, ABC).toString());
    for (int field = 0; field < 6; field++) {
      long[] counts = new long[6];
      counts[field] = -1;
      invalid(
          () -> new Comparison(counts[0], counts[1], counts[2], counts[3], counts[4], counts[5]));
    }
  }

  @Test
  void asset010MissingClaim() {
    comparison(
        manifest().compareClaims(List.of(new Observation(OTHER, 0, EMPTY))),
        1,
        0,
        0,
        0,
        1,
        0,
        false);
  }

  @Test
  void asset011UnexpectedClaim() {
    comparison(
        manifest()
            .compareClaims(
                List.of(
                    new Observation(TARGET, 3, ABC),
                    new Observation(OTHER, 0, EMPTY),
                    new Observation("unexpected", 1, ABC))),
        0,
        1,
        0,
        0,
        3,
        4,
        false);
  }

  @Test
  void asset012IndependentSizeAndHashDifferences() {
    var value = new AssetMigrationManifest(List.of(first()));
    comparison(
        value.compareClaims(List.of(new Observation(TARGET, 4, ABC))), 0, 0, 1, 0, 1, 4, false);
    comparison(
        value.compareClaims(List.of(new Observation(TARGET, 3, EMPTY))), 0, 0, 0, 1, 1, 3, false);
    comparison(
        value.compareClaims(List.of(new Observation(TARGET, 4, EMPTY))), 0, 0, 1, 1, 1, 4, false);
  }
}
