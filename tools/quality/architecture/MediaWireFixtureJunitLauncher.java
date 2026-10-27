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
 * Frozen exact Scenario Animation Music pure wire fixture method catalog only; no package discovery
 * or other tests. No production server/DB/service startup; owned fixed callback values, finite
 * workers and wire bytes and metadata only.
 */
public final class MediaWireFixtureJunitLauncher {
  private static final int EXPECTED_TESTS = 24;
  private static final int EXPECTED_SUITES = 3;

  private MediaWireFixtureJunitLauncher() {}

  private record Result(
      String type, String method, String status, String failureType, String testSourceLocation) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException(
          "new XML directory, frozen catalog and fixed locale required");
    if (!Set.of("ja-JP", "tr-TR").contains(args[2])
        || !java.util.Locale.getDefault().toLanguageTag().equals(args[2]))
      throw new IllegalArgumentException("dedicated JVM locale does not match fixed case");
    Set<String> allowed =
        Set.of(
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web166SixRequestsMatchIndependentWire",
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web167SixSuccessResponsesDecodeWithoutRetainingSecrets",
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web168ApprovedErrorsNeverExposeSuccessPayload",
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web169MalformedUncorrelatedAndForeignResponsesReject",
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web170InputAndConfigurationFaultsNeverSend",
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web171TransportFailuresDoNotRetryOrLeakPending",
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web172ConcurrentQueriesKeepContextsAndRepliesSeparate",
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#web173ResponseBoundsAndCallerOwnershipRemainExact",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web238AnimationRequests",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web239SuccessProfiles",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web240ErrorProfiles",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web241MalformedReplies",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web242CapabilitiesAndNull",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web243TransportFailures",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web244ConcurrentRequests",
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#web245OwnershipAndDiagnostics",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web254Requests",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web255SuccessProfiles",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web256ErrorProfiles",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web257MalformedReplies",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web258CapabilitiesAndNull",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web259TransportFailures",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web260ConcurrentRequests",
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#web261OwnershipAndDiagnostics");
    Map<String, List<String>> methods = new LinkedHashMap<>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 2 || !allowed.contains(row[0] + "#" + row[1])) {
        throw new IllegalStateException(
            "closed Scenario Animation Music pure wire fixture class and zero-argument method"
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
          "exact Scenario Animation Music pure wire fixture inventory required");
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
                    outcome.getThrowable().map(t -> t.getClass().getName()).orElse(""),
                    outcome
                        .getThrowable()
                        .flatMap(
                            t ->
                                java.util.Arrays.stream(t.getStackTrace())
                                    .filter(f -> f.getClassName().equals(source.getClassName()))
                                    .map(f -> f.getFileName() + ":" + f.getLineNumber())
                                    .findFirst())
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
            xml.writeAttribute("testSourceLocation", row.testSourceLocation());
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
          "exact Scenario Animation Music pure wire fixture run not successful");
  }
}
