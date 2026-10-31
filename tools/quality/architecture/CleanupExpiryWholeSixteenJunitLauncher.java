import java.util.Map;

/** Original public data codecs only; no authority, services, database or native owner. */
public final class CleanupExpiryWholeSixteenJunitLauncher {
  private CleanupExpiryWholeSixteenJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.ExpiryWorkerRequestTest", 7,
        "dev.codex.schubert.nk.batch.platform.ExpiryRequestBoundaryTest", 2,
        "dev.codex.schubert.nk.batch.platform.CleanupWorkerRequestTest", 7));
  }
}
