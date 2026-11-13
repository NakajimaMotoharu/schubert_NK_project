package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Preserves Current entry ID order independently of NK identity allocation. Data only, never a DB
 * existence, completeness, load or startup witness. NK-MIG-001; MIG003005006/MIG-DAT005/FUN004;
 * UI223 section3.2/254 section4; SS331/343 SSC343; PT-MIG-ORDER001..012.
 */
@NullMarked
public final class ScenarioEntryMigrationMap {
  private static final long MAXIMUM_N12 = 999_999_999_999L;

  public record IdPair(long currentId, long targetId) {
    public IdPair {
      n12(targetId);
    }

    @Override
    public String toString() {
      return "ScenarioIdPair[REDACTED]";
    }
  }

  public record MappedEntry(long currentId, long targetId, long displayOrder) {
    public MappedEntry {
      n12(targetId);
      n12(displayOrder);
    }

    @Override
    public String toString() {
      return "ScenarioEntryMapping[REDACTED]";
    }
  }

  private final List<MappedEntry> retainedMappings;
  private final Map<Long, MappedEntry> retainedBySource;

  public ScenarioEntryMigrationMap(List<IdPair> input) {
    var sorted =
        List.copyOf(input).stream().sorted(Comparator.comparingLong(IdPair::currentId)).toList();
    var currentIds = new HashSet<Long>();
    var targetIds = new HashSet<Long>();
    var mappings = new ArrayList<MappedEntry>();
    var bySource = new HashMap<Long, MappedEntry>();
    for (int index = 0; index < sorted.size(); index++) {
      IdPair pair = sorted.get(index);
      if (!currentIds.add(pair.currentId()) || !targetIds.add(pair.targetId())) throw invalid();
      // List's int count keeps this positive dense ordinal within the existing N12 domain.
      var entry = new MappedEntry(pair.currentId(), pair.targetId(), index + 1L);
      mappings.add(entry);
      bySource.put(pair.currentId(), entry);
    }
    retainedMappings = List.copyOf(mappings);
    retainedBySource = Map.copyOf(bySource);
  }

  public List<MappedEntry> mappings() {
    return retainedMappings;
  }

  public MappedEntry lookup(long currentId) {
    @Nullable MappedEntry entry = retainedBySource.get(currentId);
    if (entry == null) throw invalid();
    return entry;
  }

  public byte[] canonicalBytes() {
    var output = new StringBuilder("NKMIGSCENARIOORDER1\n");
    for (MappedEntry entry : retainedMappings) {
      output
          .append(entry.currentId())
          .append('\t')
          .append(entry.targetId())
          .append('\t')
          .append(entry.displayOrder())
          .append('\n');
    }
    return output.toString().getBytes(StandardCharsets.US_ASCII);
  }

  @Override
  public String toString() {
    return "ScenarioEntryMigrationMap[REDACTED]";
  }

  private static void n12(long value) {
    if (value < 1 || value > MAXIMUM_N12) throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration entry mapping is invalid");
  }
}
