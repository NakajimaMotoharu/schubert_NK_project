import java.io.PrintWriter;
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

/** Current-source eight genuine unsupported-port negative contracts, never a VM owner proof. */
public final class Pg1628SelectedLauncher {
  private Pg1628SelectedLauncher() {}

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 1)
      throw new IllegalArgumentException("new XML path required");
    var rows = new ArrayList<String>();
    var results = new ArrayList<TestExecutionResult.Status>();
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(
        summary,
        new TestExecutionListener() {
          @Override
          public void executionFinished(TestIdentifier test, TestExecutionResult result) {
            if (!test.isTest()) return;
            var method = (MethodSource) test.getSource().orElseThrow();
            rows.add(method.getClassName() + ":" + method.getMethodName());
            results.add(result.getStatus());
          }
        });
    var request =
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                DiscoverySelectors.selectClass(
                    "dev.codex.schubert.nk.batch.file.UnsupportedBackupVerificationTest"),
                DiscoverySelectors.selectClass(
                    "dev.codex.schubert.nk.batch.platform.UnsupportedServiceMarkerTest"),
                DiscoverySelectors.selectClass(
                    "dev.codex.schubert.nk.batch.file.UnsupportedOriginalProofTest"),
                DiscoverySelectors.selectClass(
                    "dev.codex.schubert.nk.batch.platform.UnsupportedRootIdentityTest"),
                DiscoverySelectors.selectClass(
                    "dev.codex.schubert.nk.batch.file.TransferCleanupFailureTest"),
                DiscoverySelectors.selectClass(
                    "dev.codex.schubert.nk.batch.file.RootRecoveryNativeAuthorityTest"))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build();
    launcher.execute(request);
    var value = summary.getSummary();
    var expected =
        List.of(
            "dev.codex.schubert.nk.batch.file.UnsupportedBackupVerificationTest:bverifyPort001UnsupportedVerificationRejectsAndClosesWithoutSecretOrRegeneration",
            "dev.codex.schubert.nk.batch.platform.UnsupportedServiceMarkerTest:serviceMarkerPort001MissingRetainedProofNeverGrantsDaemonReadiness",
            "dev.codex.schubert.nk.batch.platform.UnsupportedServiceMarkerTest:serviceMarkerPort002MissingObservationClosePreservesUnknownAndCannotRetire",
            "dev.codex.schubert.nk.batch.file.UnsupportedOriginalProofTest:originalPort001DefaultResumeVerificationNeverProvesOriginalOrRetainedOwnership",
            "dev.codex.schubert.nk.batch.platform.UnsupportedRootIdentityTest:rootIdentityPort001AbsentUidProviderRejectsOtherwiseValidSamePeerService",
            "dev.codex.schubert.nk.batch.file.TransferCleanupFailureTest:transferFailure001OneUnlinkFailureRetainsBytesCountsWarningAndContinuesOtherFile",
            "dev.codex.schubert.nk.batch.file.RootRecoveryNativeAuthorityTest:recoveryNative001SinglePublicDefaultsRejectUnprivilegedHostWithoutAnyOriginalMutation",
            "dev.codex.schubert.nk.batch.file.RootRecoveryNativeAuthorityTest:recoveryNative002PairPublicDefaultsRejectBothChildrenAndPreservePublicationFirstQuarantine");
    boolean passed =
        rows.size() == 8
            && rows.containsAll(expected)
            && results.stream().allMatch(v -> v == TestExecutionResult.Status.SUCCESSFUL)
            && value.getTestsFoundCount() == 8
            && value.getTestsStartedCount() == 8
            && value.getTestsSucceededCount() == 8
            && value.getTestsFailedCount() == 0
            && value.getTestsSkippedCount() == 0
            && value.getTestsAbortedCount() == 0
            && value.getContainersFailedCount() == 0
            && value.getContainersAbortedCount() == 0;
    try (var writer =
        Files.newBufferedWriter(
            Path.of(args[0]), StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW)) {
      writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
      writer.write(
          "<testsuite name=\"PG1628\" tests=\"8\" failures=\""
              + value.getTestsFailedCount()
              + "\" errors=\""
              + value.getContainersFailedCount()
              + "\" skipped=\""
              + (value.getTestsSkippedCount() + value.getTestsAbortedCount())
              + "\">\n");
      for (int i = 0; i < rows.size(); i++) {
        String[] name = rows.get(i).split(":", 2);
        writer.write("<testcase classname=\"" + name[0] + "\" name=\"" + name[1] + "\">");
        if (results.get(i) != TestExecutionResult.Status.SUCCESSFUL)
          writer.write("<failure message=\"selected contract failed\"/>");
        writer.write("</testcase>\n");
      }
      writer.write("</testsuite>\n");
    }
    if (!passed) {
      summary.getSummary().printFailuresTo(new PrintWriter(System.err, true));
      throw new IllegalStateException("selected unsupported port contracts failed");
    }
    System.out.println("PG1628 tests8 failures0 errors0 skipped0 aborted0 notRun0");
  }
}
