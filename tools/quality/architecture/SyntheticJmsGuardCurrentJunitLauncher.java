import java.util.Map;

/** Original six whole synthetic JMS boundary methods; no broker or connection. */
public final class SyntheticJmsGuardCurrentJunitLauncher {
  private SyntheticJmsGuardCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuardTest", 6));
  }
}
