import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import javax.xml.stream.XMLOutputFactory;
import org.junit.platform.engine.TestExecutionResult;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.engine.support.descriptor.MethodSource;
import org.junit.platform.launcher.TestExecutionListener;
import org.junit.platform.launcher.TestIdentifier;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Select exactly three frozen pure-memory pagination cases, never a historical whole suite. */
public final class PaginationBoundaryJunitLauncher {
  private static final String TYPE =
      "dev.codex.schubert.nk.protocol.layout.PayloadPaginationBoundaryTest";
  private static final List<String> METHODS =
      List.of(
          "page001SecondPageHasIndependentExpectedBounds",
          "page002MaximumEffectivePageKeepsExactNineDigitArithmetic",
          "page003RejectsIndependentRangeAndOneFieldArithmeticChanges");

  private PaginationBoundaryJunitLauncher() {}

  private record Result(String type, String method, String status, String failureType) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 1) throw new IllegalArgumentException("new XML directory required");
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
                METHODS.stream()
                    .map(method -> DiscoverySelectors.selectMethod(TYPE, method))
                    .toList())
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var value = summary.getSummary();
    boolean passed =
        value.getTestsFoundCount() == 3
            && value.getTestsStartedCount() == 3
            && value.getTestsSucceededCount() == 3
            && value.getTestsFailedCount() == 0
            && value.getTestsSkippedCount() == 0
            && value.getTestsAbortedCount() == 0
            && value.getContainersFailedCount() == 0
            && value.getContainersAbortedCount() == 0
            && results.size() == 3
            && Set.copyOf(results.stream().map(Result::method).toList()).equals(Set.copyOf(METHODS))
            && results.stream()
                .allMatch(row -> row.type().equals(TYPE) && row.status().equals("SUCCESSFUL"));
    try (var stream =
        Files.newBufferedWriter(
            output.resolve("TEST-" + TYPE + ".xml"),
            StandardCharsets.UTF_8,
            StandardOpenOption.CREATE_NEW)) {
      var xml = XMLOutputFactory.newFactory().createXMLStreamWriter(stream);
      xml.writeStartDocument("UTF-8", "1.0");
      xml.writeStartElement("testsuite");
      xml.writeAttribute("name", TYPE);
      xml.writeAttribute("tests", Integer.toString(results.size()));
      xml.writeAttribute(
          "failures",
          Long.toString(results.stream().filter(row -> row.status().equals("FAILED")).count()));
      xml.writeAttribute("errors", "0");
      xml.writeAttribute(
          "skipped",
          Long.toString(
              results.stream()
                  .filter(row -> !List.of("SUCCESSFUL", "FAILED").contains(row.status()))
                  .count()));
      for (var row : results) {
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
    if (!passed)
      throw new IllegalStateException("exact three ordinary pagination cases not successful");
  }
}
