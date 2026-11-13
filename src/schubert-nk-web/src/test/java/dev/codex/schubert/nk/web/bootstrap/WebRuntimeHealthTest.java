package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;
import java.util.function.Predicate;
import org.junit.jupiter.api.Test;

/** SS313342352 / PT-OPS-NWEB-HEALTH001..004; literal independent conjunction/ordering. */
final class WebRuntimeHealthTest {
  private static final String OWNER_STEP = "owner";
  private static final String STOP_STEP = "stop";
  private static final String TERMINAL_STEP = "terminal";
  private static final String REPLY_STEP = "reply";
  private static final String LOG_STEP = "log";
  private static final String RETRY_STEP = "retry";

  @Test
  void health001EveryRequiredConditionIndependentlyRefusesAndStopsAtItsPosition() {
    for (int rejected = 0; rejected < 10; rejected++) {
      var calls = new ArrayList<String>();
      int index = rejected;
      BooleanSupplier owner =
          () -> {
            calls.add(OWNER_STEP);
            return index == 0;
          };
      BooleanSupplier stop =
          () -> {
            calls.add(STOP_STEP);
            return index == 1;
          };
      BooleanSupplier terminal =
          () -> {
            calls.add(TERMINAL_STEP);
            return index == 2;
          };
      Predicate<String> reply =
          value -> {
            assertEquals(REPLY_STEP, value);
            calls.add(value);
            return index != 7;
          };
      Predicate<String> log =
          value -> {
            assertEquals(LOG_STEP, value);
            calls.add(value);
            return index != 8;
          };
      Predicate<String> retry =
          value -> {
            assertEquals(RETRY_STEP, value);
            calls.add(value);
            return index != 9;
          };
      assertFalse(
          WebRuntimeHealth.healthy(
              owner,
              stop,
              terminal,
              index == 3 ? null : REPLY_STEP,
              index == 4 ? null : LOG_STEP,
              index == 5 ? null : RETRY_STEP,
              index == 6 ? null : new Object(),
              reply,
              log,
              retry));
      List<String> expected =
          switch (index) {
            case 0 -> List.of(OWNER_STEP);
            case 1 -> List.of(OWNER_STEP, STOP_STEP);
            case 2, 3, 4, 5, 6 -> List.of(OWNER_STEP, STOP_STEP, TERMINAL_STEP);
            case 7 -> List.of(OWNER_STEP, STOP_STEP, TERMINAL_STEP, REPLY_STEP);
            case 8 -> List.of(OWNER_STEP, STOP_STEP, TERMINAL_STEP, REPLY_STEP, LOG_STEP);
            default ->
                List.of(OWNER_STEP, STOP_STEP, TERMINAL_STEP, REPLY_STEP, LOG_STEP, RETRY_STEP);
          };
      assertEquals(expected, calls, "literal rejection position " + index);
    }
  }

  @Test
  void health002AllPresentAndLiveCallsEachProviderOnceInOriginalOrder() {
    var calls = new ArrayList<String>();
    assertTrue(
        WebRuntimeHealth.healthy(
            () -> {
              calls.add(OWNER_STEP);
              return false;
            },
            () -> {
              calls.add(STOP_STEP);
              return false;
            },
            () -> {
              calls.add(TERMINAL_STEP);
              return false;
            },
            REPLY_STEP,
            LOG_STEP,
            RETRY_STEP,
            new Object(),
            value -> {
              calls.add(value);
              return true;
            },
            value -> {
              calls.add(value);
              return true;
            },
            value -> {
              calls.add(value);
              return true;
            }));
    assertEquals(
        List.of(OWNER_STEP, STOP_STEP, TERMINAL_STEP, REPLY_STEP, LOG_STEP, RETRY_STEP), calls);
  }

  @Test
  void health003ProviderFailureIsNotSwallowedOrConvertedToUp() {
    var primary = new IllegalStateException("literal provider failure");
    for (int failed = 0; failed < 3; failed++) {
      int position = failed;
      var calls = new ArrayList<String>();
      Predicate<String> probe =
          value -> {
            calls.add(value);
            if (value.equals(List.of(REPLY_STEP, LOG_STEP, RETRY_STEP).get(position)))
              throw primary;
            return true;
          };
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class,
              () ->
                  WebRuntimeHealth.healthy(
                      () -> false,
                      () -> false,
                      () -> false,
                      REPLY_STEP,
                      LOG_STEP,
                      RETRY_STEP,
                      new Object(),
                      probe,
                      probe,
                      probe)));
      assertEquals(List.of(REPLY_STEP, LOG_STEP, RETRY_STEP).subList(0, position + 1), calls);
    }
  }

  @Test
  void health004OwnerNotificationFailureKeepsIdentityAndDoesNotProbeResources() {
    var primary = new IllegalStateException("literal owner unavailable");
    BooleanSupplier unused =
        () -> {
          throw new AssertionError("later notification must not run");
        };
    Predicate<String> unusedProbe =
        value -> {
          throw new AssertionError("provider must not run");
        };
    assertSame(
        primary,
        assertThrows(
            IllegalStateException.class,
            () ->
                WebRuntimeHealth.healthy(
                    () -> {
                      throw primary;
                    },
                    unused,
                    unused,
                    REPLY_STEP,
                    LOG_STEP,
                    RETRY_STEP,
                    new Object(),
                    unusedProbe,
                    unusedProbe,
                    unusedProbe)));
  }

  @Test
  void health005ManagementReadyRequiresCapturedObjectAndPropagatesProbeFailure() {
    var calls = new ArrayList<String>();
    var captured = new Object();
    assertFalse(
        WebRuntimeHealth.ready(
            null,
            value -> {
              throw new AssertionError("absent management must not be probed");
            }));
    assertFalse(
        WebRuntimeHealth.ready(
            captured,
            value -> {
              assertSame(captured, value);
              calls.add("not-ready");
              return false;
            }));
    assertTrue(
        WebRuntimeHealth.ready(
            captured,
            value -> {
              assertSame(captured, value);
              calls.add("ready");
              return true;
            }));
    var primary = new LinkageError("synthetic management failure");
    assertSame(
        primary,
        assertThrows(
            LinkageError.class,
            () ->
                WebRuntimeHealth.ready(
                    captured,
                    value -> {
                      assertSame(captured, value);
                      calls.add("failed");
                      throw primary;
                    })));
    assertEquals(List.of("not-ready", "ready", "failed"), calls);
  }
}
