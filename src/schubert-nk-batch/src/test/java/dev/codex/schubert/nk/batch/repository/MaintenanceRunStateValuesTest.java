package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * NK-BAT-001/OPS009/UI251/SS331/341/343 6.13/6.15; PT-BAT-RUNSTATE-001..006. Public immutable
 * values only: no original-file, DB, Root, or runtime authority is asserted.
 */
final class MaintenanceRunStateValuesTest {
  private static final UUID RUN_ID = new UUID(0, 1);
  private static final UUID ACTIVATION_ID = new UUID(0, 2);
  private static final Instant CUTOFF = Instant.parse("2026-09-12T15:00:00Z");
  private static final Instant END = Instant.parse("2026-09-12T15:00:01Z");
  private static final BatchRun RUN = new BatchRun(RUN_ID, CUTOFF);
  private static final MaintenanceActivation ACTIVE = new MaintenanceActivation(RUN, ACTIVATION_ID);

  @Test
  void pendingStateHasNoCompletionOrAuthority() {
    var state = new MaintenanceRunState(ACTIVE, Optional.empty());
    assertSame(ACTIVE, state.activation());
    assertFalse(state.completion().isPresent());
    assertEquals("MaintenanceRunState[redacted]", state.toString());
  }

  @Test
  void equivalentActivationAcceptsItsExactCompletion() {
    var equivalent = new MaintenanceActivation(new BatchRun(RUN_ID, CUTOFF), ACTIVATION_ID);
    var completion =
        new MaintenanceCompletion(equivalent, END, MaintenanceCompletion.Outcome.WARNING);
    var state = new MaintenanceRunState(ACTIVE, Optional.of(completion));
    assertSame(ACTIVE, state.activation());
    assertSame(completion, state.completion().orElseThrow());
    assertEquals(RUN, state.completion().orElseThrow().activation().run());
    assertEquals(ACTIVATION_ID, state.completion().orElseThrow().activation().id());
    assertEquals(END, state.completion().orElseThrow().endedAt());
    assertEquals(MaintenanceCompletion.Outcome.WARNING, state.completion().orElseThrow().outcome());
  }

  @Test
  void differentRunCutoffOrActivationCannotSupplyCompletion() {
    for (var foreign :
        List.of(
            new MaintenanceActivation(RUN, new UUID(0, 3)),
            new MaintenanceActivation(new BatchRun(new UUID(0, 4), CUTOFF), ACTIVATION_ID),
            new MaintenanceActivation(
                new BatchRun(RUN_ID, CUTOFF.minusSeconds(1)), ACTIVATION_ID))) {
      var completion =
          new MaintenanceCompletion(foreign, END, MaintenanceCompletion.Outcome.SUCCESS);
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRunState(ACTIVE, Optional.of(completion)));
    }
  }

  @Test
  void constructorsRejectMissingInvariantValues() {
    assertThrows(NullPointerException.class, () -> new MaintenanceRunState(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> new MaintenanceRunState(ACTIVE, null));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceCompletion(null, END, MaintenanceCompletion.Outcome.SUCCESS));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceCompletion(ACTIVE, null, MaintenanceCompletion.Outcome.SUCCESS));
    assertThrows(NullPointerException.class, () -> new MaintenanceCompletion(ACTIVE, END, null));
  }

  @Test
  void completionUsesLiteralTimestampAndMicrosecondBounds() {
    for (String literal : List.of("2026-09-12T15:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      Instant expected = Instant.parse(literal);
      var completion =
          new MaintenanceCompletion(ACTIVE, expected, MaintenanceCompletion.Outcome.SUCCESS);
      assertEquals(expected, completion.endedAt());
    }
    for (String literal :
        List.of(
            "2026-09-12T14:59:59.999999Z",
            "+10000-01-01T00:00:00Z",
            "2026-09-12T15:00:01.000000001Z")) {
      Instant input = Instant.parse(literal);
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceCompletion(ACTIVE, input, MaintenanceCompletion.Outcome.SUCCESS));
    }
  }

  @Test
  void closedOutcomesHaveFixedCodesAndRedactedCompletion() {
    assertEquals(
        List.of("SUCCESS", "WARNING"),
        Arrays.stream(MaintenanceCompletion.Outcome.values()).map(Enum::name).toList());
    assertEquals(0, MaintenanceCompletion.Outcome.SUCCESS.exitCode());
    assertEquals(10, MaintenanceCompletion.Outcome.WARNING.exitCode());
    assertThrows(
        IllegalArgumentException.class, () -> MaintenanceCompletion.Outcome.valueOf("FAILED"));
    for (var outcome :
        List.of(MaintenanceCompletion.Outcome.SUCCESS, MaintenanceCompletion.Outcome.WARNING)) {
      var completion = new MaintenanceCompletion(ACTIVE, END, outcome);
      assertSame(ACTIVE, completion.activation());
      assertEquals(END, completion.endedAt());
      assertSame(outcome, completion.outcome());
      assertEquals("MaintenanceCompletion[identity/time=<redacted>]", completion.toString());
    }
  }
}
