import java.util.Map;

/** Original whole injected JSON object contracts, no listener or management session. */
public final class AcceptorJsonTwoJunitLauncher {
  private AcceptorJsonTwoJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.mq.AcceptorObjectBoundaryTest", 2));
  }
}
