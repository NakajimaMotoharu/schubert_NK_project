package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Independent 0=SQL,1..4=unknown table; PG179/BAT087,121, never Production expected values. */
final class JdbcResourceCases {
  private JdbcResourceCases() {}

  record Sample(
      String body, String close, int first, int second, Throwable primary, Throwable secondary) {
    void install(Map<String, Throwable> thrown) {
      if (primary != null) thrown.put(body, primary);
      thrown.put(close, secondary);
    }

    void verify(Throwable actual) {
      Throwable identity = first >= 1 ? primary : second >= 1 ? secondary : null;
      if (identity != null) {
        assertSame(identity, actual, body + " " + first + "/" + second);
        assertEquals(first >= 1 ? 1 : 0, actual.getSuppressed().length);
        for (var safe : actual.getSuppressed()) fixed(safe);
      } else fixed(actual);
    }
  }

  static List<Sample> all() {
    var samples = new ArrayList<Sample>();
    for (var pair :
        List.of(
            List.of("row.next", "row.close"),
            List.of("statement.executeQuery", "statement.close"))) {
      for (int first = 0; first < 5; first++) {
        for (int second = 0; second < 5; second++) samples.add(sample(pair, first, second, false));
        if (first >= 1) samples.add(sample(pair, first, first, true));
      }
      for (int second = 0; second < 5; second++) samples.add(sample(pair, -1, second, false));
    }
    assertEquals(68, samples.size());
    return List.copyOf(samples);
  }

  private static Sample sample(List<String> pair, int first, int second, boolean same) {
    Throwable primary = first < 0 ? null : failure(first);
    return new Sample(
        pair.get(0), pair.get(1), first, second, primary, same ? primary : failure(second));
  }

  private static Throwable failure(int kind) {
    return switch (kind) {
      case 0 -> new SQLException("public SQL fixture");
      case 1 -> new IllegalArgumentException("public argument fixture");
      case 2 -> new IllegalStateException("public state fixture");
      case 3 -> new NullPointerException("public null fixture");
      case 4 -> new AssertionError("public fatal fixture");
      default -> throw new AssertionError("invalid fixture kind");
    };
  }

  private static void fixed(Throwable value) {
    assertInstanceOf(BatchRepositoryException.class, value);
    assertEquals("batch repository operation failed", value.getMessage());
    assertNull(value.getCause());
    assertEquals(0, value.getSuppressed().length);
  }
}
