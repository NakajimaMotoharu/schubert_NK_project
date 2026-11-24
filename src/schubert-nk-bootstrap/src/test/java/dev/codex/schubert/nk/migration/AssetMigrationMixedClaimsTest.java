package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.migration.AssetMigrationManifest.Entry;
import dev.codex.schubert.nk.migration.AssetMigrationManifest.Kind;
import dev.codex.schubert.nk.migration.AssetMigrationManifest.Observation;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-MIG-ASSET-MIXED001 / SS343 SSC342: pure declarations with no storage access. */
final class AssetMigrationMixedClaimsTest {
  private static final String ABC =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String EMPTY =
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

  @Test
  void countsDifferentClaimsIndependentlyAndRetainsTheManifestForTheNextComparison() {
    var manifest =
        new AssetMigrationManifest(
            List.of(
                new Entry(Kind.SCENARIO, "old/a", "new/a", 3, ABC),
                new Entry(Kind.SCENARIO, "old/b", "new/b", 0, EMPTY),
                new Entry(Kind.AUDIO, "old/c", "new/c", 3, ABC),
                new Entry(Kind.VIDEO, "old/d", "new/d", 0, EMPTY),
                new Entry(Kind.MUSIC, "old/e", "new/e", 0, EMPTY)));
    var observed =
        List.of(
            new Observation("new/g", 2, EMPTY),
            new Observation("new/e", 0, EMPTY),
            new Observation("new/c", 3, EMPTY),
            new Observation("new/b", 1, EMPTY),
            new Observation("new/f", 5, ABC),
            new Observation("new/a", 4, EMPTY));
    var actual = manifest.compareClaims(observed);
    assertEquals(1, actual.missingFiles());
    assertEquals(2, actual.unexpectedFiles());
    assertEquals(2, actual.sizeMismatches());
    assertEquals(2, actual.hashMismatches());
    assertEquals(6, actual.observedFiles());
    assertEquals(15, actual.observedBytes());
    assertFalse(actual.metadataMatches());
    assertEquals(actual, manifest.compareClaims(observed.reversed()));

    var exact =
        manifest.compareClaims(
            List.of(
                new Observation("new/d", 0, EMPTY),
                new Observation("new/a", 3, ABC),
                new Observation("new/e", 0, EMPTY),
                new Observation("new/b", 0, EMPTY),
                new Observation("new/c", 3, ABC)));
    assertTrue(exact.metadataMatches());
    assertEquals(5, exact.observedFiles());
    assertEquals(6, exact.observedBytes());
    assertEquals(5, manifest.entries().size());
    assertEquals(6, manifest.totalBytes());
  }
}
