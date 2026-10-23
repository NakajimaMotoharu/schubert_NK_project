import java.io.File;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Set;
import java.util.TreeSet;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICounter;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Read original single-session exec and every class of one explicitly inventoried component. */
public final class ComponentCoverageAudit {
  private ComponentCoverageAudit() {}

  public static void main(String[] args) throws Exception {
    if (args.length < 3) throw new IllegalArgumentException("exec, class directory and exact names");
    Set<String> expected = new TreeSet<>(Arrays.asList(args).subList(2, args.length));
    if (expected.size() != args.length - 2) throw new IllegalArgumentException("duplicate expected class");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    if (loader.getSessionInfoStore().getInfos().size() != 1)
      throw new IllegalStateException("one genuine session, never union");
    var builder = new CoverageBuilder();
    new Analyzer(loader.getExecutionDataStore(), builder).analyzeAll(new File(args[1]));
    if (!builder.getNoMatchClasses().isEmpty()) throw new IllegalStateException("CRC mismatch");
    var actual = new TreeSet<String>();
    for (var type : builder.getClasses().stream()
        .sorted(Comparator.comparing(ICoverageNode::getName)).toList()) {
      if (type.getClassCounter().getTotalCount() == 0) {
        if (!type.getName().endsWith("/package-info"))
          throw new IllegalStateException("unknown zero-counter class");
        System.out.println("METADATA\t" + type.getName());
        continue;
      }
      actual.add(type.getName());
      if (loader.getExecutionDataStore().get(type.getId()) == null)
        throw new IllegalStateException("missing exact executed class");
      var row = new StringBuilder("CLASS\t").append(type.getName())
          .append('\t').append(Long.toUnsignedString(type.getId(), 16));
      for (var kind : new ICoverageNode.CounterEntity[] {
        ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
        ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
      }) {
        ICounter counter = type.getCounter(kind);
        if (counter.getMissedCount() != 0) throw new IllegalStateException("missed " + kind);
        if (kind != ICoverageNode.CounterEntity.BRANCH && counter.getCoveredCount() <= 0)
          throw new IllegalStateException("vacuous executable counter");
        row.append('\t').append(kind).append(':').append(counter.getMissedCount())
            .append(':').append(counter.getCoveredCount());
      }
      System.out.println(row);
    }
    if (!actual.equals(expected)) throw new IllegalStateException("exact executable inventory");
    var session = loader.getSessionInfoStore().getInfos().getFirst();
    System.out.println("SESSION\t" + session.getStartTimeStamp() + "\t" + session.getDumpTimeStamp());
    System.out.println("RESULT\t" + actual.size() + "\t0\t1");
  }
}
