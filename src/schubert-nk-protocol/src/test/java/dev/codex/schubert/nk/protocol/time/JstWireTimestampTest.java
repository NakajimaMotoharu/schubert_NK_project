package dev.codex.schubert.nk.protocol.time;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import org.junit.jupiter.api.Test;

class JstWireTimestampTest {
  @Test
  void formatsAndParsesStrictJstMilliseconds() {
    Instant instant = Instant.parse("2026-09-02T03:34:56.789Z");
    assertEquals("20260902123456789", JstWireTimestamp.format(instant));
    assertEquals(instant, JstWireTimestamp.parse("20260902123456789"));
    assertEquals(Instant.parse("2024-02-29T14:59:59.999Z"), JstWireTimestamp.parse("20240229235959999"));
    assertEquals(17, JstWireTimestamp.WIRE_LENGTH);
    assertThrows(NullPointerException.class, () -> JstWireTimestamp.format(null));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.format(Instant.parse("2026-09-02T03:34:56.789001Z")));
    assertThrows(NullPointerException.class, () -> JstWireTimestamp.parse(null));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("2026090212345678"));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("202609021234567890"));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("2026090212345678X"));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("20260229000000000"));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("20261301000000000"));
  }
}
