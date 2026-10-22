import java.io.File;
import java.util.Comparator;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICounter;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Independent read-only CRC/session/counter join of one completed host run. */
public final class CommonHarnessCoverageAudit {
  private CommonHarnessCoverageAudit() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and original classes required");
    ExecFileLoader loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    if (loader.getSessionInfoStore().getInfos().size() != 1) {
      throw new IllegalStateException("exactly one original session, no cross-run union");
    }
    CoverageBuilder builder = new CoverageBuilder();
    new Analyzer(loader.getExecutionDataStore(), builder).analyzeAll(new File(args[1]));
    if (!builder.getNoMatchClasses().isEmpty()) {
      throw new IllegalStateException("original execution and physical CRC mismatch");
    }
    if (builder.getClasses().size() != 8) throw new IllegalStateException("exact eight physical Main");
    for (var type : builder.getClasses().stream()
        .sorted(Comparator.comparing(ICoverageNode::getName)).toList()) {
      if (loader.getExecutionDataStore().get(type.getId()) == null) {
        throw new IllegalStateException("every physical Main has exact original execution data");
      }
      StringBuilder row = new StringBuilder("CLASS\t").append(type.getName())
          .append('\t').append(Long.toUnsignedString(type.getId(), 16));
      for (var kind : new ICoverageNode.CounterEntity[] {
        ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
        ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
      }) {
        ICounter counter = type.getCounter(kind);
        if (counter.getMissedCount() != 0) throw new IllegalStateException("actual missed counter");
        if (kind != ICoverageNode.CounterEntity.BRANCH && counter.getCoveredCount() <= 0) {
          throw new IllegalStateException("real executable class, no vacuous 100");
        }
        row.append('\t').append(kind).append(':').append(counter.getMissedCount())
            .append(':').append(counter.getCoveredCount());
      }
      System.out.println(row);
    }
    var session = loader.getSessionInfoStore().getInfos().getFirst();
    System.out.println("SESSION\t" + session.getStartTimeStamp() + "\t" + session.getDumpTimeStamp());
    System.out.println("RESULT\t8\t0\t1");
  }
}
