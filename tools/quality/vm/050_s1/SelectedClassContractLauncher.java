import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Map;
import java.util.TreeMap;
import org.junit.platform.engine.TestExecutionResult;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.TestExecutionListener;
import org.junit.platform.launcher.TestIdentifier;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** PT-CFDB-2916-001..003: strict whole selected class, never skipped/aborted/not-run accepted. */
public final class SelectedClassContractLauncher {
  private SelectedClassContractLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 4
        || !args[1].matches("dev\\.codex\\.schubert\\.nk\\.[A-Za-z0-9_.]+Test")
        || !args[3].matches("PG[0-9]+"))
      throw new IllegalArgumentException("XML/class/count/run required");
    int expected = Integer.parseInt(args[2]);
    if (expected <= 0) throw new IllegalArgumentException("positive actual test count required");
    Map<String, TestExecutionResult> results = new TreeMap<>();
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(
        summary,
        new TestExecutionListener() {
          @Override
          public void executionFinished(TestIdentifier id, TestExecutionResult result) {
            if (id.isTest()) results.put(id.getDisplayName(), result);
          }
        });
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(DiscoverySelectors.selectClass(args[1]))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var s = summary.getSummary();
    boolean passed =
        s.getTestsFoundCount() == expected
            && s.getTestsStartedCount() == expected
            && s.getTestsSucceededCount() == expected
            && results.size() == expected
            && s.getTestsSkippedCount() == 0
            && s.getTestsAbortedCount() == 0
            && s.getContainersFailedCount() == 0
            && s.getContainersAbortedCount() == 0;
    var xml = new StringBuilder("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    xml.append("<testsuite name=\"")
        .append(args[3])
        .append("\" tests=\"")
        .append(expected)
        .append("\" failures=\"")
        .append(s.getTestsFailedCount())
        .append("\" errors=\"")
        .append(s.getContainersFailedCount())
        .append("\" skipped=\"")
        .append(s.getTestsSkippedCount() + s.getTestsAbortedCount())
        .append("\">");
    for (var entry : results.entrySet()) {
      if (!entry.getKey().matches("[A-Za-z0-9_]+\\(\\)"))
        throw new IllegalStateException("literal method name required");
      xml.append("<testcase classname=\"")
          .append(args[1])
          .append("\" name=\"")
          .append(entry.getKey(), 0, entry.getKey().length() - 2)
          .append("\">");
      if (entry.getValue().getStatus() != TestExecutionResult.Status.SUCCESSFUL)
        xml.append("<failure message=\"selected independent contract failed\"/>");
      xml.append("</testcase>");
    }
    xml.append("</testsuite>\n");
    Files.writeString(Path.of(args[0]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    if (!passed) {
      for (var failure : s.getFailures()) failure.getException().printStackTrace(System.err);
      throw new IllegalStateException("selected failed/skipped/aborted/not-run");
    }
    System.out.println(
        args[3] + " tests" + expected + " failures0 errors0 skipped0 aborted0 notRun0");
  }
}
