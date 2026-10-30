import java.util.Map;

/** Whole original5; vector literals only, no exec/setpriv/native authority. */
public final class OriginalFixedServiceArgvJunitLauncher {
  private OriginalFixedServiceArgvJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.bootstrap.FixedServiceExecArgumentsTest", 5));
  }
}
