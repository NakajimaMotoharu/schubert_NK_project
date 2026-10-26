import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.HashSet;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Complete Protocol artifact counters from one existing locale exec; never load target classes. */
public final class ProtocolLocaleCoverageDiagnostic {
  private ProtocolLocaleCoverageDiagnostic() {}

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
    if (args.length != 4 || !Set.of("PG10740-PROTOCOL-JP", "PG10740-PROTOCOL-TR").contains(args[3]))
      throw new IllegalArgumentException(
          "one fixed locale exec, complete Main root/catalog/session required");
    var expected = new HashSet<String>();
    for (String entry : Files.readAllLines(Path.of(args[2]))) {
      if (!entry.startsWith("dev/codex/schubert/nk/protocol/")
          || !entry.endsWith(".class")
          || entry.contains("..")
          || !expected.add(entry.substring(0, entry.length() - 6)))
        throw new IllegalArgumentException("unique complete Protocol class inventory required");
    }
    if (expected.size() <= 150) throw new IllegalArgumentException("complete artifact required");
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
          && !name.startsWith("dev/codex/schubert/nk/protocol/"))
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
    }
    if (forbidden != 0) throw new IllegalStateException("non-Protocol Product probe hit");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    System.out.println("PHYSICAL_COUNT\\t" + expected.size());
    System.out.println("ANALYZED_COUNT\\t" + builder.getClasses().size());
    System.out.println("NO_MATCH_COUNT\\t" + builder.getNoMatchClasses().size());
    var reported = new HashSet<String>();
    for (var value : builder.getClasses()) reported.add(value.getName());
    for (String missing : expected.stream().filter(n -> !reported.contains(n)).sorted().toList())
      System.out.println("UNREPORTED\\t" + missing);
    for (var value : builder.getNoMatchClasses())
      System.out.println("CRC_MISMATCH\\t" + value.getName());
    if (builder.getClasses().size() != expected.size() || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("Main artifact/CRC mismatch");
    var session = sessions.getFirst();
    System.out.println(
        "SESSION\t"
            + session.getId()
            + "\t"
            + session.getStartTimeStamp()
            + "\t"
            + session.getDumpTimeStamp());
    System.out.println("FORBIDDEN_PROBE_HITS\t" + forbidden);
    for (var type :
        builder.getClasses().stream().sorted(Comparator.comparing(t -> t.getName())).toList()) {
      if (!expected.contains(type.getName()))
        throw new IllegalStateException("unlisted Main counter");
      System.out.println(
          "CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
      counters(type);
    }
    System.out.println("BUNDLE\tCOMPLETE_PROTOCOL_ARTIFACT");
    counters(builder.getBundle("complete-protocol-artifact"));
  }
}
