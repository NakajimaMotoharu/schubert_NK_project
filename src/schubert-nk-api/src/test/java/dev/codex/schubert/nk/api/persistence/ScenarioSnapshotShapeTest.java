package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-SCN-SHAPE001..004; immutable shape/value contracts without file/DB/authentication access. */
final class ScenarioSnapshotShapeTest {
  @Test
  void fileMetadataAnd10001RecordsRejectAtShapeBeforeAnyResultEscapes() {
    var file = header(DeliveryMode.FILE);
    var rejected =
        assertThrows(
            IllegalArgumentException.class, () -> new ScenarioDetailSnapshot(file, List.of()));
    assertEquals("invalid scenario snapshot shape", rejected.getMessage());
    var tooMany = Collections.nCopies(10_001, entry());
    var count =
        assertThrows(
            IllegalArgumentException.class,
            () -> new ScenarioDetailSnapshot(header(DeliveryMode.INLINE), tooMany));
    assertEquals("invalid scenario snapshot shape", count.getMessage());
    assertEquals(10_001, tooMany.size());
    assertEquals(1, tooMany.getLast().entrySequence());
  }

  @Test
  void nullMetadataListAndListElementsAreContractRejectionsWithoutNullNormalization() {
    var header = header(DeliveryMode.INLINE);
    assertThrows(NullPointerException.class, () -> new ScenarioDetailSnapshot(null, List.of()));
    assertThrows(NullPointerException.class, () -> new ScenarioDetailSnapshot(header, null));
    var rows = new ArrayList<ScenarioEntryRecord>();
    rows.add(null);
    assertThrows(NullPointerException.class, () -> new ScenarioDetailSnapshot(header, rows));
    assertEquals(1, rows.size());
  }

  @Test
  void zeroAndOneInlineRecordsKeepOnlyTheirOwnedImmutableSnapshot() {
    var header = header(DeliveryMode.INLINE);
    var empty = new ScenarioDetailSnapshot(header, List.of());
    assertTrue(empty.records().isEmpty());
    assertEquals("ScenarioDetailSnapshot[recordCount=0]", empty.toString());
    var record = entry();
    var input = new ArrayList<>(List.of(record));
    var one = new ScenarioDetailSnapshot(header, input);
    input.clear();
    assertEquals(1, one.records().size());
    assertSame(record, one.records().getFirst());
    assertSame(header, one.metadata());
    assertEquals("independent shape fixture", one.records().getFirst().bodyText());
    assertEquals("ScenarioDetailSnapshot[recordCount=1]", one.toString());
    assertThrows(UnsupportedOperationException.class, () -> one.records().clear());
  }

  @Test
  void shape004EqualLogicalSnapshotsRemainSearchableAfterInputMutation() {
    var input = new ArrayList<>(List.of(entry()));
    var captured = new ScenarioDetailSnapshot(header(DeliveryMode.INLINE), input);
    var sameValue = new ScenarioDetailSnapshot(header(DeliveryMode.INLINE), List.of(entry()));
    var values = new HashSet<ScenarioDetailSnapshot>();
    assertTrue(values.add(captured));
    input.clear();
    assertEquals(captured, sameValue);
    assertTrue(values.contains(sameValue));
    assertFalse(values.add(sameValue));

    var differentBody =
        new ScenarioDetailSnapshot(header(DeliveryMode.INLINE), List.of(entry("different body")));
    var differentTitle =
        new ScenarioDetailSnapshot(
            header(DeliveryMode.INLINE, "different title"), List.of(entry()));
    assertTrue(values.add(differentBody));
    assertTrue(values.add(differentTitle));
    assertEquals(3, values.size());
  }

  private static ScenarioEntryRecord entry() {
    return entry("independent shape fixture");
  }

  private static ScenarioEntryRecord entry(String body) {
    return new ScenarioEntryRecord(
        new EntryId(1),
        1,
        1,
        EntryType.NARRATION,
        Optional.empty(),
        body,
        0,
        Optional.empty(),
        Optional.empty());
  }

  private static ScenarioDetailResponseData header(DeliveryMode mode) {
    return header(mode, "shape fixture");
  }

  private static ScenarioDetailResponseData header(DeliveryMode mode, String title) {
    boolean file = mode == DeliveryMode.FILE;
    return new ScenarioDetailResponseData(
        new ScriptFileId(1),
        GameCode.NUKITASHI_1,
        title,
        DisplayPath.of("scenario/shape.txt"),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        mode,
        file ? Optional.of(new UUID(0, 1)) : Optional.empty(),
        file ? Optional.of(RelativePath.of("results/shape.scn")) : Optional.empty(),
        file ? 6784 : 0,
        file ? Optional.of(Sha256Hex.of("0".repeat(64))) : Optional.empty(),
        file ? 4800 : 0,
        file ? 1 : 0);
  }
}
