package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** MAIN455001/002 typed completion after all-scope return, not native execution credit. */
final class MorningCompletedMainTest {
  static final UUID RUN = UUID.fromString("00000000-0000-4000-8000-000000000455");
  static final MaintenanceActivation ACTIVATION =
      new MaintenanceActivation(
          new BatchRun(RUN, Instant.parse("2026-10-04T09:00:00Z")),
          UUID.fromString("00000000-0000-4000-8000-000000000456"));

  @Test
  void main455001TypedSuccessAndWarningOnlyAfterFullReturn() {
    for (var outcome : MaintenanceCompletion.Outcome.values()) {
      var calls = new AtomicInteger();
      int actual =
          MorningProcessMain.runCompleted(
              new String[0],
              (budget, run) -> {
                budget.requireWithin();
                assertEquals(Optional.empty(), run);
                calls.incrementAndGet();
                return new MaintenanceCompletion(
                    ACTIVATION, Instant.parse("2026-10-04T09:01:00Z"), outcome);
              });
      assertEquals(outcome == MaintenanceCompletion.Outcome.SUCCESS ? 0 : 10, actual);
      assertEquals(1, calls.get());
    }
    assertEquals(
        10,
        MorningProcessMain.runCompleted(
            new String[] {"--resume", RUN.toString()},
            (budget, run) -> {
              assertEquals(Optional.of(RUN), run);
              return new MaintenanceCompletion(
                  ACTIVATION,
                  Instant.parse("2026-10-04T09:01:00Z"),
                  MaintenanceCompletion.Outcome.WARNING);
            }));
  }

  @Test
  void main455002PartialAndCloseFailuresNeverBecomeCompleted() {
    assertEquals(
        30,
        MorningProcessMain.runCompleted(
            new String[0],
            (budget, run) -> {
              // Completion-like data inside a failing outer close is never returned to Main.
              new MaintenanceCompletion(
                  ACTIVATION,
                  Instant.parse("2026-10-04T09:01:00Z"),
                  MaintenanceCompletion.Outcome.SUCCESS);
              throw new IOException("fixed close failure");
            }));
    assertThrows(
        NullPointerException.class,
        () -> MorningProcessMain.runCompleted(new String[0], (budget, run) -> null));
    var fatal = new AssertionError("fixed failure");
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                MorningProcessMain.runCompleted(
                    new String[0],
                    (budget, run) -> {
                      throw fatal;
                    })));
    var runtime = new IllegalStateException("fixed failure");
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningProcessMain.runCompleted(
                    new String[0],
                    (budget, run) -> {
                      throw runtime;
                    })));
    assertEquals(30, MorningProcessMain.run(new String[0], budget -> {}));
  }

  @Test
  void main455003InvalidOrMissingArgsNeverEnterCompletion() {
    for (String[] args :
        List.of(
            new String[] {"x"},
            new String[] {"--resume"},
            new String[] {"--resume", "00000000-0000-0000-0000-000000000000"},
            new String[] {"--resume", "invalid"},
            new String[] {"--resume", RUN.toString(), "x"},
            new String[] {"--resume", null},
            new String[] {null, RUN.toString()})) {
      assertEquals(
          70,
          MorningProcessMain.runCompleted(
              args,
              (budget, run) -> {
                throw new AssertionError("must not execute");
              }));
    }
    assertThrows(
        NullPointerException.class,
        () -> MorningProcessMain.runCompleted(null, (budget, run) -> null));
    assertThrows(
        NullPointerException.class, () -> MorningProcessMain.runCompleted(new String[0], null));
  }

  @Test
  void parent455003OuterFailureObserverPrecedesAbortWithoutExpiredCaps() throws Exception {
    var graph = new AtomicReference<MorningControlScope.Gate>();
    var publication = new AtomicReference<MorningPermitPublication>();
    var order = new ArrayList<String>();
    graph.set(() -> order.add("whole-daemon-stop"));
    assertEquals("normal", MorningControlScope.protectGraph(graph, publication, () -> "normal"));
    assertTrue(order.isEmpty());
    var failure = new IOException("fixed outer close");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.protectGraph(
                    graph,
                    publication,
                    () -> {
                      order.add("close-failed");
                      throw failure;
                    })));
    assertEquals(List.of("close-failed", "whole-daemon-stop"), order);
    graph.set(null);
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.protectGraph(
                    graph,
                    publication,
                    () -> {
                      throw failure;
                    })));
    assertThrows(
        NullPointerException.class,
        () -> MorningControlScope.protectGraph(null, publication, () -> "normal"));
  }
}
