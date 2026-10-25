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
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-WEB-001/PT-WEB-095..100; AUT-001..004/MON-004; UI226/252; SS314/351/352. */
class WebSecurityAuditTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-09T00:00:00.123987Z"), ZoneOffset.ofHours(9));
  private static final UUID ID = UUID.fromString("00000000-0000-0000-0000-000000000123");
  private static final Optional<String> IP = Optional.of("203.0.113.1");
  private static final Optional<SessionPrincipal> ACTOR =
      Optional.of(actor("reader", UserRole.USER));

  @Test
  void web095AllSecurityEventsUseClosedIndependentJson() {
    var logger = new CapturingLogger();
    var audit = new WebSecurityAudit(logger, CLOCK, "1.2.3+build", "cfg-1");
    String[][] expected = {
      {"LOGIN_SUCCEEDED", "AUTHENTICATED", "SUCCESS", "INFO"},
      {"LOGIN_FAILED", "INVALID_CREDENTIALS", "DENIED", "WARN"},
      {"LOGIN_LOCKED", "LOCKED", "DENIED", "WARN"},
      {"AUTHORIZATION_DENIED", "CSRF", "DENIED", "WARN"},
      {"AUTHORIZATION_DENIED", "ROLE", "DENIED", "WARN"},
      {"AUTHORIZATION_DENIED", "PROXY", "DENIED", "WARN"},
      {"AUTHORIZATION_DENIED", "UNAUTHENTICATED", "DENIED", "WARN"},
      {"SESSION_EXPIRED", "API_SESSION_INVALID", "DENIED", "INFO"},
      {"LOGOUT_SUCCEEDED", "REVOKED", "SUCCESS", "INFO"},
      {"LOGOUT_REVOCATION_QUEUED", "RETRY_RETAINED", "SUCCESS", "INFO"}
    };
    for (int i = 0; i < Event.values().length; i++) {
      Event event = Event.values()[i];
      boolean hasActor = i == 0 || (i >= 3 && i <= 5) || i >= 7;
      audit.record(
          ID,
          event,
          Optional.of("2001:db8::1"),
          hasActor ? ACTOR : Optional.empty(),
          i == 2 ? 900 : 0,
          i >= 8 ? Route.LOGOUT : Route.LOGIN);
      var entry = logger.entries.get(i);
      var json = entry.json();
      var keys =
          new HashSet<>(
              Set.of(
                  "timestamp",
                  "level",
                  "service",
                  "appVersion",
                  "configVersion",
                  "category",
                  "action",
                  "outcome",
                  "requestId",
                  "remoteAddress",
                  "details"));
      if (hasActor) keys.addAll(Set.of("actorUsername", "actorRole"));
      assertEquals(keys, json.keySet());
      assertEquals("2026-09-09T00:00:00.123Z", json.get("timestamp").getAsString());
      assertEquals("WEB", json.get("service").getAsString());
      assertEquals("1.2.3+build", json.get("appVersion").getAsString());
      assertEquals("cfg-1", json.get("configVersion").getAsString());
      assertEquals("SECURITY", json.get("category").getAsString());
      assertEquals(ID.toString(), json.get("requestId").getAsString());
      assertEquals("2001:db8:0:0:0:0:0:1", json.get("remoteAddress").getAsString());
      assertEquals(expected[i][0], json.get("action").getAsString());
      assertEquals(expected[i][2], json.get("outcome").getAsString());
      assertEquals(expected[i][3], json.get("level").getAsString());
      assertEquals(i == 0 || i >= 7 ? Level.INFO : Level.WARNING, entry.level());
      if (hasActor) {
        assertEquals("reader", json.get("actorUsername").getAsString());
        assertEquals("USER", json.get("actorRole").getAsString());
      }
      var details = json.getAsJsonObject("details");
      var detailKeys = new HashSet<>(Set.of("reason", "route", "targetType"));
      assertEquals("HTTP_REQUEST", details.get("targetType").getAsString());
      assertEquals(i >= 8 ? "/logout" : "/login", details.get("route").getAsString());
      if (i == 2) {
        detailKeys.add("retryAfterSeconds");
        assertEquals(900, details.get("retryAfterSeconds").getAsInt());
      }
      assertEquals(detailKeys, details.keySet());
      assertEquals(expected[i][1], details.get("reason").getAsString());
      assertTrue(
          details.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8).length < 1024);
    }
    audit.record(ID, Event.LOGIN_LOCKED, IP, Optional.empty(), 0, Route.LOGIN);
    assertEquals(
        0,
        logger
            .entries
            .getLast()
            .json()
            .getAsJsonObject("details")
            .get("retryAfterSeconds")
            .getAsInt());
    String[] routes = {"/login", "/logout", "/**", "/admin/users/**", "/logs"};
    for (int i = 0; i < Route.values().length; i++) {
      audit.record(ID, Event.CSRF_DENIED, IP, ACTOR, 0, Route.values()[i]);
      assertEquals(
          routes[i],
          logger.entries.getLast().json().getAsJsonObject("details").get("route").getAsString());
    }
  }

  @Test
  void web096InvalidEventMetadataNeverReachesLogger() {
    var logger = new CapturingLogger();
    var audit = new WebSecurityAudit(logger, CLOCK, "a", "b");
    for (String invalid :
        List.of("", "a".repeat(65), "日本語", "a b", ".", "a\n", "a/secret", "a:1", "a\u2028")) {
      assertThrows(
          IllegalArgumentException.class, () -> new WebSecurityAudit(logger, CLOCK, invalid, "b"));
      assertThrows(
          IllegalArgumentException.class, () -> new WebSecurityAudit(logger, CLOCK, "a", invalid));
    }
    new WebSecurityAudit(logger, CLOCK, "a".repeat(64), "Z._+-012");
    assertThrows(NullPointerException.class, () -> new WebSecurityAudit(null, CLOCK, "a", "b"));
    assertThrows(NullPointerException.class, () -> new WebSecurityAudit(logger, null, "a", "b"));
    assertThrows(NullPointerException.class, () -> new WebSecurityAudit(logger, CLOCK, null, "b"));
    assertThrows(NullPointerException.class, () -> new WebSecurityAudit(logger, CLOCK, "a", null));
    assertThrows(
        NullPointerException.class,
        () -> audit.record(null, Event.LOGIN_FAILED, IP, Optional.empty(), 0, Route.LOGIN));
    assertThrows(
        NullPointerException.class,
        () -> audit.record(ID, null, IP, Optional.empty(), 0, Route.LOGIN));
    assertThrows(
        NullPointerException.class,
        () -> audit.record(ID, Event.LOGIN_FAILED, null, Optional.empty(), 0, Route.LOGIN));
    assertThrows(
        NullPointerException.class,
        () -> audit.record(ID, Event.LOGIN_FAILED, IP, null, 0, Route.LOGIN));
    assertThrows(
        NullPointerException.class,
        () -> audit.record(ID, Event.LOGIN_FAILED, IP, Optional.empty(), 0, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> audit.record(ID, Event.LOGIN_FAILED, IP, Optional.empty(), 0, Route.ALL_WEB));
    for (Event event : Event.values()) {
      var selected = event == Event.LOGIN_SUCCEEDED ? ACTOR : Optional.<SessionPrincipal>empty();
      for (int retry : new int[] {-1, 901})
        assertThrows(
            IllegalArgumentException.class,
            () -> audit.record(ID, event, IP, selected, retry, Route.LOGIN));
      if (event != Event.LOGIN_LOCKED)
        assertThrows(
            IllegalArgumentException.class,
            () -> audit.record(ID, event, IP, selected, 1, Route.LOGIN));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> audit.record(ID, Event.LOGIN_SUCCEEDED, IP, Optional.empty(), 0, Route.LOGIN));
    for (Event event :
        List.of(Event.LOGIN_FAILED, Event.LOGIN_LOCKED, Event.AUTHENTICATION_REQUIRED))
      assertThrows(
          IllegalArgumentException.class, () -> audit.record(ID, event, IP, ACTOR, 0, Route.LOGIN));
    for (Event event : List.of(Event.LOGIN_SUCCEEDED, Event.LOGIN_FAILED, Event.LOGIN_LOCKED)) {
      var selected = event == Event.LOGIN_SUCCEEDED ? ACTOR : Optional.<SessionPrincipal>empty();
      assertThrows(
          IllegalArgumentException.class,
          () -> audit.record(ID, event, Optional.empty(), selected, 0, Route.LOGIN));
    }
    for (Event event : List.of(Event.LOGOUT_SUCCEEDED, Event.LOGOUT_REVOCATION_QUEUED)) {
      assertThrows(
          IllegalArgumentException.class,
          () -> audit.record(ID, event, IP, Optional.empty(), 0, Route.LOGOUT));
      assertThrows(
          IllegalArgumentException.class,
          () -> audit.record(ID, event, Optional.empty(), ACTOR, 0, Route.LOGOUT));
      assertThrows(
          IllegalArgumentException.class, () -> audit.record(ID, event, IP, ACTOR, 0, Route.LOGIN));
    }
    for (String ip :
        List.of(
            "",
            "localhost",
            "x".repeat(46),
            "203.0.113.999",
            "fe80::1%1",
            "::1%scope",
            "203.0.113.1, 203.0.113.2",
            " 203.0.113.1")) {
      var ex =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  audit.record(
                      ID, Event.LOGIN_FAILED, Optional.of(ip), Optional.empty(), 0, Route.LOGIN));
      assertEquals("security audit address is invalid", ex.getMessage());
      assertNull(ex.getCause());
      assertEquals(0, ex.getSuppressed().length);
    }
    assertTrue(logger.entries.isEmpty());
  }

  @Test
  void web097UnicodeAndSecretCanariesRemainOutsideAudit() {
    var logger = new CapturingLogger();
    var audit = new WebSecurityAudit(logger, CLOCK, "a", "b");
    String[] names = {"e\u0301", "a\u2028b\u2029c", "\"\\<>&", "é".repeat(32)};
    String[] expected = {"é", "a b c", "\"\\<>&", "é".repeat(32)};
    for (int i = 0; i < names.length; i++) {
      audit.record(
          ID,
          Event.LOGIN_SUCCEEDED,
          IP,
          Optional.of(actor(names[i], UserRole.ADMIN)),
          0,
          Route.LOGIN);
      var entry = logger.entries.get(i);
      assertEquals(expected[i], entry.json().get("actorUsername").getAsString());
      assertEquals("ADMIN", entry.json().get("actorRole").getAsString());
      assertFalse(entry.text().contains("\n"));
      assertFalse(entry.text().contains("\r"));
      assertFalse(entry.text().contains("\u2028"));
      assertFalse(entry.text().contains("\u2029"));
      for (String denied :
          List.of(
              "ab".repeat(32),
              "loginAt",
              "authenticationContext",
              "password",
              "cookie",
              "csrf",
              "Throwable",
              "1980-01-01")) assertFalse(entry.text().contains(denied));
    }
    audit.record(ID, Event.LOGIN_FAILED, IP, Optional.empty(), 0, Route.LOGIN);
    assertFalse(logger.entries.getLast().json().has("actorUsername"));
  }

  @Test
  void web098ClockAndLoggerFaultsNeverBecomeSuccessfulAudit() {
    var logger = new CapturingLogger();
    for (boolean missing : new boolean[] {false, true}) {
      Clock clock =
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
              throw new DateTimeException("synthetic clock failure");
            }
          };
      var audit = new WebSecurityAudit(logger, clock, "a", "b");
      if (missing)
        assertThrows(
            NullPointerException.class,
            () -> audit.record(ID, Event.LOGIN_FAILED, IP, Optional.empty(), 0, Route.LOGIN));
      else
        assertThrows(
            DateTimeException.class,
            () -> audit.record(ID, Event.LOGIN_FAILED, IP, Optional.empty(), 0, Route.LOGIN));
    }
    assertTrue(logger.entries.isEmpty());
    var fault = new IllegalStateException("synthetic logger failure");
    Logger failed =
        new CapturingLogger() {
          @Override
          public void log(Level level, ResourceBundle bundle, String format, Object... params) {
            throw fault;
          }
        };
    var audit = new WebSecurityAudit(failed, CLOCK, "a", "b");
    assertSame(
        fault,
        assertThrows(
            IllegalStateException.class,
            () -> audit.record(ID, Event.LOGIN_FAILED, IP, Optional.empty(), 0, Route.LOGIN)));
  }

  @Test
  void web099RepeatedEventsHaveNoMutableJsonOrPrincipalRetention() {
    var logger = new CapturingLogger();
    var audit = new WebSecurityAudit(logger, CLOCK, "a", "b");
    audit.record(ID, Event.LOGIN_SUCCEEDED, IP, ACTOR, 0, Route.LOGIN);
    String first = logger.entries.getFirst().text();
    audit.record(
        new UUID(0, 2), Event.CSRF_DENIED, Optional.empty(), Optional.empty(), 0, Route.LOGIN);
    assertEquals(first, logger.entries.getFirst().text());
    var second = logger.entries.getLast().json();
    assertFalse(second.has("actorUsername"));
    assertFalse(second.has("actorRole"));
    assertFalse(second.has("remoteAddress"));
    assertEquals(
        Set.of("reason", "route", "targetType"), second.getAsJsonObject("details").keySet());
    assertEquals("HTTP_REQUEST", second.getAsJsonObject("details").get("targetType").getAsString());
    assertEquals("CSRF", second.getAsJsonObject("details").get("reason").getAsString());
    second.addProperty("modified", true);
    assertFalse(logger.entries.getLast().json().has("modified"));
    audit.record(
        ID,
        Event.LOGIN_FAILED,
        Optional.of("::ffff:203.0.113.1"),
        Optional.empty(),
        0,
        Route.LOGIN);
    assertEquals("203.0.113.1", logger.entries.getLast().json().get("remoteAddress").getAsString());
  }

  @Test
  void web100ConcurrentAuditEventsStayIndependent() throws Exception {
    var logger = new CapturingLogger();
    var audit = new WebSecurityAudit(logger, CLOCK, "a", "b");
    try (var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        int number = i;
        jobs.add(
            () -> {
              boolean success = number % 2 == 0;
              audit.record(
                  new UUID(0, number),
                  success ? Event.LOGIN_SUCCEEDED : Event.LOGIN_LOCKED,
                  Optional.of("203.0.113." + number),
                  success
                      ? Optional.of(actor("reader" + number, UserRole.ADMIN))
                      : Optional.empty(),
                  success ? 0 : number,
                  Route.LOGIN);
              return null;
            });
      }
      synchronized (audit) {
        for (var job : pool.invokeAll(jobs)) job.get(10, TimeUnit.SECONDS);
      }
    }
    assertEquals(100, logger.entries.size());
    var seen = new HashSet<UUID>();
    for (var entry : logger.entries) {
      var json = entry.json();
      UUID id = UUID.fromString(json.get("requestId").getAsString());
      assertTrue(seen.add(id));
      long number = id.getLeastSignificantBits();
      assertEquals("203.0.113." + number, json.get("remoteAddress").getAsString());
      if (number % 2 == 0) {
        assertEquals("reader" + number, json.get("actorUsername").getAsString());
        assertEquals("ADMIN", json.get("actorRole").getAsString());
        assertEquals(Level.INFO, entry.level());
      } else {
        assertFalse(json.has("actorUsername"));
        assertEquals(number, json.getAsJsonObject("details").get("retryAfterSeconds").getAsLong());
        assertEquals(Level.WARNING, entry.level());
      }
      assertFalse(entry.text().contains("ab".repeat(32)));
    }
  }

  private static SessionPrincipal actor(String username, UserRole role) {
    return new SessionPrincipal(
        username,
        role,
        AuthenticationContext.of("ab".repeat(32)),
        Instant.parse("1980-01-01T00:00:00Z"));
  }

  private record Entry(Level level, String text) {
    JsonObject json() {
      return JsonParser.parseString(text).getAsJsonObject();
    }
  }

  private static class CapturingLogger implements Logger {
    final List<Entry> entries = new CopyOnWriteArrayList<>();

    @Override
    public String getName() {
      return "synthetic.security";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      fail("Throwable overload must not receive security events");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... params) {
      assertNull(bundle);
      assertNull(params);
      entries.add(new Entry(level, format));
    }
  }
}
