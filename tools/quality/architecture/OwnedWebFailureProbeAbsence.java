import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Passive owned exec reader; never loads, initializes or invokes a Product class. */
public final class OwnedWebFailureProbeAbsence {
  private static final String PREFIX = "dev/codex/schubert/nk/web/bootstrap/WebStartupException";

  private OwnedWebFailureProbeAbsence() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("owned exec and session only");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    var sessions = loader.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals(args[1]))
      throw new IllegalStateException("one exact owned coverage session required");
    int records = 0;
    for (var value : loader.getExecutionDataStore().getContents()) {
      String name = value.getName();
      if (!name.equals(PREFIX) && !name.startsWith(PREFIX + "$")) continue;
      records++;
      int covered = 0;
      for (boolean probe : value.getProbes()) if (probe) covered++;
      if (covered != 0) throw new IllegalStateException("held failure code has recorded execution");
      System.out.println("ZERO_PROBES\t" + name + "\t" + value.getProbes().length);
    }
    System.out.println("OWNED_WEB_FAILURE_PREFIX_NO_TRUE_PROBES\t" + records + "\t0");
  }
}
