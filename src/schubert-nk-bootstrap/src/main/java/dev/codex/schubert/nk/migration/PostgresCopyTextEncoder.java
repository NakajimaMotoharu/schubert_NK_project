package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Pure UTF8 COPY text data, never a database/SQL operation or load witness. NK-MIG-001;
 * MIG003005006/MIG-DAT004005/DAT004; UI254; SS331 section2/343 section10 SSC346;
 * PT-MIG-COPY001..012. Caller owns column-specific type, NFC, control and reference validation.
 */
@NullMarked
public final class PostgresCopyTextEncoder {
  public byte[] encodeRow(List<@Nullable String> fields) {
    return encodeRows(List.of(fields));
  }

  public byte[] encodeRows(List<? extends List<@Nullable String>> rows) {
    var output = new StringBuilder();
    int width = 0;
    for (List<@Nullable String> row : List.copyOf(rows)) {
      var snapshot = new ArrayList<@Nullable String>(row);
      if (snapshot.isEmpty()) throw invalid();
      if (width == 0) width = snapshot.size();
      else if (snapshot.size() != width) throw invalid();
      boolean first = true;
      for (@Nullable String field : snapshot) {
        if (!first) output.append('\t');
        first = false;
        appendField(output, field);
      }
      output.append('\n');
    }
    return output.toString().getBytes(StandardCharsets.UTF_8);
  }

  @Override
  public String toString() {
    return "PostgresCopyTextEncoder[REDACTED]";
  }

  private static void appendField(StringBuilder output, @Nullable String value) {
    if (value == null) {
      output.append('\\').append('N');
      return;
    }
    for (int index = 0; index < value.length(); index++) {
      char current = value.charAt(index);
      if (Character.isHighSurrogate(current)) {
        int next = index + 1;
        if (next >= value.length() || !Character.isLowSurrogate(value.charAt(next)))
          throw invalid();
        output.append(current).append(value.charAt(next));
        index++;
      } else if (Character.isLowSurrogate(current)) {
        throw invalid();
      } else {
        switch (current) {
          case 0 -> throw invalid();
          case '\\' -> output.append('\\').append('\\');
          case '\t' -> output.append('\\').append('t');
          case '\n' -> output.append('\\').append('n');
          case '\r' -> output.append('\\').append('r');
          case '\b' -> output.append('\\').append('b');
          case '\f' -> output.append('\\').append('f');
          case 11 -> output.append('\\').append('v');
          default -> output.append(current);
        }
      }
    }
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration COPY text data is invalid");
  }
}
