import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorder;
import dev.codex.schubert.nk.api.monitoring.ExactDurationMeterRegistry;
import dev.codex.schubert.nk.api.monitoring.MqProcessingDurationMetricRecorder;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.web.monitoring.OverflowSafeHttpMeterRegistry;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import java.time.Duration;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;

/** BUG1696/1755: own literal memory fixture scalars only, never target/private observations. */
public final class HttpCdfLifetimeDiagnostic {
  private HttpCdfLifetimeDiagnostic() {}

  private static void emit(String kind, HistogramSnapshot snapshot, double helper) {
    System.out.println(
        "DIAG {\"kind\":\""
            + kind
            + "\",\"count\":"
            + snapshot.count()
            + ",\"cdf\":"
            + Arrays.toString(
                Arrays.stream(snapshot.histogramCounts()).mapToDouble(b -> b.count()).toArray())
            + ",\"nativeHelper\":"
            + helper
            + "}");
  }

  public static void main(String[] arguments) {
    if (arguments.length != 0) throw new IllegalArgumentException("no arguments");
    var clock = new MockClock();
    try (var http = new OverflowSafeHttpMeterRegistry(clock);
        var api = new ExactDurationMeterRegistry()) {
      var timer =
          Timer.builder("nk_http_request_duration_seconds")
              .publishPercentiles()
              .serviceLevelObjectives(
                  Duration.ofMillis(50),
                  Duration.ofMillis(100),
                  Duration.ofMillis(250),
                  Duration.ofMillis(500),
                  Duration.ofSeconds(1),
                  Duration.ofMillis(1500),
                  Duration.ofSeconds(2),
                  Duration.ofMillis(2500),
                  Duration.ofSeconds(5))
              .distributionStatisticExpiry(Duration.ofSeconds(1))
              .distributionStatisticBufferLength(2)
              .register(http);
      new DbQueryDurationMetricRecorder(api, "DEBUG")
          .record(
              DbQueryDurationMetricRecorder.Query.ASYNC_JOB_STATE_COUNTS,
              DbQueryDurationMetricRecorder.Outcome.SUCCESS,
              1_000_000);
      new MqProcessingDurationMetricRecorder(api, "DEBUG", new LayoutId("LGNREQ01"))
          .record(MqProcessingDurationMetricRecorder.Outcome.SUCCESS, 1_000_000);
      timer.record(50_000_000, TimeUnit.NANOSECONDS);
      emit(
          "HTTP_BEFORE",
          timer.takeSnapshot(),
          http.get("nk_http_request_duration_seconds.histogram").tag("le", "0.05").gauge().value());
      clock.add(Duration.ofSeconds(3));
      emit(
          "HTTP_AFTER",
          timer.takeSnapshot(),
          http.get("nk_http_request_duration_seconds.histogram").tag("le", "0.05").gauge().value());
      emit(
          "DB_EXACT",
          api.get("nk_db_query_duration_seconds")
              .tag("query_id", "ASYNC_JOB_STATE_COUNTS")
              .tag("outcome", "SUCCESS")
              .summary()
              .takeSnapshot(),
          0);
      emit(
          "MQ_EXACT",
          api.get("nk_mq_processing_duration_seconds")
              .tag("layout", "LGNREQ01")
              .tag("outcome", "SUCCESS")
              .summary()
              .takeSnapshot(),
          0);
    }
  }
}
