package dev.codex.schubert.nk.protocol.time;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.MessageEncodingException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class JstWireTimestampTest {
  private static final String MAXIMUM_INSTANT_TEXT = "9999-12-31T14:59:59.999Z";

  /** PT-PRO-003-T03: strict seventeen digits, not formatter's signed/expanded uuuu output. */
  @Test
  void bug037ExpandedYearsAndUnrepresentableInstantsAreRejected() {
    // YKT143: independent IANA LMT literal, not a formatter-generated oracle.
    assertEquals(
        "15821005000859000", JstWireTimestamp.format(Instant.parse("1582-10-04T14:50:00Z")));
    assertEquals(
        Instant.parse("1582-10-04T14:50:00Z"), JstWireTimestamp.parse("15821005000859000"));
    for (Instant invalid : invalidInstants()) {
      var failure =
          assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.format(invalid));
      assertNull(failure.getCause());
    }
    // Existing proleptic year semantics remain unchanged; only representable wire width is guarded.
    Instant minimum = LocalDateTime.of(0, 1, 1, 0, 0).atZone(ZoneId.of("Asia/Tokyo")).toInstant();
    assertEquals("00000101000000000", JstWireTimestamp.format(minimum));
    assertEquals(minimum, JstWireTimestamp.parse("00000101000000000"));
    assertEquals("99991231235959999", JstWireTimestamp.format(Instant.parse(MAXIMUM_INSTANT_TEXT)));
    assertThrows(
        IllegalArgumentException.class, () -> JstWireTimestamp.parse("+100000101090000000"));
    assertThrows(
        IllegalArgumentException.class, () -> JstWireTimestamp.parse("-00010101091859000"));
  }

  /** PT-PRO-003-T04/YKT-033: header rejects before copying into the next fixed field. */
  @Test
  void bug037HeaderSenderRejectsBadTimeAndPreservesAdjacentContext() {
    for (Instant invalid : invalidInstants()) {
      var failure =
          assertThrows(
              MessageEncodingException.class, () -> HeaderCodec.standard().encode(header(invalid)));
      assertInstanceOf(IllegalArgumentException.class, failure.getCause());
      assertNull(failure.getCause().getCause());
    }
    byte[] encoded = HeaderCodec.standard().encode(header(Instant.parse(MAXIMUM_INSTANT_TEXT)));
    assertEquals(256, encoded.length);
    assertEquals("99991231235959999", new String(encoded, 96, 17, StandardCharsets.US_ASCII));
    assertEquals("c".repeat(64), new String(encoded, 113, 64, StandardCharsets.US_ASCII));
    assertEquals(
        Instant.parse(MAXIMUM_INSTANT_TEXT), HeaderCodec.standard().peek(encoded).sentAt());
  }

  /** PT-PRO-003-T05/YKT-033: required numeric and optional text DATA share the same rejection. */
  @Test
  void bug037RequiredAndOptionalDataSendersRejectBadTime() {
    for (Instant invalid : invalidInstants()) {
      assertThrows(IllegalArgumentException.class, () -> TypedFieldValues.instant(invalid));
      assertThrows(
          IllegalArgumentException.class,
          () -> TypedFieldValues.optionalInstantValue(Optional.of(invalid)));
    }
    Instant maximum = Instant.parse(MAXIMUM_INSTANT_TEXT);
    assertEquals(new FieldValue.Numeric(99991231235959999L), TypedFieldValues.instant(maximum));
    assertEquals(
        new FieldValue.Text("99991231235959999"),
        TypedFieldValues.optionalInstantValue(Optional.of(maximum)));
    assertEquals(
        FieldValue.Unset.INSTANCE, TypedFieldValues.optionalInstantValue(Optional.empty()));
  }

  private static List<Instant> invalidInstants() {
    return List.of(
        Instant.parse("+10000-01-01T00:00:00Z"),
        Instant.parse("-0001-01-01T00:00:00Z"),
        Instant.MAX.truncatedTo(ChronoUnit.MILLIS),
        Instant.MIN);
  }

  private static CommonHeader header(Instant time) {
    UUID id = new UUID(0, 37);
    return new CommonHeader(
        "SCHBNK01",
        1,
        new LayoutId("GAMREQ01"),
        1,
        MessageKind.REQUEST,
        InteractionKind.SYNCHRONOUS,
        id,
        id,
        time,
        Optional.of(AuthenticationContext.of("c".repeat(64))),
        256,
        0,
        0,
        0,
        256,
        Optional.empty());
  }

  @Test
  void formatsAndParsesStrictJstMilliseconds() {
    Instant instant = Instant.parse("2026-09-02T03:34:56.789Z");
    assertEquals("20260902123456789", JstWireTimestamp.format(instant));
    assertEquals(instant, JstWireTimestamp.parse("20260902123456789"));
    assertEquals(
        Instant.parse("2024-02-29T14:59:59.999Z"), JstWireTimestamp.parse("20240229235959999"));
    assertEquals(17, JstWireTimestamp.WIRE_LENGTH);
    assertThrows(NullPointerException.class, () -> JstWireTimestamp.format(null));
    assertThrows(
        IllegalArgumentException.class,
        () -> JstWireTimestamp.format(Instant.parse("2026-09-02T03:34:56.789001Z")));
    assertThrows(NullPointerException.class, () -> JstWireTimestamp.parse(null));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("2026090212345678"));
    assertThrows(
        IllegalArgumentException.class, () -> JstWireTimestamp.parse("202609021234567890"));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("2026090212345678X"));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("20260229000000000"));
    assertThrows(IllegalArgumentException.class, () -> JstWireTimestamp.parse("20261301000000000"));
  }
}
