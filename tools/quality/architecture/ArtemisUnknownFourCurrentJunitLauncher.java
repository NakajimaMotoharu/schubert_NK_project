import java.util.Map;
/** Original whole unknown propagation on throw-only proxies; no actual broker or Root. */
public final class ArtemisUnknownFourCurrentJunitLauncher {
  private ArtemisUnknownFourCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args,Map.of("dev.codex.schubert.nk.batch.mq.ArtemisUnknownBoundaryTest",4));
  }
}
