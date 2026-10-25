import java.nio.file.Path;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Read the one actual run and entire semantic class; retain every missed counter. */
public final class SemanticBoundaryFixedCoverageMeasure {
  private SemanticBoundaryFixedCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and complete class required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1
        || !sessions.getFirst().getId().equals("PG9696-PROTOCOL-SEMANTIC-FIXED")) {
      throw new IllegalStateException("one actual semantic component session required");
    }
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(Path.of(args[1]).toFile());
    if (!builder.getClasses().stream()
            .map(type -> type.getName())
            .collect(java.util.stream.Collectors.toSet())
            .equals(Set.of("dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator"))
        || !builder.getNoMatchClasses().isEmpty()) {
      throw new IllegalStateException("whole semantic class with exact CRC required");
    }
    var type = builder.getClasses().iterator().next();
    if (exec.getExecutionDataStore().get(type.getId()) == null) {
      throw new IllegalStateException("actual current class execution data required");
    }
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
    for (var method : type.getMethods()) {
      System.out.println(
          "METHOD\t"
              + method.getName()
              + "\t"
              + method.getDesc()
              + "\t"
              + method.getLineCounter().getMissedCount()
              + "\t"
              + method.getLineCounter().getCoveredCount()
              + "\t"
              + method.getBranchCounter().getMissedCount()
              + "\t"
              + method.getBranchCounter().getCoveredCount());
    }
    for (int line = type.getFirstLine(); line <= type.getLastLine(); line++) {
      var value = type.getLine(line);
      if (value.getInstructionCounter().getTotalCount() > 0) {
        System.out.println(
            "LINE\t"
                + line
                + "\t"
                + value.getInstructionCounter().getMissedCount()
                + "\t"
                + value.getInstructionCounter().getCoveredCount()
                + "\t"
                + value.getBranchCounter().getMissedCount()
                + "\t"
                + value.getBranchCounter().getCoveredCount());
      }
    }
  }
}
