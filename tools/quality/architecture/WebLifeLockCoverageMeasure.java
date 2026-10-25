import java.nio.file.Path;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** The whole Web lifetime source unit, including every unexecuted legacy branch. */
public final class WebLifeLockCoverageMeasure {
  private WebLifeLockCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and the one complete Web class file");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1
        || !sessions.getFirst().getId().equals("PG9248-WEB-LIFE-LOCK"))
      throw new IllegalStateException("one genuine current session required");
    var builder = new CoverageBuilder();
    var analyzer = new Analyzer(exec.getExecutionDataStore(), builder);
    for (int i = 1; i < args.length; i++) analyzer.analyzeAll(Path.of(args[i]).toFile());
    var names =
        Set.of(
            "dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime");
    if (!builder.getClasses().stream()
            .map(type -> type.getName())
            .collect(java.util.stream.Collectors.toSet())
            .equals(names)
        || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("all source-unit classes and exact CRC required");
    for (var type : builder.getClasses()) {
      boolean observed = exec.getExecutionDataStore().get(type.getId()) != null;
      if (!observed)
        throw new IllegalStateException("current whole-class instrumentation record required");
      System.out.println(
          "CLASS\t"
              + type.getName()
              + "\t"
              + Long.toUnsignedString(type.getId(), 16)
              + "\t"
              + (observed ? "CURRENT_RECORD" : "UNEXECUTED_NO_RECORD_NOT_QUALIFIED"));
      for (var kind :
          new ICoverageNode.CounterEntity[] {
            ICoverageNode.CounterEntity.LINE,
            ICoverageNode.CounterEntity.METHOD,
            ICoverageNode.CounterEntity.CLASS,
            ICoverageNode.CounterEntity.BRANCH
          }) {
        var value = type.getCounter(kind);
        System.out.println(
            "COUNTER\t"
                + type.getName()
                + "\t"
                + kind
                + "\t"
                + value.getMissedCount()
                + "\t"
                + value.getCoveredCount());
      }
    }
  }
}
