package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.util.ArrayList;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** New pre-I/O maximum/middle/tail vectors; SS332 section4.2/SS333, SNAPSHOTMAX001..003. */
class ScenarioDetailSnapshotBoundaryTest {
  private static final int MAXIMUM_ROWS = 10_000;
  private static final ScenarioDetailResponseData HEADER_FIXTURE =
      new ScenarioDetailResponseData(
          new ScriptFileId(1),
          GameCode.NUKITASHI_1,
          "Snapshot fixture",
          DisplayPath.of("scenario/synthetic.txt"),
          Optional.empty(),
          Optional.empty(),
          Optional.empty(),
          Optional.empty(),
          DeliveryMode.INLINE,
          Optional.empty(),
          Optional.empty(),
          0,
          Optional.empty(),
          0,
          0);

  @Test
  void snapshotMax001MaximumRowsRemainImmutableAndKeepLastRecord() {
    var input = records();
    var snapshot = new ScenarioDetailSnapshot(HEADER_FIXTURE, input);
    input.set(0, entry(1, 1, "caller replacement"));
    input.clear();
    assertEquals(MAXIMUM_ROWS, snapshot.records().size());
    assertEquals(new EntryId(1), snapshot.records().getFirst().entryId());
    assertEquals(1, snapshot.records().getFirst().entrySequence());
    assertEquals("row-1", snapshot.records().getFirst().bodyText());
    assertEquals(new EntryId(MAXIMUM_ROWS), snapshot.records().getLast().entryId());
    assertEquals(MAXIMUM_ROWS, snapshot.records().getLast().entrySequence());
    assertEquals(MAXIMUM_ROWS, snapshot.records().getLast().lineNumber());
    assertEquals("row-10000", snapshot.records().getLast().bodyText());
    assertSame(HEADER_FIXTURE, snapshot.metadata());
    assertEquals("ScenarioDetailSnapshot[recordCount=10000]", snapshot.toString());
    assertThrows(UnsupportedOperationException.class, () -> snapshot.records().clear());
  }

  @Test
  void snapshotMax002InteriorAndTailSequenceGapsRejectWithoutChangingCaller() {
    for (int position : new int[] {201, 5000, 9999}) {
      var input = records();
      var bad = entry(position + 1, position + 2, "sequence gap");
      input.set(position, bad);
      assertThrows(
          LayoutValidationException.class, () -> new ScenarioDetailSnapshot(HEADER_FIXTURE, input));
      assertEquals(MAXIMUM_ROWS, input.size());
      assertSame(bad, input.get(position));
      assertEquals(position + 2, input.get(position).entrySequence());
    }
  }

  @Test
  void snapshotMax003TailTextPastWireBoundRejectsBeforeSnapshotEscapes() {
    var input = records();
    var bad = entry(MAXIMUM_ROWS, MAXIMUM_ROWS, "x".repeat(4097));
    input.set(MAXIMUM_ROWS - 1, bad);
    assertThrows(
        FieldEncodingException.class, () -> new ScenarioDetailSnapshot(HEADER_FIXTURE, input));
    assertEquals(MAXIMUM_ROWS, input.size());
    assertSame(bad, input.getLast());
    assertEquals(4097, input.getLast().bodyText().length());
    assertEquals("row-1", input.getFirst().bodyText());
  }

  private static ArrayList<ScenarioEntryRecord> records() {
    var rows = new ArrayList<ScenarioEntryRecord>(MAXIMUM_ROWS);
    for (int index = 1; index <= MAXIMUM_ROWS; index++)
      rows.add(entry(index, index, "row-" + index));
    return rows;
  }

  private static ScenarioEntryRecord entry(int id, int sequence, String body) {
    return new ScenarioEntryRecord(
        new EntryId(id),
        sequence,
        id,
        EntryType.NARRATION,
        Optional.empty(),
        body,
        0,
        Optional.empty(),
        Optional.empty());
  }
}
