import java.util.Map;

/** Whole original memory-only Log search sender and Proxy JMS reply decoder; no services. */
public final class LgsReplyCurrentJunitLauncher {
  private LgsReplyCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.web.messaging.LogSearchWireClientTest", 8,
            "dev.codex.schubert.nk.web.messaging.JmsReplyDecoderTest", 6));
  }
}
