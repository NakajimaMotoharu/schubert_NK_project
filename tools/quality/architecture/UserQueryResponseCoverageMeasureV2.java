import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/**
 * Exact complete User query class; reads one new execution stream, never target class initialization.
 */
public final class UserQueryResponseCoverageMeasureV2 {
  private UserQueryResponseCoverageMeasureV2() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and exact class directory");
    String name = "dev/codex/schubert/nk/api/application/admin/UserQueryRequest";
    var root = Path.of(args[1]);
    try (var files = Files.walk(root)) {
      var classes = files.filter(p -> p.toString().endsWith(".class")).toList();
      if (classes.size() != 1 || !classes.getFirst().equals(root.resolve(name + ".class")))
        throw new IllegalStateException("whole source unit, no nested or missing class");
    }
    var model = ClassFile.of().parse(Files.readAllBytes(root.resolve(name + ".class")));
    if (!model.thisClass().asInternalName().equals(name)
        || !model
            .findAttribute(Attributes.sourceFile())
            .orElseThrow()
            .sourceFile()
            .stringValue()
            .equals("UserQueryRequest.java"))
      throw new IllegalStateException("literal class and source identity");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG9936-USER-QUERY-RESPONSE"))
      throw new IllegalStateException("one actual matching session");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    if (builder.getClasses().size() != 1 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("complete single unit/CRC required");
    var type = builder.getClasses().iterator().next();
    if (!type.getName().equals(name) || exec.getExecutionDataStore().get(type.getId()) == null)
      throw new IllegalStateException("actual execution class/CRC required");
    var session = sessions.getFirst();
    System.out.println(
        "SESSION\t"
            + session.getId()
            + "\t"
            + session.getStartTimeStamp()
            + "\t"
            + session.getDumpTimeStamp());
    System.out.println("CLASS\t" + name + "\t" + Long.toUnsignedString(type.getId(), 16));
    for (var kind :
        new ICoverageNode.CounterEntity[] {
          ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
          ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
        }) {
      var counter = type.getCounter(kind);
      System.out.println(
          "COUNTER\t"
              + kind.name()
              + "\t"
              + counter.getMissedCount()
              + "\t"
              + counter.getCoveredCount());
    }
    var methods =
        type.getMethods().stream().filter(m -> m.getName().equals("validateResponse")).toList();
    if (methods.size() != 1) throw new IllegalStateException("exact response validation method");
    var method = methods.getFirst();
    System.out.println("METHOD\t" + method.getName() + "\t" + method.getDesc());
    for (var kind :
        new ICoverageNode.CounterEntity[] {
          ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
          ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
        }) {
      var counter = method.getCounter(kind);
      System.out.println(
          "METHOD_COUNTER\t"
              + kind.name()
              + "\t"
              + counter.getMissedCount()
              + "\t"
              + counter.getCoveredCount());
    }
  }
}
