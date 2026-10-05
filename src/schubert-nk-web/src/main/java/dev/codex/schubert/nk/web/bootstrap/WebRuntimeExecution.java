package dev.codex.schubert.nk.web.bootstrap;

import java.io.IOException;
import java.util.Objects;
import org.apache.catalina.LifecycleException;
import org.jspecify.annotations.NullMarked;

/**
 * NK-WEB-002/SS313342352/PG-D378/WEB-REM004. Borrowed frame remains on this stack after UNKNOWN.
 */
@NullMarked
final class WebRuntimeExecution {
  private WebRuntimeExecution() {}

  @FunctionalInterface
  interface Start {
    void run() throws IOException, LifecycleException;
  }

  @FunctionalInterface
  interface Io {
    void run() throws IOException;
  }

  static void execute(Start start, Io await, Runnable stop, Io close) throws IOException {
    Objects.requireNonNull(start, "Web start");
    Objects.requireNonNull(await, "Web await");
    Objects.requireNonNull(stop, "Web stop");
    Objects.requireNonNull(close, "Web close");
    try {
      start.run();
      await.run();
    } catch (LifecycleException failure) {
      throw new IOException("Web HTTP startup unavailable");
    } finally {
      stop.run();
      try {
        close.run();
      } catch (IOException | RuntimeException | Error unconfirmed) {
        System.err.println("WEB cleanup unconfirmed");
        // Keep this exact borrowed frame alive; each observation interval returns, not the owner.
        while (true) WebProcessLifetime.holdUnknownInterval();
      }
    }
  }
}
