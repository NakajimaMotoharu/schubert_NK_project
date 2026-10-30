import java.util.Map;

/** Whole original four pure Outbox value Tests; no dispatcher, broker or graph traversal. */
public final class OriginalCurrentOutboxThirteenJunitLauncher {
  private OriginalCurrentOutboxThirteenJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.messaging.outbound.OutboxPolicyTest", 4,
        "dev.codex.schubert.nk.api.messaging.outbound.OutboxModelTest", 4,
        "dev.codex.schubert.nk.api.messaging.outbound.OutboxDlqMetadataTest", 2,
        "dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatchReportBoundaryTest", 3));
  }
}
