import java.util.Map;

/** Three whole original protected-read facades; in-memory JMS ports, no service or auth grant. */
public final class ProtectedFacadesCurrentJunitLauncher {
  private ProtectedFacadesCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest", 8,
            "dev.codex.schubert.nk.web.messaging.MusicWireClientTest", 8,
            "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest", 8));
  }
}
