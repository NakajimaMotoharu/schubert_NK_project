package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** PT-LOG-RAW002..004 / SS351 3.3/10 / BUG-3644 / PG-D-1172. Memory-only input vectors. */
class RequestLogDetailsRawContractTest {
  private static final String SAFE_FAILURE =
      "REQUEST log details violate the safe projection contract";

  @Test
  void raw002FourFixedHashCollisionsRemainUnknownKeys() {
    String[] known = {"responseBytes", "userAgentFamily", "truncated", "projectionStatus"};
    String[] unknown = {"sFsponseBytes", "vTerAgentFamily", "uSuncated", "qSojectionStatus"};
    for (int index = 0; index < known.length; index++) {
      assertNotEquals(known[index], unknown[index]);
      assertEquals(known[index].hashCode(), unknown[index].hashCode());
      String input = "{\"" + unknown[index] + "\":1}";
      PermanentProtocolException failure =
          assertThrows(
              PermanentProtocolException.class,
              () -> RequestLogDetails.normalize(Optional.of(input), Optional.empty()));
      assertEquals(SAFE_FAILURE, failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
  }

  @Test
  void raw003ForbiddenPublicCanariesNeverEscapeThroughAnyRoleOrParserDiagnostic() {
    String marker = "PUBLIC-JSON-CANARY";
    List<Optional<UserRole>> roles =
        List.of(Optional.empty(), Optional.of(UserRole.USER), Optional.of(UserRole.ADMIN));
    for (String input :
        List.of(
            "{\"password\":\"" + marker + "\"}",
            "{\"cookie\":\"" + marker + "\"}",
            "{\"userAgentFamily\":\"" + marker + "\\ninvalid\"}",
            "{\"truncated\":true,\"unknown\":\"" + marker + "\"}",
            "{} \"" + marker + "\"")) {
      for (Optional<UserRole> role : roles) {
        PermanentProtocolException failure =
            assertThrows(
                PermanentProtocolException.class,
                () -> RequestLogDetails.normalize(Optional.of(input), role));
        assertEquals(SAFE_FAILURE, failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertFalse(failure.toString().contains(marker));
      }
    }
  }

  @Test
  void raw004BoundsTheOriginalJsonBeforeEscapeProjection() {
    String escapedJson = "{\"userAgentFamily\":\"\\u0041\"}";
    String exact = " ".repeat(1024 - escapedJson.length()) + escapedJson;
    assertEquals(1024, exact.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(
        "{\"userAgentFamily\":\"A\",\"actorRole\":\"ADMIN\"}",
        RequestLogDetails.normalize(Optional.of(exact), Optional.of(UserRole.ADMIN)));

    String oversized = exact + " ";
    assertEquals(1025, oversized.getBytes(StandardCharsets.UTF_8).length);
    var failure =
        assertThrows(
            PermanentProtocolException.class,
            () -> RequestLogDetails.normalize(Optional.of(oversized), Optional.of(UserRole.ADMIN)));
    assertEquals(SAFE_FAILURE, failure.getMessage());
    assertNull(failure.getCause());
  }
}
