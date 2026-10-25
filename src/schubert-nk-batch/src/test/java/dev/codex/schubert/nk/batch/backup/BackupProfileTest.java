package dev.codex.schubert.nk.batch.backup;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** BPROFILE001..004: literal JSON, not an expected value generated with encode(). SS343/SSC110. */
final class BackupProfileTest {
  private static final String HASH =
      "1111111111111111111111111111111111111111111111111111111111111111";
  private static final String GOLDEN =
      """
      {"profile":"NKBACKUPPROFILE1","host":"pgpt-host","app":"0.1.0-PG381","schema":"023","os":"ubuntu-26.04","jdk":"25.0.4+6","postgresql":"18.6","artemis":"2.56.0","age":"1.2.1","pgDumpWrapperSha256":"1111111111111111111111111111111111111111111111111111111111111111","pgRestoreWrapperSha256":"1111111111111111111111111111111111111111111111111111111111111111","pgDumpSha256":"1111111111111111111111111111111111111111111111111111111111111111","pgRestoreSha256":"1111111111111111111111111111111111111111111111111111111111111111","tarSha256":"1111111111111111111111111111111111111111111111111111111111111111","ageSha256":"1111111111111111111111111111111111111111111111111111111111111111","artemisArtifactSha256":"1111111111111111111111111111111111111111111111111111111111111111"}
      """;

  @Test
  void positiveDelByteIsRejectedAndOwnedInputIsWiped() {
    // PT-BAT-PROFILE1405003 / SS343: ASCII DEL 0x7f is outside printable 0x20..0x7e.
    byte[] owned = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    owned[0] = 0x7f;
    assertThrows(IllegalArgumentException.class, () -> BackupProfile.consume(owned));
    assertArrayEquals(new byte[owned.length], owned);
  }

  @Test
  void literalGoldenAndImmutableNonsecretClaims() {
    byte[] owned = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    var actual = BackupProfile.consume(owned);
    assertArrayEquals(new byte[owned.length], owned);
    assertEquals(
        new BackupVersions(
            "pgpt-host",
            "0.1.0-PG381",
            "023",
            "ubuntu-26.04",
            "25.0.4+6",
            "18.6",
            "2.56.0",
            "1.2.1"),
        actual.versions());
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), actual.encode());
    assertEquals(7, actual.toolHashes().size());
    assertTrue(actual.toolHashes().values().stream().allMatch(HASH::equals));
    assertThrows(UnsupportedOperationException.class, () -> actual.toolHashes().clear());
    var copy = new HashMap<>(actual.toolHashes());
    var profile = new BackupProfile(actual.versions(), copy);
    copy.clear();
    assertEquals(7, profile.toolHashes().size());
    assertEquals("BackupProfile[claims=<redacted>]", profile.toString());
    assertEquals(4096, BackupProfile.MAXIMUM_BYTES);
  }

  @Test
  void strictByteAndCanonicalNegativeMatrixWipesEveryInput() {
    for (String bad :
        List.of(
            "",
            "{}\n",
            GOLDEN.stripTrailing(),
            GOLDEN + "\n",
            GOLDEN.replace("\n", "\r\n"),
            GOLDEN.replace("NKBACKUPPROFILE1", "NKBACKUPPROFILE2"),
            GOLDEN.replace("\"schema\":\"023\"", "\"schema\":\"000\""),
            GOLDEN.replace("\"host\":\"pgpt-host\"", "\"host\":\"\""),
            GOLDEN.replace("\"host\":", "\"unknown\":"),
            GOLDEN.replace("{", "{ "),
            GOLDEN.replace("pgpt-host", "pgpt/host"),
            GOLDEN.replace("pgpt-host", "pgpt\\u002dhost"),
            GOLDEN.replace("pgDumpSha256", "tarSha256"),
            GOLDEN.replace(HASH, "A".repeat(64)),
            GOLDEN.replace(HASH, "1".repeat(63)),
            "x".repeat(4097),
            GOLDEN + "\u0000",
            GOLDEN + "日本")) {
      byte[] owned = bad.getBytes(StandardCharsets.UTF_8);
      assertThrows(
          IllegalArgumentException.class,
          () -> BackupProfile.consume(owned),
          bad.substring(0, Math.min(20, bad.length())));
      assertArrayEquals(new byte[owned.length], owned);
    }
    assertThrows(NullPointerException.class, () -> BackupProfile.consume(null));
  }

  @Test
  void constructorRejectsMissingUnknownNullAndMalformedHashes() {
    var valid = BackupProfile.consume(GOLDEN.getBytes(StandardCharsets.US_ASCII));
    assertThrows(NullPointerException.class, () -> new BackupProfile(null, valid.toolHashes()));
    assertThrows(NullPointerException.class, () -> new BackupProfile(valid.versions(), null));
    assertThrows(
        IllegalArgumentException.class, () -> new BackupProfile(valid.versions(), Map.of()));
    for (String bad : List.of("", "g".repeat(64), "1".repeat(63))) {
      var hashes = new HashMap<>(valid.toolHashes());
      hashes.put("tarSha256", bad);
      assertThrows(
          IllegalArgumentException.class, () -> new BackupProfile(valid.versions(), hashes));
    }
    var unknownHash = new HashMap<>(valid.toolHashes());
    unknownHash.put("unknown", HASH);
    assertThrows(
        IllegalArgumentException.class, () -> new BackupProfile(valid.versions(), unknownHash));
    var nullHash = new HashMap<>(valid.toolHashes());
    nullHash.put("tarSha256", null);
    assertThrows(NullPointerException.class, () -> new BackupProfile(valid.versions(), nullHash));
  }
}
