import java.util.Map;
public final class RequestDisplayTenCurrentJunitLauncher {
  private RequestDisplayTenCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of("dev.codex.schubert.nk.web.view.RequestDisplayContractTest", 10));
  }
}
