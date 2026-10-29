import java.util.Map;

/** Original MQ/media collector/recorder suites, own memory SDK and finite threads only. */
public final class OriginalMqMediaObservationJunitLauncher {
  private OriginalMqMediaObservationJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.api.monitoring.MqPressureMetricCollectorTest", 8,
            "dev.codex.schubert.nk.api.monitoring.MqPressureMetricRecorderTest", 8,
            "dev.codex.schubert.nk.web.monitoring.MediaStreamsMetricCollectorTest", 8,
            "dev.codex.schubert.nk.web.monitoring.MediaStreamsMetricRecorderTest", 8));
  }
}
