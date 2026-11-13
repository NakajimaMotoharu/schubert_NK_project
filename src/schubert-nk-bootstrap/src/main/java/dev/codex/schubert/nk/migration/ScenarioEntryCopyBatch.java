package dev.codex.schubert.nk.migration;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Validates declared entry mapping against COPY rows without loading or querying a database.
 * NK-MIG-001; MIG003005006/MIG-DAT004005/DAT004/FUN004; UI223/242/254; SS331/V002/343 section10
 * SSC348; PT-MIG-BATCH001..012.
 */
@NullMarked
public final class ScenarioEntryCopyBatch {
  private final List<ScenarioEntryCopyRow> retainedRows;

  public ScenarioEntryCopyBatch(
      ScenarioEntryPlacementMap placement, List<ScenarioEntryCopyRow> input) {
    Objects.requireNonNull(placement, "entry placement");
    var snapshot = List.copyOf(input);
    if (snapshot.size() != placement.entries().size()) throw invalid();
    var byTarget = new HashMap<Long, ScenarioEntryCopyRow>();
    var timestamps = new HashSet<String>();
    for (ScenarioEntryCopyRow row : snapshot) {
      long target = Long.parseLong(Objects.requireNonNull(row.fields().get(0)));
      if (byTarget.put(target, row) != null) throw invalid();
      timestamps.add(Objects.requireNonNull(row.fields().get(11)));
    }
    if (timestamps.size() > 1) throw invalid();
    var ordered = new ArrayList<ScenarioEntryCopyRow>();
    for (var entry : placement.entries()) {
      @Nullable ScenarioEntryCopyRow row = byTarget.get(entry.targetEntryId());
      if (row == null) throw invalid();
      var expected =
          List.of(
              Long.toString(entry.targetEntryId()),
              Integer.toString(entry.gameId()),
              Long.toString(entry.targetFileId()),
              Long.toString(entry.displayOrder()),
              Integer.toString(entry.entryIndex()));
      if (!row.fields().subList(0, 5).equals(expected)) throw invalid();
      ordered.add(row);
    }
    retainedRows = List.copyOf(ordered);
  }

  public List<ScenarioEntryCopyRow> rows() {
    return retainedRows;
  }

  public byte[] copyBytes(PostgresCopyTextEncoder encoder) {
    Objects.requireNonNull(encoder, "COPY text encoder");
    var fields = new ArrayList<List<@Nullable String>>();
    for (ScenarioEntryCopyRow row : retainedRows) fields.add(row.fields());
    return encoder.encodeRows(fields);
  }

  @Override
  public String toString() {
    return "ScenarioEntryCopyBatch[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration scenario COPY batch is invalid");
  }
}
