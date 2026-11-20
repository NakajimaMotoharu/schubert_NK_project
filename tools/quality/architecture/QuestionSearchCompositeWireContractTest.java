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
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** SCR022/UI224236/SS313314323; PT-QRY-HTTP001/002 composite wire boundary. */
public final class QuestionSearchCompositeWireContractTest {
  private static final String KEYWORD = "keyword";
  private static final String USERNAME = "username";
  private static final String KEYWORD_INPUT = "e\u0301".repeat(128);
  private static final String USERNAME_INPUT = "A\u030a".repeat(32);

  @Test
  void qsformWire001BothNormalizedMaximaKeepAdjacentFieldsAndPadding() {
    var form = bind(KEYWORD_INPUT, USERNAME_INPUT);
    assertTrue(form.isValid());

    var values = new TypedPayloadValues(new LayoutId("QSSREQ01"), form.toRequest(), List.of());
    byte[] actual =
        PayloadCodec.standard().encode(PayloadTypeCatalog.encode(values), false).copyData();

    byte[] expected = new byte[384];
    Arrays.fill(expected, (byte) ' ');
    var hex = HexFormat.of();
    place(expected, 0, hex.parseHex("c3a9".repeat(128)));
    place(expected, 256, hex.parseHex("c385".repeat(32)));
    place(expected, 320, ascii("ANSWERED"));
    place(expected, 332, ascii("20240430000000000"));
    place(expected, 349, ascii("20240430235959999"));
    place(expected, 366, ascii("999999050"));
    assertArrayEquals(expected, actual);
  }

  @Test
  void qsformWire002EachOverflowWithTheOtherFieldAtItsMaximumStopsAtBinding() {
    assertInvalid(bind(KEYWORD_INPUT + "x", USERNAME_INPUT), KEYWORD);
    assertInvalid(bind(KEYWORD_INPUT, USERNAME_INPUT + "x"), USERNAME);
  }

  private static QuestionSearchForm bind(String keyword, String username) {
    return QuestionSearchForm.bind(
        Map.of(
            KEYWORD,
            List.of(" " + keyword + " "),
            USERNAME,
            List.of(" " + username + " "),
            "state",
            List.of("ANSWERED"),
            "from",
            List.of("2024-04-30"),
            "to",
            List.of("2024-04-30"),
            "page",
            List.of("999999")),
        UserRole.ADMIN);
  }

  private static void assertInvalid(QuestionSearchForm form, String field) {
    assertFalse(form.isValid());
    assertEquals(Map.of(field, "入力項目を確認してください。"), form.getIssues());
    assertThrows(IllegalArgumentException.class, form::toRequest);
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void place(byte[] target, int offset, byte[] field) {
    System.arraycopy(field, 0, target, offset, field.length);
  }
}
