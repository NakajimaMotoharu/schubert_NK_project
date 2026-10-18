package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/** Independent caller-lock oracle, never a Production state/coverage port. BUG1459/YKT1223. */
public final class CallerMonitorProbe {
  private CallerMonitorProbe() {}

  @FunctionalInterface
  public interface Operation {
    void run() throws Exception;
  }

  public static void requireIndependent(Object callerVisibleOwner, Operation operation)
      throws InterruptedException {
    var finished = new CountDownLatch(1);
    var failure = new AtomicReference<Throwable>();
    var worker =
        Thread.ofPlatform()
            .unstarted(
                () -> {
                  try {
                    operation.run();
                  } catch (Throwable problem) {
                    failure.set(problem);
                  } finally {
                    finished.countDown();
                  }
                });
    try {
      synchronized (callerVisibleOwner) {
        worker.start();
        assertTrue(
            finished.await(5, TimeUnit.SECONDS),
            "caller monitor must not control private owner state");
        assertNull(failure.get(), "worker operation must genuinely succeed");
      }
    } finally {
      // Release the caller monitor before joining even on the expected old-source failure.
      worker.join(5000);
      assertFalse(worker.isAlive(), "caller-lock probe must reclaim its worker");
    }
  }
}
