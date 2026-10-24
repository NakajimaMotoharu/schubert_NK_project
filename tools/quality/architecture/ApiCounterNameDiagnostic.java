package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Meter;
import io.micrometer.prometheusmetrics.PrometheusNamingConvention;

/** BUG1691 pure own naming diagnosis, not PT PASS or permission to run business operations. */
public final class ApiCounterNameDiagnostic {
  private ApiCounterNameDiagnostic() {}

  private static void types(String key, PrometheusGaugeTextFixture registry) {
    var names = registry.scrape().lines().filter(s -> s.startsWith("# TYPE ")).toList();
    if (names.size() != 1) throw new IllegalStateException("one own synthetic family required");
    var fields = names.getFirst().split(" ");
    if (fields.length != 4 || !fields[2].matches("[a-z_]{1,128}") || !fields[3].equals("counter"))
      throw new IllegalStateException("only bounded public counter metadata");
    System.out.println(key + "\t" + fields[2]);
  }

  public static void main(String[] args) {
    if (args.length != 0) throw new IllegalArgumentException("no external arguments");
    try (var r = new PrometheusGaugeTextFixture()) {
      var owner =
          new MqMessageMetricRecorder(r, "DEBUG", new LayoutId("WLGEVT01"), BrokerTopology.WEB_LOG);
      owner.record(MqMessageMetricRecorder.Stage.ACK);
      types("EXISTING_TYPE", r);
    }
    try (var r = new PrometheusGaugeTextFixture()) {
      Counter.builder("nk_mq_messages_total").register(r).increment();
      types("NO_UNIT_TYPE", r);
    }
    var convention = new PrometheusNamingConvention();
    System.out.println(
        "SECONDS_NAME\t"
            + convention.name(
                "nk_db_query_duration_seconds", Meter.Type.DISTRIBUTION_SUMMARY, "seconds"));
    System.out.println(
        "PROCESSING_NAME\t"
            + convention.name(
                "nk_mq_processing_duration_seconds", Meter.Type.DISTRIBUTION_SUMMARY, "seconds"));
  }
}
