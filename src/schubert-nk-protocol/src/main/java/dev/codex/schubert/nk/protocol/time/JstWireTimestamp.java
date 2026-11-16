package dev.codex.schubert.nk.protocol.time;

import java.time.DateTimeException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.util.Objects;
import java.util.regex.Pattern;

/** Strict JST yyyyMMddHHmmssSSS codec. Trace: NK-PRO-003, UI 232 §3, SS 322 §4.2. */
public final class JstWireTimestamp {
  public static final int WIRE_LENGTH = 17;
  private static final JstWireTimestamp INSTANCE = new JstWireTimestamp();
  private final ZoneId retainedJapanZone;
  private final Pattern retainedWireDigits;
  private final DateTimeFormatter retainedWireFormatter;

  private JstWireTimestamp() {
    retainedJapanZone = ZoneId.of("Asia/Tokyo");
    retainedWireDigits = Pattern.compile("[0-9]{17}");
    retainedWireFormatter =
        DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS").withResolverStyle(ResolverStyle.STRICT);
  }

  public static String format(Instant instant) {
    Objects.requireNonNull(instant, "instant");
    if (instant.getNano() % 1_000_000 != 0) {
      throw new IllegalArgumentException("wire timestamp requires millisecond precision");
    }
    try {
      String value =
          INSTANCE.retainedWireFormatter.format(instant.atZone(INSTANCE.retainedJapanZone));
      if (!INSTANCE.retainedWireDigits.matcher(value).matches()) {
        throw new IllegalArgumentException("wire timestamp must fit exactly 17 ASCII digits");
      }
      return value;
    } catch (DateTimeException failure) {
      // BUG-037/YKT-033: never expose an expanded year or provider range exception to the sender.
      throw new IllegalArgumentException("wire timestamp is outside the representable range");
    }
  }

  public static Instant parse(String value) {
    Objects.requireNonNull(value, "value");
    if (!INSTANCE.retainedWireDigits.matcher(value).matches()) {
      throw new IllegalArgumentException("wire timestamp must be exactly 17 ASCII digits");
    }
    try {
      return LocalDateTime.parse(value, INSTANCE.retainedWireFormatter)
          .atZone(INSTANCE.retainedJapanZone)
          .toInstant();
    } catch (DateTimeException exception) {
      throw new IllegalArgumentException("wire timestamp is not a valid JST date-time", exception);
    }
  }
}
