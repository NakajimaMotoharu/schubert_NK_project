package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** NATIVE-LIFE001..003: notification never substitutes for confirmed resource completion. */
final class WebProcessLifetimeTest {
  @Test
  void life001StopFailureInterruptNullAndHookInstallation() throws Exception {
    try (var lifetime = new WebProcessLifetime()) {
      assertFalse(lifetime.stopping());
      lifetime.install();
      assertThrows(IllegalStateException.class, lifetime::install);
      assertThrows(NullPointerException.class, () -> lifetime.await(null));
      lifetime.shutdown(); // Owner notification returns; it does not close borrowed resources.
      assertTrue(lifetime.stopping());
      lifetime.await(() -> fail("stopped owner must not poll providers"));
    }
    try (var lifetime = new WebProcessLifetime()) {
      var error = assertThrows(IOException.class, () -> lifetime.await(() -> false));
      assertEquals("Web runtime unavailable", error.getMessage());
      assertTrue(lifetime.stopping());
    }
    try (var lifetime = new WebProcessLifetime()) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(IOException.class, () -> lifetime.await(() -> true));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
  }

  @Test
  void life002ForeignHookWaitsForActualOwnerNotificationAndPreservesInterrupt() throws Exception {
    var lifetime = new WebProcessLifetime();
    var finished = new AtomicBoolean();
    var interrupted = new AtomicBoolean();
    var thread =
        Thread.ofPlatform()
            .start(
                () -> {
                  Thread.currentThread().interrupt();
                  lifetime.shutdown();
                  interrupted.set(Thread.currentThread().isInterrupted());
                  finished.set(true);
                });
    try {
      long end = System.nanoTime() + Duration.ofSeconds(3).toNanos();
      while (!lifetime.stopping() && System.nanoTime() < end) Thread.sleep(1);
      assertTrue(lifetime.stopping());
      assertFalse(finished.get());
      assertTrue(thread.isAlive());
    } finally {
      lifetime.close();
    }
    assertTrue(thread.join(Duration.ofSeconds(3)));
    assertTrue(finished.get());
    assertTrue(interrupted.get());
    lifetime.close();
  }

  @Test
  void life003HealthyOwnerAwaitsIndependentStop() throws Exception {
    var polls = new CountDownLatch(1);
    var observed = new AtomicReference<Throwable>();
    var lifetime = new WebProcessLifetime();
    var thread =
        Thread.ofPlatform()
            .start(
                () -> {
                  try {
                    lifetime.await(
                        () -> {
                          polls.countDown();
                          return true;
                        });
                  } catch (Throwable failure) {
                    observed.set(failure);
                  }
                });
    try {
      assertTrue(polls.await(3, TimeUnit.SECONDS));
      lifetime.stop();
      assertTrue(thread.join(Duration.ofSeconds(3)));
      assertNull(observed.get());
    } finally {
      lifetime.close();
    }
  }
}
