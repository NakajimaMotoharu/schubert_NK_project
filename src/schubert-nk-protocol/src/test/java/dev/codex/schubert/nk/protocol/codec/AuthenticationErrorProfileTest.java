package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** UI234 §3 byte offsets, independently assembled; PT-CODEC-AUTHERR-001, BUG-023. */
final class AuthenticationErrorProfileTest {
  @Test
  void loginLockAndFailurePreserveOnlyApprovedErrorFields() {
    var values =
        new PayloadValues(
            new LayoutId("LGNRSP01"),
            new FieldValueSet(
                Map.of(
                    "Retry after秒", new FieldValue.Numeric(900),
                    "利用者message", new FieldValue.Text("ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。"))),
            List.of());
    byte[] expected = new byte[432];
    Arrays.fill(expected, (byte) ' ');
    System.arraycopy("000900000".getBytes(StandardCharsets.US_ASCII), 0, expected, 167, 9);
    byte[] text = "ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。".getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, expected, 176, text.length);
    assertArrayEquals(
        expected, PayloadCodec.standard().encode(values, ResultCode.LOCKED).copyData());
    var decoded =
        PayloadCodec.standard()
            .decode(new LayoutId("LGNRSP01"), expected, List.of(), ResultCode.LOCKED);
    assertEquals(new FieldValue.Numeric(900), decoded.data().getOrUnset("Retry after秒"));
    assertEquals(
        new FieldValue.Text("ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。"),
        decoded.data().getOrUnset("利用者message"));
  }
}
