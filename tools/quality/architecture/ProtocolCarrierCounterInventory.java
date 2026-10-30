import java.io.File;
import java.util.Arrays;
import java.util.Comparator;
import java.util.TreeSet;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Passive classfile inventory only; never loads Product classes or labels zero counters PASS. */
public final class ProtocolCarrierCounterInventory {
  private ProtocolCarrierCounterInventory() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 13) throw new IllegalArgumentException("exec, directory and exact11 names");
    var expected = new TreeSet<>(Arrays.asList(args).subList(2, args.length));
    if (expected.size() != 11) throw new IllegalArgumentException("eleven distinct class names");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    if (loader.getSessionInfoStore().getInfos().size() != 1)
      throw new IllegalStateException("one existing session, no exec union");
    var builder = new CoverageBuilder();
    new Analyzer(loader.getExecutionDataStore(), builder).analyzeAll(new File(args[1]));
    if (!builder.getNoMatchClasses().isEmpty()) throw new IllegalStateException("CRC mismatch");
    var actual = new TreeSet<String>();
    for (var type : builder.getClasses().stream()
        .sorted(Comparator.comparing(ICoverageNode::getName)).toList()) {
      if (!actual.add(type.getName())) throw new IllegalStateException("duplicate class");
      boolean probePresent = loader.getExecutionDataStore().get(type.getId()) != null;
      if (type.getClassCounter().getTotalCount() > 0 && !probePresent)
        throw new IllegalStateException("missing exact executed class");
      var row = new StringBuilder("INVENTORY\t").append(type.getName())
          .append('\t').append(Long.toUnsignedString(type.getId(), 16))
          .append('\t').append(probePresent);
      for (var kind : new ICoverageNode.CounterEntity[] {
        ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
        ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
      }) {
        var counter = type.getCounter(kind);
        row.append('\t').append(kind).append(':').append(counter.getMissedCount())
            .append(':').append(counter.getCoveredCount());
      }
      if (type.getClassCounter().getTotalCount() == 0
          && (type.getInstructionCounter().getTotalCount() != 0
              || type.getMethodCounter().getTotalCount() != 0
              || type.getLineCounter().getTotalCount() != 0
              || type.getBranchCounter().getTotalCount() != 0))
        throw new IllegalStateException("inconsistent zero-class counters");
      System.out.println(row);
    }
    if (!actual.equals(expected)) throw new IllegalStateException("exact eleven-class inventory");
    System.out.println("INVENTORY_RESULT\t11\t0\t1");
  }
}
