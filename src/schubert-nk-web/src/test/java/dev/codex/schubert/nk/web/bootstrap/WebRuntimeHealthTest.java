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
  @Test
  void health001EveryRequiredConditionIndependentlyRefusesAndStopsAtItsPosition() {
    for (int rejected = 0; rejected < 10; rejected++) {
      var calls = new ArrayList<String>();
      int index = rejected;
      BooleanSupplier owner =
          () -> {
            calls.add("owner");
            return index == 0;
          };
      BooleanSupplier stop =
          () -> {
            calls.add("stop");
            return index == 1;
          };
      BooleanSupplier terminal =
          () -> {
            calls.add("terminal");
            return index == 2;
          };
      Predicate<String> reply =
          value -> {
            assertEquals("reply", value);
            calls.add(value);
            return index != 7;
          };
      Predicate<String> log =
          value -> {
            assertEquals("log", value);
            calls.add(value);
            return index != 8;
          };
      Predicate<String> retry =
          value -> {
            assertEquals("retry", value);
            calls.add(value);
            return index != 9;
          };
      assertFalse(
          WebRuntimeHealth.healthy(
              owner,
              stop,
              terminal,
              index == 3 ? null : "reply",
              index == 4 ? null : "log",
              index == 5 ? null : "retry",
              index == 6 ? null : new Object(),
              reply,
              log,
              retry));
      List<String> expected =
          switch (index) {
            case 0 -> List.of("owner");
            case 1 -> List.of("owner", "stop");
            case 2, 3, 4, 5, 6 -> List.of("owner", "stop", "terminal");
            case 7 -> List.of("owner", "stop", "terminal", "reply");
            case 8 -> List.of("owner", "stop", "terminal", "reply", "log");
            default -> List.of("owner", "stop", "terminal", "reply", "log", "retry");
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
              calls.add("owner");
              return false;
            },
            () -> {
              calls.add("stop");
              return false;
            },
            () -> {
              calls.add("terminal");
              return false;
            },
            "reply",
            "log",
            "retry",
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
    assertEquals(List.of("owner", "stop", "terminal", "reply", "log", "retry"), calls);
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
            if (value.equals(List.of("reply", "log", "retry").get(position))) throw primary;
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
                      "reply",
                      "log",
                      "retry",
                      new Object(),
                      probe,
                      probe,
                      probe)));
      assertEquals(List.of("reply", "log", "retry").subList(0, position + 1), calls);
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
                    "reply",
                    "log",
                    "retry",
                    new Object(),
                    unusedProbe,
                    unusedProbe,
                    unusedProbe)));
  }
}
