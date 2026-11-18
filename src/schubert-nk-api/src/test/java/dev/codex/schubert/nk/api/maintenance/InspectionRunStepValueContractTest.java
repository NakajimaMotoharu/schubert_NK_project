package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.maintenance.InspectionStep.Outcome;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-P01810-CATALOG-016/017, SS341/351 and BUG-3222. */
final class InspectionRunStepValueContractTest {
  private static final Instant FIRST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LAST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private static final UUID RUN_ID = new UUID(3, 5);
  private static final UUID OTHER_RUN_ID = new UUID(3, 9);
  private static final UUID CURSOR = new UUID(12, 17);
  private static final UUID OTHER_CURSOR = new UUID(12, 23);

  @Test
  void runPreservesLiteralMicrosecondsAndRejectsNoncanonicalCutoffs() {
    for (Instant limit : List.of(FIRST, LAST, Instant.parse("2026-11-18T00:01:02.000003Z"))) {
      var run = new InspectionRun(RUN_ID, limit);
      assertEquals(RUN_ID, run.id());
      assertEquals(limit, run.cutoff());
      assertEquals("InspectionRun[identity/cutoff=<redacted>]", run.toString());
    }

    for (Instant invalid :
        List.of(FIRST.minusNanos(1000), LAST.plusNanos(1000), FIRST.plusNanos(1))) {
      assertThrows(IllegalArgumentException.class, () -> new InspectionRun(RUN_ID, invalid));
    }
    assertThrows(NullPointerException.class, () -> new InspectionRun(null, FIRST));
    assertThrows(NullPointerException.class, () -> new InspectionRun(RUN_ID, null));
  }

  @Test
  void runUsesBothComponentsForValueKeys() {
    var actual = new InspectionRun(RUN_ID, FIRST);
    var same = new InspectionRun(new UUID(3, 5), Instant.parse("0001-01-01T00:00:00Z"));
    var history = new HashMap<InspectionRun, String>();
    var expected = "earliest accepted run";
    history.put(actual, expected);

    assertEquals(actual, same);
    assertEquals(expected, history.get(same));
    assertFalse(history.containsKey(new InspectionRun(OTHER_RUN_ID, FIRST)));
    assertFalse(history.containsKey(new InspectionRun(RUN_ID, LAST)));
  }

  @Test
  void stepRequiresCursorOnlyForNonEndAndRedactsIt() {
    var possible = Optional.of(CURSOR);
    Map<Outcome, String> activeDiagnostics =
        Map.of(
            Outcome.DELETED, "InspectionStep[outcome=DELETED, cursor=<redacted>]",
            Outcome.PROTECTED, "InspectionStep[outcome=PROTECTED, cursor=<redacted>]");
    for (var expectation : activeDiagnostics.entrySet()) {
      var outcome = expectation.getKey();
      var step = new InspectionStep(outcome, possible);
      assertEquals(outcome, step.outcome());
      assertEquals(possible, step.cursor());
      assertEquals(expectation.getValue(), step.toString());
      assertThrows(
          IllegalArgumentException.class, () -> new InspectionStep(outcome, Optional.empty()));
    }
    var completed = new InspectionStep(Outcome.END, Optional.empty());
    assertEquals(Outcome.END, completed.outcome());
    assertEquals(Optional.empty(), completed.cursor());
    assertEquals("InspectionStep[outcome=END, cursor=<redacted>]", completed.toString());
    assertThrows(IllegalArgumentException.class, () -> new InspectionStep(Outcome.END, possible));
    assertThrows(NullPointerException.class, () -> new InspectionStep(null, possible));
    assertThrows(NullPointerException.class, () -> new InspectionStep(Outcome.END, null));
  }

  @Test
  void stepUsesBothComponentsForValueKeysAndRetainsTheOutcomeVocabulary() {
    var start = new InspectionStep(Outcome.DELETED, Optional.of(CURSOR));
    var equal = new InspectionStep(Outcome.DELETED, Optional.of(new UUID(12, 17)));
    var steps = new HashMap<InspectionStep, String>();
    var expected = "selected cursor";
    steps.put(start, expected);

    assertEquals(start, equal);
    assertEquals(expected, steps.get(equal));
    assertFalse(steps.containsKey(new InspectionStep(Outcome.PROTECTED, Optional.of(CURSOR))));
    assertFalse(steps.containsKey(new InspectionStep(Outcome.DELETED, Optional.of(OTHER_CURSOR))));

    Outcome[] vocabulary = {Outcome.DELETED, Outcome.PROTECTED, Outcome.END};
    assertArrayEquals(vocabulary, Outcome.values());
    assertEquals(Outcome.DELETED, Outcome.valueOf("DELETED"));
    assertEquals(Outcome.PROTECTED, Outcome.valueOf("PROTECTED"));
    assertEquals(Outcome.END, Outcome.valueOf("END"));
    assertThrows(IllegalArgumentException.class, () -> Outcome.valueOf("UNRECOGNIZED"));
    assertThrows(NullPointerException.class, () -> Outcome.valueOf(null));
  }
}
