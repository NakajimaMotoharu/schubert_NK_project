package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** SS313342352 / PT-OPS-WEB-REM002: the captured terminal flag, no resource operation. */
final class WebRuntimeFailureSignalTest {
  @Test
  void signal001BothCallbacksMarkOnlyCapturedFlagAndRemainIdempotent() {
    assertThrows(NullPointerException.class, () -> new WebRuntimeFailureSignal<>(null));
    var captured = new AtomicBoolean();
    var unrelated = new AtomicBoolean();
    var signal = new WebRuntimeFailureSignal<IllegalStateException>(captured);
    assertFalse(captured.get());
    signal.run();
    assertTrue(captured.get());
    signal.run();
    assertTrue(captured.get());
    assertFalse(unrelated.get());
    captured.set(false);
    signal.accept(new IllegalStateException("synthetic ignored callback"));
    assertTrue(captured.get());
    signal.accept(new IllegalStateException("second ignored callback"));
    assertTrue(captured.get());
    assertFalse(unrelated.get());
  }
}
