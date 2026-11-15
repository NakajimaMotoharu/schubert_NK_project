package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-REVOKED-VALUE001; AUT004; UI234; SS314332352/451; no actual Logout request. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class RevokedContextValueContractTest {
  @Test
  void revoked001ValueMapRedactionAndOnlyTwoAllowedResultsAtAllNullBoundaries() {
    var id = UUID.fromString("e1000000-0000-0000-0000-000000000001");
    var identity = new AuthContextIdentity(id, 7);
    var equalIdentity = new AuthContextIdentity(id, 7);
    var otherIdentity = new AuthContextIdentity(id, 8);
    var at = Instant.parse("2026-01-02T03:04:05Z");
    var value = new RevokedContext(identity, at, ResultCode.SUCCESS);
    var equal = new RevokedContext(equalIdentity, at, ResultCode.SUCCESS);
    assertNotSame(value, equal);
    assertTrue(value.equals(value));
    assertTrue(value.equals(equal));
    assertTrue(equal.equals(value));
    assertFalse(value.equals(null));
    assertFalse(value.equals("revoked"));
    assertEquals(identity, value.identity());
    assertEquals(at, value.revokedAt());
    assertEquals(ResultCode.SUCCESS, value.resultCode());
    assertEquals("RevokedContext[REDACTED]", value.toString());
    var results = new HashMap<RevokedContext, String>();
    results.put(value, "revoked-owner");
    assertEquals("revoked-owner", results.get(equal));
    for (var different :
        List.of(
            new RevokedContext(otherIdentity, at, ResultCode.SUCCESS),
            new RevokedContext(identity, at.plusNanos(1), ResultCode.SUCCESS),
            new RevokedContext(identity, at, ResultCode.IDEMPOTENT_SUCCESS))) {
      assertFalse(value.equals(different));
      assertFalse(different.equals(value));
      assertNull(results.get(different));
    }
    assertEquals(1, results.size());
    assertThrows(
        NullPointerException.class, () -> new RevokedContext(null, at, ResultCode.SUCCESS));
    assertThrows(
        NullPointerException.class, () -> new RevokedContext(identity, null, ResultCode.SUCCESS));
    assertThrows(NullPointerException.class, () -> new RevokedContext(identity, at, null));
    for (ResultCode rejected : ResultCode.values()) {
      if (rejected != ResultCode.SUCCESS && rejected != ResultCode.IDEMPOTENT_SUCCESS)
        assertThrows(
            IllegalArgumentException.class, () -> new RevokedContext(identity, at, rejected));
    }
    assertEquals(
        ResultCode.IDEMPOTENT_SUCCESS,
        new RevokedContext(identity, at, ResultCode.IDEMPOTENT_SUCCESS).resultCode());
  }
}
