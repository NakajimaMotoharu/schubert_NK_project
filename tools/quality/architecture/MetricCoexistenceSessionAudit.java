import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Original single-exec session metadata only; no application class loading or coverage claim. */
public final class MetricCoexistenceSessionAudit {
  private MetricCoexistenceSessionAudit() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and expected public session");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    var sessions = loader.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals(args[1]))
      throw new IllegalStateException("exact original single session required");
    int records = loader.getExecutionDataStore().getContents().size();
    if (records == 0) throw new IllegalStateException("nonempty original execution data required");
    var session = sessions.getFirst();
    System.out.println(
        "SESSION\t"
            + session.getId()
            + "\t"
            + session.getStartTimeStamp()
            + "\t"
            + session.getDumpTimeStamp()
            + "\t"
            + records);
  }
}
