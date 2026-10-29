import java.util.Map;

/** Runs exactly the two unmodified original scalar metadata tests, not any listener/broker suite. */
public final class OriginalDeliveryMetadataJunitLauncher {
  private OriginalDeliveryMetadataJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.messaging.inbound.DeliveryMetadataTest", 2));
  }
}
