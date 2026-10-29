import java.util.Map;

/** Parses one frozen public XML into values; no broker creation or service operation. */
public final class BrokerPublicConfigurationCurrentJunitLauncher {
  private BrokerPublicConfigurationCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    if (System.getProperty("broker.template") != null) {
      throw new IllegalStateException("unexpected public fixture override");
    }
    System.setProperty(
        "broker.template",
        "/home/mini/codex/project1/work/pgpt-runs/PG379/pg13832-snapshot-program-six-compile-v1/snapshot/src/deployment/artemis/etc/broker.xml");
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of("dev.codex.schubert.nk.api.messaging.config.ArtemisBrokerConfigurationTest", 4));
  }
}
