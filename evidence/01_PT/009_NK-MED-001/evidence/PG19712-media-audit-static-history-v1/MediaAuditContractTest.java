package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebMediaAudit.Failure;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.HashSet;
import java.util.List;
import java.util.ResourceBundle;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** MED-AUDIT-001..008; SS333351352: local JSON emitter, no delivery/auth/file activity. */
final class MediaAuditContractTest {
  private static final int OK = 200;
  private static final int PARTIAL = 206;
  private static final int RANGE_REJECTED = 416;
  private static final int UNAVAILABLE = 503;
  private static final Instant NOW = Instant.parse("2026-11-06T00:00:01.123987Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.ofHours(9));
  private static final UUID ID = new UUID(0, 11);
  private static final String APP = "1.2.3+pt";
  private static final String CONFIG = "cfg-1";
  private static final String TIMESTAMP = "timestamp";
  private static final String LEVEL = "level";
  private static final String SERVICE = "service";
  private static final String CATEGORY = "category";
  private static final String ACTION = "action";
  private static final String OUTCOME = "outcome";
  private static final String REQUEST = "requestId";
  private static final String ACTOR_NAME = "actorUsername";
  private static final String ACTOR_ROLE = "actorRole";
  private static final String STATUS = "status";
  private static final String BYTES = "responseBytes";
  private static final String DETAILS = "details";
  private static final String ERROR_CODE = "errorCode";
  private static final String MEDIA_TYPE = "mediaType";
  private static final String LOGICAL_ID = "logicalId";
  private static final String REASON = "reason";
  private static final String STREAMED = "MEDIA_STREAMED";
  private static final String DOWNLOADED = "MEDIA_DOWNLOADED";
  private static final String REJECTED = "MEDIA_RANGE_REJECTED";
  private static final String FIXTURE_USER = "public-user";
  private static final SessionPrincipal ACTOR = actor(FIXTURE_USER, UserRole.USER);
  private static final List<DescriptorCase> DESCRIPTORS =
      List.of(
          new DescriptorCase(
              MediaType.AUDIO,
              "17",
              "scenario/public-audio.ogg",
              "public-audio.ogg",
              "audio/ogg",
              ContentDisposition.INLINE,
              "AUDIO",
              STREAMED),
          new DescriptorCase(
              MediaType.AUDIO,
              "17",
              "scenario/public-audio.ogg",
              "public-audio.ogg",
              "audio/ogg",
              ContentDisposition.ATTACHMENT,
              "AUDIO",
              DOWNLOADED),
          new DescriptorCase(
              MediaType.VIDEO,
              "public-video",
              "video/public-video.mp4",
              "public-video.mp4",
              "video/mp4",
              ContentDisposition.INLINE,
              "VIDEO",
              STREAMED),
          new DescriptorCase(
              MediaType.MUSIC,
              "public-track",
              "music/public-track.wav",
              "public-track.wav",
              "audio/wav",
              ContentDisposition.ATTACHMENT,
              "MUSIC",
              DOWNLOADED));
  private static final List<FailureCase> FAILURES =
      List.of(
          new FailureCase(Failure.NONE, "INFO", Level.INFO, null),
          new FailureCase(Failure.IO, "ERROR", Level.ERROR, "FILE_IO"),
          new FailureCase(Failure.CLIENT_ABORT, "INFO", Level.INFO, null),
          new FailureCase(Failure.BUSY, "ERROR", Level.ERROR, "RESOURCE_THREAD"));

  @Test
  void media001ClosedStatusFailureMediaCatalogMatchesIndependentJson() {
    for (DescriptorCase descriptor : DESCRIPTORS)
      for (FailureCase failure : FAILURES)
        for (int status : new int[] {OK, PARTIAL, RANGE_REJECTED, UNAVAILABLE}) {
          if (failure.value() == Failure.NONE && status == UNAVAILABLE) continue;
          var logger = new CapturingLogger();
          var audit = new WebMediaAudit(logger, CLOCK, APP, CONFIG);
          audit.record(ID, ACTOR, descriptor.make(100), status, 0, failure.value());
          assertEquals(1, logger.entries.size());
          var entry = logger.entries.getFirst();
          var json = entry.json();
          Set<String> keys =
              new HashSet<>(
                  Set.of(
                      TIMESTAMP,
                      LEVEL,
                      SERVICE,
                      "appVersion",
                      "configVersion",
                      CATEGORY,
                      ACTION,
                      OUTCOME,
                      REQUEST,
                      ACTOR_NAME,
                      ACTOR_ROLE,
                      STATUS,
                      BYTES,
                      DETAILS));
          if (failure.error() != null) keys.add(ERROR_CODE);
          assertEquals(keys, json.keySet());
          assertEquals("2026-11-06T00:00:01.123Z", json.get(TIMESTAMP).getAsString());
          assertEquals(failure.level(), json.get(LEVEL).getAsString());
          assertEquals(failure.loggerLevel(), entry.level());
          assertEquals("WEB", json.get(SERVICE).getAsString());
          assertEquals(APP, json.get("appVersion").getAsString());
          assertEquals(CONFIG, json.get("configVersion").getAsString());
          assertEquals("ACTION", json.get(CATEGORY).getAsString());
          assertEquals(
              status == RANGE_REJECTED ? REJECTED : descriptor.action(),
              json.get(ACTION).getAsString());
          assertEquals(
              failure.value() != Failure.NONE
                  ? "FAILURE"
                  : status == RANGE_REJECTED ? "DENIED" : "SUCCESS",
              json.get(OUTCOME).getAsString());
          assertEquals(ID.toString(), json.get(REQUEST).getAsString());
          assertEquals(FIXTURE_USER, json.get(ACTOR_NAME).getAsString());
          assertEquals("USER", json.get(ACTOR_ROLE).getAsString());
          assertEquals(status, json.get(STATUS).getAsInt());
          assertEquals(0, json.get(BYTES).getAsLong());
          var details = json.getAsJsonObject(DETAILS);
          assertEquals(Set.of(MEDIA_TYPE, LOGICAL_ID, REASON), details.keySet());
          assertEquals(descriptor.typeName(), details.get(MEDIA_TYPE).getAsString());
          assertEquals(descriptor.logical(), details.get(LOGICAL_ID).getAsString());
          assertEquals(failure.value().name(), details.get(REASON).getAsString());
          if (failure.error() != null)
            assertEquals(failure.error(), json.get(ERROR_CODE).getAsString());
          assertFalse(entry.text().contains(descriptor.path()));
          assertFalse(entry.text().contains(descriptor.fileName()));
          assertFalse(entry.text().contains("a".repeat(64)));
          assertFalse(entry.text().contains("0".repeat(64)));
          assertFalse(entry.text().contains("authenticationContext"));
          assertFalse(entry.text().contains("loginAt"));
        }
  }

  @Test
  void media002StatusAndByteBoundariesRejectWithoutLogging() {
    var logger = new CapturingLogger();
    var audit = new WebMediaAudit(logger, CLOCK, APP, CONFIG);
    var descriptor = DESCRIPTORS.getFirst().make(100);
    for (int status :
        new int[] {Integer.MIN_VALUE, 199, 201, 205, 207, 415, 417, 502, 504, Integer.MAX_VALUE})
      assertThrows(
          IllegalArgumentException.class,
          () -> audit.record(ID, ACTOR, descriptor, status, 0, Failure.IO));
    assertThrows(
        IllegalArgumentException.class,
        () -> audit.record(ID, ACTOR, descriptor, UNAVAILABLE, 0, Failure.NONE));
    for (long bytes : new long[] {Long.MIN_VALUE, -1, 101, Long.MAX_VALUE})
      assertThrows(
          IllegalArgumentException.class,
          () -> audit.record(ID, ACTOR, descriptor, OK, bytes, Failure.NONE));
    assertTrue(logger.entries.isEmpty());
    audit.record(ID, ACTOR, descriptor, OK, 100, Failure.NONE);
    assertEquals(100, logger.entries.getFirst().json().get(BYTES).getAsLong());
    audit.record(
        ID,
        ACTOR,
        DESCRIPTORS.getFirst().make(999_999_999_999L),
        PARTIAL,
        999_999_999_999L,
        Failure.NONE);
    assertEquals(999_999_999_999L, logger.entries.getLast().json().get(BYTES).getAsLong());
  }

  @Test
  void media003ConstructorVersionsAndAllNullsEstablishBoundaryContract() {
    var logger = new CapturingLogger();
    assertThrows(NullPointerException.class, () -> new WebMediaAudit(null, CLOCK, APP, CONFIG));
    assertThrows(NullPointerException.class, () -> new WebMediaAudit(logger, null, APP, CONFIG));
    assertThrows(NullPointerException.class, () -> new WebMediaAudit(logger, CLOCK, null, CONFIG));
    assertThrows(NullPointerException.class, () -> new WebMediaAudit(logger, CLOCK, APP, null));
    for (String version :
        List.of("", "x".repeat(65), ".bad", "space bad", "日本語", "a\n", "a/b", "a\u2028")) {
      assertThrows(
          IllegalArgumentException.class, () -> new WebMediaAudit(logger, CLOCK, version, CONFIG));
      assertThrows(
          IllegalArgumentException.class, () -> new WebMediaAudit(logger, CLOCK, APP, version));
    }
    new WebMediaAudit(logger, CLOCK, "x".repeat(64), "Z._+-0");
    assertTrue(logger.entries.isEmpty());
  }

  @Test
  void media004EveryRecordNullAndMissingClockIsRejected() {
    var logger = new CapturingLogger();
    var audit = new WebMediaAudit(logger, CLOCK, APP, CONFIG);
    var descriptor = DESCRIPTORS.getFirst().make(100);
    assertThrows(
        NullPointerException.class,
        () -> audit.record(null, ACTOR, descriptor, OK, 0, Failure.NONE));
    assertThrows(
        NullPointerException.class, () -> audit.record(ID, null, descriptor, OK, 0, Failure.NONE));
    assertThrows(
        NullPointerException.class, () -> audit.record(ID, ACTOR, null, OK, 0, Failure.NONE));
    assertThrows(
        NullPointerException.class, () -> audit.record(ID, ACTOR, descriptor, OK, 0, null));
    var clock = new ControlledClock();
    clock.missing = true;
    var missing = new WebMediaAudit(logger, clock, APP, CONFIG);
    assertThrows(
        NullPointerException.class,
        () -> missing.record(ID, ACTOR, descriptor, OK, 0, Failure.NONE));
    assertTrue(logger.entries.isEmpty());
  }

  @Test
  void media005ClockFailuresAndTimezoneNeverBecomeSuccessfulEvents() {
    var logger = new CapturingLogger();
    var clock = new ControlledClock();
    var fault = new DateTimeException("public clock fixture");
    clock.failure = fault;
    var audit = new WebMediaAudit(logger, clock, APP, CONFIG);
    assertSame(
        fault,
        assertThrows(
            DateTimeException.class,
            () -> audit.record(ID, ACTOR, DESCRIPTORS.getFirst().make(100), OK, 0, Failure.NONE)));
    assertTrue(logger.entries.isEmpty());
    new WebMediaAudit(logger, Clock.fixed(NOW, ZoneOffset.ofHours(-8)), APP, CONFIG)
        .record(ID, ACTOR, DESCRIPTORS.getFirst().make(100), OK, 0, Failure.NONE);
    assertEquals(
        "2026-11-06T00:00:01.123Z", logger.entries.getFirst().json().get(TIMESTAMP).getAsString());
  }

  @Test
  void media006LoggerRuntimeAndErrorPropagateWithoutRetryOrNormalizing() {
    for (boolean after : new boolean[] {false, true})
      for (Throwable fault :
          List.of(
              new IllegalStateException("public logger fixture"),
              new AssertionError("public logger fixture"))) {
        var logger = new CapturingLogger();
        logger.failure = fault;
        logger.afterCapture = after;
        var audit = new WebMediaAudit(logger, CLOCK, APP, CONFIG);
        assertSame(
            fault,
            assertThrows(
                fault.getClass(),
                () ->
                    audit.record(
                        ID, ACTOR, DESCRIPTORS.getFirst().make(100), OK, 0, Failure.NONE)));
        assertEquals(1, logger.calls);
        assertEquals(after ? 1 : 0, logger.entries.size());
      }
  }

  @Test
  void media007UnicodeRedactionAndRepeatedImmutableJsonRemainIndependent() {
    var logger = new CapturingLogger();
    var audit = new WebMediaAudit(logger, CLOCK, APP, CONFIG);
    audit.record(
        ID,
        actor("e\u0301\u2028x\u2029y", UserRole.ADMIN),
        DESCRIPTORS.getFirst().make(100),
        OK,
        3,
        Failure.NONE);
    String first = logger.entries.getFirst().text();
    var json = logger.entries.getFirst().json();
    assertEquals("é x y", json.get(ACTOR_NAME).getAsString());
    assertEquals("ADMIN", json.get(ACTOR_ROLE).getAsString());
    for (String value :
        List.of(
            "\n",
            "\r",
            "\u2028",
            "\u2029",
            "authenticationContext",
            "storageRelativePath",
            "sha256",
            "fileName")) assertFalse(first.contains(value));
    json.addProperty("changed", true);
    assertFalse(logger.entries.getFirst().json().has("changed"));
    audit.record(
        new UUID(0, 12), ACTOR, DESCRIPTORS.getLast().make(100), PARTIAL, 5, Failure.CLIENT_ABORT);
    assertEquals(first, logger.entries.getFirst().text());
    assertEquals(3, logger.entries.getFirst().json().get(BYTES).getAsInt());
    assertEquals(5, logger.entries.getLast().json().get(BYTES).getAsInt());
    assertEquals("FAILURE", logger.entries.getLast().json().get(OUTCOME).getAsString());
  }

  @Test
  void media008OwnConcurrentCallsHaveNoMutableEventRetention() throws Exception {
    var logger = new CapturingLogger();
    var audit = new WebMediaAudit(logger, CLOCK, APP, CONFIG);
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first =
          workers.submit(
              () ->
                  audit.record(
                      new UUID(0, 21),
                      ACTOR,
                      DESCRIPTORS.getFirst().make(100),
                      PARTIAL,
                      7,
                      Failure.NONE));
      var second =
          workers.submit(
              () ->
                  audit.record(
                      new UUID(0, 22),
                      actor("public-admin", UserRole.ADMIN),
                      DESCRIPTORS.getLast().make(100),
                      OK,
                      9,
                      Failure.IO));
      first.get(5, TimeUnit.SECONDS);
      second.get(5, TimeUnit.SECONDS);
    }
    assertEquals(2, logger.entries.size());
    var byId = new java.util.HashMap<UUID, JsonObject>();
    for (Entry entry : logger.entries)
      byId.put(UUID.fromString(entry.json().get(REQUEST).getAsString()), entry.json());
    assertEquals(7, byId.get(new UUID(0, 21)).get(BYTES).getAsInt());
    assertEquals(STREAMED, byId.get(new UUID(0, 21)).get(ACTION).getAsString());
    assertEquals("USER", byId.get(new UUID(0, 21)).get(ACTOR_ROLE).getAsString());
    assertEquals(9, byId.get(new UUID(0, 22)).get(BYTES).getAsInt());
    assertEquals("FILE_IO", byId.get(new UUID(0, 22)).get(ERROR_CODE).getAsString());
    assertEquals("ADMIN", byId.get(new UUID(0, 22)).get(ACTOR_ROLE).getAsString());
  }

  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(
        name,
        role,
        AuthenticationContext.of("0".repeat(64)),
        Instant.parse("1980-01-01T00:00:00Z"));
  }

  private record DescriptorCase(
      MediaType type,
      String logical,
      String path,
      String fileName,
      String mime,
      ContentDisposition disposition,
      String typeName,
      String action) {
    MediaDescriptor make(long bytes) {
      return new MediaDescriptor(
          type, logical, path, fileName, bytes, "a".repeat(64), mime, disposition);
    }
  }

  private record FailureCase(
      Failure value, String level, Level loggerLevel, @Nullable String error) {}

  private record Entry(Level level, String text) {
    JsonObject json() {
      return JsonParser.parseString(text).getAsJsonObject();
    }
  }

  private static final class ControlledClock extends Clock {
    boolean missing;
    @Nullable RuntimeException failure;

    @Override
    public ZoneId getZone() {
      return ZoneOffset.UTC;
    }

    @Override
    public Clock withZone(ZoneId zone) {
      return this;
    }

    @Override
    public Instant instant() {
      if (failure != null) throw failure;
      return missing ? null : NOW;
    }
  }

  private static final class CapturingLogger implements Logger {
    final List<Entry> entries = new CopyOnWriteArrayList<>();
    @Nullable Throwable failure;
    boolean afterCapture;
    int calls;

    @Override
    public String getName() {
      return "public.media.fixture";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    private void failIfPresent() {
      if (failure instanceof RuntimeException runtime) throw runtime;
      if (failure instanceof Error fatal) throw fatal;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      fail("Throwable overload forbidden");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... params) {
      calls++;
      assertNull(bundle);
      assertNull(params);
      if (!afterCapture) failIfPresent();
      entries.add(new Entry(level, format));
      if (afterCapture) failIfPresent();
    }
  }
}
