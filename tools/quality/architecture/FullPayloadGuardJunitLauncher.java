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
 * Frozen exact closed three-role full-payload helper owner guard method catalog only; no package
 * discovery or other tests. No production server/DB/service startup; owned memory registries and
 * pure enum/label values only.
 */
public final class FullPayloadGuardJunitLauncher {
  private static final int EXPECTED_TESTS = 89;
  private static final int EXPECTED_SUITES = 3;

  private FullPayloadGuardJunitLauncher() {}

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
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay001StandardReadyPreservesLiteralWithoutSupplierRead",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay002StandardDownPreservesLiteralWithoutSupplierRead",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay003DebugReadyAppendsIndependentCustomAndReadsSupplierOnce",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay004DebugDownDoesNotInventHealthyReadiness",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay005UnknownModesNeverResolveSource",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay006NullModeAndSupplierFailBeforeResolution",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay007NullResolvedSourceNeverFallsBackToReadyOnly",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay008ProviderRuntimeAndErrorKeepIdentity",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay009IncompatibleSourceNeverReturnsReadyOnly",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay010FormatterRuntimeAndErrorKeepBorrowedOwner",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay011ClosedSourceIsNotReopenedOrClosedAgain",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay012SameRendererDoesNotRetainOneOfTwoSources",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apipay013FiniteConcurrentIndependentPayloads",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull001StandardKeepsLegacyBytesAndNeverAcquiresEitherSource",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull002LiteralFullOrderAndActualOfficialSdkValue",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull003UnboundAndClosedStandardNeverBecomePartialSuccess",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull004NullAndUnknownBoundariesReadNeitherProvider",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull005CustomRuntimeWinsBeforeStandardFailure",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull006CustomErrorIdentityIsPreservedWithoutStandardRead",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull007CustomFormatterFailureKeepsBorrowedResources",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull008StandardRuntimeNeverFallsBackOrClosesBorrowedCustom",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull009StandardErrorIdentityNeverBecomesReadyOnlySuccess",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull010ContractViolatingNullTextIsRejectedNotConcatenated",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull011ConcurrentFullScrapesKeepIndependentGoldenAndOwnership",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull012CallerCloseBetweenSourcesCannotReturnPartialText",
            "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest#apifull013HelperReleasesRejectedCandidateBeforeReturningOwner",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay001StandardReadyPreservesLiteralWithoutSupplierRead",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay002StandardDownPreservesLiteralWithoutSupplierRead",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay003DebugReadyAppendsIndependentCustomAndReadsSupplierOnce",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay004DebugDownDoesNotInventHealthyReadiness",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay005UnknownModesNeverResolveSource",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay006NullModeAndSupplierFailBeforeResolution",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay007NullResolvedSourceNeverFallsBackToReadyOnly",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay008ProviderRuntimeAndErrorKeepIdentity",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay009IncompatibleSourceNeverReturnsReadyOnly",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay010FormatterRuntimeAndErrorKeepBorrowedOwner",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay011ClosedSourceIsNotReopenedOrClosedAgain",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay012SameRendererDoesNotRetainOneOfTwoSources",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webpay013FiniteConcurrentIndependentPayloads",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull001StandardKeepsLegacyBytesAndNeverAcquiresEitherSource",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull002LiteralFullOrderAndActualOfficialSdkValue",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull003UnboundAndClosedStandardNeverBecomePartialSuccess",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull004NullAndUnknownBoundariesReadNeitherProvider",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull005CustomRuntimeWinsBeforeStandardFailure",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull006CustomErrorIdentityIsPreservedWithoutStandardRead",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull007CustomFormatterFailureKeepsBorrowedResources",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull008StandardRuntimeNeverFallsBackOrClosesBorrowedCustom",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull009StandardErrorIdentityNeverBecomesReadyOnlySuccess",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull010ContractViolatingNullTextIsRejectedNotConcatenated",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull011ConcurrentFullScrapesKeepIndependentGoldenAndOwnership",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull012CallerCloseBetweenSourcesCannotReturnPartialText",
            "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest#webfull013HelperReleasesRejectedCandidateBeforeReturningOwner",
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
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest#batchfull013HelperReleasesRejectedCandidateBeforeReturningOwner");
    Map<String, List<String>> methods = new LinkedHashMap<>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 2 || !allowed.contains(row[0] + "#" + row[1])) {
        throw new IllegalStateException(
            "closed closed three-role full-payload helper owner guard class and zero-argument method"
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
          "exact closed three-role full-payload helper owner guard inventory required");
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
          "exact closed three-role full-payload helper owner guard run not successful");
  }
}
