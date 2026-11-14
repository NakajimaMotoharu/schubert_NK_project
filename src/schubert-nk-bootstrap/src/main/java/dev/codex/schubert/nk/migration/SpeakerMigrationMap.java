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
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Signed Current PK to NK N12 mapping and selected stored-column conversion, never a DB witness.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC375;
 * PT-MIG-SPEAKERMAP001..024. Display/normalized names, flags and notes are never re-derived.
 */
@NullMarked
@Immutable
public final class SpeakerMigrationMap {
  private static final long MAXIMUM_N12 = 999_999_999_999L;
  private static final int CURRENT_COLUMNS = 6;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final String CURRENT_ID_PATTERN = "0|-?[1-9][0-9]{0,18}";
  private static final String HEADER = "game_id\tcurrent_speaker_id\ttarget_speaker_id\n";
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");

  public record SpeakerMapping(int gameId, long currentSpeakerId, long targetSpeakerId) {
    public SpeakerMapping {
      if ((gameId != 1 && gameId != 2) || targetSpeakerId < 1 || targetSpeakerId > MAXIMUM_N12)
        throw invalid();
    }

    @Override
    public String toString() {
      return "SpeakerMapping[REDACTED]";
    }
  }

  private final List<SpeakerMapping> retainedMappings;
  private final Map<Long, SpeakerMapping> retainedByCurrent;

  public SpeakerMigrationMap(@Nullable List<? extends @Nullable SpeakerMapping> input) {
    if (input == null) throw invalid();
    var ordered = new ArrayList<SpeakerMapping>();
    var byCurrent = new HashMap<Long, SpeakerMapping>();
    var targets = new HashSet<Long>();
    for (@Nullable SpeakerMapping mapping : new ArrayList<>(input)) {
      if (mapping == null) throw invalid();
      if (byCurrent.putIfAbsent(mapping.currentSpeakerId(), mapping) != null
          || !targets.add(mapping.targetSpeakerId())) throw invalid();
      ordered.add(mapping);
    }
    ordered.sort(Comparator.comparingLong(SpeakerMapping::currentSpeakerId));
    retainedMappings = List.copyOf(ordered);
    retainedByCurrent = Map.copyOf(byCurrent);
  }

  public List<SpeakerMapping> mappings() {
    return retainedMappings;
  }

  public long targetSpeakerId(int gameId, long currentSpeakerId) {
    @Nullable SpeakerMapping mapping = retainedByCurrent.get(currentSpeakerId);
    if (mapping == null || mapping.gameId() != gameId) throw invalid();
    return mapping.targetSpeakerId();
  }

  public byte[] canonicalBytes() {
    var result = new StringBuilder(HEADER);
    for (var mapping : retainedMappings)
      result
          .append(mapping.gameId())
          .append('\t')
          .append(mapping.currentSpeakerId())
          .append('\t')
          .append(mapping.targetSpeakerId())
          .append('\n');
    return result.toString().getBytes(StandardCharsets.UTF_8);
  }

  public SpeakerCopyBatch copyRows(
      @Nullable List<? extends @Nullable List<@Nullable String>> currentRows,
      @Nullable Instant migratedAt) {
    if (currentRows == null || migratedAt == null) throw invalid();
    validTime(migratedAt);
    String stamp = migratedAt.toString();
    var data = new ArrayList<>(currentRows);
    if (data.size() != retainedMappings.size()) throw invalid();
    var byCurrent = new HashMap<Long, SpeakerCopyRow>();
    for (@Nullable List<@Nullable String> source : data) {
      if (source == null) throw invalid();
      var row = new ArrayList<@Nullable String>(source);
      if (row.size() != CURRENT_COLUMNS) throw invalid();
      long id = parseCurrent(row.get(0));
      @Nullable SpeakerMapping mapping = retainedByCurrent.get(id);
      if (mapping == null || !Integer.toString(mapping.gameId()).equals(row.get(1)))
        throw invalid();
      var target = new ArrayList<@Nullable String>();
      target.add(Long.toString(mapping.targetSpeakerId()));
      target.add(Integer.toString(mapping.gameId()));
      target.addAll(row.subList(2, CURRENT_COLUMNS));
      target.add(stamp);
      var converted = new SpeakerCopyRow(target);
      if (byCurrent.putIfAbsent(id, converted) != null) throw invalid();
    }
    var result = new ArrayList<SpeakerCopyRow>();
    // Equal cardinality, known membership and unique source IDs establish this complete bijection.
    for (var mapping : retainedMappings)
      result.add(Objects.requireNonNull(byCurrent.get(mapping.currentSpeakerId())));
    return new SpeakerCopyBatch(result);
  }

  private static long parseCurrent(@Nullable String value) {
    if (value == null || !value.matches(CURRENT_ID_PATTERN)) throw invalid();
    try {
      return Long.parseLong(value);
    } catch (NumberFormatException failure) {
      throw invalid();
    }
  }

  private static void validTime(Instant value) {
    if (value.isBefore(EARLIEST)
        || value.isAfter(LATEST)
        || value.getNano() % NANOSECONDS_PER_MICROSECOND != 0) throw invalid();
  }

  @Override
  public String toString() {
    return "SpeakerMigrationMap[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration speaker mapping is invalid");
  }
}
