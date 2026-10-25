package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.apache.catalina.LifecycleException;
import org.junit.jupiter.api.Test;

/** SS313342352/PG-D378/WEB-REM004: independent control order and original failure identity. */
final class WebRuntimeExecutionTest {
  @Test
  void rem004NormalAndEveryStartOrAwaitFailureStopsAndClosesOnce() throws Exception {
    for (int phase : new int[] {-1, 0, 1}) {
      for (Throwable primary :
          List.of(
              new IOException("synthetic"),
              new IllegalStateException("synthetic"),
              new AssertionError("synthetic"))) {
        var events = new ArrayList<String>();
        var start =
            (WebRuntimeExecution.Start)
                () -> {
                  events.add("start");
                  if (phase == 0) raise(primary);
                };
        var await =
            (WebRuntimeExecution.Io)
                () -> {
                  events.add("await");
                  if (phase == 1) raise(primary);
                };
        if (phase == -1)
          WebRuntimeExecution.execute(
              start, await, () -> events.add("stop"), () -> events.add("close"));
        else
          assertSame(
              primary,
              assertThrows(
                  primary.getClass(),
                  () ->
                      WebRuntimeExecution.execute(
                          start, await, () -> events.add("stop"), () -> events.add("close"))));
        assertEquals(
            phase == 0
                ? List.of("start", "stop", "close")
                : List.of("start", "await", "stop", "close"),
            events);
      }
    }
    var events = new ArrayList<String>();
    IOException converted =
        assertThrows(
            IOException.class,
            () ->
                WebRuntimeExecution.execute(
                    () -> {
                      events.add("start");
                      throw new LifecycleException("synthetic private");
                    },
                    () -> fail("failed startup must not await"),
                    () -> events.add("stop"),
                    () -> events.add("close")));
    assertEquals("Web HTTP startup unavailable", converted.getMessage());
    assertNull(converted.getCause());
    assertEquals(0, converted.getSuppressed().length);
    assertEquals(List.of("start", "stop", "close"), events);
  }

  @Test
  void rem004InvariantsRejectAbsentCallbacksBeforeFirstAction() {
    WebRuntimeExecution.Start start = () -> fail("invalid callbacks must not start");
    WebRuntimeExecution.Io io = () -> fail("invalid callbacks must not borrow");
    Runnable stop = () -> fail("invalid callbacks must not stop");
    assertThrows(NullPointerException.class, () -> WebRuntimeExecution.execute(null, io, stop, io));
    assertThrows(
        NullPointerException.class, () -> WebRuntimeExecution.execute(start, null, stop, io));
    assertThrows(
        NullPointerException.class, () -> WebRuntimeExecution.execute(start, io, null, io));
    assertThrows(
        NullPointerException.class, () -> WebRuntimeExecution.execute(start, io, stop, null));
  }

  private static void raise(Throwable failure) throws IOException {
    if (failure instanceof IOException io) throw io;
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }
}
