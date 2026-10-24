import java.nio.file.Path;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Measures the entire actual class, including missed Root/TLS code; never an acceptance gate. */
public final class CaddyConfigurationCoverageMeasure {
  private CaddyConfigurationCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and exact class file required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG9016-CADDY-FORMAT"))
      throw new IllegalStateException("one genuine current session required");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(Path.of(args[1]).toFile());
    if (builder.getClasses().size() != 1 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("exact physical class and CRC required");
    var type = builder.getClasses().iterator().next();
    if (!type.getName().equals("dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration")
        || exec.getExecutionDataStore().get(type.getId()) == null)
      throw new IllegalStateException("actual instrumented configuration class required");
    System.out.println("CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
    for (var kind :
        new ICoverageNode.CounterEntity[] {
          ICoverageNode.CounterEntity.LINE,
          ICoverageNode.CounterEntity.METHOD,
          ICoverageNode.CounterEntity.CLASS,
          ICoverageNode.CounterEntity.BRANCH
        }) {
      var counter = type.getCounter(kind);
      System.out.println(
          "COUNTER\t" + kind + "\t" + counter.getMissedCount() + "\t" + counter.getCoveredCount());
    }
    System.out.println(
        "SESSION\t"
            + sessions.getFirst().getStartTimeStamp()
            + "\t"
            + sessions.getFirst().getDumpTimeStamp());
    System.out.println("MEASUREMENT_ONLY\tWHOLE_CLASS_AND_451_NOT_ACCEPTED");
  }
}
