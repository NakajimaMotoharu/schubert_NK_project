package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.MalformedInputException;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.OptionalLong;
import org.junit.jupiter.api.Test;

class FieldCodecTest {
  @Test
  void textEncodeNormalizesUtf8AndPadsWithAsciiSpace() {
    assertArrayEquals(new byte[] {'A', 'B', ' ', ' '}, FieldCodec.encodeText("AB", 4, true));
    assertArrayEquals(
        new byte[] {(byte) 0xc3, (byte) 0xa9, ' ', ' '}, FieldCodec.encodeText("e\u0301", 4, true));
    assertArrayEquals("あ".getBytes(StandardCharsets.UTF_8), FieldCodec.encodeText("あ", 3, true));
    assertArrayEquals("😀".getBytes(StandardCharsets.UTF_8), FieldCodec.encodeText("😀", 4, true));
    assertArrayEquals(new byte[] {' ', ' '}, FieldCodec.encodeText(null, 2, false));
    assertArrayEquals(new byte[] {' ', ' '}, FieldCodec.encodeText("", 2, false));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText(null, 2, true));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText("", 2, true));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText("x ", 3, true));
    for (String control : new String[] {"x\r", "x\n", "x\t", "x\0"}) {
      assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText(control, 4, true));
    }
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText("\ud800", 4, true));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText("😀x", 4, true));
    assertThrows(IllegalArgumentException.class, () -> FieldCodec.encodeText("x", 0, true));
  }

  @Test
  void textDecodeIsStrictCanonicalAndOptionalAware() {
    assertEquals(
        Optional.of("a b"), FieldCodec.decodeText(new byte[] {'a', ' ', 'b', ' ', ' '}, true));
    assertEquals(
        Optional.of("あ"), FieldCodec.decodeText("あ ".getBytes(StandardCharsets.UTF_8), true));
    assertEquals(Optional.empty(), FieldCodec.decodeText(new byte[] {' ', ' '}, false));
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.decodeText(new byte[] {' ', ' '}, true));
    assertThrows(
        PermanentProtocolException.class,
        () -> FieldCodec.decodeText(new byte[] {(byte) 0xc3, 0x28}, true));
    assertThrows(
        PermanentProtocolException.class,
        () -> FieldCodec.decodeText("e\u0301".getBytes(StandardCharsets.UTF_8), true));
    for (byte control : new byte[] {'\r', '\n', '\t', 0}) {
      assertThrows(
          PermanentProtocolException.class,
          () -> FieldCodec.decodeText(new byte[] {'x', control}, true));
    }
    assertThrows(NullPointerException.class, () -> FieldCodec.decodeText(null, false));
    assertThrows(IllegalArgumentException.class, () -> FieldCodec.decodeText(new byte[0], false));
  }

  @Test
  void numericCodecChecksDigitsRangeAndOverflow() {
    assertArrayEquals(new byte[] {'0', '0', '0'}, FieldCodec.encodeNumeric(0, 3, 0, 999));
    assertArrayEquals(new byte[] {'0', '0', '1'}, FieldCodec.encodeNumeric(1, 3, 0, 999));
    assertArrayEquals(new byte[] {'9', '9', '9'}, FieldCodec.encodeNumeric(999, 3, 0, 999));
    assertEquals(1, FieldCodec.decodeNumeric(new byte[] {'0', '0', '1'}, 0, 999));
    assertEquals(999, FieldCodec.decodeNumeric(new byte[] {'9', '9', '9'}, 0, 999));
    assertThrows(IllegalArgumentException.class, () -> FieldCodec.encodeNumeric(0, 0, 0, 1));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeNumeric(0, 1, -1, 1));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeNumeric(0, 1, 2, 1));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeNumeric(0, 1, 1, 2));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeNumeric(3, 1, 1, 2));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeNumeric(10, 1, 0, 10));
    assertThrows(NullPointerException.class, () -> FieldCodec.decodeNumeric(null, 0, 1));
    assertThrows(IllegalArgumentException.class, () -> FieldCodec.decodeNumeric(new byte[0], 0, 1));
    assertThrows(
        IllegalArgumentException.class, () -> FieldCodec.decodeNumeric(new byte[] {'0'}, -1, 1));
    assertThrows(
        IllegalArgumentException.class, () -> FieldCodec.decodeNumeric(new byte[] {'0'}, 2, 1));
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.decodeNumeric(new byte[] {'+'}, 0, 9));
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.decodeNumeric(new byte[] {':'}, 0, 9));
    assertThrows(
        PermanentProtocolException.class,
        () -> FieldCodec.decodeNumeric(new byte[] {'1', '.'}, 0, 99));
    assertThrows(
        PermanentProtocolException.class,
        () ->
            FieldCodec.decodeNumeric(
                "9999999999999999999".getBytes(StandardCharsets.US_ASCII), 0, Long.MAX_VALUE));
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.decodeNumeric(new byte[] {'0'}, 1, 9));
  }

  @Test
  void numericErrorFillerDoesNotBecomeBusinessZero() {
    assertEquals(
        OptionalLong.empty(),
        FieldCodec.decodeNumericOrErrorFiller(new byte[] {'0', '0'}, 1, 99, true));
    assertEquals(
        OptionalLong.of(0),
        FieldCodec.decodeNumericOrErrorFiller(new byte[] {'0', '0'}, 0, 99, false));
    assertEquals(
        OptionalLong.of(1),
        FieldCodec.decodeNumericOrErrorFiller(new byte[] {'0', '1'}, 1, 99, true));
    assertThrows(
        NullPointerException.class, () -> FieldCodec.decodeNumericOrErrorFiller(null, 0, 1, true));
    assertThrows(
        IllegalArgumentException.class,
        () -> FieldCodec.decodeNumericOrErrorFiller(new byte[0], 0, 1, true));
  }

  @Test
  void booleanAndReservedFieldsRejectUnknownBytes() {
    assertArrayEquals(new byte[] {'0'}, FieldCodec.encodeBoolean(Boolean.FALSE, false));
    assertArrayEquals(new byte[] {'1'}, FieldCodec.encodeBoolean(Boolean.TRUE, false));
    assertArrayEquals(new byte[] {' '}, FieldCodec.encodeBoolean(null, true));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeBoolean(null, false));
    assertEquals(Optional.of(Boolean.FALSE), FieldCodec.decodeBoolean(new byte[] {'0'}, false));
    assertEquals(Optional.of(Boolean.TRUE), FieldCodec.decodeBoolean(new byte[] {'1'}, false));
    assertEquals(Optional.empty(), FieldCodec.decodeBoolean(new byte[] {' '}, true));
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.decodeBoolean(new byte[] {' '}, false));
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.decodeBoolean(new byte[] {'2'}, true));
    assertThrows(
        PermanentProtocolException.class,
        () -> FieldCodec.decodeBoolean(new byte[] {'0', '1'}, true));
    assertThrows(NullPointerException.class, () -> FieldCodec.decodeBoolean(null, true));
    FieldCodec.requireSpaces(new byte[] {' ', ' '});
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.requireSpaces(new byte[] {' ', 'x'}));
    assertThrows(NullPointerException.class, () -> FieldCodec.requireSpaces(null));
    assertThrows(IllegalArgumentException.class, () -> FieldCodec.requireSpaces(new byte[0]));
  }

  /** PT-CODEC-NUMMAX001; SS322 §4.2/5/11; fixed decimal/semantic maxima, no production oracle. */
  @Test
  void numericSemanticCeilingIsIndependentOfWireAndLongCapacity() {
    byte[] smallMaximum = "000099".getBytes(StandardCharsets.US_ASCII);
    byte[] smallAbove = "000100".getBytes(StandardCharsets.US_ASCII);
    assertEquals(99, FieldCodec.decodeNumeric(smallMaximum, 0, 99));
    assertThrows(
        PermanentProtocolException.class, () -> FieldCodec.decodeNumeric(smallAbove, 0, 99));
    assertArrayEquals("000100".getBytes(StandardCharsets.US_ASCII), smallAbove);

    long semanticMaximum = 9_223_372_036_854_775_806L;
    byte[] longMaximum = "9223372036854775807".getBytes(StandardCharsets.US_ASCII);
    assertEquals(
        semanticMaximum,
        FieldCodec.decodeNumeric(
            "9223372036854775806".getBytes(StandardCharsets.US_ASCII), 0, semanticMaximum));
    assertEquals(Long.MAX_VALUE, FieldCodec.decodeNumeric(longMaximum, 0, Long.MAX_VALUE));
    assertThrows(
        PermanentProtocolException.class,
        () -> FieldCodec.decodeNumeric(longMaximum, 0, semanticMaximum));
    assertArrayEquals("9223372036854775807".getBytes(StandardCharsets.US_ASCII), longMaximum);
  }

  @Test // PT-CODEC-EXC-001; SS322§11 / 411§5-6
  void malformedAndOverflowFailuresRetainDiagnosticCauseWithoutEchoingInput() {
    var encoding =
        assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText("\ud800", 4, true));
    assertEquals("text field is not strict UTF-8", encoding.getMessage());
    assertEquals(
        1, assertInstanceOf(MalformedInputException.class, encoding.getCause()).getInputLength());

    byte[] malformed = {(byte) 0xc3, 0x28};
    var decoding =
        assertThrows(
            PermanentProtocolException.class, () -> FieldCodec.decodeText(malformed, true));
    assertEquals("text field contains invalid UTF-8", decoding.getMessage());
    assertEquals(
        1, assertInstanceOf(MalformedInputException.class, decoding.getCause()).getInputLength());
    assertArrayEquals(new byte[] {(byte) 0xc3, 0x28}, malformed);

    byte[] aboveLong = "9999999999999999999".getBytes(StandardCharsets.US_ASCII);
    var overflow =
        assertThrows(
            PermanentProtocolException.class,
            () -> FieldCodec.decodeNumeric(aboveLong, 0, Long.MAX_VALUE));
    assertEquals("numeric field overflows signed long", overflow.getMessage());
    assertInstanceOf(ArithmeticException.class, overflow.getCause());
    assertArrayEquals("9999999999999999999".getBytes(StandardCharsets.US_ASCII), aboveLong);

    var range =
        assertThrows(
            PermanentProtocolException.class,
            () -> FieldCodec.decodeNumeric(new byte[] {'0'}, 1, 9));
    assertEquals("numeric field is outside its semantic range", range.getMessage());
    assertNull(range.getCause());
  }
}
