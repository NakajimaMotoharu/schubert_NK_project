package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-PRO-USER-WIRE-001..004; UI236 sections 4.1 and 6.3, SS322/323. */
final class UserCommandWireUnicodeTest {
  private static final LayoutId CREATE = new LayoutId("UCRREQ01");
  private static final LayoutId RESET = new LayoutId("UPWREQ01");
  private static final int CREATE_TEXT_START = 65;
  private static final int RESET_TEXT_START = 13;
  private static final String FIXTURE_UUID = new UUID(0, 1).toString();

  @Test
  void createAccepts128TwoByteCodePointsWithoutConsumingRoleOrEnabled() {
    var result = assertInstanceOf(UserCreateRequestData.class, decode(CREATE, "c3a9".repeat(128)));
    assertTrue("é".repeat(128).equals(result.initialPassword()), "synthetic field preserved");
    assertEquals("fixture-user", result.username());
    assertEquals(UserRole.ADMIN, result.role());
    assertTrue(result.enabled());
  }

  @Test
  void resetAccepts64FourByteCodePointsWithoutConsumingVersion() {
    var result =
        assertInstanceOf(PasswordResetRequestData.class, decode(RESET, "f09f9880".repeat(64)));
    assertTrue("😀".repeat(64).equals(result.newPassword()), "synthetic field preserved");
    assertEquals(2L, result.userId().value());
    assertEquals(17L, result.expectedVersion());
  }

  @Test
  void bothFieldsRejectEncodedSurrogateAndTruncationAtTheirOwnBoundary() {
    for (LayoutId layout : List.of(CREATE, RESET)) {
      for (String hex : List.of("41".repeat(12) + "eda080", "41".repeat(255) + "f0")) {
        var failure = assertThrows(PermanentProtocolException.class, () -> decode(layout, hex));
        assertEquals("text field contains invalid UTF-8", failure.getMessage());
      }
    }
  }

  @Test
  void bothFieldsRejectNoncanonicalButWellFormedUtf8() {
    for (LayoutId layout : List.of(CREATE, RESET)) {
      var failure =
          assertThrows(
              PermanentProtocolException.class, () -> decode(layout, "41".repeat(12) + "65cc81"));
      assertEquals("text field is not NFC canonical", failure.getMessage());
    }
  }

  private static PayloadData decode(LayoutId layout, String utf8Hex) {
    boolean create = layout.equals(CREATE);
    byte[] bytes = new byte[create ? 372 : 324];
    Arrays.fill(bytes, (byte) ' ');
    byte[] text = HexFormat.of().parseHex(utf8Hex);
    if (create) {
      putAscii(bytes, 1, "fixture-user");
      putAscii(bytes, 321, "ADMIN");
      putAscii(bytes, 326, "1");
      putAscii(bytes, 327, FIXTURE_UUID);
      System.arraycopy(text, 0, bytes, CREATE_TEXT_START - 1, text.length);
    } else {
      putAscii(bytes, 1, "000000000002");
      putAscii(bytes, 269, "000000017");
      putAscii(bytes, 278, FIXTURE_UUID);
      System.arraycopy(text, 0, bytes, RESET_TEXT_START - 1, text.length);
    }
    return PayloadTypeCatalog.decode(
            PayloadCodec.standard().decode(layout, bytes, List.of(), false))
        .data();
  }

  private static void putAscii(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(bytes, 0, target, offset - 1, bytes.length);
  }
}
