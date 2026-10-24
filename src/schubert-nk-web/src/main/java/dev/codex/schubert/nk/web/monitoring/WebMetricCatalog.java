package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.Meter;
import io.prometheus.metrics.model.snapshots.Labels;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;

/** NK-OPS-001/RD171/UI252/SS351/1763 WEBCAT: Web-only seven-family closed value catalog. */
public final class WebMetricCatalog {
  private static final String HTTP = "nk_http_requests_total";
  private static final String TIMER = "nk_http_request_duration_seconds";
  private static final String POOL = "nk_db_pool_connections";
  private static final String ROWS = "nk_outbox_rows";
  private static final String AGE = "nk_outbox_oldest_seconds";
  private static final String STREAMS = "nk_media_streams";
  private static final String BYTES = "nk_media_bytes_total";
  private static final String SERVICE = "service";
  private static final String ROUTE = "route";
  private static final String MEDIA = "media_type";
  private static final String GAUGE_TYPE = "gauge";
  private static final Set<String> WEB = Set.of("WEB");
  private static final Set<String> ROUTES = Set.copyOf(new HttpMetricContract().routeTemplates());
  private static final Set<String> MEDIA_TYPES = Set.of("AUDIO", "VIDEO", "MUSIC");
  private static final Map<String, String> TYPES =
      Map.of(
          HTTP,
          "counter",
          TIMER,
          "histogram",
          POOL,
          GAUGE_TYPE,
          ROWS,
          GAUGE_TYPE,
          AGE,
          GAUGE_TYPE,
          STREAMS,
          GAUGE_TYPE,
          BYTES,
          "counter");
  private static final Map<String, Set<String>> OUTBOX =
      Map.of("store", WEB, "status", Set.of("PENDING", "SENT", "ERROR"));
  private static final Map<String, Map<String, Set<String>>> VALUES =
      Map.of(
          HTTP,
          Map.of(
              SERVICE,
              WEB,
              ROUTE,
              ROUTES,
              "method",
              Set.of(
                  "GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT",
                  "OTHER"),
              "status_class",
              Set.of("1xx", "2xx", "3xx", "4xx", "5xx")),
          TIMER,
          Map.of(SERVICE, WEB, ROUTE, ROUTES),
          POOL,
          Map.of(SERVICE, WEB, "state", Set.of("active", "idle", "pending", "max")),
          ROWS,
          OUTBOX,
          AGE,
          OUTBOX,
          STREAMS,
          Map.of(MEDIA, MEDIA_TYPES),
          BYTES,
          Map.of(
              MEDIA,
              MEDIA_TYPES,
              "mode",
              Set.of("INLINE", "DOWNLOAD", "RANGE"),
              "status",
              Set.of("200", "206", "416", "503")));

  public WebMetricCatalog() {}

  public Map<String, Set<String>> gauges() {
    return namespace(GAUGE_TYPE);
  }

  public Map<String, Set<String>> counters() {
    return namespace("counter");
  }

  public Map<String, Set<String>> timers() {
    return namespace("histogram");
  }

  private static Map<String, Set<String>> namespace(String type) {
    var result = new HashMap<String, Set<String>>();
    TYPES.forEach(
        (name, kind) -> {
          if (kind.equals(type))
            result.put(
                name,
                Set.copyOf(Objects.requireNonNull(VALUES.get(name), "metric domain").keySet()));
        });
    return Map.copyOf(result);
  }

  /** Copy once and pass these validated Labels to the model; never approve a later reread. */
  public Labels labels(Meter.Id id) {
    Objects.requireNonNull(id, "metric identity");
    var allowed = VALUES.get(Objects.requireNonNull(id.getName(), "metric name"));
    if (allowed == null) throw new IllegalArgumentException("unknown Web metric");
    var result = new TreeMap<String, String>();
    for (var tag : Objects.requireNonNull(id.getTags(), "metric tags")) {
      Objects.requireNonNull(tag, "metric tag");
      String key = Objects.requireNonNull(tag.getKey(), "metric label key");
      String value = Objects.requireNonNull(tag.getValue(), "metric label value");
      var choices = allowed.get(key);
      if (choices == null || !choices.contains(value))
        throw new IllegalArgumentException("invalid Web metric label");
      if (result.put(key, value) != null)
        throw new IllegalArgumentException("duplicate Web metric label");
    }
    if (!result.keySet().equals(allowed.keySet()))
      throw new IllegalArgumentException("missing Web metric label");
    return Labels.of(new ArrayList<>(result.keySet()), new ArrayList<>(result.values()));
  }
}
