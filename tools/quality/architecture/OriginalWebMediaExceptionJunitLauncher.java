import java.util.Map;

/** Entire original media exception values only; no service operation. */
public final class OriginalWebMediaExceptionJunitLauncher {
  private OriginalWebMediaExceptionJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.media.ExceptionValueContractTest", 1));
  }
}
