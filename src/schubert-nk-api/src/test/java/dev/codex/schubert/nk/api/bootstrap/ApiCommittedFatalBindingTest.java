package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.messaging.inbound.CommittedFatalInboundException;
import java.io.IOException;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PG-D412/SS321342: durable-fatal callback fails only its own lifecycle, never normal success. */
final class ApiCommittedFatalBindingTest {
  @Test
  void fatalBinding001CommittedEventStopsOwnerAndAwaitRemainsSanitizedNonSuccess()
      throws Exception {
    var healthyCalls = new AtomicInteger();
    try (var lifetime = new ApiProcessLifetime()) {
      assertFalse(lifetime.stopping());
      var notification = lifetime.committedFailureHandler();
      var event = new CommittedFatalInboundException(new IllegalStateException("PRIVATE_CANARY"));
      notification.accept(event);
      assertTrue(lifetime.stopping());
      notification.accept(event);
      var failure =
          assertThrows(
              IOException.class,
              () ->
                  lifetime.await(
                      () -> {
                        healthyCalls.incrementAndGet();
                        return true;
                      }));
      assertEquals("API runtime unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertEquals(0, healthyCalls.get(), "failed owner cannot resume health polling or success");
    }
  }

  @Test
  void fatalBinding002CallbackRemainsBoundToItsOwnerAndNeverReadsFailurePayload() throws Exception {
    try (var first = new ApiProcessLifetime();
        var other = new ApiProcessLifetime()) {
      // Preserve the previous callback's ignored-value semantics. A missing
      // notification payload must still fail closed, not revive the consumer.
      first.committedFailureHandler().accept(null);
      assertTrue(first.stopping());
      assertFalse(other.stopping(), "failure is not a global JVM stop notification");
      assertThrows(IOException.class, () -> first.await(() -> fail("failed owner polled")));
      other.stop();
      assertDoesNotThrow(() -> other.await(() -> fail("normal stopped owner polled")));
    }
  }
}
