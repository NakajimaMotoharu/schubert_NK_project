package dev.codex.schubert.nk.batch.monitoring;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.util.OptionalDouble;

/** Health input conversion only; PG-D531/HEAPINPUT001..009/spec1591, SS351 integer thresholds. */
final class HealthUsageRatio {
  private static final BigInteger HUNDRED = BigInteger.valueOf(100);

  OptionalDouble fromUsed(long used, long maximum) {
    if (maximum <= 0 || used < 0 || used > maximum) return OptionalDouble.empty();
    BigInteger numerator = BigInteger.valueOf(used).multiply(HUNDRED);
    BigInteger denominator = BigInteger.valueOf(maximum);
    double value =
        new BigDecimal(numerator)
            .divide(new BigDecimal(denominator), MathContext.DECIMAL128)
            .doubleValue();
    double firstLargerInteger = numerator.divide(denominator).doubleValue() + 1;
    return OptionalDouble.of(
        value >= firstLargerInteger ? Math.nextDown(firstLargerInteger) : value);
  }
}
