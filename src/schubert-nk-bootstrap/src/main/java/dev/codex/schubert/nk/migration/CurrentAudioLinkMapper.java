package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Current triples to declared link order and target IDs; no actual Current ordering or DB witness.
 * NK-MIG-001; MIG003005006/MIG-DAT001002005/FUN005/DAT004/TST; UI227242254; SS311331/V002/343
 * SSC400; PT-MIG-AUDIOLINKMAP001..024. Never derives business order from an extraction query.
 */
@NullMarked
public final class CurrentAudioLinkMapper {
  private static final int CURRENT_COLUMNS = 3;
  private static final int MAXIMUM_LINK_ORDER = 999;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final String CURRENT_ID_PATTERN = "0|-?[1-9][0-9]{0,18}";
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");

  public record LinkOrder(
      long currentEntryId, long currentAudioId, String linkType, int displayOrder) {
    public LinkOrder(
        long currentEntryId, long currentAudioId, @Nullable String linkType, int displayOrder) {
      if (linkType == null
          || !linkType.matches("voice|se|bgm|other")
          || displayOrder < 1
          || displayOrder > MAXIMUM_LINK_ORDER) throw invalid();
      this.currentEntryId = currentEntryId;
      this.currentAudioId = currentAudioId;
      this.linkType = linkType;
      this.displayOrder = displayOrder;
    }

    @Override
    public String toString() {
      return "AudioLinkOrder[REDACTED]";
    }
  }

  private final ScenarioEntryPlacementMap retainedPlacement;
  private final AudioMigrationMap retainedAudio;
  private final List<LinkOrder> retainedLinks;
  private final Map<List<String>, LinkOrder> retainedBySource;

  public CurrentAudioLinkMapper(
      @Nullable ScenarioEntryPlacementMap placement,
      @Nullable AudioMigrationMap audio,
      @Nullable List<@Nullable LinkOrder> links) {
    if (placement == null || audio == null || links == null) throw invalid();
    var snapshot = new ArrayList<LinkOrder>();
    for (@Nullable LinkOrder item : new ArrayList<>(links)) {
      if (item == null) throw invalid();
      snapshot.add(item);
    }
    var bySource = new HashMap<List<String>, LinkOrder>();
    var orderKeys = new HashSet<List<String>>();
    for (var item : snapshot) {
      var entry = placement.lookup(item.currentEntryId());
      audio.targetAudioId(entry.gameId(), item.currentAudioId());
      if (bySource.putIfAbsent(key(item), item) != null
          || !orderKeys.add(
              List.of(
                  Long.toString(item.currentEntryId()),
                  item.linkType(),
                  Integer.toString(item.displayOrder())))) throw invalid();
    }
    snapshot.sort(
        Comparator.comparingLong(LinkOrder::currentEntryId)
            .thenComparing(LinkOrder::linkType)
            .thenComparingInt(LinkOrder::displayOrder));
    retainedPlacement = placement;
    retainedAudio = audio;
    retainedLinks = List.copyOf(snapshot);
    retainedBySource = Map.copyOf(bySource);
  }

  public List<LinkOrder> links() {
    return retainedLinks;
  }

  public byte[] canonicalBytes() {
    var text = new StringBuilder("current_entry_id\tcurrent_audio_id\tlink_type\tdisplay_order\n");
    for (var item : retainedLinks)
      text.append(item.currentEntryId())
          .append('\t')
          .append(item.currentAudioId())
          .append('\t')
          .append(item.linkType())
          .append('\t')
          .append(item.displayOrder())
          .append('\n');
    return text.toString().getBytes(StandardCharsets.UTF_8);
  }

  public AudioCopyDataset copyRows(
      @Nullable List<? extends @Nullable List<@Nullable String>> currentRows,
      @Nullable ScenarioEntryCopyBatch entries,
      @Nullable List<? extends @Nullable AudioFileCopyRow> audioRows,
      @Nullable Instant migratedAt) {
    if (currentRows == null || entries == null || audioRows == null || migratedAt == null)
      throw invalid();
    if (migratedAt.isBefore(EARLIEST)
        || migratedAt.isAfter(LATEST)
        || migratedAt.getNano() % NANOSECONDS_PER_MICROSECOND != 0) throw invalid();
    var data = new ArrayList<>(currentRows);
    if (data.size() != retainedLinks.size()) throw invalid();
    var boundEntries = new ScenarioEntryCopyBatch(retainedPlacement, entries.rows());
    var audioCopy = new ArrayList<>(audioRows);
    if (audioCopy.size() != retainedAudio.mappings().size()) throw invalid();
    var games = new HashMap<String, String>();
    for (var item : retainedAudio.mappings())
      games.put(Long.toString(item.targetAudioId()), Integer.toString(item.gameId()));
    for (@Nullable AudioFileCopyRow row : audioCopy) {
      if (row == null) throw invalid();
      String id = Objects.requireNonNull(row.fields().get(0));
      @Nullable String game = games.get(id);
      if (game == null || !game.equals(row.fields().get(1))) throw invalid();
    }
    var seen = new HashSet<List<String>>();
    for (@Nullable List<@Nullable String> source : data) {
      if (source == null) throw invalid();
      var row = new ArrayList<@Nullable String>(source);
      if (row.size() != CURRENT_COLUMNS) throw invalid();
      var sourceKey =
          List.of(
              Long.toString(parseCurrent(row.get(0))),
              Long.toString(parseCurrent(row.get(1))),
              required(row.get(2)));
      if (!retainedBySource.containsKey(sourceKey) || !seen.add(sourceKey)) throw invalid();
    }
    var output = new ArrayList<List<@Nullable String>>();
    // Known, unique, equal-cardinality source triples prove every declared link is present.
    for (var item : retainedLinks) {
      var entry = retainedPlacement.lookup(item.currentEntryId());
      output.add(
          List.of(
              Long.toString(entry.targetEntryId()),
              Long.toString(retainedAudio.targetAudioId(entry.gameId(), item.currentAudioId())),
              Integer.toString(entry.gameId()),
              item.linkType(),
              Integer.toString(item.displayOrder()),
              migratedAt.toString()));
    }
    return new AudioCopyDataset(boundEntries, audioCopy, output);
  }

  private static List<String> key(LinkOrder item) {
    return List.of(
        Long.toString(item.currentEntryId()),
        Long.toString(item.currentAudioId()),
        item.linkType());
  }

  private static long parseCurrent(@Nullable String value) {
    if (value == null || !value.matches(CURRENT_ID_PATTERN)) throw invalid();
    try {
      return Long.parseLong(value);
    } catch (NumberFormatException failure) {
      throw invalid();
    }
  }

  private static String required(@Nullable String value) {
    if (value == null) throw invalid();
    return value;
  }

  @Override
  public String toString() {
    return "CurrentAudioLinkMapper[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration audio link conversion is invalid");
  }
}
