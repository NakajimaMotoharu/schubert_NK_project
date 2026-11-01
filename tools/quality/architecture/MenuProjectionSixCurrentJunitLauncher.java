import java.util.Map;
/** Internal pure menu projection, no HTTP/MVC server or DB fixture. */
public final class MenuProjectionSixCurrentJunitLauncher {
  private MenuProjectionSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.MenuProjectionContractTest", 6));
  }
}
