package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared speaker constraints and entry references, never actual master or database acceptance.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223233242254; SS311/331/V002/343 SSC368;
 * PT-MIG-SPEAKERBATCH001..016.
 */
@NullMarked
@Immutable
public final class SpeakerCopyBatch {
  private static final int ONE_TRANSACTION_TIMESTAMP = 1;
  private final List<SpeakerCopyRow> retainedRows;
  private final Map<String, String> retainedGames;
  private final Set<String> retainedTimestamps;

  public SpeakerCopyBatch(@Nullable List<? extends @Nullable SpeakerCopyRow> input) {
    if (input == null) throw invalid();
    var rows = new ArrayList<SpeakerCopyRow>();
    var games = new HashMap<String, String>();
    var names = new HashSet<List<String>>();
    var timestamps = new HashSet<String>();
    for (@Nullable SpeakerCopyRow row : new ArrayList<>(input)) {
      if (row == null) throw invalid();
      // Final immutable SpeakerCopyRow establishes these nonnull mandatory columns.
      String id = Objects.requireNonNull(row.fields().get(0));
      String game = Objects.requireNonNull(row.fields().get(1));
      String normalizedName = Objects.requireNonNull(row.fields().get(3));
      if (games.putIfAbsent(id, game) != null || !names.add(List.of(game, normalizedName)))
        throw invalid();
      timestamps.add(Objects.requireNonNull(row.fields().get(6)));
      rows.add(row);
    }
    if (timestamps.size() > ONE_TRANSACTION_TIMESTAMP) throw invalid();
    retainedRows = List.copyOf(rows);
    retainedGames = Map.copyOf(games);
    retainedTimestamps = Set.copyOf(timestamps);
  }

  public List<SpeakerCopyRow> rows() {
    return retainedRows;
  }

  public byte[] copyBytes(@Nullable PostgresCopyTextEncoder encoder) {
    if (encoder == null) throw invalid();
    var fields = new ArrayList<List<@Nullable String>>();
    for (var row : retainedRows) fields.add(row.fields());
    return encoder.encodeRows(fields);
  }

  public void writeTo(@Nullable PostgresCopyTextWriter writer, @Nullable OutputStream sink)
      throws IOException {
    if (writer == null || sink == null) throw invalid();
    var fields = new ArrayList<List<@Nullable String>>();
    for (var row : retainedRows) fields.add(row.fields());
    writer.writeRows(fields, sink);
  }

  public void validateEntries(@Nullable ScenarioEntryCopyBatch entries) {
    if (entries == null) throw invalid();
    var timestamps = new HashSet<>(retainedTimestamps);
    for (var row : entries.rows()) {
      timestamps.add(Objects.requireNonNull(row.fields().get(11)));
      @Nullable String speaker = row.fields().get(7);
      if (speaker == null) continue;
      String game = Objects.requireNonNull(row.fields().get(1));
      if (!game.equals(retainedGames.get(speaker))) throw invalid();
    }
    if (timestamps.size() > ONE_TRANSACTION_TIMESTAMP) throw invalid();
  }

  @Override
  public String toString() {
    return "SpeakerCopyBatch[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration speaker COPY batch is invalid");
  }
}
