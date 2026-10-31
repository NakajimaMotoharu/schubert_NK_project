import java.util.Map;
/** Original whole request metadata test; no real HTTP or authentication issuance. */
public final class WebRequestTraceTenCurrentJunitLauncher {
  private WebRequestTraceTenCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args,Map.of("dev.codex.schubert.nk.web.logging.WebRequestTraceTest",10));
  }
}
