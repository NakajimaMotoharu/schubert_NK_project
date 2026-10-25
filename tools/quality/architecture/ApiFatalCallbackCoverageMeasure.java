import java.nio.file.Path;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Measures the entire actual class, including missed Root/TLS code; never an acceptance gate. */
public final class ApiFatalCallbackCoverageMeasure {
  private ApiFatalCallbackCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException("exec and both exact Life class files required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG9272-API-FATAL-CALLBACK"))
      throw new IllegalStateException("one genuine current session required");
    var builder = new CoverageBuilder();
    var analyzer = new Analyzer(exec.getExecutionDataStore(), builder);
    analyzer.analyzeAll(Path.of(args[1]).toFile());
    analyzer.analyzeAll(Path.of(args[2]).toFile());
    if (builder.getClasses().size() != 2 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("exact physical class and CRC required");
    var names =
        java.util.Set.of(
            "dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime",
            "dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime$1");
    if (!builder.getClasses().stream()
        .map(type -> type.getName())
        .collect(java.util.stream.Collectors.toSet())
        .equals(names)) throw new IllegalStateException("whole current source unit required");
    for (var type : builder.getClasses()) {
      boolean observed = exec.getExecutionDataStore().get(type.getId()) != null;
      if (type.getName().endsWith("/ApiProcessLifetime") && !observed)
        throw new IllegalStateException("current outer instrumentation required");
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
        var counter = type.getCounter(kind);
        System.out.println(
            "COUNTER\t"
                + type.getName()
                + "\t"
                + kind
                + "\t"
                + counter.getMissedCount()
                + "\t"
                + counter.getCoveredCount());
      }
    }
    System.out.println(
        "SESSION\t"
            + sessions.getFirst().getStartTimeStamp()
            + "\t"
            + sessions.getFirst().getDumpTimeStamp());
    System.out.println("MEASUREMENT_ONLY\tWHOLE_CLASS_AND_451_NOT_ACCEPTED");
  }
}
