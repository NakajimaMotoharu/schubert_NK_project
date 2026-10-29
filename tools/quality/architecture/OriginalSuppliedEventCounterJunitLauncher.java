import java.util.Map;

/** Four original supplied event counter suites; no actual replay/JMS/authentication. */
public final class OriginalSuppliedEventCounterJunitLauncher {
  private OriginalSuppliedEventCounterJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.MqMessageMetricRecorderTest", 8,
        "dev.codex.schubert.nk.api.monitoring.MqRedeliveryMetricRecorderTest", 8,
        "dev.codex.schubert.nk.api.monitoring.OperationMismatchMetricRecorderTest", 8,
        "dev.codex.schubert.nk.api.monitoring.InboxReplayMetricRecorderTest", 8));
  }
}
