package dev.codex.schubert.nk.web.monitoring;

import java.time.Duration;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * Closed WEB labels before Micrometer binding, not a collector, exporter or readiness proof.
 * NK-OPS-001/P018-09; RD171 MON005..013; UI252; SS313/351; PG-D526/HTTPMETRIC001..006.
 */
public final class HttpMetricContract {
  private static final String SERVICE_LABEL = "service";
  private static final String ROUTE_LABEL = "route";
  private static final String METHOD_LABEL = "method";
  private static final String STATUS_LABEL = "status_class";
  private static final String WEB = "WEB";
  private static final int MINIMUM_STATUS = 100;
  private static final int MAXIMUM_STATUS = 599;
  private static final List<Duration> BUCKETS =
      List.of(
          Duration.ofMillis(50),
          Duration.ofMillis(100),
          Duration.ofMillis(250),
          Duration.ofMillis(500),
          Duration.ofSeconds(1),
          Duration.ofMillis(1500),
          Duration.ofSeconds(2),
          Duration.ofMillis(2500),
          Duration.ofSeconds(5));

  public enum Metric {
    REQUESTS(
        "nk_http_requests_total",
        "counter",
        Set.of(SERVICE_LABEL, ROUTE_LABEL, METHOD_LABEL, STATUS_LABEL)),
    DURATION("nk_http_request_duration_seconds", "histogram", Set.of(SERVICE_LABEL, ROUTE_LABEL));

    private final String retainedName;
    private final String retainedType;
    private final Set<String> declaredLabels;

    Metric(String name, String type, Set<String> labels) {
      retainedName = name;
      retainedType = type;
      declaredLabels = Set.copyOf(labels);
    }

    public String externalName() {
      return retainedName;
    }

    public String type() {
      return retainedType;
    }

    public Set<String> labelNames() {
      return declaredLabels;
    }

    public static Metric parse(String name) {
      Objects.requireNonNull(name, "HTTP metric name");
      for (var value : values()) if (value.retainedName.equals(name)) return value;
      throw new IllegalArgumentException("unknown HTTP metric");
    }
  }

  public enum Route {
    ROOT("/"),
    LOGIN("/login"),
    LOGOUT("/logout"),
    SEARCH("/search"),
    LOGS("/logs"),
    ERROR("/error"),
    SCENARIOS("/scenarios"),
    SCENARIO_ID("/scenarios/{id:[0-9]{1,12}}"),
    SCENARIO_GAME("/scenarios/{game:NUKITASHI[12]}"),
    SCENARIO_PREFIX("/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}"),
    ANIMATION("/animation"),
    ANIMATION_MAIN("/animation/main"),
    ANIMATION_OVA("/animation/ova"),
    ANIMATION_OPENING("/animation/opening"),
    ANIMATION_VIDEO("/animation/videos/{id}"),
    ANIMATION_MEDIA("/animation/media/{id}"),
    MUSIC("/music"),
    MUSIC_CATEGORY("/music/{category}"),
    MUSIC_SECTION("/music/{category}/{section}"),
    MUSIC_MEDIA("/music/media/{id}"),
    MUSIC_DOWNLOAD("/music/download/{id}"),
    AUDIO("/audio/{id}"),
    AUDIO_DOWNLOAD("/audio/{id}/download"),
    ADMIN_USERS("/admin/users"),
    ADMIN_USER_NEW("/admin/users/new"),
    ADMIN_USER_ID("/admin/users/{id:[0-9]{1,12}}"),
    QUESTIONS("/questions"),
    QUESTION_NEW("/questions/new"),
    QUESTION_ACCEPTED("/questions/accepted/{receiptId}"),
    QUESTION_ID("/questions/{id:[0-9]{1,12}}"),
    NOTIFICATIONS("/notifications"),
    NOTIFICATION_ID("/notifications/{id:[0-9]{1,12}}"),
    STYLES("/css/**"),
    SCRIPTS("/js/**"),
    UNKNOWN("/**");

    private static final Map<String, Route> ROUTES_BY_TEMPLATE = index();
    private final String retainedTemplate;

    Route(String template) {
      retainedTemplate = template;
    }

    public String template() {
      return retainedTemplate;
    }

    private static Map<String, Route> index() {
      var values = new HashMap<String, Route>();
      for (var route : values()) values.put(route.retainedTemplate, route);
      return Map.copyOf(values);
    }

    /** Never retain raw path/query/user values, including in an exception. */
    public static Route parse(String template) {
      return ROUTES_BY_TEMPLATE.getOrDefault(
          Objects.requireNonNull(template, "HTTP route template"), UNKNOWN);
    }
  }

  public enum Method {
    GET,
    HEAD,
    POST,
    PUT,
    PATCH,
    DELETE,
    OPTIONS,
    TRACE,
    CONNECT,
    OTHER;

    public static Method parse(String method) {
      Objects.requireNonNull(method, "HTTP method");
      try {
        return valueOf(method);
      } catch (IllegalArgumentException unknown) {
        return OTHER;
      }
    }
  }

  public enum Status {
    INFORMATIONAL("1xx"),
    SUCCESS("2xx"),
    REDIRECTION("3xx"),
    CLIENT_ERROR("4xx"),
    SERVER_ERROR("5xx");

    private final String retainedLabel;

    Status(String label) {
      retainedLabel = label;
    }

    public String label() {
      return retainedLabel;
    }

    public static Status from(int status) {
      if (status < MINIMUM_STATUS || status > MAXIMUM_STATUS)
        throw new IllegalArgumentException("invalid HTTP status");
      return values()[status / MINIMUM_STATUS - 1];
    }
  }

  public record Labels(Route route, Method method, Status status) {
    public Labels {
      Objects.requireNonNull(route, "route label");
      Objects.requireNonNull(method, "method label");
      Objects.requireNonNull(status, "status label");
    }

    public Map<String, String> requestLabels() {
      return Map.of(
          SERVICE_LABEL,
          WEB,
          ROUTE_LABEL,
          route.template(),
          METHOD_LABEL,
          method.name(),
          STATUS_LABEL,
          status.label());
    }

    public Map<String, String> durationLabels() {
      return Map.of(SERVICE_LABEL, WEB, ROUTE_LABEL, route.template());
    }
  }

  public Labels labels(String route, String method, int status) {
    return new Labels(Route.parse(route), Method.parse(method), Status.from(status));
  }

  /**
   * Requested mode only: actual detailed services/registries still require independent
   * verification.
   */
  public boolean detailedMetricsEnabled(String mode) {
    return switch (Objects.requireNonNull(mode, "monitoring mode")) {
      case "STANDARD" -> false;
      case "DEBUG" -> true;
      default -> throw new IllegalArgumentException("invalid monitoring mode");
    };
  }

  public List<Duration> durationBuckets() {
    return BUCKETS;
  }

  public List<String> routeTemplates() {
    return Arrays.stream(Route.values()).map(Route::template).toList();
  }

  public int requestCardinalityBound() {
    return Route.values().length * Method.values().length * Status.values().length;
  }

  public int durationCardinalityBound() {
    return Route.values().length;
  }
}
