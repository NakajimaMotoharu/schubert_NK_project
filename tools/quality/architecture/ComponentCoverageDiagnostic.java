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

/** Measure original single-session exec without converting missed counters to PASS. */
public final class ComponentCoverageDiagnostic {
  private ComponentCoverageDiagnostic() {}

  public static void main(String[] args) throws Exception {
    if (args.length < 3) throw new IllegalArgumentException("exec, class directory and exact names");
    var declarations = Arrays.asList(args).subList(2, args.length);
    if (new TreeSet<>(declarations).size() != declarations.size())
      throw new IllegalArgumentException("duplicate expected class or metadata");
    Set<String> expected = new TreeSet<>();
    Set<String> expectedMetadata = new TreeSet<>();
    for (String declaration : declarations) {
      if (declaration.startsWith("--metadata=")) {
        String name = declaration.substring("--metadata=".length());
        if (name.isEmpty()) throw new IllegalArgumentException("empty metadata declaration");
        expectedMetadata.add(name);
      } else expected.add(declaration);
    }
    if (expected.stream().anyMatch(expectedMetadata::contains))
      throw new IllegalArgumentException("metadata aliases executable declaration");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    if (loader.getSessionInfoStore().getInfos().size() != 1)
      throw new IllegalStateException("one genuine session, never union");
    var builder = new CoverageBuilder();
    new Analyzer(loader.getExecutionDataStore(), builder).analyzeAll(new File(args[1]));
    if (!builder.getNoMatchClasses().isEmpty()) throw new IllegalStateException("CRC mismatch");
    var actual = new TreeSet<String>();
    var actualMetadata = new TreeSet<String>();
    for (var type : builder.getClasses().stream()
        .sorted(Comparator.comparing(ICoverageNode::getName)).toList()) {
      if (type.getClassCounter().getTotalCount() == 0) {
        if (!type.getName().endsWith("/package-info") && !expectedMetadata.contains(type.getName()))
          throw new IllegalStateException("unknown zero-counter class");
        if (type.getInstructionCounter().getTotalCount() != 0
            || type.getMethodCounter().getTotalCount() != 0
            || type.getLineCounter().getTotalCount() != 0
            || type.getBranchCounter().getTotalCount() != 0)
          throw new IllegalStateException("metadata has executable counters");
        if (expectedMetadata.contains(type.getName())) actualMetadata.add(type.getName());
        System.out.println("METADATA\t" + type.getName());
        continue;
      }
      if (expectedMetadata.contains(type.getName()))
        throw new IllegalStateException("executable declared as metadata");
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
        row.append('\t').append(kind).append(':').append(counter.getMissedCount())
            .append(':').append(counter.getCoveredCount());
      }
      System.out.println(row);
      for (int line = type.getFirstLine(); line <= type.getLastLine(); line++) {
        var value = type.getLine(line);
        if (value.getBranchCounter().getMissedCount() > 0
            || value.getInstructionCounter().getMissedCount() > 0)
          System.out.println("MISSED_LINE\t" + type.getName() + "\t" + line + "\t"
              + value.getBranchCounter().getMissedCount() + "\t"
              + value.getBranchCounter().getCoveredCount());
      }
    }
    if (!actual.equals(expected)) throw new IllegalStateException("exact executable inventory");
    if (!actualMetadata.equals(expectedMetadata)) throw new IllegalStateException("exact metadata inventory");
    var session = loader.getSessionInfoStore().getInfos().getFirst();
    System.out.println("SESSION\t" + session.getStartTimeStamp() + "\t" + session.getDumpTimeStamp());
    System.out.println("RESULT\t" + actual.size() + "\t0\t1");
  }
}
