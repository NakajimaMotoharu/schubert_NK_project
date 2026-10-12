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

/** Two independent Caddy address boundaries; not native readiness. */
public final class Pg1746CaddyAddressLauncher {
  private Pg1746CaddyAddressLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1)
      throw new IllegalArgumentException("new XML path required");
    String name = "dev.codex.schubert.nk.batch.file.CaddyAddressBoundaryTest";
    var expected =
        List.of(
            "caddy1746001MissingBodyAndPartialBracketRejectBeforeUri",
            "caddy1746002Ipv4ZeroAndIpv6UnspecifiedHaveExactTlsLoginUri");
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
        rows.size() == 2
            && rows.containsAll(expected)
            && results.stream().allMatch(v -> v == TestExecutionResult.Status.SUCCESSFUL)
            && value.getTestsFoundCount() == 2
            && value.getTestsStartedCount() == 2
            && value.getTestsSucceededCount() == 2
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
              + "<testsuite name=\"PG1746\" tests=\"2\" failures=\""
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
      throw new IllegalStateException("selected generation two contracts failed");
    }
    System.out.println("PG1746 tests2 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
