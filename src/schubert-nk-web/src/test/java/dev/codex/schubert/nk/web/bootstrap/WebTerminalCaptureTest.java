package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint;
import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PG-D378/SS342343352/PT-OPS-WEB-REM005..006. Fake owner is not native authority or a pass. */
final class WebTerminalCaptureTest {
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_OPEN_35FF74AE = "open";
  private static final String FIXTURE_VERIFY1_FA6566A5 = "verify1";
  private static final String FIXTURE_VERIFY2_47D6C149 = "verify2";
  private static final String FIXTURE_CAPTURE_47EE4B87 = "capture";
  private static final String FIXTURE_FIND_3FBE8AE3 = "find";
  private static final String FIXTURE_OVERRIDE_454D2E95 = "override";
  private static final NonSecretConfigSource FORBIDDEN =
      service -> {
        throw new AssertionError("argv must reject before file IO");
      };

  @Test
  void rem005OwnerPreservesEveryOperationIdentityAndNullInvariants() throws Exception {
    Object resource = new Object();
    var events = new ArrayList<String>();
    var owner =
        new WebTerminalCapture.Owner<>(
            resource,
            actual -> {
              assertSame(resource, actual);
              events.add("verify");
            },
            actual -> {
              assertSame(resource, actual);
              events.add(FIXTURE_CLOSE_97959247);
            });
    owner.verifyOwner();
    owner.close();
    assertEquals(List.of("verify", FIXTURE_CLOSE_97959247), events);
    assertThrows(
        NullPointerException.class, () -> new WebTerminalCapture.Owner<>(null, x -> {}, x -> {}));
    assertThrows(
        NullPointerException.class, () -> new WebTerminalCapture.Owner<>(resource, null, x -> {}));
    assertThrows(
        NullPointerException.class, () -> new WebTerminalCapture.Owner<>(resource, x -> {}, null));
    assertThrows(NullPointerException.class, () -> new WebTerminalCapture(null, p -> {}));
    assertThrows(NullPointerException.class, () -> new WebTerminalCapture(() -> owner, null));
    assertThrows(
        NullPointerException.class, () -> new WebTerminalCapture(() -> null, p -> {}).open());
    assertTrue(WebTerminalCapture.currentJvm(null).isEmpty());
    for (Throwable failure :
        List.of(
            new IOException("synthetic"),
            new IllegalStateException("synthetic"),
            new AssertionError("synthetic"))) {
      var bad =
          new WebTerminalCapture.Owner<>(
              resource,
              x -> {
                raise(failure);
              },
              x -> {
                raise(failure);
              });
      assertSame(failure, assertThrows(failure.getClass(), bad::verifyOwner));
      assertSame(failure, assertThrows(failure.getClass(), bad::close));
    }
  }

  @Test
  void rem006CaptureMainEnforcesEveryBoundaryAndNeverTerminatesAfterFailure() throws Exception {
    synchronized (System.class) {
      var original = System.err;
      var thread = Thread.currentThread();
      var handler = thread.getUncaughtExceptionHandler();
      try {
        for (int failing : new int[] {-1, 0, 1, 2, 3, 4})
          for (Throwable primary :
              List.of(
                  new IOException("synthetic private"),
                  new IllegalStateException("synthetic private"),
                  new AssertionError("synthetic private"))) {
            var events = new ArrayList<String>();
            var verifies = new AtomicInteger();
            var exits = new ArrayList<Integer>();
            Object resource = new Object();
            var capture =
                new WebTerminalCapture(
                    () -> {
                      events.add(FIXTURE_OPEN_35FF74AE);
                      if (failing == 0) raise(primary);
                      return new WebTerminalCapture.Owner<>(
                          resource,
                          actual -> {
                            assertSame(resource, actual);
                            int n = verifies.getAndIncrement();
                            events.add(
                                n == 0 ? FIXTURE_VERIFY1_FA6566A5 : FIXTURE_VERIFY2_47D6C149);
                            if (failing == (n == 0 ? 1 : 3)) raise(primary);
                          },
                          actual -> {
                            assertSame(resource, actual);
                            events.add(FIXTURE_CLOSE_97959247);
                            if (failing == 4) raise(primary);
                          });
                    },
                    point -> {
                      assertEquals(FixedNativeCoverageCheckpoint.Point.TERMINAL, point);
                      events.add(FIXTURE_CAPTURE_47EE4B87);
                      if (failing == 2) raise(primary);
                    });
            var main =
                new WebProcessMain(
                    Map.of("INVOCATION_ID", "f".repeat(32)),
                    FORBIDDEN,
                    code -> {
                      events.add("exit");
                      exits.add(code);
                    },
                    inv -> {
                      assertEquals("f".repeat(32), inv);
                      events.add(FIXTURE_FIND_3FBE8AE3);
                      return Optional.of(capture);
                    });
            var bytes = new ByteArrayOutputStream();
            try (var err = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
              System.setErr(err);
              if (failing == -1) main.main(new String[] {FIXTURE_OVERRIDE_454D2E95});
              else
                assertSame(
                    primary,
                    assertThrows(
                        primary.getClass(),
                        () -> main.main(new String[] {FIXTURE_OVERRIDE_454D2E95})));
            }
            List<String> expected =
                switch (failing) {
                  case -1 ->
                      List.of(
                          FIXTURE_FIND_3FBE8AE3,
                          FIXTURE_OPEN_35FF74AE,
                          FIXTURE_VERIFY1_FA6566A5,
                          FIXTURE_CAPTURE_47EE4B87,
                          FIXTURE_VERIFY2_47D6C149,
                          FIXTURE_CLOSE_97959247,
                          "exit");
                  case 0 -> List.of(FIXTURE_FIND_3FBE8AE3, FIXTURE_OPEN_35FF74AE);
                  case 1 ->
                      List.of(
                          FIXTURE_FIND_3FBE8AE3,
                          FIXTURE_OPEN_35FF74AE,
                          FIXTURE_VERIFY1_FA6566A5,
                          FIXTURE_CLOSE_97959247);
                  case 2 ->
                      List.of(
                          FIXTURE_FIND_3FBE8AE3,
                          FIXTURE_OPEN_35FF74AE,
                          FIXTURE_VERIFY1_FA6566A5,
                          FIXTURE_CAPTURE_47EE4B87,
                          FIXTURE_CLOSE_97959247);
                  case 3 ->
                      List.of(
                          FIXTURE_FIND_3FBE8AE3,
                          FIXTURE_OPEN_35FF74AE,
                          FIXTURE_VERIFY1_FA6566A5,
                          FIXTURE_CAPTURE_47EE4B87,
                          FIXTURE_VERIFY2_47D6C149,
                          FIXTURE_CLOSE_97959247);
                  default ->
                      List.of(
                          FIXTURE_FIND_3FBE8AE3,
                          FIXTURE_OPEN_35FF74AE,
                          FIXTURE_VERIFY1_FA6566A5,
                          FIXTURE_CAPTURE_47EE4B87,
                          FIXTURE_VERIFY2_47D6C149,
                          FIXTURE_CLOSE_97959247);
                };
            assertEquals(expected, events);
            assertEquals(failing == -1 ? List.of(70) : List.of(), exits);
            assertEquals(
                failing < 0 || failing == 4
                    ? "WEB process stopped\nWEB fixed PT native capture complete\n"
                    : failing >= 2 ? "WEB process stopped\n" : "",
                bytes.toString(StandardCharsets.UTF_8));
          }
        var primary = new IOException("primary");
        var secondary = new IOException("secondary");
        var capture =
            new WebTerminalCapture(
                () ->
                    new WebTerminalCapture.Owner<>(
                        new Object(),
                        x -> {
                          throw primary;
                        },
                        x -> {
                          throw secondary;
                        }),
                p -> fail("failed verification must not capture"));
        var main =
            new WebProcessMain(
                Map.of(),
                FORBIDDEN,
                c -> fail("failed close must not terminate"),
                inv -> Optional.of(capture));
        assertSame(
            primary,
            assertThrows(
                IOException.class, () -> main.main(new String[] {FIXTURE_OVERRIDE_454D2E95})));
        assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
        assertThrows(
            NullPointerException.class,
            () -> new WebProcessMain(Map.of(), FORBIDDEN, c -> {}, null));
      } finally {
        System.setErr(original);
        thread.setUncaughtExceptionHandler(handler);
      }
    }
  }

  @Test
  void rem006NoCaptureAndLookupFailureNeverOpenAnOwner() throws Exception {
    synchronized (System.class) {
      var old = System.err;
      var t = Thread.currentThread();
      var h = t.getUncaughtExceptionHandler();
      var out = new ByteArrayOutputStream();
      var exits = new ArrayList<Integer>();
      try (var err = new PrintStream(out, false, StandardCharsets.UTF_8)) {
        System.setErr(err);
        new WebProcessMain(
                Map.of(),
                FORBIDDEN,
                exits::add,
                inv -> {
                  assertNull(inv);
                  return Optional.empty();
                })
            .main(new String[] {FIXTURE_OVERRIDE_454D2E95});
        assertEquals(List.of(70), exits);
        assertEquals("WEB process stopped\n", out.toString(StandardCharsets.UTF_8));
        var failure = new IOException("synthetic lookup");
        assertSame(
            failure,
            assertThrows(
                IOException.class,
                () ->
                    new WebProcessMain(
                            Map.of(),
                            FORBIDDEN,
                            code -> fail("lookup failure must not terminate"),
                            inv -> {
                              throw failure;
                            })
                        .main(new String[] {FIXTURE_OVERRIDE_454D2E95})));
      } finally {
        System.setErr(old);
        t.setUncaughtExceptionHandler(h);
      }
    }
  }

  private static void raise(Throwable value) throws IOException {
    if (value instanceof IOException io) throw io;
    if (value instanceof RuntimeException runtime) throw runtime;
    throw (Error) value;
  }
}
