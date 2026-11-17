package dev.codex.schubert.nk.web.media;

import java.util.Objects;
import java.util.Optional;

/**
 * First-range selection only; no HTTP, authentication or file ownership. NK-MED-001;
 * FUN-005..007/PER-004..006; UI223/237; SS333 §10; PT-MED-001..004.
 */
public final class HttpByteRangeParser {
  private static final long MAX_BODY = 1_048_576;

  /** PG-D1175/BUG3178: this namespace never owns an instance, including internal misuse. */
  private HttpByteRangeParser() {
    throw new AssertionError("static utility");
  }

  public sealed interface Selection permits Full, Partial, Unsatisfiable {}

  public record Full(long length) implements Selection {
    public Full {
      if (length <= 0) throw new IllegalArgumentException("full media length must be positive");
    }
  }

  public record Partial(long start, long end) implements Selection {
    public Partial {
      if (start < 0 || end < start || end - start >= MAX_BODY)
        throw new IllegalArgumentException("partial media interval is invalid");
    }

    public long length() {
      return end - start + 1;
    }
  }

  public enum Unsatisfiable implements Selection {
    INSTANCE
  }

  /** Absent header means full; a present invalid header or nonpositive size selects no bytes. */
  public static Selection parseFirst(Optional<String> header, long total) {
    Objects.requireNonNull(header, "header");
    if (total <= 0) return Unsatisfiable.INSTANCE;
    if (header.isEmpty()) return new Full(total);
    String value = header.orElseThrow();
    if (!value.regionMatches(true, 0, "bytes=", 0, 6)) return Unsatisfiable.INSTANCE;
    String spec = value.substring(6);
    int comma = spec.indexOf(',');
    if (comma >= 0) spec = spec.substring(0, comma);
    spec = spec.trim();
    int dash = spec.indexOf('-');
    if (dash < 0 || dash != spec.lastIndexOf('-')) return Unsatisfiable.INSTANCE;
    try {
      String left = spec.substring(0, dash);
      String right = spec.substring(dash + 1);
      long start;
      long requestedLast;
      if (left.isEmpty()) {
        long suffix = decimal(right);
        if (suffix == 0) return Unsatisfiable.INSTANCE;
        start = Math.max(Math.subtractExact(total, suffix), 0);
        requestedLast = total - 1;
      } else {
        start = decimal(left);
        requestedLast = right.isEmpty() ? total - 1 : decimal(right);
      }
      if (start >= total || requestedLast < start) return Unsatisfiable.INSTANCE;
      long last = Math.min(Math.min(requestedLast, total - 1), Math.addExact(start, MAX_BODY - 1));
      return new Partial(start, last);
    } catch (ArithmeticException | NumberFormatException invalid) {
      return Unsatisfiable.INSTANCE;
    }
  }

  private static long decimal(String value) {
    if (!value.matches("[0-9]+")) throw new NumberFormatException("invalid Range decimal");
    return Long.parseLong(value);
  }
}
