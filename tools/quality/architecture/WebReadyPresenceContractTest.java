package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS342 captured management conjunction; pure value callbacks, not service readiness admission. */
final class WebReadyPresenceContractTest {
  @Test
  void readyPresence001AbsentManagementShortCircuitsWithoutCallingProbe() {
    assertFalse(
        WebRuntimeHealth.ready(
            null,
            value -> {
              throw new AssertionError("absent management must not be probed");
            }));
    assertFalse(WebRuntimeHealth.ready(null, null));
  }

  @Test
  void readyPresence002PresentManagementUsesExactProbeResultAndFailureIdentity() {
    var management = new Object();
    var calls = new ArrayList<Object>();
    assertTrue(
        WebRuntimeHealth.ready(
            management,
            value -> {
              calls.add(value);
              return true;
            }));
    assertEquals(1, calls.size());
    assertSame(management, calls.getFirst());
    calls.clear();
    assertFalse(
        WebRuntimeHealth.ready(
            management,
            value -> {
              calls.add(value);
              return false;
            }));
    assertEquals(List.of(management), calls);
    var failure = new IllegalStateException("public fixed probe failure");
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class,
            () ->
                WebRuntimeHealth.ready(
                    management,
                    value -> {
                      assertSame(management, value);
                      throw failure;
                    })));
    assertThrows(
        NullPointerException.class, () -> WebRuntimeHealth.ready(management, null));
  }
}
