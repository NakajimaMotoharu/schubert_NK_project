package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.security.SavedRequestTarget;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.IntStream;
import org.junit.jupiter.api.Test;

/** Isolated stored values for NK-WEB-001, SS314 §7.2.1 and PT-WEB-ATTR001 through ATTR005. */
final class SessionAttributesValueTest {
  private static final Instant NOW = Instant.parse("2026-01-01T00:00:00Z");

  @Test
  void attr001OptionalStateAndBoundaryLengthsKeepTheirValues() {
    var empty = attributes(Optional.empty(), List.of());
    assertEquals(Optional.empty(), empty.principal());
    assertEquals(Optional.empty(), empty.csrfToken());
    assertEquals(Optional.empty(), empty.savedRequest());
    assertEquals(List.of(), empty.operationTokens());

    var principal =
        new SessionPrincipal(
            "fixture", UserRole.USER, AuthenticationContext.of("b".repeat(64)), NOW);
    var request = SavedRequestTarget.fromGet("GET", "/search?q=fixture");
    for (int length : new int[] {64, 128}) {
      var csrf = "a0_-".repeat(length / 4);
      var state =
          new SessionAttributes(
              Optional.of(principal), Optional.of(csrf), Optional.of(request), List.of());
      assertEquals(Optional.of(principal), state.principal());
      assertEquals(Optional.of(csrf), state.csrfToken());
      assertEquals("/search?q=fixture", state.savedRequest().orElseThrow().location());
      assertEquals("SessionAttributes[REDACTED]", state.toString());
    }
  }

  @Test
  void attr002DistinctOperationsKeepOrderAndRejectAnEleventh() {
    var ten = IntStream.rangeClosed(1, 10).mapToObj(SessionAttributesValueTest::operation).toList();
    var mutable = new ArrayList<>(ten);
    var value = attributes(Optional.empty(), mutable);
    Collections.reverse(mutable);
    assertEquals(ten, value.operationTokens());
    assertThrows(UnsupportedOperationException.class, () -> value.operationTokens().clear());
    mutable.add(operation(11));
    assertEquals(
        "session operation count is invalid",
        assertThrows(IllegalArgumentException.class, () -> attributes(Optional.empty(), mutable))
            .getMessage());
  }

  @Test
  void attr003DuplicateOperationIdentityIsRejectedAcrossPurposes() {
    var first = operation(1);
    var duplicate = new SessionOperationToken("QDLREQ01", new UUID(0, 1), NOW.plusSeconds(1));
    assertEquals(
        "session operation identity is duplicated",
        assertThrows(
                IllegalArgumentException.class,
                () -> attributes(Optional.empty(), List.of(first, duplicate)))
            .getMessage());
  }

  @Test
  void attr004EachInvalidCsrfVariantReturnsTheFixedDiagnostic() {
    for (String value : List.of("a".repeat(63), "a".repeat(129), "a".repeat(63) + "!")) {
      assertEquals(
          "session CSRF value is invalid",
          assertThrows(
                  IllegalArgumentException.class, () -> attributes(Optional.of(value), List.of()))
              .getMessage());
    }
  }

  @Test
  void attr005EqualityAndHashCodeObserveTheStoredValues() {
    var original = attributes(Optional.empty(), List.of(operation(2), operation(1)));
    var equivalent = attributes(Optional.empty(), List.of(operation(2), operation(1)));
    var reordered = attributes(Optional.empty(), List.of(operation(1), operation(2)));
    assertEquals(original, equivalent);
    assertEquals(original.hashCode(), equivalent.hashCode());
    assertNotEquals(original, reordered);
  }

  private static SessionOperationToken operation(int identity) {
    return new SessionOperationToken("QSBREQ01", new UUID(0, identity), NOW);
  }

  private static SessionAttributes attributes(
      Optional<String> csrf, List<SessionOperationToken> operations) {
    return new SessionAttributes(Optional.empty(), csrf, Optional.empty(), operations);
  }
}
