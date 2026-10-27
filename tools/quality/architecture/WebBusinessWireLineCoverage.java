import java.nio.file.Files;
import java.nio.file.Path;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.tools.ExecFileLoader;

/** Analyze one frozen exec and Main bytes; never define or invoke the target class. */
public final class WebBusinessWireLineCoverage {
  private WebBusinessWireLineCoverage() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("frozen exec and class bytes required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG11986-BUSWIRE-JP"))
      throw new IllegalStateException("original session required");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder)
        .analyzeClass(Files.readAllBytes(Path.of(args[1])), "ProtectedReadWireClient.class");
    if (builder.getClasses().size() != 1 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("one matched class required");
    var target = builder.getClasses().iterator().next();
    if (!target.getName().equals("dev/codex/schubert/nk/web/messaging/ProtectedReadWireClient")
        || !Long.toUnsignedString(target.getId(), 16).equals("e636b8ce74dc37cb"))
      throw new IllegalStateException("frozen identity required");
    System.out.println("ORIGINAL_SESSION	" + sessions.getFirst().getId());
    for (var method : target.getMethods()) {
      if (method.getInstructionCounter().getMissedCount() > 0
          || method.getBranchCounter().getMissedCount() > 0)
        System.out.println(
            "METHOD	"
                + method.getName()
                + "	"
                + method.getDesc()
                + "	"
                + method.getInstructionCounter().getMissedCount()
                + "	"
                + method.getBranchCounter().getMissedCount());
    }
    for (int n = target.getFirstLine(); n <= target.getLastLine(); n++) {
      var line = target.getLine(n);
      if (line.getInstructionCounter().getMissedCount() > 0
          || line.getBranchCounter().getMissedCount() > 0)
        System.out.println(
            "LINE	"
                + n
                + "	"
                + line.getInstructionCounter().getMissedCount()
                + "	"
                + line.getInstructionCounter().getCoveredCount()
                + "	"
                + line.getBranchCounter().getMissedCount()
                + "	"
                + line.getBranchCounter().getCoveredCount());
    }
  }
}
