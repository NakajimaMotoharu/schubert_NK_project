package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Per-row COPY transport; owns neither the iterable nor the borrowed sink. NK-MIG-001;
 * MIG003005006/MIG-DAT004005/DAT004; UI254; SS331/343 SSC351; PT-MIG-STREAM001..012. Prefix bytes
 * can remain after failure; never commits a database.
 */
@NullMarked
public final class PostgresCopyTextWriter {
  private final PostgresCopyTextEncoder encoder;

  public PostgresCopyTextWriter(@Nullable PostgresCopyTextEncoder encoder) {
    if (encoder == null) throw invalid();
    this.encoder = encoder;
  }

  public void writeRows(
      @Nullable Iterable<? extends List<@Nullable String>> rows, @Nullable OutputStream sink)
      throws IOException {
    if (rows == null || sink == null) throw invalid();
    int width = 0;
    for (List<@Nullable String> row : rows) {
      if (row == null) throw invalid();
      var snapshot = new ArrayList<@Nullable String>(row);
      if (snapshot.isEmpty()) throw invalid();
      if (width == 0) width = snapshot.size();
      else if (width != snapshot.size()) throw invalid();
      // Exactly one encoded row is retained; do not acquire the next row before sending this one.
      sink.write(encoder.encodeRow(snapshot));
    }
  }

  @Override
  public String toString() {
    return "PostgresCopyTextWriter[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration COPY stream input is invalid");
  }
}
