import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import javax.xml.stream.XMLOutputFactory;
import org.junit.platform.engine.TestExecutionResult;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.engine.support.descriptor.MethodSource;
import org.junit.platform.launcher.TestExecutionListener;
import org.junit.platform.launcher.TestIdentifier;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/**
 * Frozen exact closed Batch standard-to-text fixture method catalog only; no package discovery or
 * other tests. No production server/DB/service startup; owned memory registries, own-JVM public
 * MXBeans and fixed values only.
 */
public final class BatchStandardTextFixtureJunitLauncher {
  private static final int EXPECTED_TESTS = 107;
  private static final int EXPECTED_SUITES = 6;

  private BatchStandardTextFixtureJunitLauncher() {}

  private record Result(String type, String method, String status, String failureType) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException(
          "new XML directory, frozen catalog and fixed locale required");
    if (!Set.of("ja-JP", "tr-TR").contains(args[2])
        || !java.util.Locale.getDefault().toLanguageTag().equals(args[2]))
      throw new IllegalArgumentException("dedicated JVM locale does not match fixed case");
    Set<String> allowed =
        Set.of(
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext001LiteralCounterGoldenAndNoDuplicateSuffix",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext002GaugeUnknownInfinityNegativeAndSignedZeroVectors",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext003CounterFiniteNonnegativeBoundaries",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext004CounterRejectsNegativeNanAndInfinity",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext005EmptyDoesNotFabricateObservationOrMetadata",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext006UnknownNamesDoNotReadTagsOrValue",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext007BothSelectedTypesRejectWrongInstrument",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext008NullSourceModeAndUnknownModeFail",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext009NullListMeterIdentityAndNameFail",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext010ClosedDomainRejectsArbitraryEscapingAndNonAsciiInputs",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext011MissingAndExtraLabelsFailBeforeReadingValue",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext012DuplicateAndNullTagContractsAreNotNormalized",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext013StandardReadsNoSourceTypeClosedOrValue",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext014BorrowedSourceClosedDebugFailsAndStandardDoesNotReopen",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext015CounterRuntimeAndErrorIdentityRetained",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext016GaugeRuntimeAndErrorIdentityRetained",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext017CounterCapturedNameAndLabelsMatchSameValueModel",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext018GaugeCapturedNameAndLabelsMatchSameValueModel",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext019SixFamiliesAndSeriesHaveDeterministicOrder",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext020LaterFailureDoesNotReturnPartialText",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext021OneMeterListReadAndSortedMultipleSeries",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext022DuplicateSeriesNeverProducesAmbiguousText",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext023OneFormatterDoesNotRetainPriorSourceOrFailure",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchtext024FiniteConcurrentCallsKeepBorrowedOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull001LiteralCustomBeforeStandardAndBothOwnersRemainBorrowed",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull002StandardNeverAcquiresOrReadsDetailsEvenAfterOwnerClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull003UnboundAndClosedStandardNeverReturnPartialCustom",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull004NullAndUnknownInputsFailBeforeStandardRead",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull005CustomRuntimePreservesIdentityAndSkipsFailingStandard",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull006CustomFatalPreservesIdentityAndSkipsStandard",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull007StandardRuntimeIsNotPartialCustomSuccess",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull008StandardFatalPreservesIdentityAndOwnership",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull009NullStandardTextIsRejectedRatherThanStringifiedOrEmptySuccess",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull010EmptyCustomAndNextSourceDoNotRetainHistory",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull011ConcurrentBorrowedSourcesNeverMixOrClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull012ActualStandardSdkUsesIndependentOwnJvmCpuOracle",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost001StandardIsEntirelyLazyIncludingAfterClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost002DefaultUsesOfficialStandardTextAndFixedBatchTag",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost003UnboundScrapeNeverAcquires",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost004NullAndUnknownModesFailBeforeAcquisition",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost005ConstructorEstablishesNonNullPorts",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost006FactoryRuntimeIdentityAndNoAutomaticRetry",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost007FactoryErrorIdentityIsNotNormalized",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost008NullFactoryResultIsNotSuccess",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost009ClosedCandidateIsRejectedAndRetainedUntilCallerClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost010PartialRegistryBeforeGcRemainsOwnedAfterFailure",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost011GcRetainedBeforeFatalAndClosedInReverseOrder",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost012FailedGcCloseKeepsRegistryAndExplicitRetryOwnership",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost013FailedRegistryCloseIsNotConfirmedAndCanBeExplicitlyRetried",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost014NullGcCallbackFailsWithoutImplicitRegistryClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost015SingleBindAndIdempotentClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest#batchhost016CloseWaitsForOwnedScrapeAndThenRejectsNewScrapes",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd001RealSdkThreePhasesWithCallerGcCloseBeforeRegistry",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd002StandardDoesNotInvokeAnyPortOrOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd003ForwardOrderAndNoImplicitCleanup",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd004AllNullBoundariesFailBeforeActions",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd005UnknownModesReadNoSourceAndExecuteNoPhase",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd006ClosedDebugFailsBeforeAnyPhase",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd007EachRuntimeFailureStopsOnlyLaterPhases",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd008EachErrorKeepsIdentityWithoutCleanup",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd009GcOwnerRejectKeepsEarlierBorrowedMetricsAndCallerHandle",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd010GcOwnerFailureIsNotNormalizedOrRetried",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd011ClosedStandardDoesNotReadOrReclose",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd012IndependentDefaultScopesNeverShareGcHandles",
            "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest#batchstd013FiniteIndependentConcurrentCompositions",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm001ActualFourStandardBindersWithIndependentRuntimeClock",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm002StandardIsLazyAndDoesNotReadRegistry",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm003ExactlyFourOrderedPortsSeeSameBorrowedOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm004NullBoundariesRejectWithoutBinding",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm005UnknownModesNeverReadSourceOrFactory",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm006ClosedDebugFailsBeforeFactoryAndDoesNotReopen",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm007NullFactoryListOrElementFailsBeforeAnyBinding",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm008WrongBinderCountIsNotPartialSuccess",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm009FactoryRuntimeAndErrorKeepIdentity",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm010EachBinderRuntimeStopsLaterPortsAndKeepsPartialOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm011EachBinderErrorIsNeverNormalized",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm012StandardOnClosedOwnerDoesNotInspectOrCloseAgain",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm013SameInstanceUsesDistinctRegistryOwners",
            "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest#batchjvm014FiniteConcurrentPortsDoNotShareSourceState",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys001ActualStandardCpuFdAndIndependentCpuTimeBracket",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys002StandardIsLazyAndDoesNotReadRegistry",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys003ExactlyTwoOrderedPortsSeeSameBorrowedOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys004NullBoundariesRejectWithoutBinding",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys005UnknownModesNeverReadSourceOrFactory",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys006ClosedDebugFailsBeforeFactoryAndDoesNotReopen",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys007NullFactoryListOrElementFailsBeforeAnyBinding",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys008WrongBinderCountIsNotPartialSuccess",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys009FactoryRuntimeAndErrorKeepIdentity",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys010EachBinderRuntimeStopsLaterPortsAndKeepsPartialOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys011EachBinderErrorIsNeverNormalized",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys012StandardOnClosedOwnerDoesNotInspectOrCloseAgain",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys013SameInstanceUsesDistinctRegistryOwners",
            "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest#batchsys014FiniteConcurrentPortsDoNotShareSourceState",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc001DefaultSdkIsOwnedAndClosedBeforeBorrowedRegistry",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc002StandardIsLazyForSourceFactoryAndOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc003FactoryOwnerBindOrderAndSameHandle",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc004NullBoundariesFailBeforeActivation",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc005UnknownModesNeverInspectSourceOrCallbacks",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc006ClosedDebugFailsBeforeFactoryAndOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc007NullFactoryResultIsNeverAcknowledged",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc008FactoryRuntimeAndErrorIdentityRetained",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc009OwnerRejectMeansNoBindOrImplicitClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc010OwnerRuntimeAndErrorNeverActivateOrAutoClose",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc011BindFailureLeavesExactHandleInAcknowledgedOwner",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc012SameInstallerDoesNotMixTwoOwnerScopes",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc013FiniteIndependentConcurrentOwnerScopes",
            "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest#batchgc014RetainThenRejectOrThrowKeepsCallerCleanupWithoutActivation");
    Map<String, List<String>> methods = new LinkedHashMap<>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 2 || !allowed.contains(row[0] + "#" + row[1])) {
        throw new IllegalStateException(
            "closed closed Batch standard-to-text fixture class and zero-argument method"
                + " required");
      }
      var names = methods.computeIfAbsent(row[0], ignored -> new ArrayList<>());
      if (names.contains(row[1])) throw new IllegalStateException("duplicate method");
      names.add(row[1]);
    }
    var expected =
        methods.entrySet().stream()
            .flatMap(entry -> entry.getValue().stream().map(name -> entry.getKey() + "#" + name))
            .collect(Collectors.toSet());
    if (!expected.equals(allowed)
        || expected.size() != EXPECTED_TESTS
        || methods.size() != EXPECTED_SUITES)
      throw new IllegalStateException(
          "exact closed Batch standard-to-text fixture inventory required");
    Path output = Path.of(args[0]);
    Files.createDirectory(output);
    List<Result> results = new ArrayList<>();
    var summary = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(
        summary,
        new TestExecutionListener() {
          @Override
          public void executionFinished(TestIdentifier id, TestExecutionResult outcome) {
            if (!id.isTest()) return;
            var source = (MethodSource) id.getSource().orElseThrow();
            results.add(
                new Result(
                    source.getClassName(),
                    source.getMethodName(),
                    outcome.getStatus().name(),
                    outcome.getThrowable().map(t -> t.getClass().getName()).orElse("")));
          }

          @Override
          public void executionSkipped(TestIdentifier id, String reason) {
            if (!id.isTest()) return;
            var source = (MethodSource) id.getSource().orElseThrow();
            results.add(new Result(source.getClassName(), source.getMethodName(), "SKIPPED", ""));
          }
        });
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                methods.entrySet().stream()
                    .flatMap(
                        entry ->
                            entry.getValue().stream()
                                .map(name -> DiscoverySelectors.selectMethod(entry.getKey(), name)))
                    .toList())
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .configurationParameter("junit.jupiter.extensions.autodetection.enabled", "false")
            .build());
    var value = summary.getSummary();
    boolean passed =
        results.size() == EXPECTED_TESTS
            && expected.equals(
                results.stream().map(r -> r.type() + "#" + r.method()).collect(Collectors.toSet()))
            && results.stream().allMatch(r -> r.status().equals("SUCCESSFUL"))
            && value.getTestsFoundCount() == EXPECTED_TESTS
            && value.getTestsStartedCount() == EXPECTED_TESTS
            && value.getTestsSucceededCount() == EXPECTED_TESTS
            && value.getTestsFailedCount() == 0
            && value.getTestsSkippedCount() == 0
            && value.getTestsAbortedCount() == 0
            && value.getContainersFailedCount() == 0
            && value.getContainersAbortedCount() == 0;
    for (String type : methods.keySet()) {
      var rows = results.stream().filter(r -> r.type().equals(type)).toList();
      try (var stream =
          Files.newBufferedWriter(
              output.resolve("TEST-" + type + ".xml"),
              StandardCharsets.UTF_8,
              StandardOpenOption.CREATE_NEW)) {
        var xml = XMLOutputFactory.newFactory().createXMLStreamWriter(stream);
        xml.writeStartDocument("UTF-8", "1.0");
        xml.writeStartElement("testsuite");
        xml.writeAttribute("name", type);
        xml.writeAttribute("tests", Integer.toString(rows.size()));
        xml.writeAttribute(
            "failures",
            Long.toString(rows.stream().filter(r -> r.status().equals("FAILED")).count()));
        xml.writeAttribute("errors", "0");
        xml.writeAttribute(
            "skipped",
            Long.toString(
                rows.stream()
                    .filter(r -> !List.of("SUCCESSFUL", "FAILED").contains(r.status()))
                    .count()));
        for (var row : rows) {
          xml.writeStartElement("testcase");
          xml.writeAttribute("classname", row.type());
          xml.writeAttribute("name", row.method());
          if (!row.status().equals("SUCCESSFUL")) {
            xml.writeEmptyElement(row.status().equals("FAILED") ? "failure" : "skipped");
            xml.writeAttribute("type", row.failureType());
          }
          xml.writeEndElement();
        }
        xml.writeEndElement();
        xml.writeEndDocument();
        xml.close();
      }
    }
    String counts =
        "found="
            + value.getTestsFoundCount()
            + ";started="
            + value.getTestsStartedCount()
            + ";succeeded="
            + value.getTestsSucceededCount()
            + ";failed="
            + value.getTestsFailedCount()
            + ";skipped="
            + value.getTestsSkippedCount()
            + ";aborted="
            + value.getTestsAbortedCount()
            + ";containerFailed="
            + value.getContainersFailedCount()
            + ";containerAborted="
            + value.getContainersAbortedCount()
            + ";passed="
            + passed;
    Files.writeString(
        output.resolve("summary.safe.txt"),
        counts,
        StandardCharsets.UTF_8,
        StandardOpenOption.CREATE_NEW);
    System.out.println("locale=" + java.util.Locale.getDefault().toLanguageTag());
    System.out.println("runtime.version=" + Runtime.version());
    System.out.println("os.name=" + System.getProperty("os.name"));
    System.out.println("os.arch=" + System.getProperty("os.arch"));
    System.out.println("os.version=" + System.getProperty("os.version"));
    System.out.println(counts);
    if (!passed)
      throw new IllegalStateException(
          "exact closed Batch standard-to-text fixture run not successful");
  }
}
