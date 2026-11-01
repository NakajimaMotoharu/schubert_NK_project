import java.util.Map;

/** Exact pure management presence and original health six, no service or resource acquisition. */
public final class WebReadyPureSixCurrentJunitLauncher {
  private WebReadyPureSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.web.bootstrap.WebRuntimeHealthTest", 4,
            "dev.codex.schubert.nk.web.bootstrap.WebReadyPresenceContractTest", 2));
  }
}
