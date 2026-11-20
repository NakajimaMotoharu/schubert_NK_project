package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm.Code;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm.Field;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** SCR003, UI234 §7.1, SS313/323, PT-SCR003-WIRE-001/002. */
final class ScenarioSearchFormWireTest {
  private static final String KEYWORD = "e\u0301".repeat(128);
  private static final String SPEAKER = "A\u030a".repeat(64);
  private static final String CHAPTER = "か\u3099".repeat(85) + "z";

  @Test
  void allNormalizedMaximaKeepAdjacentFieldsAndPadding() {
    var form = bind(KEYWORD, SPEAKER, CHAPTER);
    assertTrue(form.isValid());
    var payload = new TypedPayloadValues(new LayoutId("SRCREQ01"), form.toRequest(), List.of());
    byte[] actual =
        PayloadCodec.standard().encode(PayloadTypeCatalog.encode(payload), false).copyData();

    byte[] expected = new byte[672];
    Arrays.fill(expected, (byte) ' ');
    var hex = HexFormat.of();
    place(expected, 0, hex.parseHex("c3a9".repeat(128)));
    place(expected, 256, ascii("NUKITASHI2"));
    place(expected, 268, hex.parseHex("c385".repeat(64)));
    place(expected, 396, hex.parseHex("e3818c".repeat(85) + "7a"));
    place(expected, 652, ascii("narration"));
    place(expected, 662, ascii("0999999100"));
    assertArrayEquals(expected, actual);
  }

  @Test
  void eachOverflowIsRejectedWithTheOtherTwoFieldsAtTheirMaxima() {
    assertLengthIssue(bind(KEYWORD + "x", SPEAKER, CHAPTER), Field.Q);
    assertLengthIssue(bind(KEYWORD, SPEAKER + "x", CHAPTER), Field.SPEAKER);
    assertLengthIssue(bind(KEYWORD, SPEAKER, CHAPTER + "x"), Field.CHAPTER);
  }

  private static ScenarioSearchForm bind(String keyword, String speaker, String chapter) {
    return ScenarioSearchForm.bind(
        Map.of(
            "q", List.of(" " + keyword + " "),
            "game", List.of(" NUKITASHI2 "),
            "speaker", List.of(" " + speaker + " "),
            "chapter", List.of(" " + chapter + " "),
            "entry_type", List.of("narration"),
            "voice", List.of("without"),
            "page", List.of("999999")));
  }

  private static void assertLengthIssue(ScenarioSearchForm form, Field field) {
    assertFalse(form.isValid());
    assertEquals(Map.of(field, Code.LENGTH), form.getIssues());
    assertThrows(IllegalStateException.class, form::toRequest);
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void place(byte[] target, int offset, byte[] field) {
    System.arraycopy(field, 0, target, offset, field.length);
  }
}
