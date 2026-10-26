package dev.codex.schubert.nk.api.application.question;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.Locale;
import java.util.Objects;
import java.util.UUID;

/** UI236 §§8/9/11/12, SS323/324: Test-only fixed profiles; never consult a SUT request. */
final class QuestionQueryWireOracle {
  private static final String QUESTION_TEXT = "question";

  private QuestionQueryWireOracle() {}

  static byte[] wire(
      String layout,
      UUID request,
      UUID response,
      Instant at,
      Instant rowAt,
      String code,
      int count) {
    Objects.requireNonNull(layout);
    Objects.requireNonNull(request);
    Objects.requireNonNull(response);
    Objects.requireNonNull(at);
    Objects.requireNonNull(rowAt);
    Objects.requireNonNull(code);
    if (count < 0 || count > 1) throw new IllegalArgumentException("fixture count must be 0 or 1");
    String reply =
        switch (layout) {
          case "QSSREQ01" -> "QSSRSP01";
          case "QSDREQ01" -> "QSDRSP01";
          case "NTSREQ01" -> "NTSRSP01";
          case "NTDREQ01" -> "NTDRSP01";
          default -> throw new IllegalArgumentException("unknown fixture profile");
        };
    boolean success = code.equals("0000") || code.equals("0200");
    boolean detail = layout.equals("QSDREQ01") || layout.equals("NTDREQ01");
    boolean question = layout.equals("QSSREQ01") || layout.equals("QSDREQ01");
    int dataLength = detail ? (question ? 8352 : 8896) : 48;
    int recordLength = detail ? 0 : (question ? 672 : 624);
    int records = success && !detail ? count : 0;
    byte[] b = new byte[256 + dataLength + recordLength * records];
    Arrays.fill(b, (byte) 32);
    put(b, 0, "SCHBNK01001");
    put(b, 11, reply);
    put(b, 19, "001SS");
    put(b, 24, response.toString());
    put(b, 60, request.toString());
    put(b, 96, time(at));
    put(b, 113, "b".repeat(64));
    put(
        b,
        177,
        String.format(
            Locale.ROOT, "0256%06d%06d%06d%09d", dataLength, recordLength, records, b.length));
    put(b, 208, code);
    if (!detail) {
      put(
          b,
          256,
          success
              ? String.format(
                  Locale.ROOT, "000001050%09d000001%09d%09d", count, count == 0 ? 0 : 1, count)
              : "0".repeat(42));
      if (records > 0) {
        put(b, 304, "999999999999");
        put(b, 316, "0".repeat(26));
        if (question) {
          put(b, 342, "u1");
          put(b, 406, QUESTION_TEXT);
          put(b, 918, "UNANSWERED");
          put(b, 930, time(rowAt));
        } else {
          put(b, 342, "ACCEPTED");
          put(b, 354, "RECEIVED");
          put(b, 366, time(rowAt));
          put(b, 383, time(rowAt));
          put(b, 400, QUESTION_TEXT);
          put(b, 912, "0");
        }
      }
    } else {
      put(b, 256, success ? "999999999999" : "0".repeat(12));
      if (question) {
        put(b, 8562, success ? time(rowAt) : "0".repeat(17));
        if (success) {
          put(b, 268, "0".repeat(26));
          put(b, 294, "u1");
          put(b, 358, "UNANSWERED");
          put(b, 370, QUESTION_TEXT);
        }
      } else {
        put(b, 318, success ? time(rowAt) : "0".repeat(17));
        if (success) put(b, 403, "0");
        if (success) {
          put(b, 268, "0".repeat(26));
          put(b, 294, "ACCEPTED");
          put(b, 306, "RECEIVED");
          put(b, 404, QUESTION_TEXT);
          put(b, 9124, "999999999999");
        }
      }
    }
    return b;
  }

  private static String time(Instant at) {
    return DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS", Locale.ROOT)
        .withZone(ZoneId.of("Asia/Tokyo"))
        .format(at);
  }

  private static void put(byte[] bytes, int offset, String text) {
    byte[] value = text.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(value, 0, bytes, offset, value.length);
  }
}
