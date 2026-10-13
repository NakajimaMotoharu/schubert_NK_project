import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** PT-OPS-ROOTCTX-010, fixed independent ordinary-host kernel UID boundary. */
public final class Pg2220RootUidLauncher {
  private Pg2220RootUidLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1)
      throw new IllegalArgumentException("new XML path required");
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(summary);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                DiscoverySelectors.selectMethod(
                    "dev.codex.schubert.nk.batch.platform.RootStartupContextTest",
                    "rootctx010NativeServiceUidRejectsInvalidPidAndOrdinaryCaller"))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var v = summary.getSummary();
    boolean passed =
        v.getTestsFoundCount() == 1
            && v.getTestsStartedCount() == 1
            && v.getTestsSucceededCount() == 1
            && v.getTestsFailedCount() == 0
            && v.getTestsSkippedCount() == 0
            && v.getTestsAbortedCount() == 0
            && v.getContainersFailedCount() == 0
            && v.getContainersAbortedCount() == 0;
    String xml =
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<testsuite name=\"PG2220\" tests=\"1\" failures=\""
            + v.getTestsFailedCount()
            + "\" errors=\""
            + v.getContainersFailedCount()
            + "\" skipped=\""
            + (v.getTestsSkippedCount() + v.getTestsAbortedCount())
            + "\">\n"
            + "<testcase classname=\"dev.codex.schubert.nk.batch.platform.RootStartupContextTest\" "
            + "name=\"rootctx010NativeServiceUidRejectsInvalidPidAndOrdinaryCaller\">"
            + (passed ? "" : "<failure message=\"kernel UID boundary failed\"/>")
            + "</testcase></testsuite>\n";
    Files.writeString(Path.of(args[0]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    if (!passed) throw new IllegalStateException("selected UID boundary failed or not executed");
    System.out.println("PG2220 tests1 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
