package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** UI236 §8.1/11.1, SS322/323, P013-01, YKT-2328 site 2. */
final class QuestionNotificationWireTest {
  private static final LayoutId QUESTIONS = new LayoutId("QSSREQ01");
  private static final LayoutId NOTIFICATIONS = new LayoutId("NTSREQ01");
  private static final int KEYWORD = 1;
  private static final int USERNAME = 257;
  private static final int NOTIFICATION_TYPE = 1;
  private static final int NOTIFICATION_FROM = 13;
  private static final int NOTIFICATION_TO = 30;
  private static final String JANUARY_2024 = "20240101090000000";
  private static final String JANUARY_2025 = "20250101090000000";

  @Test
  void qss001DecodesExactKeywordUsernameAndBlankFields() {
    byte[] input = base(384, 367, 373);
    hex(input, KEYWORD, "e5958fe9a18cf09f9880");
    hex(input, USERNAME, "436166c3a9");
    ascii(input, 321, "UNANSWERED");
    ascii(input, 333, JANUARY_2024);
    ascii(input, 350, JANUARY_2025);
    var row = decodeQuestion(input);
    assertEquals(Optional.of("問題😀"), row.keyword());
    assertEquals(Optional.of("Café"), row.username());
    assertEquals(Optional.of(AnswerState.UNANSWERED), row.answerState());
    assertEquals(Optional.of(Instant.parse("2024-01-01T00:00:00Z")), row.submittedFrom());
    assertEquals(Optional.of(Instant.parse("2025-01-01T00:00:00Z")), row.submittedTo());
    assertEquals(1, row.page());
    assertEquals(50, row.pageSize());

    var absent = decodeQuestion(base(384, 367, 373));
    assertEquals(Optional.empty(), absent.keyword());
    assertEquals(Optional.empty(), absent.username());
    assertEquals(Optional.empty(), absent.answerState());
    assertEquals(Optional.empty(), absent.submittedFrom());
    assertEquals(Optional.empty(), absent.submittedTo());
  }

  @Test
  void qss002RejectsMalformedAndNonNfcAtBothTextOffsets() {
    for (int start : List.of(KEYWORD, USERNAME)) {
      byte[] badEncoding = base(384, 367, 373);
      hex(badEncoding, start, "edb080");
      var malformed =
          assertThrows(PermanentProtocolException.class, () -> decodeQuestion(badEncoding));
      assertEquals("text field contains invalid UTF-8", malformed.getMessage());

      byte[] nonNfc = base(384, 367, 373);
      hex(nonNfc, start, "65cc81");
      var decomposed = assertThrows(PermanentProtocolException.class, () -> decodeQuestion(nonNfc));
      assertEquals("text field is not NFC canonical", decomposed.getMessage());
    }
  }

  @Test
  void nts001DecodesEveryDefinedTypeAndTheExactUtcDateBoundary() {
    for (var pair :
        Map.of(
                "ACCEPTED", NotificationType.ACCEPTED,
                "COMPLETED", NotificationType.COMPLETED,
                "ERROR", NotificationType.ERROR)
            .entrySet()) {
      var row = decodeNotification(notification(pair.getKey(), JANUARY_2024, JANUARY_2025));
      assertEquals(Optional.of(pair.getValue()), row.notificationType());
      assertEquals(Optional.of(Instant.parse("2024-01-01T00:00:00Z")), row.submittedFrom());
      assertEquals(Optional.of(Instant.parse("2025-01-01T00:00:00Z")), row.submittedTo());
      assertEquals(1, row.page());
      assertEquals(50, row.pageSize());
    }
    var absent = decodeNotification(base(64, 47, 53));
    assertEquals(Optional.empty(), absent.notificationType());
    assertEquals(Optional.empty(), absent.submittedFrom());
    assertEquals(Optional.empty(), absent.submittedTo());
  }

  @Test
  void nts002RejectsUnknownTypeInvalidDateReversalAndOneMillisecondOver() {
    assertThrows(
        LayoutValidationException.class,
        () -> decodeNotification(notification("UNKNOWN", JANUARY_2024, JANUARY_2025)));
    assertThrows(
        LayoutValidationException.class,
        () -> decodeNotification(notification("ACCEPTED", "20240230090000000", JANUARY_2025)));
    var reversed =
        assertThrows(
            LayoutValidationException.class,
            () -> decodeNotification(notification("COMPLETED", JANUARY_2025, JANUARY_2024)));
    assertEquals("layout semantic violation: date range is reversed", reversed.getMessage());
    var tooLong =
        assertThrows(
            LayoutValidationException.class,
            () -> decodeNotification(notification("ERROR", JANUARY_2024, "20250101090000001")));
    assertEquals("layout semantic violation: date range is too long", tooLong.getMessage());
  }

  private static byte[] notification(String type, String from, String to) {
    byte[] input = base(64, 47, 53);
    ascii(input, NOTIFICATION_TYPE, type);
    ascii(input, NOTIFICATION_FROM, from);
    ascii(input, NOTIFICATION_TO, to);
    return input;
  }

  private static byte[] base(int length, int page, int size) {
    byte[] input = new byte[length];
    Arrays.fill(input, (byte) ' ');
    ascii(input, page, "000001");
    ascii(input, size, "050");
    return input;
  }

  private static void hex(byte[] input, int start, String value) {
    put(input, start, HexFormat.of().parseHex(value));
  }

  private static void ascii(byte[] input, int start, String value) {
    put(input, start, value.getBytes(StandardCharsets.US_ASCII));
  }

  private static void put(byte[] input, int start, byte[] value) {
    System.arraycopy(value, 0, input, start - 1, value.length);
  }

  private static QuestionSearchRequestData decodeQuestion(byte[] input) {
    return assertInstanceOf(QuestionSearchRequestData.class, decode(QUESTIONS, input));
  }

  private static NotificationSearchRequestData decodeNotification(byte[] input) {
    return assertInstanceOf(NotificationSearchRequestData.class, decode(NOTIFICATIONS, input));
  }

  private static Object decode(LayoutId layout, byte[] input) {
    var fields = PayloadCodec.standard().decode(layout, input, List.of(), false);
    return PayloadTypeCatalog.decode(fields).data();
  }
}
