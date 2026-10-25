package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/PT-OPS-STOP-001..008; independent fixed systemd property vectors; SS341/343. */
final class ApplicationStopGateTest {
  private static final String API =
      "Id=schubert-nk-api.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\n";
  private static final String WEB =
      "Id=schubert-nk-web.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\n";

  @Test
  void literalAndOrder() {
    assertDoesNotThrow(() -> UnitStateParser.requireStopped(ApplicationUnit.API, bytes(API)));
    assertDoesNotThrow(() -> UnitStateParser.requireStopped(ApplicationUnit.WEB, bytes(WEB)));
    var lines = new ArrayList<>(List.of(API.stripTrailing().split("\n")));
    for (int i = 0; i < 7; i++) {
      Collections.rotate(lines, 1);
      assertDoesNotThrow(
          () ->
              UnitStateParser.requireStopped(
                  ApplicationUnit.API, bytes(String.join("\n", lines) + "\n")));
    }
  }

  @Test
  void nonStoppedStates() {
    for (var entry :
        Map.of(
                "LoadState",
                List.of("not-found", "masked", "error", ""),
                "ActiveState",
                List.of("active", "failed", "activating", "deactivating", ""),
                "SubState",
                List.of("running", "exited", "stop-sigterm", ""),
                "Job",
                List.of("0", "1", "queued", "~"),
                "MainPID",
                List.of("1", "00", "-1", ""),
                "ControlPID",
                List.of("1", "00", "-1", ""))
            .entrySet()) {
      for (String value : entry.getValue())
        reject(StopGateFailure.NOT_STOPPED, replace(entry.getKey(), value));
    }
  }

  @Test
  void malformedFields() {
    for (String line : API.stripTrailing().split("\n")) {
      reject(StopGateFailure.MALFORMED_STATE, API.replace(line + "\n", ""));
      reject(StopGateFailure.MALFORMED_STATE, API + line + "\n");
      reject(StopGateFailure.MALFORMED_STATE, API.replace(line, "Unknown" + line));
    }
    reject(StopGateFailure.MALFORMED_STATE, API.replace("Job=", "MainPID="));
    reject(StopGateFailure.MALFORMED_STATE, API.replace("Job=", "MainPID=0"));
    reject(StopGateFailure.MALFORMED_STATE, API.replace("Job=", "no-equals"));
    reject(StopGateFailure.MALFORMED_STATE, API.replace("Job=", "=empty-key"));
    reject(StopGateFailure.MALFORMED_STATE, API.replace("Job=", "Job=x=y"));
    reject(StopGateFailure.MALFORMED_STATE, API.replace("Id=", "id="));
    reject(
        StopGateFailure.MALFORMED_STATE,
        API.replace("schubert-nk-api.service", "schubert-nk-web.service"));
    reject(StopGateFailure.MALFORMED_STATE, replace("Id", ""));
  }

  @Test
  void byteAndNullContracts() {
    reject(StopGateFailure.MALFORMED_STATE, "");
    reject(StopGateFailure.MALFORMED_STATE, API.stripTrailing());
    reject(StopGateFailure.MALFORMED_STATE, API + "\n");
    reject(StopGateFailure.MALFORMED_STATE, "\n" + API);
    for (int value = 0; value <= 31; value++) {
      byte[] bad = bytes(API);
      bad[2] = (byte) value;
      failure(
          StopGateFailure.MALFORMED_STATE,
          () -> UnitStateParser.requireStopped(ApplicationUnit.API, bad));
    }
    for (int position = 0; position < API.length(); position++)
      for (int value : List.of(0, 13, 127, 128, 255)) {
        byte[] bad = bytes(API);
        bad[position] = (byte) value;
        failure(
            StopGateFailure.MALFORMED_STATE,
            () -> UnitStateParser.requireStopped(ApplicationUnit.API, bad));
      }
    String boundary = replace("Job", "x".repeat(1024 - API.length()));
    assertEquals(1024, bytes(boundary).length);
    reject(StopGateFailure.NOT_STOPPED, boundary);
    reject(StopGateFailure.MALFORMED_STATE, boundary.replace("Job=", "Job=x"));
    assertThrows(
        NullPointerException.class, () -> UnitStateParser.requireStopped(null, bytes(API)));
    assertThrows(
        NullPointerException.class,
        () -> UnitStateParser.requireStopped(ApplicationUnit.API, null));
  }

  @Test
  void gateOrderAndFreshReads() {
    var calls = new ArrayList<ApplicationUnit>();
    var gate =
        new ApplicationStopGate(
            unit -> {
              calls.add(unit);
              return literal(unit);
            });
    gate.requireStopped();
    gate.requireStopped();
    assertEquals(
        List.of(ApplicationUnit.API, ApplicationUnit.WEB, ApplicationUnit.API, ApplicationUnit.WEB),
        calls);
    for (ApplicationUnit stoppedAt : ApplicationUnit.values()) {
      calls.clear();
      var rejected =
          new ApplicationStopGate(
              unit -> {
                calls.add(unit);
                return unit == stoppedAt ? new byte[0] : literal(unit);
              });
      failure(StopGateFailure.MALFORMED_STATE, rejected::requireStopped);
      assertEquals(
          stoppedAt == ApplicationUnit.API
              ? List.of(ApplicationUnit.API)
              : List.of(ApplicationUnit.API, ApplicationUnit.WEB),
          calls);
    }
  }

  @Test
  void interruptAndFailure() {
    var calls = new AtomicInteger();
    try {
      Thread.currentThread().interrupt();
      failure(
          StopGateFailure.INTERRUPTED,
          new ApplicationStopGate(
                  unit -> {
                    calls.incrementAndGet();
                    return literal(unit);
                  })
              ::requireStopped);
      assertEquals(0, calls.get());
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    for (var interruptAt : ApplicationUnit.values())
      try {
        var gate =
            new ApplicationStopGate(
                unit -> {
                  if (unit == interruptAt) Thread.currentThread().interrupt();
                  return literal(unit);
                });
        failure(StopGateFailure.INTERRUPTED, gate::requireStopped);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    var expected = new StopGateException(StopGateFailure.COMMAND_FAILURE);
    assertSame(
        expected,
        assertThrows(
            StopGateException.class,
            new ApplicationStopGate(
                    unit -> {
                      throw expected;
                    })
                ::requireStopped));
    var runtime = new IllegalStateException("programming failure");
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            new ApplicationStopGate(
                    unit -> {
                      throw runtime;
                    })
                ::requireStopped));
    assertThrows(NullPointerException.class, new ApplicationStopGate(unit -> null)::requireStopped);
  }

  @Test
  void concurrentChecks() throws Exception {
    var api = new AtomicInteger();
    var web = new AtomicInteger();
    var gate =
        new ApplicationStopGate(
            unit -> {
              (unit == ApplicationUnit.API ? api : web).incrementAndGet();
              return literal(unit);
            });
    try (var executor = Executors.newFixedThreadPool(16)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            () -> {
              gate.requireStopped();
              return true;
            });
      for (var done : executor.invokeAll(tasks)) assertTrue(done.get(5, TimeUnit.SECONDS));
    }
    assertEquals(64, api.get());
    assertEquals(64, web.get());
  }

  @Test
  void factoryAndContracts() {
    assertThrows(NullPointerException.class, () -> new ApplicationStopGate(null));
    assertThrows(NullPointerException.class, () -> new StopGateException(null));
    assertEquals("schubert-nk-api.service", ApplicationUnit.API.serviceName());
    assertEquals("schubert-nk-web.service", ApplicationUnit.WEB.serviceName());
    assertEquals(
        List.of("MALFORMED_STATE", "NOT_STOPPED", "COMMAND_FAILURE", "TIMEOUT", "INTERRUPTED"),
        Arrays.stream(StopGateFailure.values()).map(Enum::name).toList());
    // Dedicated PG/PT host has no deployed NK units: not-found/inactive must not become success.
    failure(StopGateFailure.NOT_STOPPED, ApplicationStopGate.create()::requireStopped);
  }

  private static byte[] literal(ApplicationUnit unit) {
    return bytes(unit == ApplicationUnit.API ? API : WEB);
  }

  private static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  private static String replace(String key, String value) {
    return API.replaceAll("(?m)^" + key + "=[^\n]*", key + "=" + value);
  }

  private static void reject(StopGateFailure expected, String text) {
    failure(expected, () -> UnitStateParser.requireStopped(ApplicationUnit.API, bytes(text)));
  }

  private static void failure(StopGateFailure expected, Runnable action) {
    var failure = assertThrows(StopGateException.class, action::run);
    assertEquals(expected, failure.reason());
    assertEquals("application stop check failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
