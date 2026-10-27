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
 * Complete fixed Storage or Batch artifact counters from the same one-session exec; no target class
 * loading.
 */
public final class PureResourceProfileArtifactCoverageMeasure {
  private PureResourceProfileArtifactCoverageMeasure() {}

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
    if (args.length != 5 || !args[3].matches("PG[1-9][0-9]{3,}-PURERESOURCEPROFILE-JP"))
      throw new IllegalArgumentException(
          "one fixed locale exec, complete Main root/catalog/session required");
    if (!java.util.Set.of("batch", "bootstrap", "storage").contains(args[4]))
      throw new IllegalArgumentException("fixed artifact role required");
    String prefix = "dev/codex/schubert/nk/";
    var expected = new HashSet<String>();
    for (String entry : Files.readAllLines(Path.of(args[2]))) {
      if (!entry.startsWith(prefix)
          || !entry.endsWith(".class")
          || entry.contains("..")
          || !expected.add(entry.substring(0, entry.length() - 6)))
        throw new IllegalArgumentException("unique complete artifact class inventory required");
    }
    if (expected.size()
        != (args[4].equals("storage") ? 80 : args[4].equals("bootstrap") ? 117 : 645))
      throw new IllegalArgumentException("complete artifact required");
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
          && !java.util.Set.of(
                  "dev/codex/schubert/nk/storage/ResourceScope",
                  "dev/codex/schubert/nk/storage/ResourceScope$Action",
                  "dev/codex/schubert/nk/storage/ResourceScope$Acquire",
                  "dev/codex/schubert/nk/storage/ResourceScope$Release",
                  "dev/codex/schubert/nk/storage/ResourceScope$OwnedAction",
                  "dev/codex/schubert/nk/storage/StorageIoException",
                  "dev/codex/schubert/nk/storage/StorageIoException$Reason",
                  "dev/codex/schubert/nk/storage/StorageRootLayout",
                  "dev/codex/schubert/nk/storage/ServiceConfigFiles$Service",
                  "dev/codex/schubert/nk/storage/ServiceConfigFiles$Contents",
                  "dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile",
                  "dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile$Phase",
                  "dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile$TerminalRole",
                  "dev/codex/schubert/nk/batch/file/RootServiceFacts$Facts",
                  "dev/codex/schubert/nk/batch/platform/RootReleaseAdmission$EffectiveConfigurations",
                  "dev/codex/schubert/nk/batch/file/MorningBrokerExecution$Observations",
                  "dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence$Summary",
                  "dev/codex/schubert/nk/batch/mq/ArtemisStartupObservation$Evidence",
                  "dev/codex/schubert/nk/storage/ResourceScopeTest",
                  "dev/codex/schubert/nk/storage/FactoryResourceScopeTest",
                  "dev/codex/schubert/nk/storage/FactoryResourceScopeTest$Token",
                  "dev/codex/schubert/nk/storage/FactoryResourceScopeTest$Harness",
                  "dev/codex/schubert/nk/storage/ExceptionValueContractTest",
                  "dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfileTest",
                  "dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest")
              .contains(name)) for (boolean probe : value.getProbes()) if (probe) forbidden++;
    }
    if (forbidden != 0)
      throw new IllegalStateException(
          "outside-reviewed-pure-resource-profile-value Product probe hit");
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
