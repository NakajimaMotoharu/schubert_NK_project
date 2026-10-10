import java.io.PrintWriter;
import java.util.Arrays;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Explicit selected classes only, no package scan or parallel forks. */
public final class DeputySuiteRunner {
  private DeputySuiteRunner() {}

  public static void main(String[] args) {
    if (args.length == 0) throw new IllegalArgumentException("explicit suite required");
    var builder = LauncherDiscoveryRequestBuilder.request()
        .configurationParameter("junit.jupiter.execution.parallel.enabled", "false");
    Arrays.stream(args).forEach(name -> builder.selectors(DiscoverySelectors.selectClass(name)));
    var listener = new SummaryGeneratingListener();
    LauncherFactory.create().execute(builder.build(), listener);
    var summary = listener.getSummary();
    var output = new PrintWriter(System.out, true);
    summary.printTo(output);
    summary.printFailuresTo(output);
    if (summary.getTestsFoundCount() == 0 || summary.getTestsFailedCount() != 0
        || summary.getTestsSkippedCount() != 0 || summary.getTestsAbortedCount() != 0
        || summary.getContainersFailedCount() != 0
        || summary.getTestsSucceededCount() != summary.getTestsFoundCount()) System.exit(1);
  }
}
