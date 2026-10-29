import java.util.Map;

/** Original whole business wire suite: supplied memory sender only, no JMS connection. */
public final class OriginalWebBusinessWireJunitLauncher {
  private OriginalWebBusinessWireJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.web.messaging.WebBusinessWireClientsTest", 12));
  }
}
