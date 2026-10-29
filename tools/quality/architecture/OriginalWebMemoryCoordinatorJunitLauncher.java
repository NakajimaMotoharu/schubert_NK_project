import java.util.Map;

/** Three original in-memory coordinator suites, no broker/connection/service operations. */
public final class OriginalWebMemoryCoordinatorJunitLauncher {
  private OriginalWebMemoryCoordinatorJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.web.messaging.JmsRequestReplyClientTest", 8,
            "dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistryTest", 5,
            "dev.codex.schubert.nk.web.messaging.ReplyCorrelationTerminalRaceTest", 4));
  }
}
