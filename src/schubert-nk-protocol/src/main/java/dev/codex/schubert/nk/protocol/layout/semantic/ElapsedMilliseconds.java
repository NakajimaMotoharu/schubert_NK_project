package dev.codex.schubert.nk.protocol.layout.semantic;

import java.util.Objects;
import java.util.regex.Pattern;

/** Elapsed time projected into an X9 wire field. Trace: UI 235, SS 351, PT-PRO-001-T04. */
public record ElapsedMilliseconds(int value) {
  private static final int MAXIMUM = 999_999_999;
  private static final Pattern WIRE = Pattern.compile("[0-9]{1,9}");

  public ElapsedMilliseconds {
    if (value < 0 || value > MAXIMUM) {
      throw new IllegalArgumentException("elapsed milliseconds must be between 0 and 999999999");
    }
  }

  public static ElapsedMilliseconds parse(String wireValue) {
    Objects.requireNonNull(wireValue, "wireValue");
    if (!WIRE.matcher(wireValue).matches()) {
      throw new IllegalArgumentException("elapsed milliseconds must contain 1 to 9 ASCII digits");
    }
    return new ElapsedMilliseconds(Integer.parseInt(wireValue));
  }

  public String wireValue() {
    return Integer.toString(value);
  }
}
