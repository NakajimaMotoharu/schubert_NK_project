package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.UnsupportedLayoutException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** UI234 fixed offsets, independent of production catalog/encode methods. PT-SCN-008-W03. */
class ScenarioRecordEncodingTest {
  @Test
  void w03SingleRecordGoldenHasNoInventedDataAndRejectsNullUnknownAndNonRecordLayouts() {
    var fields =
        new FieldValueSet(
            Map.of(
                "Entry ID", new FieldValue.Numeric(71),
                "Entry sequence", new FieldValue.Numeric(1),
                "Line番号", new FieldValue.Numeric(42),
                "Entry type", new FieldValue.Text("narration"),
                "本文", new FieldValue.Text("本文"),
                "Audio sequence", new FieldValue.Numeric(0)));
    byte[] expected = golden();
    PayloadCodec codec = PayloadCodec.standard();
    LayoutId scenario = new LayoutId("SCNRSP01");
    byte[] actual = codec.encodeRecord(scenario, fields);
    assertArrayEquals(expected, actual);
    actual[0] = '9';
    assertArrayEquals(expected, codec.encodeRecord(scenario, fields));
    assertThrows(NullPointerException.class, () -> codec.encodeRecord(null, fields));
    assertThrows(NullPointerException.class, () -> codec.encodeRecord(scenario, null));
    assertThrows(
        UnsupportedLayoutException.class,
        () -> codec.encodeRecord(new LayoutId("ZZZZZZZZ"), fields));
    assertThrows(
        MessageEncodingException.class, () -> codec.encodeRecord(new LayoutId("LGNREQ01"), fields));
    assertThrows(
        MessageEncodingException.class, () -> codec.encodeRecord(scenario, FieldValueSet.empty()));
  }

  @Test
  void rd02SingleRecordDecodeUsesLiteralGoldenAndOwnsItsValues() {
    byte[] input = golden();
    FieldValueSet actual = PayloadCodec.standard().decodeRecord(new LayoutId("SCNRSP01"), input);
    assertEquals(new FieldValue.Numeric(71), actual.getOrUnset("Entry ID"));
    assertEquals(new FieldValue.Numeric(1), actual.getOrUnset("Entry sequence"));
    assertEquals(new FieldValue.Numeric(42), actual.getOrUnset("Line番号"));
    assertEquals(new FieldValue.Text("narration"), actual.getOrUnset("Entry type"));
    assertEquals(new FieldValue.Text("本文"), actual.getOrUnset("本文"));
    assertEquals(new FieldValue.Numeric(0), actual.getOrUnset("Audio sequence"));
    for (String name : new String[] {"Speaker名", "Audio ID", "Audio display path"}) {
      assertEquals(FieldValue.Unset.INSTANCE, actual.getOrUnset(name));
    }
    Arrays.fill(input, (byte) '#');
    assertEquals(new FieldValue.Numeric(71), actual.getOrUnset("Entry ID"));
    assertEquals(new FieldValue.Text("本文"), actual.getOrUnset("本文"));
  }

  @Test
  void rd02RejectsNullUnknownNonRecordLengthAndMalformedFieldBytes() {
    PayloadCodec codec = PayloadCodec.standard();
    LayoutId scenario = new LayoutId("SCNRSP01");
    assertThrows(NullPointerException.class, () -> codec.decodeRecord(null, golden()));
    assertThrows(NullPointerException.class, () -> codec.decodeRecord(scenario, null));
    assertThrows(
        UnsupportedLayoutException.class,
        () -> codec.decodeRecord(new LayoutId("ZZZZZZZZ"), golden()));
    assertThrows(
        PermanentProtocolException.class,
        () -> codec.decodeRecord(new LayoutId("LGNREQ01"), new byte[0]));
    for (int length : new int[] {0, 4799, 4801}) {
      assertThrows(
          PermanentProtocolException.class,
          () -> codec.decodeRecord(scenario, Arrays.copyOf(golden(), length)));
    }
    byte[] missing = golden();
    Arrays.fill(missing, 0, 12, (byte) ' ');
    byte[] utf8 = golden();
    utf8[164] = (byte) 0xc3;
    utf8[165] = (byte) 0x28;
    byte[] decomposed = golden();
    put(decomposed, 164, "か\u3099");
    byte[] reserved = golden();
    reserved[4799] = '#';
    for (byte[] invalid : new byte[][] {missing, utf8, decomposed, reserved}) {
      assertThrows(PermanentProtocolException.class, () -> codec.decodeRecord(scenario, invalid));
    }
  }

  private static byte[] golden() {
    byte[] expected = new byte[4800];
    Arrays.fill(expected, (byte) ' ');
    put(expected, 0, "000000000071");
    put(expected, 12, "000001");
    put(expected, 18, "00000042");
    put(expected, 26, "narration");
    put(expected, 164, "本文");
    put(expected, 4260, "000");
    return expected;
  }

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }
}
