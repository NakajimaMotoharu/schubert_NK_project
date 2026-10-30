import java.util.Map;

/** Entire original logging exception values only; no service operation. */
public final class OriginalWebLoggingExceptionJunitLauncher {
  private OriginalWebLoggingExceptionJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.logging.ExceptionValueContractTest", 1));
  }
}
