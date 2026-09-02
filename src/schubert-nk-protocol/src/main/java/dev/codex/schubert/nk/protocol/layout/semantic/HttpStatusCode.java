package dev.codex.schubert.nk.protocol.layout.semantic;

import java.util.Objects;
import java.util.regex.Pattern;

/** HTTP status projected into an X3 wire field. Trace: UI 235, SS 351, PT-PRO-001-T04. */
public record HttpStatusCode(int value) {
  private static final Pattern WIRE = Pattern.compile("[0-9]{3}");

  public HttpStatusCode {
    if (value < 100 || value > 599) {
      throw new IllegalArgumentException("HTTP status must be between 100 and 599");
    }
  }

  public static HttpStatusCode parse(String wireValue) {
    Objects.requireNonNull(wireValue, "wireValue");
    if (!WIRE.matcher(wireValue).matches()) {
      throw new IllegalArgumentException("HTTP status must contain exactly three ASCII digits");
    }
    return new HttpStatusCode(Integer.parseInt(wireValue));
  }

  public String wireValue() {
    return Integer.toString(value);
  }
}
