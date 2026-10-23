package dev.codex.schubert.nk.batch.monitoring;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.nio.file.FileStore;
import java.util.Objects;
import java.util.OptionalDouble;

/**
 * Borrowed filesystem health input, not a custom metric/exporter or path admission authority.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D529/FSINPUT001..007/spec1582.
 */
public final class FilesystemHealthObservation {
  private static final BigInteger HUNDRED = BigInteger.valueOf(100);
  private final FileStore store;

  public FilesystemHealthObservation(FileStore store) {
    this.store = Objects.requireNonNull(store, "filesystem health source");
  }

  /** IOException/invalid provider statistics are UNKNOWN, never invented zero usage. */
  public OptionalDouble read() {
    final long total;
    final long usable;
    try {
      total = store.getTotalSpace();
      usable = store.getUsableSpace();
    } catch (IOException unavailable) {
      return OptionalDouble.empty();
    }
    if (total <= 0 || usable < 0 || usable > total) return OptionalDouble.empty();
    BigInteger numerator = BigInteger.valueOf(total - usable).multiply(HUNDRED);
    BigInteger denominator = BigInteger.valueOf(total);
    double value =
        new BigDecimal(numerator)
            .divide(new BigDecimal(denominator), MathContext.DECIMAL128)
            .doubleValue();
    // Exact integer thresholds (80/90/95 included) must not be crossed by double rounding.
    double firstLargerInteger = numerator.divide(denominator).doubleValue() + 1;
    return OptionalDouble.of(
        value >= firstLargerInteger ? Math.nextDown(firstLargerInteger) : value);
  }
}
