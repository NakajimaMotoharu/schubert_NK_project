import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** PT-MDB-2780-001; exact independent resume skipped pair guard case, not an added Main class. */
public final class Pg2780ResumeSkippedLauncher {
  private Pg2780ResumeSkippedLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1) throw new IllegalArgumentException("new XML required");
    String type = "dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest";
    String method = "mdb2780001ResumeRejectsEitherNonSkippedAttemptBeforeCommit";
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(DiscoverySelectors.selectMethod(type, method))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var s = listener.getSummary();
    boolean passed =
        s.getTestsFoundCount() == 1
            && s.getTestsStartedCount() == 1
            && s.getTestsSucceededCount() == 1
            && s.getTestsFailedCount() == 0
            && s.getTestsSkippedCount() == 0
            && s.getTestsAbortedCount() == 0
            && s.getContainersFailedCount() == 0
            && s.getContainersAbortedCount() == 0;
    String xml =
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<testsuite name=\"PG2780\" tests=\"1\" failures=\""
            + s.getTestsFailedCount()
            + "\" errors=\""
            + s.getContainersFailedCount()
            + "\" skipped=\""
            + (s.getTestsSkippedCount() + s.getTestsAbortedCount())
            + "\"><testcase classname=\""
            + type
            + "\" name=\""
            + method
            + "\">"
            + (passed ? "" : "<failure message=\"resume skipped pair guard failed\"/>")
            + "</testcase></testsuite>\n";
    Files.writeString(Path.of(args[0]), xml, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    if (!passed) throw new IllegalStateException("selected DB handoff case failed/not-run");
    System.out.println("PG2780 tests1 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
