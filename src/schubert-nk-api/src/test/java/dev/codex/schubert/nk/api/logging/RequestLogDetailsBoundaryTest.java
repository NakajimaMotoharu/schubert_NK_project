package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SS351 section 3.3, PT-IDEM-012-JSON-001 and PT-IDEM-012-JSON-002. */
final class RequestLogDetailsBoundaryTest {
  @Test
  void decodedPropertyIdentityControlsDuplicatesAndRoleOwnership() {
    assertEquals(
        "{\"truncated\":false,\"actorRole\":\"USER\"}",
        normalize("{\"\\u0074runcated\":false}", UserRole.USER));
    for (String text :
        List.of(
            "{\"truncated\":false,\"\\u0074runcated\":true}",
            "{\"\\u0074runcated\":true,\"truncated\":false}",
            "{\"actor\\u0052ole\":\"ADMIN\"}")) {
      assertRejected(text);
    }
    assertEquals(
        "{\"projectionStatus\":\"FAILED\",\"actorRole\":\"ADMIN\"}",
        normalize("{\"\\u0070rojectionStatus\":\"FAILED\"}", UserRole.ADMIN));
  }

  @Test
  void numericZeroRequiresAnUnsignedDecimalIntegerSpelling() {
    assertEquals(
        "{\"responseBytes\":0,\"actorRole\":\"USER\"}",
        normalize("{\"responseBytes\":0}", UserRole.USER));
    for (String number : List.of("-0", "+0", "0.0", "0e0", "0E+0", "\"0\"")) {
      assertRejected("{\"responseBytes\":" + number + "}");
    }
  }

  private static void assertRejected(String text) {
    var failure =
        assertThrows(PermanentProtocolException.class, () -> normalize(text, UserRole.USER));
    assertEquals("REQUEST log details violate the safe projection contract", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static String normalize(String text, UserRole role) {
    return RequestLogDetails.normalize(Optional.of(text), Optional.of(role));
  }
}
