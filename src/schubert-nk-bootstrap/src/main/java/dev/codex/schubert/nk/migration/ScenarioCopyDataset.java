package dev.codex.schubert.nk.migration;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Joins declared immutable COPY batches, never an actual DB or full migration witness. NK-MIG-001;
 * MIG003005006/MIG-DAT004005/DAT004/FUN004; UI223/242/254; SS331/V002/343 section10 SSC350;
 * PT-MIG-DATASET001..012.
 */
@NullMarked
public final class ScenarioCopyDataset {
  private static final int MAXIMUM_TRANSACTION_TIMESTAMPS = 1;
  private final ScenarioFileCopyBatch retainedFiles;
  private final ScenarioEntryCopyBatch retainedEntries;

  public ScenarioCopyDataset(
      @Nullable ScenarioFileCopyBatch files, @Nullable ScenarioEntryCopyBatch entries) {
    if (files == null || entries == null) throw invalid();
    var fileGames = new HashMap<String, String>();
    var stamps = new HashSet<String>();
    // These nonnull columns are constructor-established invariants of the final immutable batches.
    for (var row : files.rows()) {
      fileGames.put(Objects.requireNonNull(row.get(0)), Objects.requireNonNull(row.get(1)));
      stamps.add(Objects.requireNonNull(row.get(10)));
    }
    for (var row : entries.rows()) {
      @Nullable String game = fileGames.get(row.fields().get(2));
      if (game == null || !game.equals(row.fields().get(1))) throw invalid();
      stamps.add(Objects.requireNonNull(row.fields().get(11)));
    }
    if (stamps.size() > MAXIMUM_TRANSACTION_TIMESTAMPS) throw invalid();
    retainedFiles = files;
    retainedEntries = entries;
  }

  public ScenarioFileCopyBatch files() {
    return retainedFiles;
  }

  public ScenarioEntryCopyBatch entries() {
    return retainedEntries;
  }

  public byte[] fileCopyBytes(@Nullable PostgresCopyTextEncoder encoder) {
    if (encoder == null) throw invalid();
    return retainedFiles.copyBytes(encoder);
  }

  public byte[] entryCopyBytes(@Nullable PostgresCopyTextEncoder encoder) {
    if (encoder == null) throw invalid();
    return retainedEntries.copyBytes(encoder);
  }

  @Override
  public String toString() {
    return "ScenarioCopyDataset[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration scenario COPY dataset is invalid");
  }
}
