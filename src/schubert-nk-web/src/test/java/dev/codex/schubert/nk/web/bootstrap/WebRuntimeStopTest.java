package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.Test;

/** SS342352 / PT-OPS-NWEB-STOP001..005. Independent literal 30s/phase/UNKNOWN oracle. */
final class WebRuntimeStopTest {
  private static final String FIXTURE_HTTP_DA90D362 = "HTTP";
  private static final String FIXTURE_BROKER_4F6E4F9C = "broker";

  @Test
  void stop001NormalPhaseOrderAndRepeatedCloseNeverReleaseTwice() throws Exception {
    var clock = new AtomicLong(1_000_000_000L);
    var owner = new WebRuntimeStop(clock::get);
    owner.begin();
    var calls = new ArrayList<String>();
    WebRuntimeStop.Step[] steps = {
      left -> {
        assertEquals(Duration.ofSeconds(30), left);
        calls.add(FIXTURE_HTTP_DA90D362);
        clock.addAndGet(2_000_000_000L);
      },
      left -> {
        assertEquals(Duration.ofSeconds(28), left);
        calls.add("worker");
      },
      left -> {
        assertEquals(Duration.ofSeconds(28), left);
        calls.add(FIXTURE_BROKER_4F6E4F9C);
      }
    };
    owner.close(steps);
    clock.set(80_000_000_000L);
    owner.close(steps);
    assertEquals(List.of(FIXTURE_HTTP_DA90D362, "worker", FIXTURE_BROKER_4F6E4F9C), calls);
    assertThrows(NullPointerException.class, () -> new WebRuntimeStop(null));
  }

  @Test
  void stop002UnknownPhaseRetainsLaterResourcesAndRetryUsesOriginalDeadline() throws Exception {
    var clock = new AtomicLong(0);
    var owner = new WebRuntimeStop(clock::get);
    owner.begin();
    var calls = new ArrayList<String>();
    WebRuntimeStop.Step[] failed = {
      left -> calls.add(FIXTURE_HTTP_DA90D362),
      left -> {
        calls.add("worker-unknown");
        throw new IOException("private detail");
      },
      left -> {
        throw new AssertionError("later broker must remain owned");
      }
    };
    var failure = assertThrows(IOException.class, () -> owner.close(failed));
    assertEquals("Web stop unconfirmed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    clock.set(5_000_000_000L);
    owner.close(
        new WebRuntimeStop.Step[] {
          left -> {
            throw new AssertionError("confirmed HTTP must not close again");
          },
          left -> {
            assertEquals(Duration.ofSeconds(25), left);
            calls.add("worker-confirmed");
          },
          left -> {
            assertEquals(Duration.ofSeconds(25), left);
            calls.add(FIXTURE_BROKER_4F6E4F9C);
          }
        });
    assertEquals(
        List.of(
            FIXTURE_HTTP_DA90D362, "worker-unknown", "worker-confirmed", FIXTURE_BROKER_4F6E4F9C),
        calls);
  }

  @Test
  void stop003DeadlineBoundaryDoesNotExtendAndExpiredRemainingIsZero() throws Exception {
    var clock = new AtomicLong(0);
    var owner = new WebRuntimeStop(clock::get);
    owner.begin();
    clock.set(30_000_000_000L);
    owner.close(new WebRuntimeStop.Step[] {left -> assertEquals(Duration.ZERO, left)});
    var expired = new WebRuntimeStop(clock::get);
    expired.begin();
    clock.set(60_000_000_001L);
    var error =
        assertThrows(
            IOException.class,
            () ->
                expired.close(
                    new WebRuntimeStop.Step[] {
                      left -> assertEquals(Duration.ZERO, left),
                      left -> {
                        throw new AssertionError("deadline exhausted before next phase");
                      }
                    }));
    assertEquals("Web stop unconfirmed", error.getMessage());
    assertNull(error.getCause());
  }

  @Test
  void stop004LifecycleAndRuntimeFailuresRemainFixedAndDoNotAdvance() {
    for (boolean lifecycle : new boolean[] {false, true}) {
      var owner = new WebRuntimeStop(() -> 0);
      owner.begin();
      var calls = new AtomicLong();
      WebRuntimeStop.Step[] steps = {
        left -> {
          calls.incrementAndGet();
          if (lifecycle) throw new org.apache.catalina.LifecycleException("private lifecycle");
          throw new IllegalStateException("private provider");
        }
      };
      for (int attempt = 0; attempt < 2; attempt++) {
        var failure = assertThrows(IOException.class, () -> owner.close(steps));
        assertEquals("Web stop unconfirmed", failure.getMessage());
        assertNull(failure.getCause());
      }
      assertEquals(2, calls.get());
    }
  }

  @Test
  void stop005FatalIdentityDirectAndNestedNeverTurnsIntoNormalStop() {
    var fatal = new AssertionError("synthetic fatal");
    for (boolean nested : new boolean[] {false, true}) {
      var owner = new WebRuntimeStop(() -> 0);
      owner.begin();
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  owner.close(
                      new WebRuntimeStop.Step[] {
                        left -> {
                          if (nested) throw new IOException("synthetic provider", fatal);
                          throw fatal;
                        },
                        left -> {
                          throw new AssertionError("fatal keeps later resource held");
                        }
                      })));
    }
  }
}
