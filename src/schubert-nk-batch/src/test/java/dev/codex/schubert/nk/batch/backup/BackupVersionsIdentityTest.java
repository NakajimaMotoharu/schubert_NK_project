package dev.codex.schubert.nk.batch.backup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-P01810-CATALOG-044A/B; SS341 section 6.4 and SS351 section 3. */
final class BackupVersionsIdentityTest {
  private static final List<String> CLAIMS =
      List.of("Host1", "App2", "001", "Os3", "Jdk4", "Pg5", "Mq6", "Age7");

  @Test
  void everyIndividualClaimParticipatesInValueIdentity() {
    String[] claims = CLAIMS.toArray(String[]::new);
    var base = versions(claims);
    var byVersion = new HashMap<>(Map.of(base, "synthetic value"));
    assertEquals("synthetic value", byVersion.get(versions(claims)));
    for (int index = 0; index < claims.length; index++) {
      String[] different = claims.clone();
      different[index] = index == 2 ? "999" : "R2.dev+1_fix";
      var changed = versions(different);
      String claim = "claim index " + index;
      assertNotEquals(base, changed, claim);
      assertNotEquals(changed, base, claim);
      assertNull(byVersion.get(changed), claim);
    }
  }

  @Test
  void unrelatedIdentityDoesNotAppearInFixedDiagnostic() {
    var base = versions(CLAIMS.toArray(String[]::new));
    assertNotEquals(base, CLAIMS);
    assertNotEquals(base, null);
    assertEquals("BackupVersions[release=<redacted>]", base.toString());
  }

  @Test
  void exposesEveryIndependentClaimAtItsComponent() {
    var value = versions(CLAIMS.toArray(String[]::new));
    assertEquals(
        CLAIMS,
        List.of(
            value.host(),
            value.app(),
            value.schema(),
            value.os(),
            value.jdk(),
            value.postgresql(),
            value.artemis(),
            value.age()));
    String[] longest = CLAIMS.toArray(String[]::new);
    longest[0] = "x".repeat(128);
    assertEquals(longest[0], versions(longest).host());
  }

  @Test
  void rejectsInvalidReleaseTokensAndSchemasBeforeUse() {
    String[] tooLong = CLAIMS.toArray(String[]::new);
    tooLong[0] = "x".repeat(129);
    assertEquals(
        "invalid backup release token",
        assertThrows(IllegalArgumentException.class, () -> versions(tooLong)).getMessage());
    for (String badSchema : List.of("000", "A01")) {
      String[] invalid = CLAIMS.toArray(String[]::new);
      invalid[2] = badSchema;
      assertEquals(
          "invalid backup schema",
          assertThrows(IllegalArgumentException.class, () -> versions(invalid)).getMessage());
    }
    String[] valid = CLAIMS.toArray(String[]::new);
    for (int index = 0; index < valid.length; index++) {
      String[] missing = new String[valid.length];
      System.arraycopy(valid, 0, missing, 0, index);
      int after = index + 1;
      System.arraycopy(valid, after, missing, after, valid.length - after);
      assertThrows(NullPointerException.class, () -> versions(missing), "claim index " + index);
    }
  }

  private static BackupVersions versions(String[] claims) {
    return new BackupVersions(
        claims[0], claims[1], claims[2], claims[3], claims[4], claims[5], claims[6], claims[7]);
  }
}
