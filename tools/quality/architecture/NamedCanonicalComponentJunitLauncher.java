import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
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
 * One explicit current semantic component gate, not classpath or historical whole-run discovery.
 */
public final class NamedCanonicalComponentJunitLauncher {
  private static final String PREFIX = "dev.codex.schubert.nk.protocol.layout.";
  private static final Map<String, List<String>> METHODS =
      Map.of(
          PREFIX + "SemanticDirectBoundaryTest",
          List.of(
              "sem001PasswordCharacterByteAndUsernameLimits",
              "sem002InclusiveDateLimitsAndOneSidedFilters",
              "sem003QuestionAndWebLogTextContracts"),
          PREFIX + "PayloadTypeCatalogTest",
          List.of(
              "allNamedTypesHaveIndependentDirectionalFieldMeaning",
              "explicitCatalogMatchesIndependentSs323NamedTypeFixture",
              "allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes",
              "optionalFieldsSupportUnsetAndPresentValuesWithoutLosingWireNames",
              "catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes",
              "typedModelsAndHelpersRejectNullMissingAndWrongKinds"),
          PREFIX + "PayloadPaginationBoundaryTest",
          List.of(
              "page001SecondPageHasIndependentExpectedBounds",
              "page002MaximumEffectivePageKeepsExactNineDigitArithmetic",
              "page003RejectsIndependentRangeAndOneFieldArithmeticChanges"),
          PREFIX + "PayloadSemanticValidatorTest",
          List.of(
              "pageConstantsCountsAndArithmeticAreEnforced",
              "listRecordConditionsAndOrderingAreEnforced",
              "scenarioInlineAndLargeFileConditionsAreEnforced",
              "mediaAnimationAndMusicConditionsAreEnforced",
              "loginUserPasswordDateAndSessionRulesAreEnforced",
              "notificationCancellationAndQuestionStateConditionsAreEnforced",
              "receiptWebAndDefensiveContractsAreEnforced",
              "deletedNotificationNeverContainsAnswer"));

  private NamedCanonicalComponentJunitLauncher() {}

  private record Result(String type, String method, String status, String failureType) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 1) throw new IllegalArgumentException("new output directory required");
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
                METHODS.entrySet().stream()
                    .flatMap(
                        entry ->
                            entry.getValue().stream()
                                .map(
                                    method ->
                                        DiscoverySelectors.selectMethod(entry.getKey(), method)))
                    .toList())
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var value = summary.getSummary();
    Set<String> expected =
        METHODS.entrySet().stream()
            .flatMap(
                entry -> entry.getValue().stream().map(method -> entry.getKey() + "#" + method))
            .collect(Collectors.toSet());
    boolean passed =
        expected.size() == 20
            && results.size() == 20
            && expected.equals(
                results.stream().map(r -> r.type() + "#" + r.method()).collect(Collectors.toSet()))
            && results.stream().allMatch(r -> r.status().equals("SUCCESSFUL"))
            && value.getTestsFoundCount() == 20
            && value.getTestsStartedCount() == 20
            && value.getTestsSucceededCount() == 20
            && value.getTestsFailedCount() == 0
            && value.getTestsSkippedCount() == 0
            && value.getTestsAbortedCount() == 0
            && value.getContainersFailedCount() == 0
            && value.getContainersAbortedCount() == 0;
    for (String type : METHODS.keySet()) {
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
    System.out.println("runtime.version=" + Runtime.version());
    System.out.println("os.name=" + System.getProperty("os.name"));
    System.out.println("os.arch=" + System.getProperty("os.arch"));
    System.out.println("os.version=" + System.getProperty("os.version"));
    System.out.println(counts);
    if (!passed) throw new IllegalStateException("exact twenty component cases not successful");
  }
}
