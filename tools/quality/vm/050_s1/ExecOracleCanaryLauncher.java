import java.util.Set;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Private oracle diagnosis only, no runtime authority, agent, PT or coverage credit. */
public final class ExecOracleCanaryLauncher {
  private ExecOracleCanaryLauncher() {}

  public static void main(String[] arguments) {
    if (arguments == null
        || arguments.length != 1
        || !Set.of(
                "opsExec001LiteralVectorsAndArenaLifetime",
                "opsExec007ConcurrentInputsRemainIndependent",
                "largeResultMaximum")
            .contains(arguments[0]))
      throw new IllegalArgumentException("fixed exec oracle selector");
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                DiscoverySelectors.selectMethod(
                    arguments[0].equals("largeResultMaximum")
                        ? "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest"
                        : "dev.codex.schubert.nk.storage.LinuxProcessExecTest",
                    arguments[0].equals("largeResultMaximum")
                        ? "acceptsTheDocumentedTenThousandRecordFortyEightMillionByteMaximum"
                        : arguments[0]))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var result = listener.getSummary();
    if (result.getTestsFoundCount() != 1
        || result.getTestsStartedCount() != 1
        || result.getTestsSkippedCount() != 0
        || result.getTestsAbortedCount() != 0
        || result.getContainersFailedCount() != 0
        || result.getContainersAbortedCount() != 0)
      throw new IllegalStateException("one actual selected test required");
    for (var failure : result.getFailures()) {
      System.out.println("CANARY_FAILURE_CLASS=" + failure.getException().getClass().getName());
      Throwable current = failure.getException();
      boolean assertion = false;
      for (int depth = 0; depth < 16 && current != null; depth++) {
        assertion |= current.getClass().getName().equals("org.opentest4j.AssertionFailedError");
        current = current.getCause();
      }
      System.out.println("CANARY_ASSERTION_CAUSE=" + assertion);
    }
    System.out.println(
        "CANARY_STARTED=1 SUCCEEDED="
            + result.getTestsSucceededCount()
            + " FAILED="
            + result.getTestsFailedCount());
    if (result.getTestsSucceededCount() != 1) System.exit(1);
  }
}
