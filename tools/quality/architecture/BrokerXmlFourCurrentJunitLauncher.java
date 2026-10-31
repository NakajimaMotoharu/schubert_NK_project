import java.util.Map;

/** Original whole public Broker XML parse tests; never starts an Artemis server. */
public final class BrokerXmlFourCurrentJunitLauncher {
  private BrokerXmlFourCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.messaging.config.ArtemisBrokerConfigurationTest", 4));
  }
}
