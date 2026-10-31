import java.util.Map;

/** Whole original Login contracts using only memory senders and synthetic local Spring tokens. */
public final class MqLoginMemoryFourteenJunitLauncher {
  private MqLoginMemoryFourteenJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.security.MqLoginClientTest", 6,
        "dev.codex.schubert.nk.web.security.MqLoginContextProbeTest", 3,
        "dev.codex.schubert.nk.web.security.MqAuthenticationProviderTest", 5));
  }
}
