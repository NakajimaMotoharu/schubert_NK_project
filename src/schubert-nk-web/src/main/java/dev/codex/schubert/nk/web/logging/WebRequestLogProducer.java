package dev.codex.schubert.nk.web.logging;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.log.WebLogEventData;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.bootstrap.WebStartupException;
import dev.codex.schubert.nk.web.security.LoginClientAddress;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Local-first REQUEST -> existing encrypted outbox; UI235252/SS312351/SSC172/PG-D354/REQ001..016.
 */
@NullMarked
public final class WebRequestLogProducer {
  private static final long N12 = 999999999999L;
  private static final long N9 = 999999999L;
  private static final Set<String> METHODS =
      Set.of("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT");
  private static final DateTimeFormatter TIME =
      new DateTimeFormatterBuilder().appendInstant(3).toFormatter(Locale.ROOT);
  private final DataSource database;
  private final WebLogPayloadCodec codec;
  private final WebLogOutboxRepository repository;
  private final Logger logger;
  private final Clock clock;
  private final Supplier<UUID> retainedIdentifiers;
  private final String appVersion;
  private final String configVersion;
  private final Runnable onTerminal;

  /** All dependencies remain owned by the outer HTTP/worker/DB/JMS/key lifetime. */
  public WebRequestLogProducer(
      DataSource database,
      WebLogPayloadCodec codec,
      WebLogOutboxRepository repository,
      Logger logger,
      Clock clock,
      Supplier<UUID> identifiers,
      String appVersion,
      String configVersion,
      Runnable onTerminal) {
    this.database = Objects.requireNonNull(database, "database");
    this.codec = Objects.requireNonNull(codec, "codec");
    this.repository = Objects.requireNonNull(repository, "repository");
    this.logger = Objects.requireNonNull(logger, "logger");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.retainedIdentifiers = Objects.requireNonNull(identifiers, "identifiers");
    this.appVersion = version(appVersion);
    this.configVersion = version(configVersion);
    this.onTerminal = Objects.requireNonNull(onTerminal, "onTerminal");
  }

  Supplier<UUID> identifiers() {
    return retainedIdentifiers;
  }

  private static String version(String value) {
    Objects.requireNonNull(value, "version");
    if (!value.matches("[A-Za-z0-9][A-Za-z0-9._+\\-]{0,63}"))
      throw new IllegalArgumentException("request audit version is invalid");
    return value;
  }

  /** Metadata fault, not an invented HTTP success or a trusted-address grant. */
  public void metadataInvalid() {
    var json = base(Objects.requireNonNull(clock.instant(), "instant"));
    json.addProperty("level", "WARN");
    json.addProperty("category", "SYSTEM");
    json.addProperty("action", "INTEGRITY_FAILED");
    json.addProperty("outcome", "UNKNOWN");
    json.addProperty("errorCode", "WEB_REQUEST_LOG_METADATA_INVALID");
    local(Level.WARNING, json);
  }

  /** Only the native terminal hook supplies final status, byte count and elapsed nanoseconds. */
  public void complete(
      WebRequestTrace trace,
      int status,
      long elapsedNanos,
      long responseBytes,
      String method,
      Optional<String> remoteAddress) {
    Objects.requireNonNull(trace, "trace");
    if (!completeOne(
        trace,
        status,
        elapsedNanos,
        responseBytes,
        method,
        remoteAddress,
        WebHttpLogKind.REQUEST,
        trace.eventId(),
        trace.correlationId())) return;
    if (WebHttpLogKind.MENU_VIEWED.eligible(
        trace.menuViewCandidate(), method, status, trace.route(), trace.actor().isPresent())) {
      UUID eventId = retainedIdentifiers.get();
      if (eventId == null
          || eventId.equals(trace.eventId())
          || eventId.equals(trace.requestId())
          || eventId.equals(trace.correlationId())) {
        metadataInvalid();
        return;
      }
      completeOne(
          trace,
          status,
          elapsedNanos,
          responseBytes,
          method,
          remoteAddress,
          WebHttpLogKind.MENU_VIEWED,
          eventId,
          trace.correlationIdFor(eventId));
    }
  }

  private boolean completeOne(
      WebRequestTrace trace,
      int status,
      long elapsedNanos,
      long responseBytes,
      String method,
      Optional<String> remoteAddress,
      WebHttpLogKind kind,
      UUID eventId,
      UUID correlationId) {
    Objects.requireNonNull(trace, "trace");
    Objects.requireNonNull(method, "method");
    Objects.requireNonNull(remoteAddress, "remoteAddress");
    if (status < 100 || status > 599 || elapsedNanos < 0 || responseBytes < 0) {
      metadataInvalid();
      return false;
    }
    // BUG577: caller metadata must never reach even the local sink before numeric-IP validation.
    final Optional<String> address;
    try {
      address =
          remoteAddress.map(
              value ->
                  InetAddress.ofLiteral(new LoginClientAddress(value).value()).getHostAddress());
    } catch (IllegalArgumentException invalidAddress) {
      metadataInvalid();
      return false;
    }
    Instant now = Objects.requireNonNull(clock.instant(), "instant").truncatedTo(ChronoUnit.MILLIS);
    String verb = METHODS.contains(method) ? method : "OTHER";
    long elapsed = elapsedNanos / 1000000L;
    boolean truncated = elapsed > N9 || responseBytes > N12;
    long bytes = Math.min(responseBytes, N12);
    int wireElapsed = (int) Math.min(elapsed, N9);
    LogLevel level = status >= 500 ? LogLevel.ERROR : status >= 400 ? LogLevel.WARN : LogLevel.INFO;
    Level localLevel = status >= 500 ? Level.ERROR : status >= 400 ? Level.WARNING : Level.INFO;
    var json = base(now);
    json.addProperty("level", level.name());
    json.addProperty("category", kind.category().name());
    json.addProperty("action", kind.action());
    json.addProperty("outcome", status >= 400 ? "FAILURE" : "SUCCESS");
    json.addProperty("messageId", eventId.toString());
    json.addProperty("correlationId", correlationId.toString());
    json.addProperty("requestId", trace.requestId().toString());
    json.addProperty("message", kind.message());
    json.addProperty("httpMethod", verb);
    json.addProperty("path", trace.route());
    json.addProperty("status", status);
    json.addProperty("elapsedMs", Math.min(elapsed, N12));
    Optional<String> username =
        trace
            .actor()
            .map(
                a ->
                    a.getUsername()
                        .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " ")
                        .replaceFirst(" +$", ""))
            .filter(v -> !v.isEmpty());
    Optional<UserRole> role =
        username.isPresent()
            ? trace.actor().map(a -> UserRole.valueOf(a.getRole()))
            : Optional.empty();
    username.ifPresent(v -> json.addProperty("actorUsername", v));
    role.ifPresent(v -> json.addProperty("actorRole", v.name()));
    address.ifPresent(v -> json.addProperty("remoteAddress", v));
    var details = new JsonObject();
    details.addProperty("responseBytes", bytes);
    details.addProperty("projectionStatus", "PENDING");
    if (truncated) details.addProperty("truncated", true);
    json.add("details", details);
    if (!local(localLevel, json)) return false;
    try {
      if (address.isEmpty())
        throw new IllegalArgumentException("verified transport is unavailable");
      var event =
          new WebLogEventData(
              now,
              kind.category(),
              level,
              Optional.of(kind.action()),
              kind.message(),
              trace.requestId(),
              verb,
              trace.route(),
              new HttpStatusCode(status),
              new ElapsedMilliseconds(wireElapsed),
              address.orElseThrow(),
              username,
              role,
              Optional.of(details.toString()));
      byte[] wire = wire(eventId, correlationId, now, event);
      try {
        var identity = new WebLogPayloadIdentity(eventId, correlationId);
        project(identity, codec.encrypt(identity, wire), now);
      } finally {
        Arrays.fill(wire, (byte) 0);
      }
    } catch (SQLException | RuntimeException failure) {
      // SS312/332/351/354, SSC329330/BUG1592: only ordinary failures reach FAILED audit.
      SessionStoreException.preserveFatal(failure);
      // Projection is explicitly FAILED; no exception is turned into logging success. Boundaries
      // and constructor null contracts are checked outside this best-effort projection scope.
      details.addProperty("projectionStatus", "FAILED");
      json.addProperty("errorCode", "WEB_REQUEST_LOG_PROJECTION_FAILED");
      json.addProperty("level", localLevel == Level.ERROR ? "ERROR" : "WARN");
      return local(localLevel == Level.ERROR ? Level.ERROR : Level.WARNING, json);
    }
    return true;
  }

  private JsonObject base(Instant now) {
    var json = new JsonObject();
    json.addProperty("timestamp", TIME.format(now));
    json.addProperty("service", "WEB");
    json.addProperty("appVersion", appVersion);
    json.addProperty("configVersion", configVersion);
    return json;
  }

  /** A broken primitive local sink is terminal, never a successful audit observation. */
  private boolean local(Level level, JsonObject json) {
    @Nullable RuntimeException localFailure = null;
    try {
      if (logger.isLoggable(level)) {
        logger.log(level, json.toString());
        return true;
      }
    } catch (RuntimeException failure) {
      // SSC331/BUG1601: retain only until the existing owner signal has been attempted.
      localFailure = failure;
    }
    try {
      onTerminal.run();
    } catch (RuntimeException failedSignal) {
      // Preserve the callback's precedence, but never mask a remaining logger fatal.
      WebStartupException.preserveFatal(failedSignal);
      if (localFailure != null) WebStartupException.preserveFatal(localFailure);
      throw new IllegalStateException("request audit terminal signal failed");
    }
    if (localFailure != null) WebStartupException.preserveFatal(localFailure);
    return false;
  }

  private static byte[] wire(UUID eventId, UUID correlationId, Instant now, WebLogEventData data) {
    var layout = new LayoutId("WLGEVT01");
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            layout,
            1,
            MessageKind.EVENT,
            InteractionKind.INTERNAL,
            eventId,
            correlationId,
            now,
            Optional.empty(),
            256,
            2080,
            0,
            0,
            2336,
            Optional.empty());
    var payload =
        PayloadCodec.standard()
            .encode(
                PayloadTypeCatalog.encode(new TypedPayloadValues(layout, data, List.of())), false);
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private void project(WebLogPayloadIdentity identity, EncryptedWebLogPayload payload, Instant now)
      throws SQLException {
    try (Connection connection = Objects.requireNonNull(database.getConnection(), "connection")) {
      connection.setAutoCommit(false);
      try {
        if (!repository.enqueue(connection, identity, payload, now))
          throw new SQLException("request event identity already exists", "23505");
        connection.commit();
      } catch (SQLException | RuntimeException | Error failure) {
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException rollback) {
          WebStartupException.attachSecondary(failure, rollback);
        } catch (Error fatal) {
          if (fatal != failure) fatal.addSuppressed(failure);
          throw fatal;
        }
        throw failure;
      }
    }
  }
}
