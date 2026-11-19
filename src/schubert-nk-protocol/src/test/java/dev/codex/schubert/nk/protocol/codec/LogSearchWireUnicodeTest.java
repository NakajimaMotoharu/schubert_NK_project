package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.time.Instant;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** UI235 §11, SS322/323 §9.5. Uses independent DATA positions and fixed byte vectors. */
final class LogSearchWireUnicodeTest {
  private static final LayoutId LOG_SEARCH = new LayoutId("LGSREQ01");
  private static final HexFormat HEX = HexFormat.of();
  private static final int KEYWORD = 1;
  private static final int ACTION = 273;
  private static final int PATH = 337;

  @Test
  void retainsNfcAndSupplementaryCharactersWithoutConflatingAbsentFields() {
    byte[] input = emptyQuery();
    put(input, KEYWORD, "e8aa9ef09f9880");
    put(input, ACTION, "41c3a9");
    put(input, PATH, "2fe99fb3f09f9880");
    put(input, 257, "52455155455354");
    put(input, 593, "5741524e");
    put(input, 601, "3230323631313139303830303030303030");
    put(input, 618, "3230323631313139303930303030303030");

    LogSearchRequestData populated = decode(input);
    assertEquals(Optional.of("語😀"), populated.keyword());
    assertEquals(Optional.of("Aé"), populated.action());
    assertEquals(Optional.of("/音😀"), populated.path());
    assertEquals(Optional.of(LogType.REQUEST), populated.logType());
    assertEquals(Optional.of(LogLevel.WARN), populated.level());
    assertEquals(Optional.of(Instant.parse("2026-11-18T23:00:00Z")), populated.fromAt());
    assertEquals(Optional.of(Instant.parse("2026-11-19T00:00:00Z")), populated.toAt());

    LogSearchRequestData absent = decode(emptyQuery());
    assertEquals(Optional.empty(), absent.keyword());
    assertEquals(Optional.empty(), absent.action());
    assertEquals(Optional.empty(), absent.path());
    assertEquals(Optional.empty(), absent.logType());
    assertEquals(Optional.empty(), absent.level());
    assertEquals(Optional.empty(), absent.fromAt());
    assertEquals(Optional.empty(), absent.toAt());
    assertEquals(1, absent.page());
    assertEquals(100, absent.pageSize());
  }

  @Test
  void rejectsMalformedAndNonNfcInputAtEachFreeTextPosition() {
    for (int offset : List.of(KEYWORD, ACTION, PATH)) {
      assertRejected(offset, "eda080", "text field contains invalid UTF-8");
      assertRejected(offset, "65cc81", "text field is not NFC canonical");
    }
  }

  private static void assertRejected(int offset, String vector, String expected) {
    byte[] input = emptyQuery();
    put(input, offset, vector);
    var failure = assertThrows(PermanentProtocolException.class, () -> decode(input));
    assertEquals(expected, failure.getMessage());
  }

  private static byte[] emptyQuery() {
    byte[] input = new byte[656];
    Arrays.fill(input, (byte) 0x20);
    put(input, 635, "303030303031");
    put(input, 641, "313030");
    return input;
  }

  private static void put(byte[] input, int position, String vector) {
    byte[] bytes = HEX.parseHex(vector);
    System.arraycopy(bytes, 0, input, position - 1, bytes.length);
  }

  private static LogSearchRequestData decode(byte[] input) {
    var fields = PayloadCodec.standard().decode(LOG_SEARCH, input, List.of(), false);
    return assertInstanceOf(LogSearchRequestData.class, PayloadTypeCatalog.decode(fields).data());
  }
}
