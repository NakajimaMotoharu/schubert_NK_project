package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.io.OutputStream;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared audio/link constraints and borrowed streams, never an actual migration witness.
 * NK-MIG-001; MIG-DAT-001/MIG-DAT-002/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004; UI227/242/254;
 * SS311/331/V002/343 section10 SSC355; PT-MIG-AUDIODATA001..020.
 */
@NullMarked
public final class AudioCopyDataset {
  private static final int LINK_COLUMNS = 6;
  private static final int MAXIMUM_TRANSACTION_TIMESTAMPS = 1;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final List<AudioFileCopyRow> retainedAudio;
  private final List<List<@Nullable String>> retainedLinks;

  public AudioCopyDataset(
      @Nullable ScenarioEntryCopyBatch entries,
      @Nullable List<? extends @Nullable AudioFileCopyRow> audio,
      @Nullable List<? extends @Nullable List<@Nullable String>> links) {
    if (entries == null || audio == null || links == null) throw invalid();
    var entryGames = new HashMap<String, String>();
    var audioGames = new HashMap<String, String>();
    var paths = new HashSet<List<String>>();
    var stamps = new HashSet<String>();
    // The final Row/Batch constructors already establish these nonnull immutable column invariants.
    for (var row : entries.rows()) {
      entryGames.put(
          Objects.requireNonNull(row.fields().get(0)), Objects.requireNonNull(row.fields().get(1)));
      stamps.add(Objects.requireNonNull(row.fields().get(11)));
    }
    var audioCopy = new ArrayList<AudioFileCopyRow>();
    for (@Nullable AudioFileCopyRow row : audio) {
      if (row == null) throw invalid();
      String id = Objects.requireNonNull(row.fields().get(0));
      String game = Objects.requireNonNull(row.fields().get(1));
      String path = Objects.requireNonNull(row.fields().get(2));
      if (audioGames.putIfAbsent(id, game) != null || !paths.add(List.of(game, path)))
        throw invalid();
      stamps.add(Objects.requireNonNull(row.fields().get(11)));
      audioCopy.add(row);
    }
    var primaryKeys = new HashSet<List<String>>();
    var orderKeys = new HashSet<List<String>>();
    var linkCopy = new ArrayList<List<@Nullable String>>();
    for (@Nullable List<@Nullable String> input : links) {
      if (input == null) throw invalid();
      var row = new ArrayList<@Nullable String>(input);
      if (row.size() != LINK_COLUMNS) throw invalid();
      String entryId = required(row, 0);
      String audioId = required(row, 1);
      String game = required(row, 2);
      String type = required(row, 3);
      String order = required(row, 4);
      String stamp = required(row, 5);
      positiveN12(entryId);
      positiveN12(audioId);
      if (!game.equals("1") && !game.equals("2")) throw invalid();
      if (!type.matches("voice|se|bgm|other")) throw invalid();
      if (!order.matches("[1-9][0-9]{0,2}")) throw invalid();
      timestamp(stamp);
      if (!game.equals(entryGames.get(entryId)) || !game.equals(audioGames.get(audioId)))
        throw invalid();
      if (!primaryKeys.add(List.of(entryId, audioId, type))) throw invalid();
      if (!orderKeys.add(List.of(entryId, type, order))) throw invalid();
      // order1..999 and UK(entry,type,order) imply count<=999; no unreachable duplicate count
      // branch.
      stamps.add(stamp);
      linkCopy.add(Collections.unmodifiableList(row));
    }
    if (stamps.size() > MAXIMUM_TRANSACTION_TIMESTAMPS) throw invalid();
    retainedAudio = List.copyOf(audioCopy);
    retainedLinks = List.copyOf(linkCopy);
  }

  public List<AudioFileCopyRow> audioRows() {
    return retainedAudio;
  }

  public List<List<@Nullable String>> linkRows() {
    return retainedLinks;
  }

  /** Borrowed sink; row references only, no whole-stream byte buffer, close, flush or commit. */
  public void writeAudio(@Nullable PostgresCopyTextWriter writer, @Nullable OutputStream sink)
      throws IOException {
    if (writer == null) throw invalid();
    var rows = new ArrayList<List<@Nullable String>>();
    for (var row : retainedAudio) rows.add(row.fields());
    writer.writeRows(rows, sink);
  }

  public void writeLinks(@Nullable PostgresCopyTextWriter writer, @Nullable OutputStream sink)
      throws IOException {
    if (writer == null) throw invalid();
    writer.writeRows(retainedLinks, sink);
  }

  @Override
  public String toString() {
    return "AudioCopyDataset[REDACTED]";
  }

  private static String required(List<@Nullable String> row, int index) {
    @Nullable String value = row.get(index);
    if (value == null) throw invalid();
    return value;
  }

  private static void positiveN12(String value) {
    if (!value.matches("[1-9][0-9]{0,11}")) throw invalid();
  }

  private static void timestamp(String text) {
    Instant value;
    try {
      value = Instant.parse(text);
    } catch (DateTimeParseException failure) {
      throw invalid();
    }
    if (value.isBefore(EARLIEST) || value.isAfter(LATEST)) throw invalid();
    if (value.getNano() % NANOSECONDS_PER_MICROSECOND != 0 || !value.toString().equals(text))
      throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration audio COPY dataset is invalid");
  }
}
