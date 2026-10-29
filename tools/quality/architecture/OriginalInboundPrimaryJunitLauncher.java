import java.util.Map;

/** Exactly five existing finite-proxy primary tests, never listener broker or graph9 suites. */
public final class OriginalInboundPrimaryJunitLauncher {
  private OriginalInboundPrimaryJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.messaging.inbound.InboundTransactionsPrimaryContractTest", 5));
  }
}
