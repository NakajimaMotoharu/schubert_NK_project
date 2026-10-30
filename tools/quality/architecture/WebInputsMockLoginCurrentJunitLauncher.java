import java.util.Map;

/** Whole original Web inputs4 and in-memory MockMvc login4; no service or real authentication. */
public final class WebInputsMockLoginCurrentJunitLauncher {
  private WebInputsMockLoginCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest", 4,
        "dev.codex.schubert.nk.web.controller.LoginControllerTest", 4));
  }
}
