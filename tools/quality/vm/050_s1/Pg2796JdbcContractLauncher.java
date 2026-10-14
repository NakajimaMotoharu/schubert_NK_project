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

/** PT-MDB-2796-001: entire Session contract with independent real DB/resource fixtures. */
public final class Pg2796JdbcContractLauncher {
  private Pg2796JdbcContractLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("new XML and count required");
    String type = "dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest";
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
            .selectors(DiscoverySelectors.selectClass(type))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var s = summary.getSummary();
    int expected = Integer.parseInt(args[1]);
    boolean passed =
        s.getTestsFoundCount() == expected
            && s.getTestsStartedCount() == expected
            && s.getTestsSucceededCount() == expected
            && results.size() == expected
            && s.getTestsSkippedCount() == 0
            && s.getTestsAbortedCount() == 0
            && s.getContainersFailedCount() == 0
            && s.getContainersAbortedCount() == 0;
    StringBuilder xml = new StringBuilder("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    xml.append("<testsuite name=\"PG2796\" tests=\"")
        .append(expected)
        .append("\" failures=\"")
        .append(s.getTestsFailedCount())
        .append("\" errors=\"")
        .append(s.getContainersFailedCount())
        .append("\" skipped=\"")
        .append(s.getTestsSkippedCount() + s.getTestsAbortedCount())
        .append("\">");
    for (var e : results.entrySet()) {
      if (!e.getKey().matches("[A-Za-z0-9_]+\\(\\)"))
        throw new IllegalStateException("exact method required");
      xml.append("<testcase classname=\"")
          .append(type)
          .append("\" name=\"")
          .append(e.getKey().substring(0, e.getKey().length() - 2))
          .append("\">");
      if (e.getValue().getStatus() != TestExecutionResult.Status.SUCCESSFUL)
        xml.append("<failure message=\"independent JDBC contract failed\"/>");
      xml.append("</testcase>");
    }
    xml.append("</testsuite>\n");
    Files.writeString(Path.of(args[0]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    if (!passed) {
      for (var failure : s.getFailures()) failure.getException().printStackTrace(System.err);
      throw new IllegalStateException("Session failed/skipped/aborted/not-run");
    }
    System.out.println("PG2796 tests" + expected + " failures0 errors0 skipped0 aborted0 notRun0");
  }
}
