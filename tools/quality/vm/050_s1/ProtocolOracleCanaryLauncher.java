import java.util.Set;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Isolated oracle diagnosis only. No agent, runtime authority, or PT count credit. */
public final class ProtocolOracleCanaryLauncher {
  private ProtocolOracleCanaryLauncher() {}

  public static void main(String[] arguments) {
    if (arguments == null
        || arguments.length != 1
        || !Set.of(
                "layout.PayloadTypeCatalogTest#allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes",
                "layout.PayloadTypeCatalogTest#namedLoginFieldsHaveIndependentDirectionalMeaning",
                "codec.PayloadGoldenVectorTest#sharedCodecProducesIdenticalBytesUnderConcurrentUse")
            .contains(arguments[0]))
      throw new IllegalArgumentException("fixed protocol oracle selector required");
    String[] selector = arguments[0].split("#", -1);
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                DiscoverySelectors.selectMethod(
                    "dev.codex.schubert.nk.protocol." + selector[0], selector[1]))
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
    for (var failure : result.getFailures())
      System.out.println("CANARY_FAILURE_CLASS=" + failure.getException().getClass().getName());
    System.out.println(
        "CANARY_STARTED=1 SUCCEEDED="
            + result.getTestsSucceededCount()
            + " FAILED="
            + result.getTestsFailedCount());
    if (result.getTestsSucceededCount() != 1) System.exit(1);
  }
}
