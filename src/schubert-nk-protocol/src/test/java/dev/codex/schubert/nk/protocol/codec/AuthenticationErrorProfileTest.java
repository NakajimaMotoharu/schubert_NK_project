package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalog;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** UI234 §3 byte offsets, independently assembled; PT-CODEC-AUTHERR-001, BUG-023. */
final class AuthenticationErrorProfileTest {
  private static final String LOGIN_RESPONSE_LAYOUT = "LGNRSP01";
  private static final String RETRY_AFTER_FIELD = "Retry after秒";
  private static final String USER_MESSAGE_FIELD = "利用者message";

  @Test
  void loginLockAndFailurePreserveOnlyApprovedErrorFields() {
    var values =
        new PayloadValues(
            new LayoutId(LOGIN_RESPONSE_LAYOUT),
            new FieldValueSet(
                Map.of(
                    RETRY_AFTER_FIELD, new FieldValue.Numeric(900),
                    USER_MESSAGE_FIELD,
                        new FieldValue.Text("ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。"))),
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
            .decode(new LayoutId(LOGIN_RESPONSE_LAYOUT), expected, List.of(), ResultCode.LOCKED);
    assertEquals(new FieldValue.Numeric(900), decoded.data().getOrUnset(RETRY_AFTER_FIELD));
    assertEquals(
        new FieldValue.Text("ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。"),
        decoded.data().getOrUnset(USER_MESSAGE_FIELD));
    for (int retry : new int[] {0, 1, 900}) {
      var data = new LinkedHashMap<String, FieldValue>();
      data.put(RETRY_AFTER_FIELD, new FieldValue.Numeric(retry));
      data.put("Username", new FieldValue.Text("synthetic-identity-canary"));
      data.put("認証context ID", new FieldValue.Text("e".repeat(64)));
      data.put("残り試行回数", new FieldValue.Numeric(5));
      byte[] golden = loginGolden(retry, "");
      assertArrayEquals(golden, encode(data, ResultCode.LOCKED));
      var read =
          PayloadCodec.standard()
              .decode(new LayoutId(LOGIN_RESPONSE_LAYOUT), golden, List.of(), ResultCode.LOCKED);
      assertEquals(new FieldValue.Numeric(retry), read.data().getOrUnset(RETRY_AFTER_FIELD));
      for (String field :
          List.of("Username", "Role", "認証context ID", "発行日時", "期限日時", "残り試行回数", USER_MESSAGE_FIELD))
        assertSame(FieldValue.Unset.INSTANCE, read.data().getOrUnset(field));
    }
    String failure = "ユーザー名またはパスワードが正しくありません。";
    assertArrayEquals(
        loginGolden(0, failure),
        encode(
            Map.of(USER_MESSAGE_FIELD, new FieldValue.Text(failure)),
            ResultCode.AUTHENTICATION_FAILED));
    assertArrayEquals(
        loginGolden(0, failure),
        encode(
            Map.of(
                RETRY_AFTER_FIELD,
                new FieldValue.Numeric(0),
                USER_MESSAGE_FIELD,
                new FieldValue.Text(failure)),
            ResultCode.TEMPORARY_FAILURE));
  }

  @Test
  void malformedLoginErrorBoundariesAndTypesAreRejected() {
    for (FieldValue retry :
        List.of(
            new FieldValue.Numeric(-1),
            new FieldValue.Numeric(901),
            new FieldValue.Text("900"),
            FieldValue.Unset.INSTANCE))
      assertThrows(
          MessageEncodingException.class,
          () -> encode(Map.of(RETRY_AFTER_FIELD, retry), ResultCode.LOCKED));
    for (FieldValue retry : List.of(new FieldValue.Numeric(1), new FieldValue.Text("0")))
      assertThrows(
          MessageEncodingException.class,
          () -> encode(Map.of(RETRY_AFTER_FIELD, retry), ResultCode.AUTHENTICATION_FAILED));
    for (String invalid : List.of("x".repeat(257), "bad\nmessage", "trailing "))
      assertThrows(
          FieldEncodingException.class,
          () ->
              encode(
                  Map.of(USER_MESSAGE_FIELD, new FieldValue.Text(invalid)),
                  ResultCode.AUTHENTICATION_FAILED));
    assertThrows(NullPointerException.class, () -> new FieldValue.Text(null));
    assertThrows(
        MessageEncodingException.class,
        () ->
            encode(
                Map.of(USER_MESSAGE_FIELD, new FieldValue.Numeric(1)),
                ResultCode.AUTHENTICATION_FAILED));
    String max = "あ".repeat(85) + "x";
    byte[] golden = loginGolden(900, max);
    assertEquals(256, max.getBytes(StandardCharsets.UTF_8).length);
    assertArrayEquals(
        golden,
        encode(
            Map.of(
                RETRY_AFTER_FIELD,
                new FieldValue.Numeric(900),
                USER_MESSAGE_FIELD,
                new FieldValue.Text(max)),
            ResultCode.LOCKED));
    assertEquals(
        new FieldValue.Text(max),
        PayloadCodec.standard()
            .decode(new LayoutId(LOGIN_RESPONSE_LAYOUT), golden, List.of(), ResultCode.LOCKED)
            .data()
            .getOrUnset(USER_MESSAGE_FIELD));
    for (int offset : new int[] {0, 64, 69, 133, 150, 173}) {
      byte[] bad = loginGolden(900, "");
      bad[offset] = '1';
      assertThrows(
          PermanentProtocolException.class,
          () ->
              PayloadCodec.standard()
                  .decode(new LayoutId(LOGIN_RESPONSE_LAYOUT), bad, List.of(), ResultCode.LOCKED));
    }
    for (byte[] bad : List.of(loginGolden(901, ""), loginGolden(0, "bad\nmessage")))
      assertThrows(
          PermanentProtocolException.class,
          () ->
              PayloadCodec.standard()
                  .decode(new LayoutId(LOGIN_RESPONSE_LAYOUT), bad, List.of(), ResultCode.LOCKED));
    byte[] badDigit = loginGolden(900, "");
    badDigit[167] = '-';
    assertThrows(
        PermanentProtocolException.class,
        () ->
            PayloadCodec.standard()
                .decode(
                    new LayoutId(LOGIN_RESPONSE_LAYOUT), badDigit, List.of(), ResultCode.LOCKED));
    assertThrows(
        PermanentProtocolException.class,
        () ->
            PayloadCodec.standard()
                .decode(
                    new LayoutId(LOGIN_RESPONSE_LAYOUT),
                    loginGolden(1, ""),
                    List.of(),
                    ResultCode.AUTHENTICATION_FAILED));
  }

  @Test
  void allOtherResponseErrorProfilesRetainTheirIndividualContracts() throws IOException {
    List<String[]> independentLayouts = independentRows("layouts-ui233.tsv");
    List<String[]> independentFields = independentRows("fields-ui234-236.tsv");
    int responses = 0;
    for (var layout : LayoutFieldCatalog.standard().all()) {
      if (layout.layout().messageKind() != MessageKind.RESPONSE) continue;
      responses++;
      for (ResultCode code : ResultCode.values()) {
        if (code.usesSuccessProfile()) continue;
        var fields = new LinkedHashMap<String, FieldValue>();
        String[] definition =
            independentLayouts.stream()
                .filter(row -> row[0].equals(layout.id().value()))
                .findFirst()
                .orElseThrow();
        byte[] expected = new byte[Integer.parseInt(definition[3])];
        Arrays.fill(expected, (byte) ' ');
        for (String[] field : independentFields) {
          if (!field[0].equals(layout.id().value()) || !field[1].equals("DATA")) continue;
          if (field[5].equals("N")) {
            int start = Integer.parseInt(field[3]) - 1;
            Arrays.fill(expected, start, start + Integer.parseInt(field[4]), (byte) '0');
          }
          if (field[6].equals("F")) assertEquals("Reserved", field[2]);
        }
        if (layout.id().value().equals(LOGIN_RESPONSE_LAYOUT)) {
          fields.put(USER_MESSAGE_FIELD, new FieldValue.Text("安全な利用者message"));
          if (code == ResultCode.LOCKED) fields.put(RETRY_AFTER_FIELD, new FieldValue.Numeric(900));
          expected = loginGolden(code == ResultCode.LOCKED ? 900 : 0, "安全な利用者message");
        }
        if (layout.id().value().equals("NTCRSP01") && code == ResultCode.NOT_CANCELLABLE) {
          fields.put("更新後状態", new FieldValue.Text("PROCESSING"));
          System.arraycopy("PROCESSING".getBytes(StandardCharsets.US_ASCII), 0, expected, 0, 10);
        }
        var encoded =
            PayloadCodec.standard()
                .encode(new PayloadValues(layout.id(), new FieldValueSet(fields), List.of()), code);
        assertArrayEquals(expected, encoded.copyData(), layout.id().value() + "/" + code);
        assertEquals(0, encoded.recordCount());
        var decoded = PayloadCodec.standard().decode(layout.id(), expected, List.of(), code);
        for (var field : fields.entrySet())
          assertEquals(field.getValue(), decoded.data().getOrUnset(field.getKey()));
      }
    }
    assertEquals(31, responses);
  }

  private static byte[] encode(Map<String, FieldValue> data, ResultCode code) {
    return PayloadCodec.standard()
        .encode(
            new PayloadValues(
                new LayoutId(LOGIN_RESPONSE_LAYOUT), new FieldValueSet(data), List.of()),
            code)
        .copyData();
  }

  private static List<String[]> independentRows(String filename) throws IOException {
    try (var input =
        java.util.Objects.requireNonNull(
            AuthenticationErrorProfileTest.class.getResourceAsStream("/protocol/" + filename))) {
      return new String(input.readAllBytes(), StandardCharsets.UTF_8)
          .lines()
          .filter(line -> !line.startsWith("#"))
          .map(line -> line.split("\t", -1))
          .toList();
    }
  }

  private static byte[] loginGolden(int retry, String message) {
    byte[] bytes = new byte[432];
    Arrays.fill(bytes, (byte) ' ');
    byte[] digits =
        String.format(java.util.Locale.ROOT, "%06d000", retry).getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(digits, 0, bytes, 167, 9);
    byte[] text = message.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, bytes, 176, text.length);
    return bytes;
  }
}
