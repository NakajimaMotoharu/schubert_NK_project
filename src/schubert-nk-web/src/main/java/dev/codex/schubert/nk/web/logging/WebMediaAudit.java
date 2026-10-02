package dev.codex.schubert.nk.web.logging;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.time.Clock;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.Locale;
import java.util.Objects;
import java.util.UUID;

/** Local closed media actions only. FUN005..007/MON/UI252/SS333,351; PG-D-343/PT-MED-HTTP. */
public final class WebMediaAudit {
  public enum Failure {
    NONE,
    IO,
    CLIENT_ABORT,
    BUSY
  }

  private static final DateTimeFormatter TIMESTAMP =
      new DateTimeFormatterBuilder().appendInstant(3).toFormatter(Locale.ROOT);
  private final Logger logger;
  private final Clock clock;
  private final String appVersion;
  private final String configVersion;

  public WebMediaAudit(Logger logger, Clock clock, String appVersion, String configVersion) {
    this.logger = Objects.requireNonNull(logger, "logger");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.appVersion = version(appVersion);
    this.configVersion = version(configVersion);
  }

  /**
   * Descriptor is transient, never logged wholesale; physical path/name/hash/context are omitted.
   */
  public void record(
      UUID requestId,
      SessionPrincipal actor,
      MediaDescriptor descriptor,
      int status,
      long bytes,
      Failure failure) {
    Objects.requireNonNull(requestId, "requestId");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(descriptor, "descriptor");
    Objects.requireNonNull(failure, "failure");
    if ((status != 200 && status != 206 && status != 416 && status != 503)
        || (failure == Failure.NONE && status == 503)
        || bytes < 0
        || bytes > descriptor.byteLength())
      throw new IllegalArgumentException("media audit values are invalid");
    Level level = failure == Failure.IO || failure == Failure.BUSY ? Level.ERROR : Level.INFO;
    var json = new JsonObject();
    json.addProperty(
        "timestamp", TIMESTAMP.format(Objects.requireNonNull(clock.instant(), "instant")));
    json.addProperty("level", level == Level.INFO ? "INFO" : "ERROR");
    json.addProperty("service", "WEB");
    json.addProperty("appVersion", appVersion);
    json.addProperty("configVersion", configVersion);
    json.addProperty("category", "ACTION");
    json.addProperty(
        "action",
        status == 416
            ? "MEDIA_RANGE_REJECTED"
            : descriptor.disposition() == ContentDisposition.ATTACHMENT
                ? "MEDIA_DOWNLOADED"
                : "MEDIA_STREAMED");
    json.addProperty(
        "outcome", failure != Failure.NONE ? "FAILURE" : status == 416 ? "DENIED" : "SUCCESS");
    json.addProperty("requestId", requestId.toString());
    json.addProperty(
        "actorUsername", actor.username().replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
    json.addProperty("actorRole", actor.role().name());
    json.addProperty("status", status);
    json.addProperty("responseBytes", bytes);
    var details = new JsonObject();
    details.addProperty("mediaType", descriptor.mediaType().name());
    details.addProperty("logicalId", descriptor.logicalId());
    details.addProperty("reason", failure.name());
    json.add("details", details);
    if (failure == Failure.IO) json.addProperty("errorCode", "FILE_IO");
    if (failure == Failure.BUSY) json.addProperty("errorCode", "RESOURCE_THREAD");
    logger.log(level, json.toString());
  }

  private static String version(String value) {
    Objects.requireNonNull(value, "version");
    if (!value.matches("[A-Za-z0-9][A-Za-z0-9._+\\-]{0,63}"))
      throw new IllegalArgumentException("media audit version is invalid");
    return value;
  }
}
