import java.util.Set;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Test-oracle mutation only; no agent, production PT count or coverage credit. */
public final class HeaderOracleCanaryLauncher {
  private HeaderOracleCanaryLauncher() {}

  public static void main(String[] arguments) {
    if (arguments == null
        || arguments.length != 1
        || !Set.of(
                "headerConstructorRejectsEveryStructuralViolation",
                "enumsMapOnlyApprovedWireValues")
            .contains(arguments[0]))
      throw new IllegalArgumentException("fixed header oracle selection required");
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                DiscoverySelectors.selectMethod(
                    "dev.codex.schubert.nk.protocol.header.HeaderModelTest", arguments[0]))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var summary = listener.getSummary();
    if (summary.getTestsFoundCount() != 1
        || summary.getTestsStartedCount() != 1
        || summary.getTestsSkippedCount() != 0
        || summary.getTestsAbortedCount() != 0
        || summary.getContainersFailedCount() != 0
        || summary.getContainersAbortedCount() != 0)
      throw new IllegalStateException("one actually selected header test required");
    for (var failure : summary.getFailures())
      System.out.println("CANARY_FAILURE_CLASS=" + failure.getException().getClass().getName());
    System.out.println(
        "CANARY_STARTED=1 SUCCEEDED="
            + summary.getTestsSucceededCount()
            + " FAILED="
            + summary.getTestsFailedCount());
    if (summary.getTestsSucceededCount() != 1) System.exit(1);
  }
}
