package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.io.OutputStream;
import java.util.HashSet;
import java.util.Objects;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Six-table declared immutable assembly, never an actual master/DB receipt. NK-MIG-001;
 * MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC370;
 * PT-MIG-MASTER001..020.
 */
@NullMarked
@Immutable
public final class MigrationMasterCopyDataset {
  private static final int ONE_TRANSACTION_TIMESTAMP = 1;
  private final SpeakerCopyBatch retainedSpeakers;
  private final MigrationCopyDataset retainedContent;

  public MigrationMasterCopyDataset(
      @Nullable SpeakerCopyBatch speakers, @Nullable MigrationCopyDataset content) {
    if (speakers == null || content == null) throw invalid();
    speakers.validateEntries(content.scenario().entries());
    var stamps = new HashSet<String>();
    // Each final immutable row has established the nonnull timestamp-column invariant.
    for (var row : speakers.rows()) stamps.add(Objects.requireNonNull(row.fields().get(6)));
    for (var row : content.scenario().files().rows())
      stamps.add(Objects.requireNonNull(row.get(10)));
    for (var row : content.scenario().entries().rows())
      stamps.add(Objects.requireNonNull(row.fields().get(11)));
    for (var row : content.audio().audioRows())
      stamps.add(Objects.requireNonNull(row.fields().get(11)));
    for (var row : content.media().rows()) stamps.add(row.createdAt());
    for (var row : content.audio().linkRows()) stamps.add(Objects.requireNonNull(row.get(5)));
    if (stamps.size() > ONE_TRANSACTION_TIMESTAMP) throw invalid();
    retainedSpeakers = speakers;
    retainedContent = content;
  }

  public SpeakerCopyBatch speakers() {
    return retainedSpeakers;
  }

  public MigrationCopyDataset content() {
    return retainedContent;
  }

  /** Validate every borrowed output before the first write; stop at the original failure. */
  public void writeAll(
      @Nullable PostgresCopyTextWriter writer,
      @Nullable OutputStream speakers,
      @Nullable OutputStream files,
      @Nullable OutputStream entries,
      @Nullable OutputStream audio,
      @Nullable OutputStream media,
      @Nullable OutputStream links)
      throws IOException {
    if (writer == null
        || speakers == null
        || files == null
        || entries == null
        || audio == null
        || media == null
        || links == null) throw invalid();
    retainedSpeakers.writeTo(writer, speakers);
    retainedContent.writeAll(writer, files, entries, audio, media, links);
  }

  @Override
  public String toString() {
    return "MigrationMasterCopyDataset[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration six-table COPY dataset is invalid");
  }
}
