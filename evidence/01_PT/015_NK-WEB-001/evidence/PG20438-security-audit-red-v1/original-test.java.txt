package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** AUT/MON/UI226252/SS314351352/PT-WEB-SECAUD001..010, no actual log backend or DB. */
final class WebSecurityAuditPortTest {
  private static final String K_TIMESTAMP = "timestamp";
  private static final String K_LEVEL = "level";
  private static final String K_SERVICE = "service";
  private static final String K_APP_VERSION = "appVersion";
  private static final String K_CONFIG_VERSION = "configVersion";
  private static final String K_CATEGORY = "category";
  private static final String K_ACTION = "action";
  private static final String K_OUTCOME = "outcome";
  private static final String K_REQUEST = "requestId";
  private static final String K_TARGET_TYPE = "targetType";
  private static final String APP = "v1.0+fixture";
  private static final String CONFIG = "config-1";
  private static final String READER = "public-view";
  private static final String IP = "192.0.2.9";
  private static final String INFO = "INFO";
  private static final String WARN = "WARN";
  private static final String DENIED = "DENIED";
  private static final String SUCCESS = "SUCCESS";
  private static final String AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED";
  private static final String K_ACTOR = "actorUsername";
  private static final String K_ROLE = "actorRole";
  private static final String K_REMOTE = "remoteAddress";
  private static final String K_DETAILS = "details";
  private static final String K_ROUTE = "route";
  private static final String K_REASON = "reason";
  private static final String K_RETRY = "retryAfterSeconds";
  private static final String METADATA_ERROR = "security audit metadata is invalid";
  private static final Instant AT = Instant.parse("2026-11-06T00:00:00.123456789Z");
  private static final Clock CLOCK = Clock.fixed(AT, ZoneOffset.ofHours(9));
  private static final UUID REQUEST = new UUID(0, 1);
  private static final Optional<String> CLIENT = Optional.of(IP);
  private static final Optional<SessionPrincipal> ACTOR =
      Optional.of(displayPrincipal(READER, UserRole.USER));
  private static final Map<Route, String> ROUTES =
      Map.of(
          Route.LOGIN,
          "/login",
          Route.LOGOUT,
          "/logout",
          Route.ALL_WEB,
          "/**",
          Route.ADMIN_USERS,
          "/admin/users/**",
          Route.LOGS,
          "/logs");

  private record Logged(Level level, String message) {}

  private record Golden(
      Event event,
      String action,
      String reason,
      String outcome,
      Level level,
      Route route,
      boolean actor) {}

  private static final List<Golden> CATALOG =
      List.of(
          new Golden(
              Event.LOGIN_SUCCEEDED,
              "LOGIN_SUCCEEDED",
              "AUTHENTICATED",
              SUCCESS,
              Level.INFO,
              Route.LOGIN,
              true),
          new Golden(
              Event.LOGIN_FAILED,
              "LOGIN_FAILED",
              "INVALID_CREDENTIALS",
              DENIED,
              Level.WARNING,
              Route.LOGIN,
              false),
          new Golden(
              Event.LOGIN_LOCKED,
              "LOGIN_LOCKED",
              "LOCKED",
              DENIED,
              Level.WARNING,
              Route.LOGIN,
              false),
          new Golden(
              Event.CSRF_DENIED,
              AUTHORIZATION_DENIED,
              "CSRF",
              DENIED,
              Level.WARNING,
              Route.ALL_WEB,
              false),
          new Golden(
              Event.ROLE_DENIED,
              AUTHORIZATION_DENIED,
              "ROLE",
              DENIED,
              Level.WARNING,
              Route.ADMIN_USERS,
              true),
          new Golden(
              Event.PROXY_DENIED,
              AUTHORIZATION_DENIED,
              "PROXY",
              DENIED,
              Level.WARNING,
              Route.ALL_WEB,
              false),
          new Golden(
              Event.AUTHENTICATION_REQUIRED,
              AUTHORIZATION_DENIED,
              "UNAUTHENTICATED",
              DENIED,
              Level.WARNING,
              Route.ALL_WEB,
              false),
          new Golden(
              Event.API_SESSION_INVALID,
              "SESSION_EXPIRED",
              "API_SESSION_INVALID",
              DENIED,
              Level.INFO,
              Route.LOGS,
              true),
          new Golden(
              Event.LOGOUT_SUCCEEDED,
              "LOGOUT_SUCCEEDED",
              "REVOKED",
              SUCCESS,
              Level.INFO,
              Route.LOGOUT,
              true),
          new Golden(
              Event.LOGOUT_REVOCATION_QUEUED,
              "LOGOUT_REVOCATION_QUEUED",
              "RETRY_RETAINED",
              SUCCESS,
              Level.INFO,
              Route.LOGOUT,
              true));

  private static final class Sink implements Logger {
    final ConcurrentLinkedQueue<Logged> rows = new ConcurrentLinkedQueue<>();
    final AtomicInteger attempts = new AtomicInteger();
    Throwable failure;

    @Override
    public String getName() {
      return "owned-memory-security-audit";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      attempts.incrementAndGet();
      assertNull(bundle);
      assertNull(thrown);
      if (failure instanceof RuntimeException runtime) throw runtime;
      if (failure instanceof Error error) throw error;
      rows.add(new Logged(level, message));
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... args) {
      throw new AssertionError("unexpected formatted logger overload");
    }
  }

  private static SessionPrincipal displayPrincipal(String username, UserRole role) {
    return new SessionPrincipal(
        username, role, AuthenticationContext.of("c".repeat(64)), Instant.EPOCH);
  }

  private static WebSecurityAudit audit(Sink sink) {
    return new WebSecurityAudit(sink, CLOCK, APP, CONFIG);
  }

  private static JsonObject single(Sink sink) {
    assertEquals(1, sink.rows.size());
    return JsonParser.parseString(sink.rows.element().message()).getAsJsonObject();
  }

  private static void expected(
      JsonObject json, Golden row, boolean address, String username, String role, int retry) {
    var keys =
        new HashSet<>(
            Set.of(
                K_TIMESTAMP,
                K_LEVEL,
                K_SERVICE,
                K_APP_VERSION,
                K_CONFIG_VERSION,
                K_CATEGORY,
                K_ACTION,
                K_OUTCOME,
                K_REQUEST,
                K_DETAILS));
    if (row.actor()) {
      keys.add(K_ACTOR);
      keys.add(K_ROLE);
    }
    if (address) keys.add(K_REMOTE);
    assertEquals(keys, json.keySet());
    assertEquals("2026-11-06T00:00:00.123Z", json.get(K_TIMESTAMP).getAsString());
    assertEquals(row.level() == Level.INFO ? INFO : WARN, json.get(K_LEVEL).getAsString());
    assertEquals("WEB", json.get(K_SERVICE).getAsString());
    assertEquals(APP, json.get(K_APP_VERSION).getAsString());
    assertEquals(CONFIG, json.get(K_CONFIG_VERSION).getAsString());
    assertEquals("SECURITY", json.get(K_CATEGORY).getAsString());
    assertEquals(row.action(), json.get(K_ACTION).getAsString());
    assertEquals(row.outcome(), json.get(K_OUTCOME).getAsString());
    assertEquals("00000000-0000-0000-0000-000000000001", json.get(K_REQUEST).getAsString());
    if (row.actor()) {
      assertEquals(username, json.get(K_ACTOR).getAsString());
      assertEquals(role, json.get(K_ROLE).getAsString());
    }
    if (address) assertEquals(IP, json.get(K_REMOTE).getAsString());
    var details = json.getAsJsonObject(K_DETAILS);
    var detailKeys = new HashSet<>(Set.of(K_REASON, K_ROUTE, K_TARGET_TYPE));
    if (row.event() == Event.LOGIN_LOCKED) detailKeys.add(K_RETRY);
    assertEquals(detailKeys, details.keySet());
    assertEquals(row.reason(), details.get(K_REASON).getAsString());
    assertEquals(ROUTES.get(row.route()), details.get(K_ROUTE).getAsString());
    assertEquals("HTTP_REQUEST", details.get(K_TARGET_TYPE).getAsString());
    if (row.event() == Event.LOGIN_LOCKED) assertEquals(retry, details.get(K_RETRY).getAsInt());
  }

  @Test
  void allTenEventsMatchIndependentCatalogAndJsonSchema() {
    assertEquals(
        Set.of(Event.values()), new HashSet<>(CATALOG.stream().map(Golden::event).toList()));
    for (var row : CATALOG) {
      var sink = new Sink();
      var principal = row.actor() ? ACTOR : Optional.<SessionPrincipal>empty();
      int retry = row.event() == Event.LOGIN_LOCKED ? 900 : 0;
      audit(sink).record(REQUEST, row.event(), CLIENT, principal, retry, row.route());
      expected(single(sink), row, true, READER, "USER", retry);
      assertEquals(row.level(), sink.rows.element().level());
      assertEquals(1, sink.attempts.get());
    }
  }

  @Test
  void allFiveRegisteredRoutesAndOptionalFieldsRemainClosed() {
    assertEquals(5, ROUTES.size());
    for (var entry : ROUTES.entrySet()) {
      var sink = new Sink();
      audit(sink)
          .record(
              REQUEST, Event.ROLE_DENIED, Optional.empty(), Optional.empty(), 0, entry.getKey());
      var json = single(sink);
      assertEquals(entry.getValue(), json.getAsJsonObject(K_DETAILS).get(K_ROUTE).getAsString());
      assertFalse(json.has(K_REMOTE));
      assertFalse(json.has(K_ACTOR));
      assertFalse(json.has(K_ROLE));
      assertEquals(AUTHORIZATION_DENIED, json.get(K_ACTION).getAsString());
    }
  }

  @Test
  void actorSeparatorsAreRedactedAndContextNeverAppears() {
    var sink = new Sink();
    var user = displayPrincipal("first\u2028middle\u2029last", UserRole.ADMIN);
    audit(sink).record(REQUEST, Event.ROLE_DENIED, CLIENT, Optional.of(user), 0, Route.ADMIN_USERS);
    var json = single(sink);
    assertEquals("first middle last", json.get(K_ACTOR).getAsString());
    assertEquals("ADMIN", json.get(K_ROLE).getAsString());
    String text = sink.rows.element().message();
    assertFalse(text.contains("c".repeat(64)));
    assertFalse(text.contains("\u2028"));
    assertFalse(text.contains("\u2029"));
    for (String name : List.of("é".repeat(32), "e\u0301")) {
      var second = new Sink();
      audit(second)
          .record(
              REQUEST,
              Event.LOGIN_SUCCEEDED,
              CLIENT,
              Optional.of(displayPrincipal(name, UserRole.USER)),
              0,
              Route.LOGIN);
      assertEquals(name.equals("e\u0301") ? "é" : name, single(second).get(K_ACTOR).getAsString());
    }
  }

  @Test
  void lockRetryBoundariesZeroOneAndNineHundredAreExplicit() {
    for (int retry : new int[] {0, 1, 900}) {
      var sink = new Sink();
      audit(sink).record(REQUEST, Event.LOGIN_LOCKED, CLIENT, Optional.empty(), retry, Route.LOGIN);
      assertEquals(retry, single(sink).getAsJsonObject(K_DETAILS).get(K_RETRY).getAsInt());
    }
  }

  private record Bad(
      Event event,
      Optional<String> address,
      Optional<SessionPrincipal> actor,
      int retry,
      Route route) {}

  @Test
  void invalidMetadataNeverEmitsARecord() {
    List<Bad> bad =
        List.of(
            new Bad(Event.LOGIN_LOCKED, CLIENT, Optional.empty(), -1, Route.LOGIN),
            new Bad(Event.LOGIN_LOCKED, CLIENT, Optional.empty(), 901, Route.LOGIN),
            new Bad(Event.LOGIN_FAILED, CLIENT, Optional.empty(), 1, Route.LOGIN),
            new Bad(Event.LOGIN_SUCCEEDED, CLIENT, Optional.empty(), 0, Route.LOGIN),
            new Bad(Event.AUTHENTICATION_REQUIRED, CLIENT, ACTOR, 0, Route.ALL_WEB),
            new Bad(Event.LOGIN_FAILED, CLIENT, ACTOR, 0, Route.LOGIN),
            new Bad(Event.LOGIN_LOCKED, CLIENT, ACTOR, 0, Route.LOGIN),
            new Bad(Event.LOGIN_SUCCEEDED, Optional.empty(), ACTOR, 0, Route.LOGIN),
            new Bad(Event.LOGIN_FAILED, Optional.empty(), Optional.empty(), 0, Route.LOGIN),
            new Bad(Event.LOGIN_LOCKED, Optional.empty(), Optional.empty(), 0, Route.LOGIN),
            new Bad(Event.LOGIN_SUCCEEDED, CLIENT, ACTOR, 0, Route.LOGS),
            new Bad(Event.LOGOUT_SUCCEEDED, CLIENT, Optional.empty(), 0, Route.LOGOUT),
            new Bad(Event.LOGOUT_REVOCATION_QUEUED, CLIENT, Optional.empty(), 0, Route.LOGOUT),
            new Bad(Event.LOGOUT_SUCCEEDED, Optional.empty(), ACTOR, 0, Route.LOGOUT),
            new Bad(Event.LOGOUT_REVOCATION_QUEUED, Optional.empty(), ACTOR, 0, Route.LOGOUT),
            new Bad(Event.LOGOUT_SUCCEEDED, CLIENT, ACTOR, 0, Route.LOGIN),
            new Bad(Event.LOGOUT_REVOCATION_QUEUED, CLIENT, ACTOR, 0, Route.LOGS));
    for (var item : bad) {
      var sink = new Sink();
      var e =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  audit(sink)
                      .record(
                          REQUEST,
                          item.event(),
                          item.address(),
                          item.actor(),
                          item.retry(),
                          item.route()));
      assertEquals(METADATA_ERROR, e.getMessage());
      assertEquals(0, sink.attempts.get());
      assertTrue(sink.rows.isEmpty());
    }
  }

  @Test
  void nullConstructorAndRecordContractsReject() {
    var sink = new Sink();
    for (Executable invalid :
        List.<Executable>of(
            () -> new WebSecurityAudit(null, CLOCK, APP, CONFIG),
            () -> new WebSecurityAudit(sink, null, APP, CONFIG),
            () -> new WebSecurityAudit(sink, CLOCK, null, CONFIG),
            () -> new WebSecurityAudit(sink, CLOCK, APP, null),
            () -> audit(sink).record(null, Event.ROLE_DENIED, CLIENT, ACTOR, 0, Route.ALL_WEB),
            () -> audit(sink).record(REQUEST, null, CLIENT, ACTOR, 0, Route.ALL_WEB),
            () -> audit(sink).record(REQUEST, Event.ROLE_DENIED, null, ACTOR, 0, Route.ALL_WEB),
            () -> audit(sink).record(REQUEST, Event.ROLE_DENIED, CLIENT, null, 0, Route.ALL_WEB),
            () -> audit(sink).record(REQUEST, Event.ROLE_DENIED, CLIENT, ACTOR, 0, null)))
      assertThrows(NullPointerException.class, invalid);
    assertEquals(0, sink.attempts.get());
  }

  @Test
  void literalAddressesCanonicalizeWithoutDnsAndInvalidInputsDoNotLog() {
    Map<String, String> good =
        Map.of(
            IP,
            IP,
            "2001:0db8:0000:0000:0000:0000:0000:0001",
            "2001:db8:0:0:0:0:0:1",
            "ffff:ffff:ffff:ffff:ffff:ffff:255.255.255.255",
            "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff");
    for (var address : good.entrySet()) {
      var sink = new Sink();
      audit(sink)
          .record(
              REQUEST,
              Event.ROLE_DENIED,
              Optional.of(address.getKey()),
              Optional.empty(),
              0,
              Route.ALL_WEB);
      assertEquals(address.getValue(), single(sink).get(K_REMOTE).getAsString());
    }
    for (String address :
        List.of("", "not-a-hostname.example", "1".repeat(46), "fe80::1%2", "192.0.2.999")) {
      var sink = new Sink();
      var e =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  audit(sink)
                      .record(
                          REQUEST,
                          Event.ROLE_DENIED,
                          Optional.of(address),
                          Optional.empty(),
                          0,
                          Route.ALL_WEB));
      assertEquals("security audit address is invalid", e.getMessage());
      assertNull(e.getCause());
      assertEquals(0, sink.attempts.get());
    }
  }

  @Test
  void versionOneAndSixtyFourAreRetainedAndInvalidFormatsReject() {
    for (String version : List.of("a", "A".repeat(64), "v1.0+fixture")) {
      var sink = new Sink();
      new WebSecurityAudit(sink, CLOCK, version, version)
          .record(REQUEST, Event.ROLE_DENIED, Optional.empty(), Optional.empty(), 0, Route.ALL_WEB);
      var json = single(sink);
      assertEquals(version, json.get(K_APP_VERSION).getAsString());
      assertEquals(version, json.get(K_CONFIG_VERSION).getAsString());
    }
    for (String version : List.of("", "_bad", "a".repeat(65), "é", "a\nb", "a b")) {
      var sink = new Sink();
      assertThrows(
          IllegalArgumentException.class, () -> new WebSecurityAudit(sink, CLOCK, version, CONFIG));
      assertThrows(
          IllegalArgumentException.class, () -> new WebSecurityAudit(sink, CLOCK, APP, version));
      assertEquals(0, sink.attempts.get());
    }
  }

  @Test
  void clockAndLoggerFailuresPropagateWithoutProviderDiagnostics() {
    for (Throwable failure :
        List.of(
            new IllegalStateException("synthetic sink fault"),
            new AssertionError("synthetic fatal"))) {
      var sink = new Sink();
      sink.failure = failure;
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () ->
                  audit(sink).record(REQUEST, Event.ROLE_DENIED, CLIENT, ACTOR, 0, Route.ALL_WEB)));
      assertEquals(1, sink.attempts.get());
      assertTrue(sink.rows.isEmpty());
    }
    var clockFailure = new IllegalStateException("synthetic clock fault");
    for (boolean missing : List.of(false, true)) {
      Clock broken =
          new Clock() {
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
              if (missing) return null;
              throw clockFailure;
            }
          };
      var sink = new Sink();
      var audit = new WebSecurityAudit(sink, broken, APP, CONFIG);
      if (missing)
        assertThrows(
            NullPointerException.class,
            () -> audit.record(REQUEST, Event.ROLE_DENIED, CLIENT, ACTOR, 0, Route.ALL_WEB));
      else
        assertSame(
            clockFailure,
            assertThrows(
                IllegalStateException.class,
                () -> audit.record(REQUEST, Event.ROLE_DENIED, CLIENT, ACTOR, 0, Route.ALL_WEB)));
      assertEquals(0, sink.attempts.get());
    }
  }

  @Test
  void concurrentRecordsKeepRequestIdsAndActorsSeparate() throws Exception {
    var sink = new Sink();
    var audit = audit(sink);
    try (var workers = Executors.newFixedThreadPool(2)) {
      var pending = new ArrayList<Future<Boolean>>();
      for (int i = 0; i < 8; i++) {
        int number = i;
        pending.add(
            workers.submit(
                () -> {
                  audit.record(
                      new UUID(1, number + 1),
                      Event.ROLE_DENIED,
                      CLIENT,
                      Optional.of(displayPrincipal(READER + number, UserRole.USER)),
                      0,
                      Route.ADMIN_USERS);
                  return true;
                }));
      }
      for (var future : pending) assertTrue(future.get(10, TimeUnit.SECONDS));
    }
    assertEquals(8, sink.rows.size());
    var ids = new HashSet<String>();
    var names = new HashSet<String>();
    for (var row : sink.rows) {
      var json = JsonParser.parseString(row.message()).getAsJsonObject();
      ids.add(json.get(K_REQUEST).getAsString());
      names.add(json.get(K_ACTOR).getAsString());
    }
    assertEquals(8, ids.size());
    assertEquals(8, names.size());
    for (int i = 0; i < 8; i++) {
      assertTrue(ids.contains(new UUID(1, i + 1).toString()));
      assertTrue(names.contains(READER + i));
    }
  }
}
