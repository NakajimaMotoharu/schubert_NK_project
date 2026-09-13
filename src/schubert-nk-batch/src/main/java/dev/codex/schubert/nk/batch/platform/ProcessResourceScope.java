package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import org.jspecify.annotations.NullMarked;

/**
 * Package-owned trusted query cleanup precedence. NK-OPS-001/OPS009/UI251/SS343;
 * PG173/SSC063/BUG195/YKT154; STOP014/UNIT015, 017051. Caller registers one acquired resource and
 * normalizes only declared stop failures.
 */
@NullMarked
final class ProcessResourceScope {
  private ProcessResourceScope() {}

  @FunctionalInterface
  interface QueryWork {
    void run() throws IOException, InterruptedException;
  }

  // SSC063/BUG195: fixed stop diagnostics, not raw suppressed process/stream failures.
  static void use(Runnable release, QueryWork work) throws IOException, InterruptedException {
    try {
      work.run();
    } catch (IOException | InterruptedException | RuntimeException | Error primary) {
      try {
        release.run();
      } catch (RuntimeException | Error cleanup) {
        if ((primary instanceof IOException
                || primary instanceof InterruptedException
                || primary instanceof StopGateException)
            && !(cleanup instanceof StopGateException)) {
          // Preserve cancellation even when an unknown cleanup must take precedence.
          if (primary instanceof InterruptedException) Thread.currentThread().interrupt();
          throw cleanup;
        }
        primary.addSuppressed(new StopGateException(StopGateFailure.COMMAND_FAILURE));
      }
      throw primary;
    }
    release.run();
  }
}
