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

/**
 * PT-MDB2490-001/002: actual isolated DB and independent successful-pair refusal postconditions.
 */
public final class Pg2490BackupOriginalLauncher {
  private Pg2490BackupOriginalLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1)
      throw new IllegalArgumentException("new XML path required");
    String type = "dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest";
    var expected =
        List.of(
            "mdb2490001SkippedBackupRequiresOriginalManifestAndActualReverseOrderedPair",
            "mdb2490002TerminalPairRejectsMissingAndExtraDriverRows");
    var rows = new ArrayList<String>();
    var statuses = new ArrayList<TestExecutionResult.Status>();
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(
        summary,
        new TestExecutionListener() {
          @Override
          public void executionFinished(TestIdentifier t, TestExecutionResult r) {
            if (!t.isTest()) {
              if (r.getStatus() != TestExecutionResult.Status.SUCCESSFUL)
                System.err.println(
                    "PG2490_CONTAINER_FAILED status="
                        + r.getStatus()
                        + " type="
                        + r.getThrowable().map(f -> f.getClass().getName()).orElse("missing"));
              return;
            }
            var m = (MethodSource) t.getSource().orElseThrow();
            if (!type.equals(m.getClassName()))
              throw new IllegalStateException("foreign test scope");
            rows.add(m.getMethodName());
            statuses.add(r.getStatus());
            if (r.getStatus() != TestExecutionResult.Status.SUCCESSFUL) {
              Throwable failure = r.getThrowable().orElse(null);
              for (int depth = 0; failure != null && depth < 8; depth++) {
                System.err.println(
                    "PG2490_FAILED test="
                        + m.getMethodName()
                        + " type="
                        + failure.getClass().getName());
                int count = 0;
                for (var frame : failure.getStackTrace()) {
                  if (frame.getClassName().startsWith("dev.codex.schubert.nk.") && count++ < 8)
                    System.err.println(
                        "PG2490_FRAME class="
                            + frame.getClassName()
                            + " method="
                            + frame.getMethodName()
                            + " line="
                            + frame.getLineNumber());
                }
                Throwable next = failure.getCause();
                if (next == failure) break;
                failure = next;
              }
            }
          }
        });
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                expected.stream().map(n -> DiscoverySelectors.selectMethod(type, n)).toList())
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var v = summary.getSummary();
    boolean passed =
        rows.size() == 2
            && rows.containsAll(expected)
            && statuses.stream().allMatch(s -> s == TestExecutionResult.Status.SUCCESSFUL)
            && v.getTestsFoundCount() == 2
            && v.getTestsStartedCount() == 2
            && v.getTestsSucceededCount() == 2
            && v.getTestsFailedCount() == 0
            && v.getTestsSkippedCount() == 0
            && v.getTestsAbortedCount() == 0
            && v.getContainersFailedCount() == 0
            && v.getContainersAbortedCount() == 0;
    var xml = new StringBuilder("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    xml.append("<testsuite name=\"PG2490\" tests=\"2\" failures=\"")
        .append(v.getTestsFailedCount())
        .append("\" errors=\"")
        .append(v.getContainersFailedCount())
        .append("\" skipped=\"")
        .append(v.getTestsSkippedCount() + v.getTestsAbortedCount())
        .append("\">\n");
    for (int i = 0; i < rows.size(); i++) {
      xml.append("<testcase classname=\"")
          .append(type)
          .append("\" name=\"")
          .append(rows.get(i))
          .append("\">");
      if (statuses.get(i) != TestExecutionResult.Status.SUCCESSFUL)
        xml.append("<failure message=\"Morning database guard failed\"/>");
      xml.append("</testcase>\n");
    }
    xml.append("</testsuite>\n");
    Files.writeString(Path.of(args[0]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    if (!passed)
      throw new IllegalStateException("selected Morning database guard failed or not executed");
    System.out.println("PG2490 tests2 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
