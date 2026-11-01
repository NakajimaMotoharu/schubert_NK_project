import java.util.Map;
/** Whole original owned Web HTTP/admission tests, never a production Unit admission. */
public final class WebMvcLoopbackFifteenCurrentJunitLauncher {
  private WebMvcLoopbackFifteenCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.bootstrap.WebHttpServerTest", 12,
        "dev.codex.schubert.nk.web.bootstrap.WebHttpAdmissionTest", 3));
  }
}
