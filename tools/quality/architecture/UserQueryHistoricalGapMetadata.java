import java.nio.file.Path;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Existing execution-data metadata only; target classes never enter the runtime classpath. */
public final class UserQueryHistoricalGapMetadata {
  private UserQueryHistoricalGapMetadata() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("existing exec and exact class file");
    var loader = new ExecFileLoader();
    loader.load(Path.of(args[0]).toFile());
    var sessions = loader.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG9972-PLAIN-QUERY-CORE"))
      throw new IllegalStateException("original historical session only");
    var builder = new CoverageBuilder();
    int count =
        new Analyzer(loader.getExecutionDataStore(), builder).analyzeAll(Path.of(args[1]).toFile());
    if (count != 1 || builder.getClasses().size() != 1 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("single original class and CRC match");
    var type = builder.getClasses().iterator().next();
    if (!type.getName().equals("dev/codex/schubert/nk/api/application/admin/UserQueryRequest")
        || loader.getExecutionDataStore().get(type.getId()) == null)
      throw new IllegalStateException("original User query class");
    System.out.println("CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
    for (var method : type.getMethods()) {
      System.out.print("METHOD\t" + method.getName() + "\t" + method.getDesc());
      for (var kind :
          new ICoverageNode.CounterEntity[] {
            ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
            ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
          }) {
        var counter = method.getCounter(kind);
        System.out.print("\t" + counter.getMissedCount() + "/" + counter.getCoveredCount());
      }
      System.out.println();
    }
  }
}
