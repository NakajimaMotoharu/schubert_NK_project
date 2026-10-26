import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Read the existing ten-method exec and five complete Main classes; never load targets. */
public final class TraceFallbackCoverageMeasure {
  private TraceFallbackCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("exec and closed Main directory required");
    var expected =
        Set.of(
            "dev/codex/schubert/nk/web/logging/WebRequestTrace",
            "dev/codex/schubert/nk/web/logging/WebRequestTrace$Scope",
            "dev/codex/schubert/nk/web/security/WebRequestContext",
            "dev/codex/schubert/nk/web/logging/WebRequestRouteInterceptor",
            "dev/codex/schubert/nk/web/config/RequestLogMvcConfiguration");
    Path root = Path.of(args[1]);
    try (var paths = Files.walk(root)) {
      var files = paths.filter(p -> p.toString().endsWith(".class")).toList();
      if (files.size() != expected.size())
        throw new IllegalStateException("five complete classes required");
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
                .equals(source)) throw new IllegalStateException("Main source/identity mismatch");
      }
    }
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG10542-TRACE-FALLBACK"))
      throw new IllegalStateException("single current trace session required");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents()) {
      String name = value.getName();
      if (name.startsWith("dev/codex/schubert/nk/api/")
          || name.startsWith("dev/codex/schubert/nk/batch/")
          || name.startsWith("dev/codex/schubert/nk/bootstrap/")
          || name.startsWith("dev/codex/schubert/nk/storage/")
          || name.startsWith("dev/codex/schubert/nk/web/bootstrap/")
          || name.startsWith("dev/codex/schubert/nk/web/transport/")
          || name.startsWith("dev/codex/schubert/nk/web/session/JdbcWebSessionStore"))
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
    }
    if (forbidden != 0) throw new IllegalStateException("unselected/held product execution");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    if (builder.getClasses().size() != expected.size() || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("Main class CRC mismatch");
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
      if (!expected.contains(type.getName())
          || exec.getExecutionDataStore().get(type.getId()) == null)
        throw new IllegalStateException("missing Main execution");
      System.out.println(
          "CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
      for (var kind :
          new ICoverageNode.CounterEntity[] {
            ICoverageNode.CounterEntity.LINE,
            ICoverageNode.CounterEntity.METHOD,
            ICoverageNode.CounterEntity.CLASS,
            ICoverageNode.CounterEntity.BRANCH
          }) {
        var count = type.getCounter(kind);
        System.out.println(
            "COUNTER\t"
                + kind.name()
                + "\t"
                + count.getMissedCount()
                + "\t"
                + count.getCoveredCount());
      }
    }
  }
}
