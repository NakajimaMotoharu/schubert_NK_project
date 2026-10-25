import java.nio.file.Path;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Whole physical source unit and this one genuine session only; misses are not hidden. */
public final class WebCloseHandoffCoverageMeasure {
  private WebCloseHandoffCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("exec and the complete Web class required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG9580-WEB-CLOSE-HANDOFF"))
      throw new IllegalStateException("one genuine selected session required");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(Path.of(args[1]).toFile());
    if (!builder.getClasses().stream()
            .map(type -> type.getName())
            .collect(java.util.stream.Collectors.toSet())
            .equals(Set.of("dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime"))
        || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("whole physical class and exact CRC required");
    var type = builder.getClasses().iterator().next();
    if (exec.getExecutionDataStore().get(type.getId()) == null)
      throw new IllegalStateException("actual current class record required");
    System.out.println("CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
    for (var kind :
        new ICoverageNode.CounterEntity[] {
          ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
          ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
        }) {
      var counter = type.getCounter(kind);
      System.out.println(
          "COUNTER\t" + kind + "\t" + counter.getMissedCount() + "\t" + counter.getCoveredCount());
    }
  }
}
