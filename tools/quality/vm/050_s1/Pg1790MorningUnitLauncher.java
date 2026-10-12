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

/** SSC278 BUG1162: actual Unit byte fixture; no service/owner operations. */
public final class Pg1790MorningUnitLauncher {
  private Pg1790MorningUnitLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 2)
      throw new IllegalArgumentException("fixed repo/XML required");
    System.setProperty("nk.pt.repository", args[0]);
    String clazz = "dev.codex.schubert.nk.batch.platform.MorningServiceUnitTest";
    var expected =
        List.of(
            "munit001FixedRootActorAndRealJavaEntrypoint",
            "munit002NoUnscopedInputsOrSuccessOverride",
            "munit003DependencyAndNoForcedKill",
            "munit004ParentOnlyTargetCannotParallelStartChildren");
    var names = new ArrayList<String>();
    var statuses = new ArrayList<TestExecutionResult.Status>();
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(
        summary,
        new TestExecutionListener() {
          @Override
          public void executionFinished(TestIdentifier test, TestExecutionResult result) {
            if (!test.isTest()) return;
            var method = (MethodSource) test.getSource().orElseThrow();
            if (!method.getClassName().equals(clazz))
              throw new IllegalStateException("foreign test");
            names.add(method.getMethodName());
            statuses.add(result.getStatus());
          }
        });
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(DiscoverySelectors.selectClass(clazz))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var s = summary.getSummary();
    boolean complete =
        names.size() == expected.size()
            && names.containsAll(expected)
            && names.stream().distinct().count() == expected.size()
            && s.getTestsFoundCount() == expected.size()
            && s.getTestsStartedCount() == expected.size()
            && s.getTestsSkippedCount() == 0
            && s.getTestsAbortedCount() == 0
            && s.getContainersFailedCount() == 0
            && s.getContainersAbortedCount() == 0;
    StringBuilder xml = new StringBuilder("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    xml.append("<testsuite name=\"PG1790\" tests=\"")
        .append(expected.size())
        .append("\" failures=\"")
        .append(s.getTestsFailedCount())
        .append("\" errors=\"0\" skipped=\"")
        .append(s.getTestsSkippedCount())
        .append("\">\n");
    for (int i = 0; i < names.size(); i++) {
      xml.append("<testcase classname=\"")
          .append(clazz)
          .append("\" name=\"")
          .append(names.get(i))
          .append("\">");
      if (statuses.get(i) != TestExecutionResult.Status.SUCCESSFUL)
        xml.append(
            "<failure message=\"Unit contract assertion failed; private source retained\"/>");
      xml.append("</testcase>\n");
    }
    xml.append("</testsuite>\n");
    Files.writeString(Path.of(args[1]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    System.out.println(
        "PG1790 tests="
            + s.getTestsStartedCount()
            + " failures="
            + s.getTestsFailedCount()
            + " complete="
            + complete);
    if (!complete || s.getTestsSucceededCount() != expected.size()) System.exit(1);
  }
}
