package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** PT-IDEM-012, SS351 section 3.3: independent literal JSON oracle. */
final class RequestLogDetailsTest {
  @Test
  void allowedScalarsAndRolesMatchLiteralJson() {
    assertEquals("{}", RequestLogDetails.normalize(Optional.empty(), Optional.empty()));
    assertEquals("{}", normalize(" {} \t"));
    String all =
        "{\"responseBytes\":999999999999,\"userAgentFamily\":\""
            + "A".repeat(32)
            + "\",\"truncated\":true,\"projectionStatus\":\"PENDING\"}";
    assertEquals(all, normalize(all));
    assertEquals(
        "{\"responseBytes\":0,\"userAgentFamily\":\"A\",\"truncated\":false,\"projectionStatus\":\"FAILED\"}",
        normalize(
            "{\"responseBytes\":0,\"userAgentFamily\":\"A\",\"truncated\":false,\"projectionStatus\":\"FAILED\"}"));
    assertEquals(
        "{\"actorRole\":\"USER\"}",
        RequestLogDetails.normalize(Optional.empty(), Optional.of(UserRole.USER)));
    assertEquals(
        "{\"actorRole\":\"ADMIN\"}",
        RequestLogDetails.normalize(Optional.of("{}"), Optional.of(UserRole.ADMIN)));
    assertEquals(
        "{\"userAgentFamily\":\"Browser 1.0_x-y\"}",
        normalize("{\"userAgentFamily\":\"Browser 1.0_x-y\"}"));
  }

  @Test
  void unsafeMalformedDuplicateAndWrongTypesAreRejected() {
    for (String invalid :
        List.of(
            "",
            "null",
            "[]",
            "1",
            "{",
            "{} {}",
            "{} true",
            "{}/*comment*/",
            "{\"truncated\":true,\"truncated\":false}",
            "{\"unknown\":1}",
            "{\"actorRole\":\"ADMIN\"}",
            "{\"userAgentFamily\":null}",
            "{\"userAgentFamily\":1}",
            "{\"userAgentFamily\":\"\"}",
            "{\"userAgentFamily\":\"a/b\"}",
            "{\"userAgentFamily\":\"日本語\"}",
            "{\"userAgentFamily\":\"" + "a".repeat(33) + "\"}",
            "{\"responseBytes\":\"0\"}",
            "{\"responseBytes\":null}",
            "{\"responseBytes\":-1}",
            "{\"responseBytes\":1.0}",
            "{\"responseBytes\":1e2}",
            "{\"responseBytes\":1000000000000}",
            "{\"responseBytes\":01}",
            "{\"truncated\":\"true\"}",
            "{\"truncated\":null}",
            "{\"truncated\":1}",
            "{\"projectionStatus\":\"SENT\"}",
            "{\"projectionStatus\":false}",
            "{\"truncated\":{\"a\":{\"b\":1}}}",
            "{\"truncated\":true,}",
            "{truncated:true}",
            " ".repeat(1023) + "{}",
            "あ".repeat(342))) {
      var failure =
          assertThrows(PermanentProtocolException.class, () -> normalize(invalid), invalid);
      assertEquals(
          "REQUEST log details violate the safe projection contract", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertEquals("{}", normalize(" ".repeat(1022) + "{}"));
    assertThrows(
        NullPointerException.class, () -> RequestLogDetails.normalize(null, Optional.empty()));
    assertThrows(
        NullPointerException.class, () -> RequestLogDetails.normalize(Optional.empty(), null));
  }

  private static String normalize(String text) {
    return RequestLogDetails.normalize(Optional.of(text), Optional.empty());
  }

  @Test
  void rejectsMalformedUnicodeInKeysAndFamilyButPreservesAsciiEscapes() {
    for (String spelling :
        List.of(Character.toString(0xd800), Character.toString(0xdc00), "\\uD800", "\\uDC00")) {
      for (String invalid :
          List.of(
              "{\"trunc" + spelling + "ated\":true}",
              "{\"userAgentFamily\":\"A" + spelling + "\"}")) {
        var failure = assertThrows(PermanentProtocolException.class, () -> normalize(invalid));
        assertEquals(
            "REQUEST log details violate the safe projection contract", failure.getMessage());
        assertNull(failure.getCause());
      }
    }
    assertEquals("{\"userAgentFamily\":\"A\"}", normalize("{\"userAgentFamily\":\"\\u0041\"}"));
  }
}
