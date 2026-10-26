import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.Map;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Read one existing exec; never load target classes or invoke repository code. */
public final class ScenarioMediaBoundaryCoverageMeasure {
  private ScenarioMediaBoundaryCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3) throw new IllegalArgumentException("exec, Main directory, Test directory");
    String prefix = "dev/codex/schubert/nk/api/persistence/";
    var expected = Map.of(
        prefix + "ScenarioRepository", "ScenarioRepository.java",
        prefix + "ScenarioRepository$RowMapper", "ScenarioRepository.java",
        prefix + "MediaRepository", "MediaRepository.java",
        prefix + "MediaRepository$RowMapper", "MediaRepository.java");
    var root = Path.of(args[1]);
    try (var paths = Files.walk(root)) {
      var files = paths.filter(p -> p.toString().endsWith(".class")).toList();
      if (files.size() != expected.size()) throw new IllegalStateException("complete four physical Main");
      for (var file : files) {
        var model = ClassFile.of().parse(Files.readAllBytes(file));
        String name = model.thisClass().asInternalName();
        if (!expected.containsKey(name) || !file.equals(root.resolve(name + ".class"))
            || !model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile()
                .stringValue().equals(expected.get(name)))
          throw new IllegalStateException("source/identity mismatch");
        if (name.endsWith("$RowMapper") && (!model.flags().has(java.lang.reflect.AccessFlag.INTERFACE)
            || model.methods().stream().anyMatch(m -> m.code().isPresent())))
          throw new IllegalStateException("no-Code interface required");
      }
    }
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG10264-SCENARIO-MEDIA-BOUNDARY"))
      throw new IllegalStateException("one original session only");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents()) {
      String name = value.getName();
      if (name.startsWith("dev/codex/schubert/nk/api/error/TemporaryInfrastructureException")
          || name.startsWith("dev/codex/schubert/nk/web/")
          || name.startsWith("dev/codex/schubert/nk/batch/")
          || name.startsWith("dev/codex/schubert/nk/bootstrap/")
          || name.startsWith("dev/codex/schubert/nk/storage/")
          || name.startsWith("dev/codex/schubert/nk/api/idempotency/")) {
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
      }
    }
    if (forbidden != 0) throw new IllegalStateException("held product probe hit");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    if (builder.getClasses().size() != expected.size() || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("Main CRC mismatch");
    var sqlMethods = Map.of(
        prefix + "ScenarioRepository", Set.of("requireReadTransaction", "bind", "searchRecord", "number", "integer", "required", "title", "entryType", "game"),
        prefix + "MediaRepository", Set.of("descriptor", "text", "number", "integer", "bounded", "pairRole"));
    var session = sessions.getFirst();
    System.out.println("SESSION\t" + session.getId() + "\t" + session.getStartTimeStamp() + "\t" + session.getDumpTimeStamp());
    System.out.println("FORBIDDEN_PROBE_HITS\t" + forbidden);
    for (var type : builder.getClasses().stream().sorted(Comparator.comparing(t -> t.getName())).toList()) {
      if (!expected.containsKey(type.getName()) || (!type.getName().endsWith("$RowMapper")
          && exec.getExecutionDataStore().get(type.getId()) == null))
        throw new IllegalStateException("missing Main execution");
      for (var method : type.getMethods()) {
        if (sqlMethods.getOrDefault(type.getName(), Set.of()).contains(method.getName())
            && method.getInstructionCounter().getCoveredCount() != 0)
          throw new IllegalStateException("SQL helper unexpectedly executed: " + type.getName() + "/" + method.getName());
      }
      System.out.println("CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(),16));
      for (var kind : new ICoverageNode.CounterEntity[] { ICoverageNode.CounterEntity.LINE,
          ICoverageNode.CounterEntity.METHOD, ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH }) {
        var c = type.getCounter(kind);
        System.out.println("COUNTER\t" + kind.name() + "\t" + c.getMissedCount() + "\t" + c.getCoveredCount());
      }
    }
    int guards = 0;
    for (String test : Set.of("ScenarioPreSqlBoundaryTest", "MediaPreSqlBoundaryTest")) {
      var fixture = new CoverageBuilder();
      byte[] raw = Files.readAllBytes(Path.of(args[2]).resolve(prefix + test + "$NoSql.class"));
      new Analyzer(exec.getExecutionDataStore(),fixture).analyzeClass(raw,test);
      if (fixture.getClasses().size() != 1 || !fixture.getNoMatchClasses().isEmpty())
        throw new IllegalStateException("fixture CRC mismatch");
      var type = fixture.getClasses().iterator().next();
      if (exec.getExecutionDataStore().get(type.getId()) == null) throw new IllegalStateException("fixture missing");
      for (var method : type.getMethods()) {
        if (method.getName().startsWith("lambda$port$")) {
          if (method.getInstructionCounter().getCoveredCount() != 0) throw new IllegalStateException("JDBC guard called");
          guards++;
        }
      }
    }
    if (guards != 2) throw new IllegalStateException("two JDBC guards required");
    System.out.println("SQL_HELPER_HITS\t0");
    System.out.println("JDBC_GUARD_HITS\t0\t" + guards);
  }
}
