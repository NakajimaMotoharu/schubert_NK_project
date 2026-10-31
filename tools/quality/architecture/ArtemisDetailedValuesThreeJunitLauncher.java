import java.util.Map;

/** Whole original injected-reader values contracts; no default broker or startup operations. */
public final class ArtemisDetailedValuesThreeJunitLauncher {
  private ArtemisDetailedValuesThreeJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.mq.ArtemisDetailedValuesTest", 3));
  }
}
