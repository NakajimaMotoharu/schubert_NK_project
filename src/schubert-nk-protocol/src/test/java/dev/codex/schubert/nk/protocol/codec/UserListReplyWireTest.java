package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import org.junit.jupiter.api.Test;

/** USRRSP01, UI234 §2, UI236 §3.3, SS323, P016-15, YKT-2328 site 34. */
final class UserListReplyWireTest {
  private static final int USERNAME_START = 13;
  private static final LayoutId USER_LIST = new LayoutId("USRRSP01");
  private static final String ASTRAL_HEX = "f09f9880";
  private static final String ONE_NINE_DIGITS = "000000001";

  @Test
  void usr001DecodesNfcAndPreservesTheNextFieldAtThe64ByteLimit() {
    var shortName = decode("e5908d" + ASTRAL_HEX);
    assertEquals("名😀", shortName.username());
    assertEquals(UserRole.ADMIN, shortName.role());

    var fullName = decode("41".repeat(60) + ASTRAL_HEX);
    assertEquals("A".repeat(60) + "😀", fullName.username());
    assertEquals(UserRole.ADMIN, fullName.role());
  }

  @Test
  void usr002RejectsTheAllSpaceMandatoryField() {
    var failure = assertThrows(PermanentProtocolException.class, () -> decode(""));
    assertEquals("mandatory text field is empty", failure.getMessage());
  }

  @Test
  void usr003RejectsSurrogateEncodingAndTruncationAtTheFieldEnd() {
    for (String bytes : List.of("eda080", "41".repeat(63) + "f0")) {
      var failure = assertThrows(PermanentProtocolException.class, () -> decode(bytes));
      assertEquals("text field contains invalid UTF-8", failure.getMessage());
    }
  }

  @Test
  void usr004RejectsValidUtf8ThatIsNotNfc() {
    var failure = assertThrows(PermanentProtocolException.class, () -> decode("65cc81"));
    assertEquals("text field is not NFC canonical", failure.getMessage());
  }

  private static UserRecord decode(String nameHex) {
    byte[] data = new byte[48];
    Arrays.fill(data, (byte) ' ');
    ascii(data, 1, "000001");
    ascii(data, 7, "050");
    ascii(data, 10, ONE_NINE_DIGITS);
    ascii(data, 19, "000001");
    ascii(data, 25, ONE_NINE_DIGITS);
    ascii(data, 34, ONE_NINE_DIGITS);

    byte[] record = new byte[168];
    Arrays.fill(record, (byte) ' ');
    ascii(record, 1, "000000000001");
    put(record, USERNAME_START, HexFormat.of().parseHex(nameHex));
    ascii(record, 77, "ADMIN");
    ascii(record, 82, "ACTIVE");
    ascii(record, 124, "20260101090000000");
    ascii(record, 141, "20260101090000000");
    ascii(record, 158, ONE_NINE_DIGITS);
    var decoded =
        PayloadCodec.standard().decode(USER_LIST, data, List.of(record), ResultCode.SUCCESS);
    return assertInstanceOf(
        UserRecord.class, PayloadTypeCatalog.decode(decoded).records().getFirst());
  }

  private static void ascii(byte[] target, int start, String value) {
    put(target, start, value.getBytes(StandardCharsets.US_ASCII));
  }

  private static void put(byte[] target, int start, byte[] bytes) {
    System.arraycopy(bytes, 0, target, start - 1, bytes.length);
  }
}
