import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.HashSet;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/**
 * Complete fixed API or Web artifact counters from the same one-session exec; no target class
 * loading.
 */
public final class MetricContextOwnedArtifactCoverageMeasure {
  private MetricContextOwnedArtifactCoverageMeasure() {}

  private static void counters(ICoverageNode node) {
    for (var kind :
        new ICoverageNode.CounterEntity[] {
          ICoverageNode.CounterEntity.LINE,
          ICoverageNode.CounterEntity.METHOD,
          ICoverageNode.CounterEntity.CLASS,
          ICoverageNode.CounterEntity.BRANCH
        }) {
      var count = node.getCounter(kind);
      System.out.println(
          "COUNTER\t"
              + kind.name()
              + "\t"
              + count.getMissedCount()
              + "\t"
              + count.getCoveredCount());
    }
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 5 || !args[3].matches("PG[1-9][0-9]{3,}-METRICCTX-JP"))
      throw new IllegalArgumentException(
          "one fixed locale exec, complete Main root/catalog/session required");
    if (!java.util.Set.of("api", "web", "batch", "protocol", "storage", "bootstrap").contains(args[4]))
      throw new IllegalArgumentException("fixed artifact role required");
    String prefix = "dev/codex/schubert/nk/";
    var expected = new HashSet<String>();
    for (String entry : Files.readAllLines(Path.of(args[2]))) {
      if (!entry.startsWith(prefix)
          || !entry.endsWith(".class")
          || entry.contains("..")
          || !expected.add(entry.substring(0, entry.length() - 6)))
        throw new IllegalArgumentException("unique complete Web class inventory required");
    }
    if (expected.size() != java.util.Map.of("api", 467, "web", 358, "batch", 645, "protocol", 176, "storage", 80, "bootstrap", 117).get(args[4])) throw new IllegalArgumentException("complete physical artifact required");
    Path root = Path.of(args[1]);
    try (var paths = Files.walk(root)) {
      var files = paths.filter(p -> p.toString().endsWith(".class")).toList();
      if (files.size() != expected.size()) throw new IllegalStateException("incomplete Main files");
      for (var file : files) {
        var model = ClassFile.of().parse(Files.readAllBytes(file));
        String name = model.thisClass().asInternalName();
        String source = name.substring(name.lastIndexOf('/') + 1).split("\\$", -1)[0] + ".java";
        if (!expected.contains(name)
            || !file.equals(root.resolve(name + ".class"))
            || !model
                .findAttribute(Attributes.sourceFile())
                .orElseThrow()
                .sourceFile()
                .stringValue()
                .equals(source)) throw new IllegalStateException("Main identity/source mismatch");
      }
    }
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals(args[3]))
      throw new IllegalStateException("single fresh same-locale session required");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents()) {
      String name = value.getName();
      if (name.startsWith("dev/codex/schubert/nk/")
          && java.util.Set.of(
                  "dev/codex/schubert/nk/api/monitoring/ApiCustomMetricPayload",
                  "dev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporter",
                  "dev/codex/schubert/nk/api/monitoring/ApiGcMetricRegistration",
                  "dev/codex/schubert/nk/api/monitoring/ApiJvmMetrics",
                  "dev/codex/schubert/nk/api/monitoring/ApiMetricCatalog",
                  "dev/codex/schubert/nk/api/monitoring/ApiMetricContext",
                  "dev/codex/schubert/nk/api/monitoring/ApiMetricContextTest",
                  "dev/codex/schubert/nk/api/monitoring/ApiMetricScrape",
                  "dev/codex/schubert/nk/api/monitoring/ApiScalarMetricExporter",
                  "dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSource",
                  "dev/codex/schubert/nk/api/monitoring/ApiStandardMetrics",
                  "dev/codex/schubert/nk/api/monitoring/ApiSystemMetrics",
                  "dev/codex/schubert/nk/api/monitoring/ExactDurationMeterRegistry",
                  "dev/codex/schubert/nk/api/monitoring/ExactDurationSupport",
                  "dev/codex/schubert/nk/protocol/header/InteractionKind",
                  "dev/codex/schubert/nk/protocol/header/MessageKind",
                  "dev/codex/schubert/nk/protocol/header/ResultCode",
                  "dev/codex/schubert/nk/protocol/layout/LayoutDefinition",
                  "dev/codex/schubert/nk/protocol/layout/LayoutId",
                  "dev/codex/schubert/nk/protocol/layout/LayoutRegistry",
                  "dev/codex/schubert/nk/protocol/layout/LayoutValidationException",
                  "dev/codex/schubert/nk/protocol/layout/UnsupportedLayoutException",
                  "dev/codex/schubert/nk/protocol/transport/BrokerTopology",
                  "dev/codex/schubert/nk/web/monitoring/HttpMetricContract",
                  "dev/codex/schubert/nk/web/monitoring/OverflowSafeDurationSupport",
                  "dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry",
                  "dev/codex/schubert/nk/web/monitoring/WebCounterMetricExporter",
                  "dev/codex/schubert/nk/web/monitoring/WebCustomMetricPayload",
                  "dev/codex/schubert/nk/web/monitoring/WebDurationMetricExporter",
                  "dev/codex/schubert/nk/web/monitoring/WebGaugeMetricExporter",
                  "dev/codex/schubert/nk/web/monitoring/WebGcMetricRegistration",
                  "dev/codex/schubert/nk/web/monitoring/WebJvmMetrics",
                  "dev/codex/schubert/nk/web/monitoring/WebMetricCatalog",
                  "dev/codex/schubert/nk/web/monitoring/WebMetricContext",
                  "dev/codex/schubert/nk/web/monitoring/WebMetricContextTest",
                  "dev/codex/schubert/nk/web/monitoring/WebMetricScrape",
                  "dev/codex/schubert/nk/web/monitoring/WebMetricText",
                  "dev/codex/schubert/nk/web/monitoring/WebStandardMetricSource",
                  "dev/codex/schubert/nk/web/monitoring/WebStandardMetrics",
                  "dev/codex/schubert/nk/web/monitoring/WebSystemMetrics")
              .stream()
              .noneMatch(rootName -> name.equals(rootName) || name.startsWith(rootName + "$")))
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
    }
    if (forbidden != 0)
      throw new IllegalStateException("outside-reviewed-pool-capacity-value Product probe hit");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    if (!builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("Main CRC mismatch");
    var reported = new HashSet<String>();
    for (var type : builder.getClasses()) reported.add(type.getName());
    var packageMetadata = expected.stream().filter(n -> !reported.contains(n)).sorted().toList();
    for (String name : packageMetadata) {
      var model = ClassFile.of().parse(Files.readAllBytes(root.resolve(name + ".class")));
      if (!name.endsWith("/package-info")
          || !model.fields().isEmpty()
          || !model.methods().isEmpty()
          || !model
              .findAttribute(Attributes.sourceFile())
              .orElseThrow()
              .sourceFile()
              .stringValue()
              .equals("package-info.java"))
        throw new IllegalStateException("unreported executable or unknown class");
    }
    if (reported.size() + packageMetadata.size() != expected.size())
      throw new IllegalStateException("all physical artifact classes must be accounted for");
    var session = sessions.getFirst();
    System.out.println(
        "SESSION\t"
            + session.getId()
            + "\t"
            + session.getStartTimeStamp()
            + "\t"
            + session.getDumpTimeStamp());
    System.out.println("FORBIDDEN_PROBE_HITS\t" + forbidden);
    for (String name : packageMetadata) System.out.println("PACKAGE_METADATA_ONLY\t" + name);
    for (var type :
        builder.getClasses().stream().sorted(Comparator.comparing(t -> t.getName())).toList()) {
      if (!expected.contains(type.getName()))
        throw new IllegalStateException("unlisted Main counter");
      System.out.println(
          "CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
      counters(type);
    }
    System.out.println(
        "BUNDLE\tCOMPLETE_" + args[4].toUpperCase(java.util.Locale.ROOT) + "_ARTIFACT");
    counters(builder.getBundle("complete-" + args[4] + "-artifact"));
  }
}
