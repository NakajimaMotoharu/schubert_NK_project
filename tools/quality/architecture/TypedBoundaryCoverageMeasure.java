import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Complete selected source units and all nested classes, including every unexecuted counter. */
public final class TypedBoundaryCoverageMeasure {
  private TypedBoundaryCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException("exec, classes and exact inventory required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1
        || !sessions.getFirst().getId().equals("PG9714-PROTOCOL-TYPED-BOUNDARIES")) {
      throw new IllegalStateException("one actual current named component session required");
    }
    var names = Files.readAllLines(Path.of(args[2]));
    Set<String> expected = new HashSet<>(names);
    if (names.size() != expected.size()
        || expected.size() < 73
        || expected.stream()
            .anyMatch(
                n ->
                    !n.matches(
                        "dev/codex/schubert/nk/protocol/layout/(?:[A-Za-z0-9_$]+/)*[A-Za-z0-9_$]+"))) {
      throw new IllegalStateException("complete independently bound named source units required");
    }
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(Path.of(args[1]).toFile());
    if (!builder.getClasses().stream()
            .map(c -> c.getName())
            .collect(Collectors.toSet())
            .equals(expected)
        || !builder.getNoMatchClasses().isEmpty()) {
      throw new IllegalStateException(
          "all physical selected classes and exact execution CRC required");
    }
    var session = sessions.getFirst();
    System.out.println(
        "SESSION\t"
            + session.getId()
            + "\t"
            + session.getStartTimeStamp()
            + "\t"
            + session.getDumpTimeStamp());
    for (var type :
        builder.getClasses().stream()
            .sorted(java.util.Comparator.comparing(c -> c.getName()))
            .toList()) {
      var actual = exec.getExecutionDataStore().get(type.getId());
      System.out.println(
          "CLASS\t"
              + type.getName()
              + "\t"
              + Long.toUnsignedString(type.getId(), 16)
              + "\t"
              + (actual != null));
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
      for (var method : type.getMethods()) {
        if (method.getLineCounter().getMissedCount() != 0
            || method.getBranchCounter().getMissedCount() != 0) {
          System.out.println(
              "MISS_METHOD\t"
                  + type.getName()
                  + "\t"
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
      }
    }
  }
}
