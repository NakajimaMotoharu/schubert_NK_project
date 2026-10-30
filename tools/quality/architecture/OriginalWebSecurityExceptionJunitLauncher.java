import java.util.Map;

/** Whole scalar exception contract only; no Login or session operation. */
public final class OriginalWebSecurityExceptionJunitLauncher {
  private OriginalWebSecurityExceptionJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.security.ExceptionValueContractTest", 1));
  }
}
