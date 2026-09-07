package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.*;

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
    byte[] expected = new byte[4800];
    Arrays.fill(expected, (byte) ' ');
    put(expected, 0, "000000000071");
    put(expected, 12, "000001");
    put(expected, 18, "00000042");
    put(expected, 26, "narration");
    put(expected, 164, "本文");
    put(expected, 4260, "000");
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

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }
}
