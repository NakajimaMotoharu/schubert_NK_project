package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * Plain SS323 §9.4 field metadata only: no fingerprint/crypto/connection/worker fixture.
 * NK-ADM-001; WBS-P010-01; PT-ADM-CORE001..004; specification 2012.
 */
class UserQueryCanonicalCoreTest {
  private static final String SEARCH_LAYOUT = "USRREQ01";
  private static final String DETAIL_LAYOUT = "UDTREQ01";
  private static final String PREFIX = "Équipe";
  private static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");

  @Test
  void core001FilledSearchFieldsUseIndependentLiteralMetadata() {
    var request = UserQueryRequest.decode(wire(SEARCH_LAYOUT, searchBytes(true)));
    var actor = new AuthenticatedActor(7, "unit7", Role.ADMIN);
    // Ordinary cleanup only: no after-close assertion, key material or concurrent close.
    try (var canonical = request.canonical(actor)) {
      assertEquals("7", canonical.ownerScope());
      assertEquals(SEARCH_LAYOUT, canonical.layoutId());
      assertEquals("001", canonical.layoutVersion());
      assertEquals("REQUEST:USRREQ01", canonical.target());
      assertEquals(5, canonical.fields().size());
      field(canonical.fields().get(0), "usernamePrefix", "X1", PREFIX);
      field(canonical.fields().get(1), "role", "X1", "ADMIN");
      field(canonical.fields().get(2), "state", "X1", "ACTIVE");
      field(canonical.fields().get(3), "page", "N1", "1");
      field(canonical.fields().get(4), "pageSize", "N1", "50");
    }
  }

  @Test
  void core002MissingOptionalsAndDetailRetainOriginalValues() {
    var request = UserQueryRequest.decode(wire(SEARCH_LAYOUT, searchBytes(false)));
    var actor = new AuthenticatedActor(8, "unit8", Role.ADMIN);
    var detail = detail();
    try (var canonical = request.canonical(actor);
        var exact = detail.canonical(actor)) {
      assertEquals("8", canonical.ownerScope());
      assertEquals(5, canonical.fields().size());
      var names = List.of("usernamePrefix", "role", "state");
      for (int index = 0; index < names.size(); index++) {
        var value = canonical.fields().get(index);
        assertEquals(names.get(index), value.name());
        assertEquals("X1", value.typeVersion());
        assertNull(value.value());
      }
      field(canonical.fields().get(3), "page", "N1", "1");
      field(canonical.fields().get(4), "pageSize", "N1", "50");
      assertEquals("8", exact.ownerScope());
      assertEquals(DETAIL_LAYOUT, exact.layoutId());
      assertEquals("001", exact.layoutVersion());
      assertEquals("REQUEST:UDTREQ01", exact.target());
      assertEquals(1, exact.fields().size());
      field(exact.fields().getFirst(), "userId", "N1", "3");
    }
  }

  @Test
  void core003RedactedMetadataAndInvalidDecodeStayBounded() {
    var request = UserQueryRequest.decode(wire(SEARCH_LAYOUT, searchBytes(true)));
    assertEquals("UserQueryRequest[REDACTED]", request.toString());
    var unsupported = wire("LGNREQ01", searchBytes(false));
    var failure =
        assertThrows(PermanentProtocolException.class, () -> UserQueryRequest.decode(unsupported));
    assertEquals("user query request is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertThrows(NullPointerException.class, () -> UserQueryRequest.decode(null));
  }

  @Test
  void core004NullActorsAndRepositoriesStopWithoutDelegation() {
    var request = UserQueryRequest.decode(wire(SEARCH_LAYOUT, searchBytes(false)));
    var detail = detail();
    assertThrows(NullPointerException.class, () -> request.canonical(null));
    assertThrows(NullPointerException.class, () -> detail.canonical(null));
    // No repository/connection is constructed; no non-null backend receiver exists.
    assertThrows(NullPointerException.class, () -> request.query(null, null, null, null));
    assertThrows(NullPointerException.class, () -> detail.query(null, null, null, null));
  }

  private static void field(CanonicalField actual, String name, String type, String expected) {
    assertEquals(name, actual.name());
    assertEquals(type, actual.typeVersion());
    assertArrayEquals(expected.getBytes(StandardCharsets.UTF_8), actual.value());
  }

  private static UserQueryRequest detail() {
    return UserQueryRequest.decode(
        wire(DETAIL_LAYOUT, "000000000003".getBytes(StandardCharsets.US_ASCII)));
  }

  private static byte[] searchBytes(boolean filled) {
    byte[] data = new byte[96];
    Arrays.fill(data, (byte) 32);
    if (filled) {
      put(data, 0, PREFIX);
      put(data, 64, "ADMIN");
      put(data, 69, "ACTIVE");
    }
    put(data, 77, "000001050");
    return data;
  }

  private static void put(byte[] data, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, data, offset, bytes.length);
  }

  private static WireMessage<FixedPayload> wire(String layout, byte[] data) {
    UUID message = new UUID(2012, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            message,
            message,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }
}
