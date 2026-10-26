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

/** Read the existing 14-method exec and fourteen complete Main classes; never load targets. */
public final class PublicTemplate14CoverageMeasure {
  private PublicTemplate14CoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("exec and closed Main directory required");
    String prefix = "dev/codex/schubert/nk/web/";
    var expected =
        Set.of(
            prefix + "view/AnimationMenuViewModel",
            prefix + "view/AnimationListViewModel",
            prefix + "view/AnimationListViewModel$Video",
            prefix + "view/AnimationListViewModel$Row",
            prefix + "view/MusicCategoryViewModel",
            prefix + "view/MusicCategoryViewModel$Card",
            prefix + "view/MusicSectionViewModel",
            prefix + "view/MusicSectionViewModel$Card",
            prefix + "view/TopBarViewModel",
            prefix + "config/WebMvcConfiguration",
            prefix + "controller/ErrorController",
            prefix + "controller/MenuController",
            prefix + "controller/LoginController",
            prefix + "error/ProblemViewFactory");
    Path root = Path.of(args[1]);
    try (var paths = Files.walk(root)) {
      var files = paths.filter(p -> p.toString().endsWith(".class")).toList();
      if (files.size() != expected.size())
        throw new IllegalStateException("fourteen complete classes required");
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
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG10488-PUBLIC-TEMPLATE14"))
      throw new IllegalStateException("single current public-template session required");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents()) {
      String name = value.getName();
      if (name.startsWith("dev/codex/schubert/nk/api/")
          || name.startsWith("dev/codex/schubert/nk/batch/")
          || name.startsWith("dev/codex/schubert/nk/bootstrap/")
          || name.startsWith("dev/codex/schubert/nk/storage/")
          || name.startsWith("dev/codex/schubert/nk/web/bootstrap/")
          || name.startsWith("dev/codex/schubert/nk/web/logging/")
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
