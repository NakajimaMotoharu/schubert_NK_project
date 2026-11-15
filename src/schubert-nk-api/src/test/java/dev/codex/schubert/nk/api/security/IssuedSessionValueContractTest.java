package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.time.Instant;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-ISSUED-VALUE001/REASON-VALUE002; AUT001004; UI226; SS314331352/451. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class IssuedSessionValueContractTest {
  @Test
  void issued001ValueIdentityMapLookupRedactionAndEveryConstructorBoundary() {
    var identity =
        new AuthContextIdentity(UUID.fromString("d1000000-0000-0000-0000-000000000001"), 7);
    var sameIdentity =
        new AuthContextIdentity(UUID.fromString("d1000000-0000-0000-0000-000000000001"), 7);
    var otherIdentity =
        new AuthContextIdentity(UUID.fromString("d1000000-0000-0000-0000-000000000002"), 7);
    var context = AuthenticationContext.of("a".repeat(64));
    var sameContext = AuthenticationContext.of("a".repeat(64));
    var otherContext = AuthenticationContext.of("b".repeat(64));
    var issued = Instant.parse("2026-01-02T03:04:05Z");
    var expiry = Instant.parse("2026-01-02T11:04:05Z");
    var value = new IssuedContext(identity, context, issued, expiry);
    var sameValue = new IssuedContext(sameIdentity, sameContext, issued, expiry);
    assertNotSame(value, sameValue);
    assertTrue(value.equals(value));
    assertTrue(value.equals(sameValue));
    assertTrue(sameValue.equals(value));
    assertFalse(value.equals(null));
    assertFalse(value.equals("issued"));
    assertSame(identity, value.identity());
    assertSame(context, value.context());
    assertEquals(issued, value.issuedAt());
    assertEquals(expiry, value.expiresAt());
    assertEquals("IssuedContext[REDACTED]", value.toString());
    var values = new HashMap<IssuedContext, String>();
    values.put(value, "owner");
    assertEquals("owner", values.get(sameValue));
    for (IssuedContext different :
        List.of(
            new IssuedContext(otherIdentity, context, issued, expiry),
            new IssuedContext(identity, otherContext, issued, expiry),
            new IssuedContext(identity, context, issued.minusNanos(1), expiry),
            new IssuedContext(identity, context, issued, expiry.plusNanos(1)))) {
      assertFalse(value.equals(different));
      assertFalse(different.equals(value));
      assertNull(values.get(different));
    }
    assertEquals(1, values.size());
    assertThrows(
        NullPointerException.class, () -> new IssuedContext(null, context, issued, expiry));
    assertThrows(
        NullPointerException.class, () -> new IssuedContext(identity, null, issued, expiry));
    assertThrows(
        NullPointerException.class, () -> new IssuedContext(identity, context, null, expiry));
    assertThrows(
        NullPointerException.class, () -> new IssuedContext(identity, context, issued, null));
    assertThrows(
        IllegalArgumentException.class, () -> new IssuedContext(identity, context, issued, issued));
    assertThrows(
        IllegalArgumentException.class,
        () -> new IssuedContext(identity, context, issued, issued.minusNanos(1)));
    assertEquals(
        issued.plusNanos(1),
        new IssuedContext(identity, context, issued, issued.plusNanos(1)).expiresAt());
  }

  @Test
  void reason002ClosedVocabularyLookupOrderAndDefensiveValues() {
    assertEquals(
        List.of("LOGOUT", "DISABLED", "PASSWORD_RESET", "ADMIN", "EXPIRED", "REPLACED"),
        Arrays.stream(SessionRevocationReason.values()).map(Enum::name).toList());
    assertSame(SessionRevocationReason.LOGOUT, SessionRevocationReason.valueOf("LOGOUT"));
    assertSame(SessionRevocationReason.DISABLED, SessionRevocationReason.valueOf("DISABLED"));
    assertSame(
        SessionRevocationReason.PASSWORD_RESET, SessionRevocationReason.valueOf("PASSWORD_RESET"));
    assertSame(SessionRevocationReason.ADMIN, SessionRevocationReason.valueOf("ADMIN"));
    assertSame(SessionRevocationReason.EXPIRED, SessionRevocationReason.valueOf("EXPIRED"));
    assertSame(SessionRevocationReason.REPLACED, SessionRevocationReason.valueOf("REPLACED"));
    var exposed = SessionRevocationReason.values();
    exposed[0] = SessionRevocationReason.ADMIN;
    assertSame(SessionRevocationReason.LOGOUT, SessionRevocationReason.values()[0]);
    for (String unknown : List.of("UNKNOWN", "", "logout", " LOGOUT "))
      assertThrows(IllegalArgumentException.class, () -> SessionRevocationReason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> SessionRevocationReason.valueOf(null));
  }
}
