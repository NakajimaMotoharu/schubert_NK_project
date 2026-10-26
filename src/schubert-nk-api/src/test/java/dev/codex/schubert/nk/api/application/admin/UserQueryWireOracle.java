package dev.codex.schubert.nk.api.application.admin;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.Locale;
import java.util.UUID;

/** UI236 §§3/5, SS321/324: fixed Test profiles, not Production request decoding. */
final class UserQueryWireOracle {
  private UserQueryWireOracle() {}

  static byte[] wire(
      String layout,
      UUID request,
      UUID response,
      Instant time,
      Instant rowAt,
      String code,
      int count,
      long total,
      int page,
      long target,
      boolean optional) {
    boolean detail =
        switch (layout) {
          case "USRREQ01" -> false;
          case "UDTREQ01" -> true;
          default -> throw new IllegalArgumentException("unknown fixture profile");
        };
    boolean success = code.equals("0000") || code.equals("0200");
    int dataLength = detail ? 320 : 48;
    int recordLength = detail ? 0 : 168;
    int records = success ? count : 0;
    byte[] bytes = new byte[256 + dataLength + recordLength * records];
    Arrays.fill(bytes, (byte) 32);
    put(bytes, 0, "SCHBNK01001");
    put(bytes, 11, detail ? "UDTRSP01" : "USRRSP01");
    put(bytes, 19, "001SS");
    put(bytes, 24, response.toString());
    put(bytes, 60, request.toString());
    put(bytes, 96, time(time));
    put(bytes, 113, "b".repeat(64));
    put(
        bytes,
        177,
        String.format(
            Locale.ROOT, "0256%06d%06d%06d%09d", dataLength, recordLength, records, bytes.length));
    put(bytes, 208, code);
    if (detail) {
      put(bytes, 256, String.format(Locale.ROOT, "%012d", success ? target : 0));
      for (int offset : new int[] {379, 396, 413})
        put(bytes, offset, success ? time(rowAt) : "0".repeat(17));
      put(bytes, 430, success && optional ? "002" : "000");
      put(bytes, 433, "000000000");
      if (success) {
        put(bytes, 268, "u" + target);
        put(bytes, 332, "USER");
        put(bytes, 337, "ACTIVE");
        if (optional) {
          put(bytes, 345, time(rowAt));
          put(bytes, 362, time(rowAt));
        }
        put(bytes, 442, "SYSTEM");
        put(bytes, 506, "SYSTEM");
      }
    } else {
      if (success)
        put(
            bytes,
            256,
            String.format(
                Locale.ROOT,
                "%06d050%09d%06d%09d%09d",
                page,
                total,
                Math.max(1, (total + 49) / 50),
                total == 0 ? 0 : (page - 1L) * 50 + 1,
                Math.min(page * 50L, total)));
      else put(bytes, 256, "0".repeat(42));
      for (int i = 1; i <= records; i++) {
        int offset = 304 + (i - 1) * 168;
        put(bytes, offset, String.format(Locale.ROOT, "%012d", i));
        put(bytes, offset + 12, "u" + i);
        put(bytes, offset + 76, "USER");
        put(bytes, offset + 81, "ACTIVE");
        put(bytes, offset + 123, time(rowAt));
        put(bytes, offset + 140, time(rowAt));
        put(bytes, offset + 157, "000000000");
      }
    }
    return bytes;
  }

  private static String time(Instant at) {
    return DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS", Locale.ROOT)
        .withZone(ZoneId.of("Asia/Tokyo"))
        .format(at);
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] raw = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(raw, 0, bytes, offset, raw.length);
  }
}
