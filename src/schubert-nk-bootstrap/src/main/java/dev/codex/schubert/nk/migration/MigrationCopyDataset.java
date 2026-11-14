package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.io.OutputStream;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Five-table declared values and borrowed streams; no DB, COPY session or migration receipt.
 * NK-MIG-001; MIG-DAT001..005/MIG003005006/DAT004/FUN004; UI223227242254; SS311/331/V002/343
 * SSC364; PT-MIG-FIVE001..020.
 */
@NullMarked
@Immutable
public final class MigrationCopyDataset {
  private static final int ONE_TRANSACTION_TIMESTAMP = 1;
  private final ScenarioCopyDataset retainedScenario;
  private final AudioCopyDataset retainedAudio;
  private final MediaAssetCopyBatch retainedMedia;

  public MigrationCopyDataset(
      @Nullable ScenarioCopyDataset scenario,
      @Nullable List<? extends @Nullable AudioFileCopyRow> audioRows,
      @Nullable List<? extends @Nullable List<@Nullable String>> links,
      @Nullable MediaAssetCopyBatch media) {
    if (scenario == null || media == null) throw invalid();
    var audio = new AudioCopyDataset(scenario.entries(), audioRows, links);
    var timestamps = new HashSet<String>();
    // Final immutable row constructors establish these nonnull timestamp columns.
    for (var row : scenario.files().rows()) timestamps.add(Objects.requireNonNull(row.get(10)));
    for (var row : scenario.entries().rows())
      timestamps.add(Objects.requireNonNull(row.fields().get(11)));
    for (var row : audio.audioRows()) timestamps.add(Objects.requireNonNull(row.fields().get(11)));
    for (var row : media.rows()) timestamps.add(row.createdAt());
    for (var row : audio.linkRows()) timestamps.add(Objects.requireNonNull(row.get(5)));
    if (timestamps.size() > ONE_TRANSACTION_TIMESTAMP) throw invalid();
    retainedScenario = scenario;
    retainedAudio = audio;
    retainedMedia = media;
  }

  public ScenarioCopyDataset scenario() {
    return retainedScenario;
  }

  public AudioCopyDataset audio() {
    return retainedAudio;
  }

  public MediaAssetCopyBatch media() {
    return retainedMedia;
  }

  /** Validate all borrowed arguments before the first write; preserve partial failure verbatim. */
  public void writeAll(
      @Nullable PostgresCopyTextWriter writer,
      @Nullable OutputStream files,
      @Nullable OutputStream entries,
      @Nullable OutputStream audio,
      @Nullable OutputStream media,
      @Nullable OutputStream links)
      throws IOException {
    if (writer == null
        || files == null
        || entries == null
        || audio == null
        || media == null
        || links == null) throw invalid();
    retainedScenario.writeFiles(writer, files);
    retainedScenario.writeEntries(writer, entries);
    retainedAudio.writeAudio(writer, audio);
    retainedMedia.writeTo(writer, media);
    retainedAudio.writeLinks(writer, links);
  }

  @Override
  public String toString() {
    return "MigrationCopyDataset[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration five-table COPY dataset is invalid");
  }
}
