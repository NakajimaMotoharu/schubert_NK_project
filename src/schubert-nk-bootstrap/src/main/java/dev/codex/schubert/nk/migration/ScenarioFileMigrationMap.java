package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Pure file ID/order mapping, never an ETL, DB completeness or startup witness. NK-MIG-001;
 * MIG003005006/MIG-DAT005/FUN004; UI223 section3.2/4/5, UI254 section4; SS331/343 SSC344;
 * PT-MIG-FILEORDER001..012. Game IDs are already resolved to the two fixed V004 NK games.
 */
@NullMarked
public final class ScenarioFileMigrationMap {
  private static final long MAXIMUM_N12 = 999_999_999_999L;

  public record FilePair(int gameId, long currentFileId, long targetFileId) {
    public FilePair {
      game(gameId);
      n12(targetFileId);
    }

    @Override
    public String toString() {
      return "ScenarioFilePair[REDACTED]";
    }
  }

  public record MappedFile(int gameId, long currentFileId, long targetFileId, long displayOrder) {
    public MappedFile {
      game(gameId);
      n12(targetFileId);
      n12(displayOrder);
    }

    @Override
    public String toString() {
      return "ScenarioFileMapping[REDACTED]";
    }
  }

  // SSC363: JDK immutable (game, source ID) key; never exposed or logged.

  private final List<MappedFile> retainedFiles;
  private final Map<List<Long>, Integer> retainedPositions;

  public ScenarioFileMigrationMap(List<FilePair> input) {
    var sorted =
        List.copyOf(input).stream()
            .sorted(
                Comparator.comparingInt(FilePair::gameId)
                    .thenComparingLong(FilePair::currentFileId))
            .toList();
    var positions = new HashMap<List<Long>, Integer>();
    var targetIds = new HashSet<Long>();
    var files = new ArrayList<MappedFile>();
    var ranks = new long[2];
    for (FilePair pair : sorted) {
      var key = List.of((long) pair.gameId(), pair.currentFileId());
      if (positions.containsKey(key) || !targetIds.add(pair.targetFileId())) throw invalid();
      positions.put(key, files.size());
      // Validated game index is 0/1; List's int count bounds each dense ordinal within N12.
      ranks[pair.gameId() - 1]++;
      files.add(
          new MappedFile(
              pair.gameId(), pair.currentFileId(), pair.targetFileId(), ranks[pair.gameId() - 1]));
    }
    retainedFiles = List.copyOf(files);
    retainedPositions = Map.copyOf(positions);
  }

  public List<MappedFile> files() {
    return retainedFiles;
  }

  public MappedFile lookup(int gameId, long currentFileId) {
    return retainedFiles.get(position(gameId, currentFileId));
  }

  public Optional<MappedFile> previous(int gameId, long currentFileId) {
    int index = position(gameId, currentFileId);
    return index == 0 ? Optional.empty() : Optional.of(retainedFiles.get(index - 1));
  }

  public Optional<MappedFile> next(int gameId, long currentFileId) {
    int index = position(gameId, currentFileId);
    return index + 1 == retainedFiles.size()
        ? Optional.empty()
        : Optional.of(retainedFiles.get(index + 1));
  }

  public byte[] canonicalBytes() {
    var output = new StringBuilder("NKMIGFILEORDER1\n");
    for (MappedFile file : retainedFiles) {
      output
          .append(file.gameId())
          .append('\t')
          .append(file.currentFileId())
          .append('\t')
          .append(file.targetFileId())
          .append('\t')
          .append(file.displayOrder())
          .append('\n');
    }
    return output.toString().getBytes(StandardCharsets.US_ASCII);
  }

  @Override
  public String toString() {
    return "ScenarioFileMigrationMap[REDACTED]";
  }

  private int position(int gameId, long currentFileId) {
    game(gameId);
    @Nullable Integer index = retainedPositions.get(List.of((long) gameId, currentFileId));
    if (index == null) throw invalid();
    return index;
  }

  private static void game(int value) {
    if (value < 1 || value > 2) throw invalid();
  }

  private static void n12(long value) {
    if (value < 1 || value > MAXIMUM_N12) throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration file mapping is invalid");
  }
}
