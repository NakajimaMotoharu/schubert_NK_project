import java.util.Map;

/** Whole existing unknown propagation tests, explicit throw-only proxies and memory callbacks. */
public final class ArtemisUnknownCurrentFourJunitLauncher {
  private ArtemisUnknownCurrentFourJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.mq.ArtemisUnknownBoundaryTest", 4));
  }
}
