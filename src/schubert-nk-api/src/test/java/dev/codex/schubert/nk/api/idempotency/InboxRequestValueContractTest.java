package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-IDEM-REQUESTVALUE001002; MQ006..010/DAT009/UI241242/SS3244..6; no DB/auth grant. */
final class InboxRequestValueContractTest {
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID CORRELATION = new UUID(0, 2);
  private static final UUID TOKEN = new UUID(0, 3);
  private static final Instant RECEIVED = Instant.parse("2026-01-01T00:00:00Z");
  private static final Instant EXPIRES = Instant.parse("2026-01-02T00:00:00Z");
  private static final OptionalLong OWNER = OptionalLong.of(7);
  private static final String READ = "QSTREQ01";
  private static final String SUBMIT = "QSBREQ01";
  private static final String READ_TARGET = "read";
  private static final String UPDATE_TARGET = "update";

  @Test
  void requestValue001SevenNullContractsOwnerScopeTokenAndStrictExpiry() {
    try (CanonicalRequest read = canonical("7", READ, READ_TARGET);
        CanonicalRequest login = canonical("ANONYMOUS", "LGNREQ01", "login");
        CanonicalRequest mismatch = canonical("8", READ, READ_TARGET)) {
      assertEquals(
          OptionalLong.empty(),
          request(OptionalLong.empty(), Optional.empty(), login).ownerUserId());
      assertEquals(OWNER, request(OWNER, Optional.empty(), read).ownerUserId());
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  null, CORRELATION, OWNER, Optional.empty(), read, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () -> new InboxRequest(MESSAGE, null, OWNER, Optional.empty(), read, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE, CORRELATION, null, Optional.empty(), read, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () -> new InboxRequest(MESSAGE, CORRELATION, OWNER, null, read, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE, CORRELATION, OWNER, Optional.empty(), null, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(MESSAGE, CORRELATION, OWNER, Optional.empty(), read, null, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE, CORRELATION, OWNER, Optional.empty(), read, RECEIVED, null));
      assertThrows(IllegalArgumentException.class, () -> request(OWNER, Optional.empty(), login));
      assertThrows(
          IllegalArgumentException.class,
          () -> request(OptionalLong.empty(), Optional.empty(), read));
      assertEquals(
          "canonical owner scope does not match Inbox owner",
          assertThrows(
                  IllegalArgumentException.class, () -> request(OWNER, Optional.empty(), mismatch))
              .getMessage());
      assertThrows(IllegalArgumentException.class, () -> request(OWNER, Optional.of(TOKEN), read));
      assertThrows(
          IllegalArgumentException.class,
          () -> request(OptionalLong.empty(), Optional.of(TOKEN), login));
      for (Instant invalid : List.of(RECEIVED, RECEIVED.minusSeconds(1))) {
        assertEquals(
            "Inbox expiry must be after receipt time",
            assertThrows(
                    IllegalArgumentException.class,
                    () ->
                        new InboxRequest(
                            MESSAGE, CORRELATION, OWNER, Optional.empty(), read, RECEIVED, invalid))
                .getMessage());
      }
      assertEquals(
          RECEIVED.plusSeconds(1),
          new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OWNER,
                  Optional.empty(),
                  read,
                  RECEIVED,
                  RECEIVED.plusSeconds(1))
              .expiresAt());
    }
    for (long owner : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      try (CanonicalRequest value = canonical(Long.toString(owner), READ, READ_TARGET)) {
        assertEquals(
            "ownerUserId is outside N12",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> request(OptionalLong.of(owner), Optional.empty(), value))
                .getMessage());
      }
    }
    for (long owner : new long[] {1, 999_999_999_999L}) {
      try (CanonicalRequest value = canonical(Long.toString(owner), READ, READ_TARGET)) {
        assertEquals(
            OptionalLong.of(owner),
            request(OptionalLong.of(owner), Optional.empty(), value).ownerUserId());
      }
    }
    for (String layout :
        List.of(
            "UCRREQ01",
            "USTREQ01",
            "URLREQ01",
            "UPWREQ01",
            "ULKREQ01",
            SUBMIT,
            "NTCREQ01",
            "QDLREQ01")) {
      try (CanonicalRequest value = canonical("7", layout, UPDATE_TARGET)) {
        assertEquals(
            Optional.of(TOKEN), request(OWNER, Optional.of(TOKEN), value).operationToken());
        assertEquals(
            "operation token presence does not match request layout",
            assertThrows(
                    IllegalArgumentException.class, () -> request(OWNER, Optional.empty(), value))
                .getMessage());
      }
    }
  }

  @Test
  void requestValue002OrderedValueComponentsAndFixedRedactionRetainBorrowedCanonical() {
    try (CanonicalRequest canonical = canonical("7", SUBMIT, UPDATE_TARGET);
        CanonicalRequest equalCanonical = canonical("7", SUBMIT, UPDATE_TARGET);
        CanonicalRequest otherOwner = canonical("8", SUBMIT, UPDATE_TARGET);
        CanonicalRequest otherTarget = canonical("7", SUBMIT, "other")) {
      InboxRequest value = request(OWNER, Optional.of(TOKEN), canonical);
      InboxRequest equal = request(OWNER, Optional.of(TOKEN), equalCanonical);
      assertEquals(MESSAGE, value.messageId());
      assertEquals(CORRELATION, value.correlationId());
      assertEquals(OWNER, value.ownerUserId());
      assertEquals(Optional.of(TOKEN), value.operationToken());
      assertEquals(canonical, value.canonicalRequest());
      assertEquals(RECEIVED, value.receivedAt());
      assertEquals(EXPIRES, value.expiresAt());
      assertEquals(
          "InboxRequest[message/correlation/owner/token/request/time=<redacted>]",
          value.toString());
      assertEquals(value, value);
      assertEquals(value, equal);
      assertEquals(equal, value);
      assertEquals("retained", new java.util.HashMap<>(Map.of(value, "retained")).get(equal));
      assertNotEquals(value, null);
      assertNotEquals(value, "other type");
      for (InboxRequest other :
          List.of(
              new InboxRequest(
                  new UUID(0, 4),
                  CORRELATION,
                  OWNER,
                  Optional.of(TOKEN),
                  canonical,
                  RECEIVED,
                  EXPIRES),
              new InboxRequest(
                  MESSAGE, new UUID(0, 4), OWNER, Optional.of(TOKEN), canonical, RECEIVED, EXPIRES),
              request(OptionalLong.of(8), Optional.of(TOKEN), otherOwner),
              request(OWNER, Optional.of(new UUID(0, 4)), canonical),
              request(OWNER, Optional.of(TOKEN), otherTarget),
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OWNER,
                  Optional.of(TOKEN),
                  canonical,
                  RECEIVED.plusSeconds(1),
                  EXPIRES),
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OWNER,
                  Optional.of(TOKEN),
                  canonical,
                  RECEIVED,
                  EXPIRES.plusSeconds(1)))) {
        assertNotEquals(value, other);
        assertNotEquals(other, value);
      }
      assertEquals(List.of(), canonical.fields());
    }
  }

  private static CanonicalRequest canonical(String owner, String layout, String target) {
    return new CanonicalRequest(owner, layout, "001", target, List.of());
  }

  private static InboxRequest request(
      OptionalLong owner, Optional<UUID> token, CanonicalRequest canonical) {
    return new InboxRequest(MESSAGE, CORRELATION, owner, token, canonical, RECEIVED, EXPIRES);
  }
}
