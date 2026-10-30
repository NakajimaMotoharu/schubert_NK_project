import java.util.Map;

/** Entire original session exception values only; no service operation. */
public final class OriginalWebSessionExceptionJunitLauncher {
  private OriginalWebSessionExceptionJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.session.ExceptionValueContractTest", 1));
  }
}
