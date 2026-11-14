package dev.codex.schubert.nk.migration;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Current ten-column values to declared target COPY rows; no actual database or source repair.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311331/V002/343 SSC390;
 * PT-MIG-ENTRYMAP001..024. Existing placement and speaker mappings own target identities.
 */
@NullMarked
public final class CurrentScenarioEntryMapper {
  private static final int CURRENT_COLUMNS = 10;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final String CURRENT_ID_PATTERN = "0|-?[1-9][0-9]{0,18}";
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final ScenarioFileMigrationMap retainedFiles;
  private final ScenarioEntryPlacementMap retainedPlacement;
  private final SpeakerMigrationMap retainedSpeakers;

  public CurrentScenarioEntryMapper(
      @Nullable ScenarioFileMigrationMap files,
      @Nullable ScenarioEntryPlacementMap placement,
      @Nullable SpeakerMigrationMap speakers) {
    if (files == null || placement == null || speakers == null) throw invalid();
    retainedFiles = files;
    retainedPlacement = placement;
    retainedSpeakers = speakers;
  }

  public ScenarioEntryCopyBatch copyRows(
      @Nullable List<? extends @Nullable List<@Nullable String>> currentRows,
      @Nullable Instant migratedAt) {
    if (currentRows == null || migratedAt == null) throw invalid();
    validTime(migratedAt);
    var data = new ArrayList<>(currentRows);
    if (data.size() != retainedPlacement.entries().size()) throw invalid();
    var byCurrent = new HashMap<Long, ScenarioEntryCopyRow>();
    for (@Nullable List<@Nullable String> source : data) {
      if (source == null) throw invalid();
      var row = new ArrayList<@Nullable String>(source);
      if (row.size() != CURRENT_COLUMNS) throw invalid();
      long id = parseCurrent(row.get(0));
      var entry = retainedPlacement.lookup(id);
      if (!Integer.toString(entry.gameId()).equals(row.get(1))
          || !Integer.toString(entry.entryIndex()).equals(row.get(3))) throw invalid();
      var file = retainedFiles.lookup(entry.gameId(), parseCurrent(row.get(2)));
      if (file.targetFileId() != entry.targetFileId()) throw invalid();
      @Nullable String sourceSpeaker = row.get(6);
      @Nullable String targetSpeaker =
          sourceSpeaker == null
              ? null
              : Long.toString(
                  retainedSpeakers.targetSpeakerId(entry.gameId(), parseCurrent(sourceSpeaker)));
      var target = new ArrayList<@Nullable String>();
      target.add(Long.toString(entry.targetEntryId()));
      target.add(Integer.toString(entry.gameId()));
      target.add(Long.toString(entry.targetFileId()));
      target.add(Long.toString(entry.displayOrder()));
      target.add(Integer.toString(entry.entryIndex()));
      // Establish required source text before Row construction: no accidental NPE or NULL repair.
      target.add(required(row.get(4)));
      target.add(required(row.get(5)));
      target.add(targetSpeaker);
      target.add(row.get(7));
      target.add(required(row.get(8)));
      target.add(required(row.get(9)));
      target.add(migratedAt.toString());
      var converted = new ScenarioEntryCopyRow(target);
      if (byCurrent.putIfAbsent(id, converted) != null) throw invalid();
    }
    var result = new ArrayList<ScenarioEntryCopyRow>();
    // Known unique source membership plus equal cardinality proves this complete bijection.
    for (var entry : retainedPlacement.entries())
      result.add(Objects.requireNonNull(byCurrent.get(entry.currentEntryId())));
    return new ScenarioEntryCopyBatch(retainedPlacement, result);
  }

  private static String required(@Nullable String value) {
    if (value == null) throw invalid();
    return value;
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
    return "CurrentScenarioEntryMapper[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration entry conversion is invalid");
  }
}
