package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.BackupUnitStartClient;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.Test;

/**
 * SSC237/PT-OPS-COMPLETION790001..004; literal mutations/proofs, independent of code-generated
 * expected.
 */
final class MorningCompletionRetirementTest {
  private static final String FIXTURE_PENDING_12ADAC54 = "pending";
  private static final String FIXTURE_RETIRED_C6F3C288 = "retired";
  private static final String FIXTURE_PRIVATE_SECONDARY_5CBC33CB = "PRIVATE secondary";
  private static final List<String> EXPECTED =
      List.of(
          FIXTURE_PENDING_12ADAC54,
          "unlink:CADDY",
          FIXTURE_PENDING_12ADAC54,
          FIXTURE_PENDING_12ADAC54,
          "unlink:WEB",
          FIXTURE_RETIRED_C6F3C288,
          "api-held",
          FIXTURE_RETIRED_C6F3C288,
          FIXTURE_RETIRED_C6F3C288,
          "unlink:API",
          FIXTURE_RETIRED_C6F3C288,
          FIXTURE_RETIRED_C6F3C288);

  private static MorningStartupLaunchOwner.CompletionRetirement attempt(
      String service, List<String> events) {
    return (before, after) -> {
      before.verify();
      events.add("unlink:" + service);
      after.verify();
    };
  }

  private static void run(
      List<String> events,
      BackupUnitStartClient.RetirementGate pending,
      BackupUnitStartClient.RetirementGate retired,
      MorningStartupLaunchOwner.CompletionProgress progress)
      throws IOException {
    MorningStartupLaunchOwner.retireCompleted(
        attempt("CADDY", events),
        attempt("WEB", events),
        attempt("API", events),
        gate -> {
          events.add("api-held");
          gate.verify();
        },
        pending,
        retired,
        progress);
  }

  @Test
  void completion790001EveryBoundaryUsesFullProofAndSameThread() throws Exception {
    var events = new ArrayList<String>();
    var lines = new ArrayList<String>();
    var time = new AtomicLong(100);
    long thread = Thread.currentThread().threadId();
    var progress =
        new MorningStartupLaunchOwner.CompletionProgress(time::getAndIncrement, lines::add);
    run(
        events,
        () -> {
          assertEquals(thread, Thread.currentThread().threadId());
          events.add(FIXTURE_PENDING_12ADAC54);
        },
        () -> {
          assertEquals(thread, Thread.currentThread().threadId());
          events.add(FIXTURE_RETIRED_C6F3C288);
        },
        progress);
    assertEquals(EXPECTED, events);
    assertEquals(
        List.of(
            "CADDY_BEFORE",
            "CADDY_AFTER",
            "WEB_BEFORE",
            "WEB_AFTER",
            "API_HELD",
            "API_BEFORE",
            "API_AFTER",
            "ALL_RETIRED"),
        lines.stream().map(s -> s.split(" ")[1].substring("phase=".length())).toList());
    assertEquals(
        "event=morning.completion phase=CADDY_BEFORE classification=VERIFY elapsedNanos=1",
        lines.getFirst());
    assertEquals(
        "event=morning.completion phase=ALL_RETIRED classification=VERIFY elapsedNanos=8",
        lines.getLast());
  }

  @Test
  void completion790002EveryRowSealReceiptPeerFailureStopsNextUnlinkAndDone() {
    for (int boundary = 0; boundary < 8; boundary++)
      for (String cause : List.of("row", "seal", "receipt", "peer", "budget", "close"))
        for (Throwable failure :
            List.of(
                new IOException("PRIVATE " + cause),
                new IllegalStateException("PRIVATE " + cause),
                new AssertionError("PRIVATE " + cause))) {
          var events = new ArrayList<String>();
          var lines = new ArrayList<String>();
          int failAt = boundary;
          int[] calls = {0};
          var progress = new MorningStartupLaunchOwner.CompletionProgress(() -> 42, lines::add);
          BackupUnitStartClient.RetirementGate pending =
              () -> {
                if (calls[0]++ == failAt) raise(failure);
                events.add(FIXTURE_PENDING_12ADAC54);
              };
          BackupUnitStartClient.RetirementGate retired =
              () -> {
                if (calls[0]++ == failAt) raise(failure);
                events.add(FIXTURE_RETIRED_C6F3C288);
              };
          var actual =
              assertThrows(
                  failure.getClass(),
                  () -> {
                    run(events, pending, retired, progress);
                    events.add("DONE");
                  });
          assertSame(failure, actual);
          assertEquals(boundary + 1, calls[0]);
          assertFalse(events.contains("DONE"));
          int prefix = List.of(0, 2, 3, 5, 7, 8, 10, 11).get(boundary);
          assertEquals(EXPECTED.subList(0, prefix), events);
          progress.failure(actual);
          assertFalse(String.join("\n", lines).contains("PRIVATE"));
          assertTrue(
              lines
                  .getLast()
                  .contains(
                      "classification="
                          + (failure instanceof IOException
                              ? "IO"
                              : failure instanceof Error ? "FATAL" : "RUNTIME")));
        }
  }

  @Test
  void completion790003NullContractsCannotEmitOrMutate() {
    var events = new ArrayList<String>();
    var progress = new MorningStartupLaunchOwner.CompletionProgress(() -> 0, events::add);
    var op = attempt("literal", events);
    BackupUnitStartClient.RetirementGate proof = () -> events.add("proof");
    MorningStartupLaunchOwner.ApiRetained hold = gate -> gate.verify();
    for (int missing = 0; missing < 7; missing++) {
      int n = missing;
      assertThrows(
          NullPointerException.class,
          () ->
              MorningStartupLaunchOwner.retireCompleted(
                  n == 0 ? null : op,
                  n == 1 ? null : op,
                  n == 2 ? null : op,
                  n == 3 ? null : hold,
                  n == 4 ? null : proof,
                  n == 5 ? null : proof,
                  n == 6 ? null : progress));
    }
    assertThrows(
        NullPointerException.class,
        () -> new MorningStartupLaunchOwner.CompletionProgress(null, events::add));
    assertThrows(
        NullPointerException.class,
        () -> new MorningStartupLaunchOwner.CompletionProgress(() -> 0, null));
    assertThrows(NullPointerException.class, () -> progress.phase(null));
    assertThrows(NullPointerException.class, () -> progress.failure(null));
    assertEquals(List.of(), events);
  }

  @Test
  void completion790004DonePhaseAndFixedDiagnosticsNeverInspectExceptionMessage() {
    var lines = new ArrayList<String>();
    var time = new AtomicLong(17);
    var progress =
        new MorningStartupLaunchOwner.CompletionProgress(time::getAndIncrement, lines::add);
    progress.phase(MorningStartupLaunchOwner.CompletionPhase.DONE_BEFORE);
    progress.phase(MorningStartupLaunchOwner.CompletionPhase.DONE_AFTER);
    for (Throwable failure :
        List.of(
            new IOException("password=PRIVATE"),
            new IllegalStateException("token=PRIVATE"),
            new AssertionError("session=PRIVATE"))) progress.failure(failure);
    assertEquals(
        List.of(
            "event=morning.completion phase=DONE_BEFORE classification=VERIFY elapsedNanos=1",
            "event=morning.completion phase=DONE_AFTER classification=VERIFY elapsedNanos=2",
            "event=morning.completion phase=DONE_AFTER classification=IO elapsedNanos=3",
            "event=morning.completion phase=DONE_AFTER classification=RUNTIME elapsedNanos=4",
            "event=morning.completion phase=DONE_AFTER classification=FATAL elapsedNanos=5"),
        lines);
  }

  private static void raise(Throwable failure) throws IOException {
    if (failure instanceof IOException checked) throw checked;
    if (failure instanceof RuntimeException unchecked) throw unchecked;
    throw (Error) failure;
  }

  @Test
  void completion326001FailureDiagnosticCannotThrowBeforeOwnerRetention() {
    var vectors = new ArrayList<org.junit.jupiter.api.function.Executable>();
    var primary =
        List.of(
            new IOException("PRIVATE primary"),
            new IllegalStateException("PRIVATE primary"),
            new AssertionError("PRIVATE primary"));
    var labels = List.of("IO", "RUNTIME", "FATAL");
    for (int index = 0; index < primary.size(); index++) {
      var original = primary.get(index);
      var label = labels.get(index);
      for (boolean clockFailure : List.of(false, true))
        for (boolean error : List.of(false, true))
          vectors.add(
              () -> {
                var reads = new AtomicLong();
                var lines = new ArrayList<String>();
                var secondary =
                    error
                        ? new AssertionError(FIXTURE_PRIVATE_SECONDARY_5CBC33CB)
                        : new IllegalStateException(FIXTURE_PRIVATE_SECONDARY_5CBC33CB);
                var progress =
                    new MorningStartupLaunchOwner.CompletionProgress(
                        () -> {
                          long call = reads.incrementAndGet();
                          if (clockFailure && call == 2) throwUnchecked(secondary);
                          return 100;
                        },
                        line -> {
                          lines.add(line);
                          throwUnchecked(secondary);
                        });
                assertDoesNotThrow(() -> progress.failure(original));
                assertEquals(2, reads.get());
                assertEquals(
                    clockFailure
                        ? List.of()
                        : List.of(
                            "event=morning.completion phase=CADDY_BEFORE classification="
                                + label
                                + " elapsedNanos=0"),
                    lines);
              });
    }
    assertAll(vectors);
  }

  @Test
  void completion326002NormalPhaseDiagnosticStillPropagatesIdenticalFailure() {
    for (boolean clockFailure : List.of(false, true))
      for (boolean error : List.of(false, true)) {
        var reads = new AtomicLong();
        var secondary =
            error
                ? new AssertionError(FIXTURE_PRIVATE_SECONDARY_5CBC33CB)
                : new IllegalStateException(FIXTURE_PRIVATE_SECONDARY_5CBC33CB);
        var progress =
            new MorningStartupLaunchOwner.CompletionProgress(
                () -> {
                  long call = reads.incrementAndGet();
                  if (clockFailure && call == 2) throwUnchecked(secondary);
                  return 100;
                },
                line -> throwUnchecked(secondary));
        assertSame(
            secondary,
            assertThrows(
                secondary.getClass(),
                () -> progress.phase(MorningStartupLaunchOwner.CompletionPhase.DONE_AFTER)));
        assertEquals(2, reads.get());
      }
  }

  private static void throwUnchecked(Throwable failure) {
    if (failure instanceof Error fatal) throw fatal;
    throw (RuntimeException) failure;
  }
}
