import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
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
 * Exact two in-memory API scalar exporter host-only classes; ordinary JUnit results, no synthetic
 * PASS or exception formatting.
 */
public final class ApiScalarExporterJunitLauncher {
  private ApiScalarExporterJunitLauncher() {}

  private record Result(
      String type, String method, String status, String failureType, String failureLocation) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 1) throw new IllegalArgumentException("new XML directory required");
    Path output = Path.of(args[0]);
    Files.createDirectory(output);
    List<String> types =
        List.of(
            "dev.codex.schubert.nk.api.monitoring.ApiScalarMetricExporterTest",
            "dev.codex.schubert.nk.api.monitoring.ApiScalarPrecisionContractTest");
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
                    outcome.getThrowable().map(t -> t.getClass().getName()).orElse(""),
                    outcome
                        .getThrowable()
                        .map(
                            t ->
                                java.util.Arrays.stream(t.getStackTrace())
                                    .filter(
                                        f -> f.getClassName().startsWith("dev.codex.schubert.nk."))
                                    .limit(8)
                                    .map(
                                        f ->
                                            f.getClassName()
                                                + "."
                                                + f.getMethodName()
                                                + ":"
                                                + f.getLineNumber())
                                    .collect(java.util.stream.Collectors.joining(";")))
                        .orElse("")));
          }

          @Override
          public void executionSkipped(TestIdentifier id, String reason) {
            if (!id.isTest()) return;
            var source = (MethodSource) id.getSource().orElseThrow();
            results.add(
                new Result(source.getClassName(), source.getMethodName(), "SKIPPED", "", ""));
          }
        });
    Instant started = Instant.now();
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(types.stream().map(DiscoverySelectors::selectClass).toList())
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    Map<String, List<Result>> byType = new LinkedHashMap<>();
    for (var type : types) byType.put(type, new ArrayList<>());
    for (var result : results) byType.get(result.type()).add(result);
    for (var entry : byType.entrySet()) {
      var rows = entry.getValue();
      try (var stream =
          Files.newBufferedWriter(
              output.resolve("TEST-" + entry.getKey() + ".xml"),
              StandardCharsets.UTF_8,
              StandardOpenOption.CREATE_NEW)) {
        var xml = XMLOutputFactory.newFactory().createXMLStreamWriter(stream);
        xml.writeStartDocument("UTF-8", "1.0");
        xml.writeStartElement("testsuite");
        xml.writeAttribute("name", entry.getKey());
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
        xml.writeAttribute("timestamp", started.toString());
        for (var row : rows) {
          xml.writeStartElement("testcase");
          xml.writeAttribute("classname", row.type());
          xml.writeAttribute("name", row.method());
          if (!row.status().equals("SUCCESSFUL")) {
            xml.writeEmptyElement(row.status().equals("FAILED") ? "failure" : "skipped");
            xml.writeAttribute("type", row.failureType());
            // Bounded own-source frames only: no Throwable message, cause/suppressed walk or raw
            // values.
            xml.writeAttribute("location", row.failureLocation());
          }
          xml.writeEndElement();
        }
        xml.writeEndElement();
        xml.writeEndDocument();
        xml.close();
      }
    }
    var value = summary.getSummary();
    boolean passed =
        value.getTestsFoundCount() == 32
            && value.getTestsStartedCount() == 32
            && value.getTestsSucceededCount() == 32
            && value.getTestsFailedCount() == 0
            && value.getTestsSkippedCount() == 0
            && value.getTestsAbortedCount() == 0
            && value.getContainersFailedCount() == 0
            && value.getContainersAbortedCount() == 0
            && results.size() == 32;
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
    Files.writeString(output.resolve("summary.safe.txt"), counts, StandardOpenOption.CREATE_NEW);
    System.out.println(counts);
    if (!passed) throw new IllegalStateException("selected host PT failed or not run");
  }
}
