import java.util.Map;
/** Exact six in-memory projection checks; no context installation or authentication transaction. */
public final class ClosedProjectionSixCurrentJunitLauncher {
  private ClosedProjectionSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.security.ClosedProjectionValueContractTest", 6));
  }
}
