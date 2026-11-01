import java.io.File;
import java.nio.file.Files;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.tools.ExecFileLoader;

/** Passive original-helper method coverage only. Never loads or invokes a Product/Test class. */
public final class OriginalHelperLifecycleAbsenceV1 {
  private OriginalHelperLifecycleAbsenceV1() {}
  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and original outer Test class");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    if (loader.getSessionInfoStore().getInfos().size() != 1)
      throw new IllegalStateException("one original session");
    var builder = new CoverageBuilder();
    new Analyzer(loader.getExecutionDataStore(), builder)
        .analyzeClass(Files.readAllBytes(new File(args[1]).toPath()), "original-helper");
    if (builder.getClasses().size() != 1 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("exact original CRC/class");
    var type = builder.getClasses().iterator().next();
    if (!type.getName().equals("dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest"))
      throw new IllegalStateException("fixed helper class");
    var allowed = Set.of("<clinit>", "credential", "proxy");
    boolean before = false;
    boolean after = false;
    for (var method : type.getMethods()) {
      String name = method.getName();
      int covered = method.getInstructionCounter().getCoveredCount();
      if (covered > 0 && !allowed.contains(name) && !name.matches("lambda\\$proxy\\$[0-9]+"))
        throw new IllegalStateException("unselected helper method executed: " + name);
      if (name.equals("database")) before = true;
      if (name.equals("stop")) after = true;
      System.out.println("METHOD\t" + name + "\t" + covered + "\t"
          + method.getInstructionCounter().getMissedCount());
    }
    if (!before || !after) throw new IllegalStateException("actual lifecycle methods present");
    System.out.println("NO_UNSELECTED_METHOD_HITS=true");
  }
}
