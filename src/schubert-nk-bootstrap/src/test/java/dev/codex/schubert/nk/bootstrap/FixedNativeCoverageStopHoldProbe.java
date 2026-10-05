package dev.codex.schubert.nk.bootstrap;

import java.util.concurrent.CountDownLatch;

/** Test-only real JVM TERM ordering probe, never a Production main/coverage substitute. */
public final class FixedNativeCoverageStopHoldProbe {
  private FixedNativeCoverageStopHoldProbe() {}

  public static void main(String[] args) throws Exception {
    var oldApplicationFinished = new CountDownLatch(1);
    try (var hold = FixedNativeCoverageStopHold.open()) {
      hold.verifyOwner();
      Runtime.getRuntime()
          .addShutdownHook(
              new Thread(
                  () -> {
                    oldApplicationFinished.countDown();
                    System.out.println("OLD_HOOK_RETURNED");
                  }));
      System.out.println("READY");
      oldApplicationFinished.await();
      System.out.println("APPLICATION_SCOPES_RETURNED");
      if (System.in.read() != 'C') throw new IllegalStateException("test capture command missing");
      hold.verifyOwner();
      System.out.println("CAPTURE_COMPLETE");
    }
  }
}
