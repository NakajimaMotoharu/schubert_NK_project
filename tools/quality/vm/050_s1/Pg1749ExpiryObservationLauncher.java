import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import org.junit.platform.engine.TestExecutionResult;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.engine.support.descriptor.MethodSource;
import org.junit.platform.launcher.TestExecutionListener;
import org.junit.platform.launcher.TestIdentifier;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Four independent Expiry observation data matrices; not native ownership. */
public final class Pg1749ExpiryObservationLauncher {
  private Pg1749ExpiryObservationLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1)
      throw new IllegalArgumentException("new XML path required");
    String name = "dev.codex.schubert.nk.batch.repository.MorningExpiryObservationInvariantTest";
    var expected =
        List.of(
            "expiry1749001FreshAndSkipCarryLiteralFieldsNotReceiptAuthority",
            "expiry1749002EveryFreshProjectionMismatchAndWrongReceiptTargetRejects",
            "expiry1749003EverySkipObservationBindingCounterexampleRejects",
            "expiry1749004BeginRoleAndPresenceNullTimeContractsRejectBeforeIo");
    var rows = new ArrayList<String>();
    var results = new ArrayList<TestExecutionResult.Status>();
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(
        summary,
        new TestExecutionListener() {
          @Override
          public void executionFinished(TestIdentifier test, TestExecutionResult result) {
            if (!test.isTest()) return;
            var method = (MethodSource) test.getSource().orElseThrow();
            if (!method.getClassName().equals(name))
              throw new IllegalStateException("foreign test");
            rows.add(method.getMethodName());
            results.add(result.getStatus());
          }
        });
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(DiscoverySelectors.selectClass(name))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var value = summary.getSummary();
    boolean passed =
        rows.size() == 4
            && rows.containsAll(expected)
            && results.stream().allMatch(v -> v == TestExecutionResult.Status.SUCCESSFUL)
            && value.getTestsFoundCount() == 4
            && value.getTestsStartedCount() == 4
            && value.getTestsSucceededCount() == 4
            && value.getTestsFailedCount() == 0
            && value.getTestsSkippedCount() == 0
            && value.getTestsAbortedCount() == 0
            && value.getContainersFailedCount() == 0
            && value.getContainersAbortedCount() == 0;
    try (var writer =
        Files.newBufferedWriter(
            Path.of(args[0]), StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW)) {
      writer.write(
          "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
              + "<testsuite name=\"PG1749\" tests=\"2\" failures=\""
              + value.getTestsFailedCount()
              + "\" errors=\""
              + value.getContainersFailedCount()
              + "\" skipped=\""
              + (value.getTestsSkippedCount() + value.getTestsAbortedCount())
              + "\">\n");
      for (int i = 0; i < rows.size(); i++) {
        writer.write("<testcase classname=\"" + name + "\" name=\"" + rows.get(i) + "\">");
        if (results.get(i) != TestExecutionResult.Status.SUCCESSFUL)
          writer.write("<failure message=\"selected contract failed\"/>");
        writer.write("</testcase>\n");
      }
      writer.write("</testsuite>\n");
    }
    if (!passed) {
      value.printFailuresTo(new PrintWriter(System.err, true));
      throw new IllegalStateException("selected generation four contracts failed");
    }
    System.out.println("PG1749 tests4 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
