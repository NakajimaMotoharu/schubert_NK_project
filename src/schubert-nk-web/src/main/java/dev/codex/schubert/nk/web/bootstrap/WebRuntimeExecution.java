package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.io.IOException;
import java.lang.ref.Reference;
import java.util.Objects;
import org.apache.catalina.LifecycleException;
import org.jspecify.annotations.NullMarked;

/**
 * NK-WEB-002/SS313342352/PG-D378/WEB-REM004. Borrowed frame remains on this stack after UNKNOWN.
 */
@NullMarked
final class WebRuntimeExecution {
  // SSC325/PG-D479: prepare policies before the first callback can borrow/acquire resources.
  private static final Runnable UNKNOWN_DIAGNOSTIC = WebRuntimeExecution::diagnoseUnknown;
  private static final Runnable UNKNOWN_INTERVAL =
      ServiceProcessResources.unknownReleaseObservationPolicy();

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
      SessionStoreException.preserveFatal(failure);
      throw new IOException("Web HTTP startup unavailable");
    } finally {
      stop.run();
      try {
        close.run();
      } catch (IOException | RuntimeException | Error unconfirmed) {
        UNKNOWN_DIAGNOSTIC.run();
        // Keep this exact borrowed frame alive; each observation interval returns, not the owner.
        while (true) {
          UNKNOWN_INTERVAL.run();
          Reference.reachabilityFence(start);
          Reference.reachabilityFence(await);
          Reference.reachabilityFence(stop);
          Reference.reachabilityFence(close);
          Reference.reachabilityFence(unconfirmed);
        }
      }
    }
  }

  private static void diagnoseUnknown() {
    try {
      System.err.println("WEB cleanup unconfirmed");
    } catch (RuntimeException | Error unavailableDiagnostic) {
      // Diagnostic failure never confirms cleanup or permits the borrowed frame to unwind.
    }
  }
}
