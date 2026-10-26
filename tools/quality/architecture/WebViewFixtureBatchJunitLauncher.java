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
 * Frozen exact closed Web view method catalog only; no package discovery or other tests. No
 * production server/DB/service startup; explicitly reviewed MVC/MockServlet only.
 */
public final class WebViewFixtureBatchJunitLauncher {
  private static final int EXPECTED_TESTS = 68;
  private static final int EXPECTED_SUITES = 8;

  private WebViewFixtureBatchJunitLauncher() {}

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
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web262CompleteRow",
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web263OptionalFields",
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web264PageBounds",
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web265OrderingAndIdentity",
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web266NullRoleAndOwnership",
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web267ClosedBeansAndRedaction",
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web268SyntheticHtmlEscaping",
            "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#web269ConcurrentProjection",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log084LayoutAndFilters",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log085RowsAndOptional",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log086Pagination",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log087Escaping",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log088InvalidDisplay",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log089CsrfAndClosedSurface",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log090StylesAndResources",
            "dev.codex.schubert.nk.web.view.LogSearchTemplateTest#log091ConcurrentRendering",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web286SuccessfulSnapshot",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web287Pagination",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web288QueryEncoding",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web289ResponseBinding",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web290InvalidFields",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web291NullRoleOwnership",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web292ClosedBeanAndEscaping",
            "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#web293ConcurrentViews",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail017HeaderAndCommonLayout",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail018PreviousNext",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail019EntriesAndVoices",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail020EmptyScenario",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail021HtmlAndUrlSafety",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail022MaximumRecordsAndVoices",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail023CssAndViewBoundary",
            "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest#detail024ConcurrentRendering",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web194HeaderAndNavigation",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web195GroupingAndAudio",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web196EmptyAndBounds",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web197NullContracts",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web198NavigationPairs",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web199SequenceRejection",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web200EntryMetadataConsistency",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web201ImmutableSnapshot",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web202ClosedBeanContract",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web203SyntheticHtmlEscaping",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web204ConcurrentProjection",
            "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#web205RedactedDiagnostics",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web206LiteralRowsAndAudio",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web207PageBounds",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web208PageRecordMismatch",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web209AudioAndLineInvariants",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web210NullAndOwnership",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web211ClosedBeansAndRedaction",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web212SyntheticEscaping",
            "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#web213ConcurrentProjection",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search026CommonLayoutAndInputs",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search027ResultsAndAudio",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search028PaginationAndEmpty",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search029ValidationErrors",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search030EscapingAndCsp",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search031MaximumRowsAndCandidates",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search032CssResourcesAndViewBoundary",
            "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest#search033ConcurrentRendering",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web222SuccessfulSnapshot",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web223PaginationUrls",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web224QueryEncoding",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web225ResponseBindingAndBounds",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web226InvalidFieldDisplay",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web227NullAndOwnership",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web228ClosedBeansAndRedaction",
            "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#web229ConcurrentSnapshots");
    Map<String, List<String>> methods = new LinkedHashMap<>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 2 || !allowed.contains(row[0] + "#" + row[1])) {
        throw new IllegalStateException(
            "closed closed Web view class and zero-argument method" + " required");
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
      throw new IllegalStateException("exact closed Web view inventory required");
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
    if (!passed) throw new IllegalStateException("exact closed Web view run not successful");
  }
}
