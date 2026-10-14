import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** PT-MDB2570-001: isolated PostgreSQL abandoned pair matrix, never production DB. */
public final class Pg2570FailedGuardLauncher {
  private Pg2570FailedGuardLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1)
      throw new IllegalArgumentException("fresh XML path required");
    String type = "dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest";
    String method = "mdb2570001FailedBackupFinalGuardsRejectDriverAndOwnerDriftWithoutChangingPair";
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(DiscoverySelectors.selectMethod(type, method))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var summary = listener.getSummary();
    boolean passed =
        summary.getTestsFoundCount() == 1
            && summary.getTestsStartedCount() == 1
            && summary.getTestsSucceededCount() == 1
            && summary.getTestsFailedCount() == 0
            && summary.getTestsSkippedCount() == 0
            && summary.getTestsAbortedCount() == 0
            && summary.getContainersFailedCount() == 0
            && summary.getContainersAbortedCount() == 0;
    for (var failure : summary.getFailures()) {
      Throwable current = failure.getException();
      for (int depth = 0; current != null && depth < 8; depth++) {
        System.err.println("PG2570_FAILED type=" + current.getClass().getName());
        int count = 0;
        for (var frame : current.getStackTrace())
          if (frame.getClassName().startsWith("dev.codex.schubert.nk.") && count++ < 8)
            System.err.println(
                "PG2570_FRAME class="
                    + frame.getClassName()
                    + " method="
                    + frame.getMethodName()
                    + " line="
                    + frame.getLineNumber());
        Throwable next = current.getCause();
        if (next == current) break;
        current = next;
      }
    }
    String xml =
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<testsuite name=\"PG2570\" tests=\"1\" failures=\""
            + summary.getTestsFailedCount()
            + "\" errors=\""
            + summary.getContainersFailedCount()
            + "\" skipped=\""
            + (summary.getTestsSkippedCount() + summary.getTestsAbortedCount())
            + "\">\n"
            + "<testcase classname=\""
            + type
            + "\" name=\""
            + method
            + "\">"
            + (passed ? "" : "<failure message=\"abandoned pair matrix failed or not run\"/>")
            + "</testcase>\n</testsuite>\n";
    Files.writeString(Path.of(args[0]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    if (!passed) throw new IllegalStateException("isolated abandoned pair matrix failed");
    System.out.println("PG2570 tests1 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
