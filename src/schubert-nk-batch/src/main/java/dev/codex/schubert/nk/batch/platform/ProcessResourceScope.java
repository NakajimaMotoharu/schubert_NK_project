package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.util.Objects;
import java.util.function.Consumer;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Package-owned trusted query cleanup precedence. NK-OPS-001/OPS009/UI251/SS343;
 * PG173/SSC063/BUG195/YKT154; STOP014/UNIT015, 017051. Caller registers one acquired resource and
 * normalizes only declared stop failures.
 */
@NullMarked
final class ProcessResourceScope {
  private ProcessResourceScope() {
    throw new AssertionError("process resource scope is static");
  }

  @FunctionalInterface
  interface QueryWork {
    void run() throws IOException, InterruptedException;
  }

  @FunctionalInterface
  interface OwnedQuery<R> {
    void run(R resource) throws IOException, InterruptedException;
  }

  /**
   * SSC308: ports precede acquisition; factory E stays raw; use's query cleanup priority stays
   * exact.
   */
  static <R> void acquire(
      ResourceScope.Acquire<R, IOException> acquire, Consumer<R> release, OwnedQuery<R> work)
      throws IOException, InterruptedException {
    Objects.requireNonNull(acquire, "query acquire");
    Objects.requireNonNull(release, "query release");
    Objects.requireNonNull(work, "query work");
    @Nullable R resource = acquire.open();
    R owned;
    try {
      owned = Objects.requireNonNull(resource, "acquired query resource");
      work.run(owned);
    } catch (IOException | InterruptedException | RuntimeException | Error primary) {
      if (resource != null) {
        try {
          release.accept(resource);
        } catch (RuntimeException | Error cleanup) {
          if ((primary instanceof IOException
                  || primary instanceof InterruptedException
                  || primary instanceof StopGateException)
              && !(cleanup instanceof StopGateException)) {
            if (primary instanceof InterruptedException) Thread.currentThread().interrupt();
            throw cleanup;
          }
          primary.addSuppressed(new StopGateException(StopGateFailure.COMMAND_FAILURE));
        }
      }
      throw primary;
    }
    release.accept(owned);
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
