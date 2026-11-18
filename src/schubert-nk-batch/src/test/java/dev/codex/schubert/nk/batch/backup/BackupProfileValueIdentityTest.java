package dev.codex.schubert.nk.batch.backup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-P01810-CATALOG-043-value-identity, BUG-3220. */
final class BackupProfileValueIdentityTest {
  private static final String HASH =
      "1111111111111111111111111111111111111111111111111111111111111111";
  private static final String AGE_TOOL = "ageSha256";

  @Test
  void independentlyConstructedPublicationClaimsAreStableMapKeys() {
    var release =
        new BackupVersions(
            "public-example", "1.2.3", "025", "linux", "25.0.4", "18.6", "2.56.0", "1.2.1");
    var claims =
        Map.of(
            "pgDumpWrapperSha256",
            HASH,
            "pgRestoreWrapperSha256",
            HASH,
            "pgDumpSha256",
            HASH,
            "pgRestoreSha256",
            HASH,
            "tarSha256",
            HASH,
            AGE_TOOL,
            HASH,
            "artemisArtifactSha256",
            HASH);
    var published = new BackupProfile(release, claims);
    var equalRelease =
        new BackupVersions(
            release.host(),
            release.app(),
            release.schema(),
            release.os(),
            release.jdk(),
            release.postgresql(),
            release.artemis(),
            release.age());
    var equal = new BackupProfile(equalRelease, new HashMap<>(claims));
    var result = new HashMap<BackupProfile, String>();
    var expectedResult = "public fixture lookup";
    result.put(published, expectedResult);

    assertEquals(published, equal);
    assertEquals(equal, published);
    assertEquals(expectedResult, result.get(equal));

    var otherRelease =
        new BackupVersions(
            release.host(),
            "1.2.4",
            release.schema(),
            release.os(),
            release.jdk(),
            release.postgresql(),
            release.artemis(),
            release.age());
    var otherClaims = new HashMap<>(claims);
    otherClaims.put(AGE_TOOL, "2".repeat(64));
    var differentVersion = new BackupProfile(otherRelease, claims);
    var differentHash = new BackupProfile(release, otherClaims);
    assertNotEquals(published, differentVersion);
    assertNotEquals(published, differentHash);
    assertFalse(result.containsKey(differentVersion));
    assertFalse(result.containsKey(differentHash));
  }
}
