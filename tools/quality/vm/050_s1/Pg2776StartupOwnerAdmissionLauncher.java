import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** PT-OPS-2776-001/002; exact publication entry negative cases, no fake native ownership. */
public final class Pg2776StartupOwnerAdmissionLauncher {
  private Pg2776StartupOwnerAdmissionLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1) throw new IllegalArgumentException("new XML required");
    String type = "dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwnerAdmissionTest";
    String first = "launch2776001UntrustedPublicationValuesRejectBeforeProviders";
    String second = "launch2776002EveryNullBoundaryRejectsBeforeProviders";
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                DiscoverySelectors.selectMethod(type, first),
                DiscoverySelectors.selectMethod(type, second))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var s = listener.getSummary();
    boolean passed =
        s.getTestsFoundCount() == 2
            && s.getTestsStartedCount() == 2
            && s.getTestsSucceededCount() == 2
            && s.getTestsFailedCount() == 0
            && s.getTestsSkippedCount() == 0
            && s.getTestsAbortedCount() == 0
            && s.getContainersFailedCount() == 0
            && s.getContainersAbortedCount() == 0;
    String cases = "";
    for (String method : new String[] {first, second})
      cases +=
          "<testcase classname=\""
              + type
              + "\" name=\""
              + method
              + "\">"
              + (passed ? "" : "<failure message=\"entry test failed or not-run\"/>")
              + "</testcase>";
    String xml =
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<testsuite name=\"PG2776\" tests=\"2\" failures=\""
            + s.getTestsFailedCount()
            + "\" errors=\""
            + s.getContainersFailedCount()
            + "\" skipped=\""
            + (s.getTestsSkippedCount() + s.getTestsAbortedCount())
            + "\">"
            + cases
            + "</testsuite>\n";
    Files.writeString(Path.of(args[0]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    if (!passed) {
      // Private selected log retains literal fixture diagnostics; never provider secrets.
      for (var f : s.getFailures()) f.getException().printStackTrace(System.err);
      throw new IllegalStateException("entry cases failed/not-run");
    }
    System.out.println("PG2776 tests2 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
