import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Synthetic semantic enum proof only, never a Production test or coverage capture. */
public final class WireEnumOracleCanaryLauncher {
  private WireEnumOracleCanaryLauncher() {}
  public static void main(String[] arguments) {
    if (arguments == null || arguments.length != 0) throw new IllegalArgumentException("fixed canary required");
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create(); launcher.registerTestExecutionListeners(listener);
    launcher.execute(LauncherDiscoveryRequestBuilder.request().selectors(DiscoverySelectors.selectMethod(
        "dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest",
        "approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTables"))
        .configurationParameter("junit.jupiter.execution.parallel.enabled", "false").build());
    var summary = listener.getSummary();
    boolean ran = summary.getTestsFoundCount() == 1 && summary.getTestsStartedCount() == 1
        && summary.getTestsSkippedCount() == 0 && summary.getTestsAbortedCount() == 0
        && summary.getContainersFailedCount() == 0 && summary.getContainersAbortedCount() == 0;
    for (var failure : summary.getFailures())
      System.out.println("CANARY_FAILURE_CLASS=" + failure.getException().getClass().getName());
    if (!ran) throw new IllegalStateException("one real selected canary required");
    System.out.println("CANARY_STARTED=1 SUCCEEDED=" + summary.getTestsSucceededCount()
        + " FAILED=" + summary.getTestsFailedCount());
    if (summary.getTestsSucceededCount() != 1) System.exit(1);
  }
}
