package dev.codex.schubert.nk.api.application.scenario;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshot;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SS323/332; CARRIER001..002. Positive-only carriers; held null/query/file cases not executed. */
final class ScenarioCarrierSuccessContractTest {
  @Test
  void carrier001InlineRetainsTheSameNamedImmutableValueWithoutAQuery() {
    var data = new GameListResponseData(0);
    var typed = new TypedPayloadValues(new LayoutId("GAMRSP01"), data, List.of());
    ScenarioQuerySnapshot carrier = new ScenarioQuerySnapshot.Inline(typed);
    assertTrue(carrier instanceof ScenarioQuerySnapshot.Inline);
    var value = ((ScenarioQuerySnapshot.Inline) carrier).value();
    assertSame(typed, value);
    assertSame(data, value.data());
    assertEquals("GAMRSP01", value.layoutId().value());
    assertEquals(0L, ((GameListResponseData) value.data()).totalCount());
    assertTrue(value.records().isEmpty());
  }
  @Test
  void carrier002DetailPreservesAbsenceAndPresentPureSnapshotWithoutFileAccess() {
    var absent = new ScenarioQuerySnapshot.Detail(Optional.empty());
    assertTrue(absent.value().isEmpty());
    var metadata = new ScenarioDetailResponseData(
        new ScriptFileId(19), GameCode.NUKITASHI_1, "PUBLIC SCENARIO",
        DisplayPath.of("public/scenario.txt"), Optional.empty(), Optional.empty(),
        Optional.empty(), Optional.empty(), DeliveryMode.INLINE, Optional.empty(),
        Optional.empty(), 0, Optional.empty(), 0, 0);
    var snapshot = new ScenarioDetailSnapshot(metadata, List.of());
    var reference = Optional.of(snapshot);
    var present = new ScenarioQuerySnapshot.Detail(reference);
    assertSame(reference, present.value());
    assertSame(snapshot, present.value().orElseThrow());
    assertSame(metadata, present.value().orElseThrow().metadata());
    assertEquals(new ScriptFileId(19), present.value().orElseThrow().metadata().scriptFileId());
    assertEquals("PUBLIC SCENARIO", present.value().orElseThrow().metadata().displayTitle());
    assertTrue(present.value().orElseThrow().records().isEmpty());
    assertTrue(absent.value().isEmpty());
  }
}
