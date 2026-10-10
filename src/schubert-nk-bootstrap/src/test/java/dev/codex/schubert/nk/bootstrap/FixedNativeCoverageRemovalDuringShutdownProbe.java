package dev.codex.schubert.nk.bootstrap;

import java.util.concurrent.CountDownLatch;

/**
 * Test-only native Runtime refusal after actual TERM. Separate from the no-early-exit hold probe:
 * this witness permits observing shutdown, it is not evidence of application capture lifetime.
 */
public final class FixedNativeCoverageRemovalDuringShutdownProbe {
  private FixedNativeCoverageRemovalDuringShutdownProbe() {}

  public static void main(String[] arguments) throws Exception {
    var release = new CountDownLatch(1);
    var ordinary = new Thread(() -> {});
    Runtime.getRuntime().addShutdownHook(ordinary);
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  System.out.println("SHUTDOWN_STARTED");
                  try {
                    release.await();
                  } catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException("owned test witness interrupted", interrupted);
                  }
                }));
    System.out.println("READY");
    try {
      if (System.in.read() != 'C') throw new IllegalStateException("owned test command refused");
      if (FixedNativeCoverageStopHold.removeNative(ordinary)
          != FixedNativeCoverageStopHold.Removal.SHUTTING_DOWN)
        throw new AssertionError("actual Runtime shutdown must refuse hook removal");
      // The automatic JaCoCo hook may already have returned. Explicitly save only
      // this newly owned host test JVM after the independent literal refusal check.
      // No reflection into Production internals and no fabricated branch/state.
      var agent = Class.forName("org.jacoco.agent.rt.RT").getMethod("getAgent").invoke(null);
      agent.getClass().getMethod("dump", boolean.class).invoke(agent, false);
      System.out.println("REMOVAL_SHUTTING_DOWN_CAPTURED");
    } finally {
      release.countDown();
    }
  }
}
