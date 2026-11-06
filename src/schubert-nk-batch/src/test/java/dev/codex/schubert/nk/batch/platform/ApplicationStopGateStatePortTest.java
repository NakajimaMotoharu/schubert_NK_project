package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/** PT-OPS-STOPPORT001..006 / OPS009 UI251 SS341/343. Fixed bytes, no OS state query. */
final class ApplicationStopGateStatePortTest {
  private static final String API_STATE =
      "Id=schubert-nk-api.service\n"
          + "LoadState=loaded\n"
          + "ActiveState=inactive\n"
          + "SubState=dead\n"
          + "Job=\n"
          + "MainPID=0\n"
          + "ControlPID=0\n";
  private static final String WEB_STATE =
      "Id=schubert-nk-web.service\n"
          + "LoadState=loaded\n"
          + "ActiveState=inactive\n"
          + "SubState=dead\n"
          + "Job=\n"
          + "MainPID=0\n"
          + "ControlPID=0\n";
  private static final String BAD_STATE = "public malformed projection\n";

  @BeforeEach
  void requireUninterruptedOwnTestThread() {
    assertFalse(Thread.currentThread().isInterrupted());
  }

  @AfterEach
  void restoreOwnTestThreadInterruptFlag() {
    Thread.interrupted();
  }

  @Test
  void constructorsRequireSourceAndFactoryOnlyBuildsIndependentDormantGates() {
    assertThrows(NullPointerException.class, () -> new ApplicationStopGate(null));
    var first = ApplicationStopGate.create();
    var second = ApplicationStopGate.create();
    assertNotSame(first, second);
    assertEquals(ApplicationStopGate.class, first.getClass());
    // Deliberately never call requireStopped on a factory-created default OS source.
  }

  @Test
  void everyCheckReadsBothFixedProjectionsInApiThenWebOrderWithoutCaching() {
    var calls = new ArrayList<ApplicationUnit>();
    var arrays = new ArrayList<byte[]>();
    var gate =
        new ApplicationStopGate(
            unit -> {
              calls.add(unit);
              byte[] value = state(unit);
              arrays.add(value);
              return value;
            });
    gate.requireStopped();
    gate.requireStopped();
    assertEquals(
        List.of(ApplicationUnit.API, ApplicationUnit.WEB, ApplicationUnit.API, ApplicationUnit.WEB),
        calls);
    for (int index = 0; index < arrays.size(); index++) {
      assertArrayEquals(
          state(index % 2 == 0 ? ApplicationUnit.API : ApplicationUnit.WEB), arrays.get(index));
    }
    assertNotSame(arrays.get(0), arrays.get(2));
    assertFalse(Thread.currentThread().isInterrupted());
  }

  @Test
  void sourceFailuresAndInvalidBytesRejectBeforeLaterUnitWithoutNormalizingFailure() {
    for (Throwable failure :
        List.of(
            new IllegalStateException("public source failure"),
            new AssertionError("public source error"))) {
      var calls = new ArrayList<ApplicationUnit>();
      var gate =
          new ApplicationStopGate(
              unit -> {
                calls.add(unit);
                if (failure instanceof RuntimeException typed) throw typed;
                throw (Error) failure;
              });
      assertSame(failure, assertThrows(failure.getClass(), gate::requireStopped));
      assertEquals(List.of(ApplicationUnit.API), calls);
    }
    var nullCalls = new ArrayList<ApplicationUnit>();
    assertThrows(
        NullPointerException.class,
        () ->
            new ApplicationStopGate(
                    unit -> {
                      nullCalls.add(unit);
                      return null;
                    })
                .requireStopped());
    assertEquals(List.of(ApplicationUnit.API), nullCalls);
    for (boolean malformed : new boolean[] {false, true}) {
      var calls = new ArrayList<ApplicationUnit>();
      var gate =
          new ApplicationStopGate(
              unit -> {
                calls.add(unit);
                return (malformed
                        ? BAD_STATE
                        : API_STATE.replace("ActiveState=inactive", "ActiveState=active"))
                    .getBytes(StandardCharsets.US_ASCII);
              });
      var failure = assertThrows(StopGateException.class, gate::requireStopped);
      assertEquals(
          malformed ? StopGateFailure.MALFORMED_STATE : StopGateFailure.NOT_STOPPED,
          failure.reason());
      assertEquals("application stop check failed", failure.getMessage());
      assertEquals(List.of(ApplicationUnit.API), calls);
    }
  }

  @Test
  void existingAndCallbackInterruptionsRetainFlagAndStopAtEachOwnedBoundary() {
    var calls = new ArrayList<ApplicationUnit>();
    var gate =
        new ApplicationStopGate(
            unit -> {
              calls.add(unit);
              return state(unit);
            });
    Thread.currentThread().interrupt();
    try {
      assertEquals(
          StopGateFailure.INTERRUPTED,
          assertThrows(StopGateException.class, gate::requireStopped).reason());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(List.of(), calls);
    } finally {
      Thread.interrupted();
    }
    for (ApplicationUnit interruptAt : ApplicationUnit.values()) {
      var observed = new ArrayList<ApplicationUnit>();
      var interrupted =
          new ApplicationStopGate(
              unit -> {
                observed.add(unit);
                if (unit == interruptAt) Thread.currentThread().interrupt();
                return state(unit);
              });
      try {
        assertEquals(
            StopGateFailure.INTERRUPTED,
            assertThrows(StopGateException.class, interrupted::requireStopped).reason());
        assertTrue(Thread.currentThread().isInterrupted());
        assertEquals(
            interruptAt == ApplicationUnit.API
                ? List.of(ApplicationUnit.API)
                : List.of(ApplicationUnit.API, ApplicationUnit.WEB),
            observed);
      } finally {
        Thread.interrupted();
      }
    }
  }

  @Test
  void failedProjectionDoesNotBecomeCachedSuccessAndLaterCheckReadsFreshBothUnits() {
    var first = new AtomicBoolean(true);
    var calls = new ArrayList<ApplicationUnit>();
    var gate =
        new ApplicationStopGate(
            unit -> {
              calls.add(unit);
              return first.getAndSet(false)
                  ? BAD_STATE.getBytes(StandardCharsets.US_ASCII)
                  : state(unit);
            });
    assertEquals(
        StopGateFailure.MALFORMED_STATE,
        assertThrows(StopGateException.class, gate::requireStopped).reason());
    gate.requireStopped();
    assertEquals(List.of(ApplicationUnit.API, ApplicationUnit.API, ApplicationUnit.WEB), calls);
  }

  @Test
  void sharedGateUsesSixteenIndependentWorkerProjectionsWithoutSharedCache() throws Exception {
    var observed = ThreadLocal.withInitial(ArrayList<ApplicationUnit>::new);
    var gate =
        new ApplicationStopGate(
            unit -> {
              observed.get().add(unit);
              return state(unit);
            });
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<?>>();
      for (int index = 0; index < 16; index++) {
        jobs.add(
            workers.submit(
                () -> {
                  observed.remove();
                  try {
                    assertFalse(Thread.currentThread().isInterrupted());
                    gate.requireStopped();
                    gate.requireStopped();
                    assertEquals(
                        List.of(
                            ApplicationUnit.API,
                            ApplicationUnit.WEB,
                            ApplicationUnit.API,
                            ApplicationUnit.WEB),
                        observed.get());
                  } finally {
                    observed.remove();
                  }
                  return null;
                }));
      }
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
    }
  }

  private static byte[] state(ApplicationUnit unit) {
    return (unit == ApplicationUnit.API ? API_STATE : WEB_STATE)
        .getBytes(StandardCharsets.US_ASCII);
  }
}
