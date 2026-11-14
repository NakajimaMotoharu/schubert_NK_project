package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
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
 * Composes declared entry/file references and orders, never actual DB or migration completion.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004; UI223 section3.2/4/5,254; SS331/343 SSC345;
 * PT-MIG-PLACE001..012. Actual source game/index extraction remains the ETL caller's
 * responsibility.
 */
@NullMarked
public final class ScenarioEntryPlacementMap {
  private static final long MAXIMUM_N12 = 999_999_999_999L;

  public record Placement(int gameId, long currentFileId, long currentEntryId, int entryIndex) {
    public Placement {
      game(gameId);
      index(entryIndex);
    }

    @Override
    public String toString() {
      return "ScenarioPlacement[REDACTED]";
    }
  }

  public record PlacedEntry(
      long currentEntryId,
      long targetEntryId,
      long displayOrder,
      int gameId,
      long targetFileId,
      int entryIndex) {
    public PlacedEntry {
      n12(targetEntryId);
      n12(displayOrder);
      game(gameId);
      n12(targetFileId);
      index(entryIndex);
    }

    @Override
    public String toString() {
      return "ScenarioPlacedEntry[REDACTED]";
    }
  }

  // SSC363: JDK immutable (file ID, index) uniqueness key; never exposed or logged.

  private final ScenarioFileMigrationMap retainedFileMap;
  private final List<PlacedEntry> retainedEntries;
  private final Map<Long, PlacedEntry> retainedBySource;

  public ScenarioEntryPlacementMap(
      ScenarioFileMigrationMap files, ScenarioEntryMigrationMap entries, List<Placement> input) {
    retainedFileMap = Objects.requireNonNull(files, "file mapping");
    Objects.requireNonNull(entries, "entry mapping");
    var snapshot = List.copyOf(input);
    if (snapshot.size() != entries.mappings().size()) throw invalid();
    var sourceIds = new HashSet<Long>();
    var filePositions = new HashSet<List<Long>>();
    var result = new ArrayList<PlacedEntry>();
    var bySource = new HashMap<Long, PlacedEntry>();
    for (Placement placement : snapshot) {
      var file = files.lookup(placement.gameId(), placement.currentFileId());
      var entry = entries.lookup(placement.currentEntryId());
      if (!sourceIds.add(placement.currentEntryId())
          || !filePositions.add(List.of(file.targetFileId(), (long) placement.entryIndex())))
        throw invalid();
      var placed =
          new PlacedEntry(
              placement.currentEntryId(),
              entry.targetId(),
              entry.displayOrder(),
              placement.gameId(),
              file.targetFileId(),
              placement.entryIndex());
      result.add(placed);
      bySource.put(placement.currentEntryId(), placed);
    }
    retainedEntries =
        List.copyOf(
            result.stream().sorted(Comparator.comparingLong(PlacedEntry::displayOrder)).toList());
    retainedBySource = Map.copyOf(bySource);
  }

  public List<PlacedEntry> entries() {
    return retainedEntries;
  }

  public PlacedEntry lookup(long currentEntryId) {
    @Nullable PlacedEntry entry = retainedBySource.get(currentEntryId);
    if (entry == null) throw invalid();
    return entry;
  }

  public List<PlacedEntry> entriesForFile(int gameId, long currentFileId) {
    var file = retainedFileMap.lookup(gameId, currentFileId);
    return retainedEntries.stream()
        .filter(entry -> entry.targetFileId() == file.targetFileId())
        .sorted(Comparator.comparingInt(PlacedEntry::entryIndex))
        .toList();
  }

  public byte[] canonicalBytes() {
    var output = new StringBuilder("NKMIGENTRYPLACEMENT1\n");
    for (PlacedEntry entry : retainedEntries) {
      output
          .append(entry.currentEntryId())
          .append('\t')
          .append(entry.targetEntryId())
          .append('\t')
          .append(entry.displayOrder())
          .append('\t')
          .append(entry.gameId())
          .append('\t')
          .append(entry.targetFileId())
          .append('\t')
          .append(entry.entryIndex())
          .append('\n');
    }
    return output.toString().getBytes(StandardCharsets.US_ASCII);
  }

  @Override
  public String toString() {
    return "ScenarioEntryPlacementMap[REDACTED]";
  }

  private static void game(int value) {
    if (value < 1 || value > 2) throw invalid();
  }

  private static void index(int value) {
    if (value < 0) throw invalid();
  }

  private static void n12(long value) {
    if (value < 1 || value > MAXIMUM_N12) throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration entry placement is invalid");
  }
}
