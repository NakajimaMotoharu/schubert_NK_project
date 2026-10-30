import java.util.Map;

/** Entire original revocation exception values only; no service operation. */
public final class OriginalWebRevocationExceptionJunitLauncher {
  private OriginalWebRevocationExceptionJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.revocation.ExceptionValueContractTest", 1));
  }
}
