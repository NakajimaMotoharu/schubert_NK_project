package dev.codex.schubert.nk.web.logging;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.net.InetAddress;
import java.time.Clock;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Local SECURITY JSON only; API critical DB audit remains authoritative. No request, Throwable,
 * password, context or arbitrary details reach the logger. NK-WEB-001; AUT-001..004/MON-004;
 * UI226/252; SS314/351/352; PG-D-107/PT-WEB-095..100.
 */
public final class WebSecurityAudit {
  private static final int MAXIMUM_IP_LITERAL_CHARACTERS = 45;

  private static final java.lang.String LITERAL_DENIED = "DENIED";

  private static final java.lang.String LITERAL_AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED";

  /** Actual registered handler/filter patterns only, never a raw URI or fallback parser. */
  public enum Route {
    LOGIN("/login"),
    LOGOUT("/logout"),
    ALL_WEB("/**"),
    ADMIN_USERS("/admin/users/**"),
    LOGS("/logs");
    private final String template;

    Route(String template) {
      this.template = template;
    }
  }

  /** Closed local events; denial event names are not additional SS351 action names. */
  public enum Event {
    LOGIN_SUCCEEDED("LOGIN_SUCCEEDED", "AUTHENTICATED", "SUCCESS", Level.INFO),
    LOGIN_FAILED("LOGIN_FAILED", "INVALID_CREDENTIALS", LITERAL_DENIED, Level.WARNING),
    LOGIN_LOCKED("LOGIN_LOCKED", "LOCKED", LITERAL_DENIED, Level.WARNING),
    CSRF_DENIED(LITERAL_AUTHORIZATION_DENIED, "CSRF", LITERAL_DENIED, Level.WARNING),
    ROLE_DENIED(LITERAL_AUTHORIZATION_DENIED, "ROLE", LITERAL_DENIED, Level.WARNING),
    PROXY_DENIED(LITERAL_AUTHORIZATION_DENIED, "PROXY", LITERAL_DENIED, Level.WARNING),
    AUTHENTICATION_REQUIRED(
        LITERAL_AUTHORIZATION_DENIED, "UNAUTHENTICATED", LITERAL_DENIED, Level.WARNING),
    API_SESSION_INVALID("SESSION_EXPIRED", "API_SESSION_INVALID", LITERAL_DENIED, Level.INFO),
    LOGOUT_SUCCEEDED("LOGOUT_SUCCEEDED", "REVOKED", "SUCCESS", Level.INFO),
    LOGOUT_REVOCATION_QUEUED("LOGOUT_REVOCATION_QUEUED", "RETRY_RETAINED", "SUCCESS", Level.INFO);

    private final String action;
    private final String reason;
    private final String outcome;
    private final Level level;

    Event(String action, String reason, String outcome, Level level) {
      this.action = action;
      this.reason = reason;
      this.outcome = outcome;
      this.level = level;
    }
  }

  private static final Set<Event> LOGIN =
      Set.of(Event.LOGIN_SUCCEEDED, Event.LOGIN_FAILED, Event.LOGIN_LOCKED);
  private static final Set<Event> LOGOUT =
      Set.of(Event.LOGOUT_SUCCEEDED, Event.LOGOUT_REVOCATION_QUEUED);
  private static final DateTimeFormatter TIMESTAMP =
      new DateTimeFormatterBuilder().appendInstant(3).toFormatter(Locale.ROOT);
  private final Logger logger;
  private final Clock clock;
  private final String appVersion;
  private final String configVersion;

  public WebSecurityAudit(Logger logger, Clock clock, String appVersion, String configVersion) {
    this.logger = Objects.requireNonNull(logger, "logger");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.appVersion = version(appVersion);
    this.configVersion = version(configVersion);
  }

  /**
   * Caller supplies a server-generated request ID and only an already trusted client address. Login
   * failures intentionally omit untrusted attempted usernames; lock alone has retry seconds. Actor
   * is transiently projected to username/role and never retained. Logger failures propagate.
   */
  public void record(
      UUID requestId,
      Event event,
      Optional<String> remoteAddress,
      Optional<SessionPrincipal> actor,
      int retryAfterSeconds,
      Route route) {
    Objects.requireNonNull(requestId, "requestId");
    Objects.requireNonNull(event, "event");
    Objects.requireNonNull(remoteAddress, "remoteAddress");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(route, "route");
    if (retryAfterSeconds < 0
        || retryAfterSeconds > 900
        || (event != Event.LOGIN_LOCKED && retryAfterSeconds != 0)
        || (event == Event.LOGIN_SUCCEEDED && actor.isEmpty())
        || (event == Event.AUTHENTICATION_REQUIRED && actor.isPresent())
        || ((event == Event.LOGIN_FAILED || event == Event.LOGIN_LOCKED) && actor.isPresent())
        || (LOGIN.contains(event) && remoteAddress.isEmpty())
        || (LOGIN.contains(event) && route != Route.LOGIN)
        || (LOGOUT.contains(event) && actor.isEmpty())
        || (LOGOUT.contains(event) && remoteAddress.isEmpty())
        || (LOGOUT.contains(event) && route != Route.LOGOUT))
      throw new IllegalArgumentException("security audit metadata is invalid");
    Optional<String> client = remoteAddress.map(WebSecurityAudit::canonicalAddress);
    var json = new JsonObject();
    json.addProperty(
        "timestamp", TIMESTAMP.format(Objects.requireNonNull(clock.instant(), "instant")));
    json.addProperty("level", event.level == Level.INFO ? "INFO" : "WARN");
    json.addProperty("service", "WEB");
    json.addProperty("appVersion", appVersion);
    json.addProperty("configVersion", configVersion);
    json.addProperty("category", "SECURITY");
    json.addProperty("action", event.action);
    json.addProperty("outcome", event.outcome);
    json.addProperty("requestId", requestId.toString());
    actor.ifPresent(
        value -> {
          json.addProperty(
              "actorUsername", value.username().replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
          json.addProperty("actorRole", value.role().name());
        });
    client.ifPresent(value -> json.addProperty("remoteAddress", value));
    var details = new JsonObject();
    details.addProperty("reason", event.reason);
    details.addProperty("route", route.template);
    details.addProperty("targetType", "HTTP_REQUEST");
    if (event == Event.LOGIN_LOCKED) details.addProperty("retryAfterSeconds", retryAfterSeconds);
    json.add("details", details);
    logger.log(event.level, json.toString());
  }

  private static String version(String value) {
    Objects.requireNonNull(value, "version");
    if (!value.matches("[A-Za-z0-9][A-Za-z0-9._+\\-]{0,63}"))
      throw new IllegalArgumentException("security audit version is invalid");
    return value;
  }

  private static String canonicalAddress(String value) {
    try {
      if (value.length() > MAXIMUM_IP_LITERAL_CHARACTERS) throw new IllegalArgumentException();
      String canonical = InetAddress.ofLiteral(value).getHostAddress();
      if (canonical.contains("%")) throw new IllegalArgumentException();
      return canonical;
    } catch (IllegalArgumentException invalid) {
      throw new IllegalArgumentException("security audit address is invalid");
    }
  }
}
