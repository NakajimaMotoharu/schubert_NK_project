import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Reads only an owned coverage data file, never loads or initializes a Product class. */
public final class CoverageSessionIdentity {
  private CoverageSessionIdentity() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("owned exec and exact tool identity");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    var infos = loader.getSessionInfoStore().getInfos();
    if (infos.size() != 1 || !infos.getFirst().getId().equals(args[1]))
      throw new IllegalStateException("one exact owned coverage session required");
    System.out.println("OWNED_COVERAGE_SESSION_MATCH\t1");
  }
}
