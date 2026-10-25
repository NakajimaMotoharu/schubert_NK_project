package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

/** NK-WEB-001/PT-WEB-044..049; FUN-001/AUT-001..004; UI226; SS314/331/352; SSC-042. */
class SpringWebSessionTest {
  private static WebLogDatabaseFixture db;
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final SessionPrincipal PRINCIPAL =
      new SessionPrincipal(
          "reader",
          UserRole.ADMIN,
          AuthenticationContext.of("b".repeat(64)),
          Instant.parse("2026-09-08T00:00:00Z"));

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @Test
  void web044LifecycleRotateAndTouchPreserveIdentity() throws Exception {
    try (var f = new Fixture(db)) {
      var first = f.repository.create();
      var rotated = f.repository.rotate(first.sessionId()).orElseThrow();
      assertNotEquals(first.sessionId().cookieValue(), rotated.sessionId().cookieValue());
      assertEquals(new UUID(0, 2), rotated.row().identity().id());
      assertEquals("04".repeat(32), rotated.attributes().csrfToken().orElseThrow());
      assertTrue(rotated.attributes().principal().isEmpty());
      assertTrue(f.repository.rotate(first.sessionId()).isEmpty());
      assertTrue(f.repository.touch(first.sessionId(), NOW).isEmpty());
      var loggedIn = f.repository.authenticate(rotated.sessionId(), PRINCIPAL).orElseThrow();
      var again = f.repository.rotate(loggedIn.sessionId()).orElseThrow();
      assertEquals(PRINCIPAL, again.attributes().principal().orElseThrow());
      var touched =
          f.repository.touch(again.sessionId(), NOW.plusSeconds(20).plusNanos(789)).orElseThrow();
      assertEquals(NOW.plusSeconds(20), touched.row().lastAccessedAt());
      assertEquals(NOW.plusSeconds(28820), touched.row().expiresAt());
      f.clock.value = NOW.plusSeconds(10);
      assertEquals(
          touched.row().lastAccessedAt(),
          f.repository
              .touch(again.sessionId(), NOW.minusSeconds(1))
              .orElseThrow()
              .row()
              .lastAccessedAt());
      f.random.fixed = 7;
      unavailable(() -> f.repository.rotate(again.sessionId()));
      f.random.fixed = null;
      f.failure = "connection.commit";
      unavailable(() -> f.repository.touch(again.sessionId(), NOW));
      unavailable(() -> f.repository.rotate(again.sessionId()));
      f.failure = "";
      assertEquals(1, count());
      f.clock.value = NOW.plusSeconds(28820);
      assertTrue(f.repository.touch(again.sessionId(), NOW).isEmpty());
      assertEquals(0, count());
      assertThrows(NullPointerException.class, () -> f.repository.rotate(null));
      assertThrows(NullPointerException.class, () -> f.repository.touch(null, NOW));
      assertThrows(NullPointerException.class, () -> f.repository.touch(again.sessionId(), null));
    }
  }

  @Test
  void web045ProjectionAndImmediatePersistenceAreClosed() throws Exception {
    try (var f = new Fixture(db)) {
      var repo = adapter(f);
      var session = repo.createSession();
      assertEquals(Set.of("csrfToken", "operationTokens"), session.getAttributeNames());
      assertNull(session.getAttribute("principal"));
      assertNull(session.getAttribute("savedRequest"));
      assertNull(session.getAttribute("unknown"));
      assertEquals(List.of(), session.getAttribute("operationTokens"));
      String originalId = session.getId();
      String csrf = session.getAttribute("csrfToken");
      assertEquals("02".repeat(32), csrf);
      session.setAttribute("csrfToken", csrf);
      session.removeAttribute("principal");
      session.setAttribute("savedRequest", "/logs?q=abc");
      session.setAttribute("operationTokens", SessionAttributeCodecTest.tokens(2));
      var reloaded = Objects.requireNonNull(repo.findById(originalId));
      assertEquals("/logs?q=abc", reloaded.getAttribute("savedRequest"));
      assertEquals(SessionAttributeCodecTest.tokens(2), reloaded.getAttribute("operationTokens"));
      session.setAttribute("principal", PRINCIPAL);
      assertEquals(PRINCIPAL, session.getAttribute("principal"));
      assertEquals(
          Set.of("principal", "csrfToken", "savedRequest", "operationTokens"),
          session.getAttributeNames());
      assertNotEquals(originalId, session.getId());
      assertNull(repo.findById(originalId));
      assertEquals("04".repeat(32), session.getAttribute("csrfToken"));
      assertEquals("/logs?q=abc", session.getAttribute("savedRequest"));
      assertEquals(SessionAttributeCodecTest.tokens(2), session.getAttribute("operationTokens"));
      assertEquals(NOW, session.getCreationTime());
      assertEquals(NOW, session.getLastAccessedTime());
      assertEquals(Duration.ofHours(8), session.getMaxInactiveInterval());
      assertEquals("SpringWebSession[REDACTED]", session.toString());
      session.removeAttribute("savedRequest");
      // QA049 supersedes legacy pending deletion; only dedicated issue retires consumed.
      unavailable(() -> session.setAttribute("operationTokens", null));
      assertNull(session.getAttribute("savedRequest"));
      assertEquals(SessionAttributeCodecTest.tokens(2), session.getAttribute("operationTokens"));
      assertThrows(UnsupportedOperationException.class, () -> session.getAttributeNames().clear());
      List<SessionOperationToken> tokens = session.getAttribute("operationTokens");
      assertThrows(
          UnsupportedOperationException.class,
          () -> tokens.add(SessionAttributeCodecTest.tokens(1).getFirst()));
      for (String name :
          List.of(
              "password",
              "SPRING_SECURITY_CONTEXT",
              "principal",
              "csrfToken",
              "savedRequest",
              "operationTokens"))
        assertThrows(
            IllegalArgumentException.class, () -> session.setAttribute(name, new Object()));
      assertThrows(IllegalArgumentException.class, () -> session.removeAttribute("principal"));
      assertThrows(IllegalArgumentException.class, () -> session.removeAttribute("csrfToken"));
      assertThrows(IllegalArgumentException.class, () -> session.removeAttribute("unknown"));
      for (String invalid : List.of("", "//outside", "https://outside", "/../logs"))
        assertThrows(
            IllegalArgumentException.class, () -> session.setAttribute("savedRequest", invalid));
      assertThrows(
          IllegalArgumentException.class,
          () -> session.setAttribute("operationTokens", Arrays.asList((Object) null)));
      assertThrows(
          IllegalArgumentException.class,
          () -> session.setAttribute("operationTokens", List.of("bad")));
      assertThrows(
          IllegalArgumentException.class,
          () -> session.setAttribute("operationTokens", SessionAttributeCodecTest.tokens(11)));
      verifyStoredHash(session.getId());
      var legacy = f.repository.create();
      var attributes =
          new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), List.of());
      byte[] envelope = f.codec.encrypt(legacy.row().identity(), attributes).ciphertext();
      try (var c = db.web();
          var s =
              c.prepareStatement(
                  "update schubert_web_session.web_http_sessions set attributes_ciphertext=? where id=?")) {
        s.setBytes(1, envelope);
        s.setObject(2, legacy.row().identity().id());
        assertEquals(1, s.executeUpdate());
      }
      var absentCsrf = Objects.requireNonNull(repo.findById(legacy.sessionId().cookieValue()));
      assertEquals(Set.of("operationTokens"), absentCsrf.getAttributeNames());
      assertNull(absentCsrf.getAttribute("csrfToken"));
      absentCsrf.removeAttribute("csrfToken");
      absentCsrf.changeSessionId();
      String issued = absentCsrf.getAttribute("csrfToken");
      assertNotNull(issued);
      assertEquals(64, issued.length());
      assertNull(absentCsrf.getAttribute("principal"));
    }
  }

  @Test
  void web046TokenDeltasPreserveConcurrentChanges() throws Exception {
    try (var f = new Fixture(db)) {
      var repo = adapter(f);
      var initial = repo.createSession();
      var tokenA = SessionAttributeCodecTest.tokens(1).getFirst();
      initial.setAttribute("operationTokens", List.of(tokenA));
      var staleDeletion = Objects.requireNonNull(repo.findById(initial.getId()));
      var alreadyRemoved = Objects.requireNonNull(repo.findById(initial.getId()));
      unavailable(() -> initial.setAttribute("operationTokens", List.of()));
      unavailable(() -> alreadyRemoved.removeAttribute("operationTokens"));
      assertEquals(List.of(tokenA), alreadyRemoved.getAttribute("operationTokens"));
      var tokenB = new SessionOperationToken("QDLREQ01", tokenA.token(), tokenA.issuedAt());
      assertThrows(
          IllegalArgumentException.class,
          () -> initial.setAttribute("operationTokens", List.of(tokenB)));
      unavailable(() -> staleDeletion.removeAttribute("operationTokens"));
      assertEquals(
          List.of(tokenA),
          Objects.requireNonNull(repo.findById(initial.getId())).getAttribute("operationTokens"));
      repo.deleteById(initial.getId());
    }
    try (var f = new Fixture(db);
        var pool = Executors.newFixedThreadPool(10)) {
      var repo = adapter(f);
      var original = repo.createSession();
      original.setAttribute("savedRequest", "/logs");
      String id = original.getId();
      var values = SessionAttributeCodecTest.tokens(10);
      for (boolean add : new boolean[] {true, false}) {
        var jobs = new ArrayList<Callable<Void>>();
        for (int iteration = 0; iteration < 100; iteration++) {
          var token = values.get(iteration % values.size());
          var session = Objects.requireNonNull(repo.findById(id));
          var desired = add ? new ArrayList<SessionOperationToken>() : new ArrayList<>(values);
          if (add) desired.add(token);
          else assertTrue(desired.remove(token));
          jobs.add(
              () -> {
                if (add) session.setAttribute("operationTokens", desired);
                else unavailable(() -> session.setAttribute("operationTokens", desired));
                return null;
              });
        }
        for (var future : pool.invokeAll(jobs)) future.get(30, TimeUnit.SECONDS);
        var current = Objects.requireNonNull(repo.findById(id));
        List<SessionOperationToken> actual = current.getAttribute("operationTokens");
        assertEquals(new HashSet<>(values), new HashSet<>(actual));
        assertEquals("/logs", current.getAttribute("savedRequest"));
        assertEquals("02".repeat(32), current.getAttribute("csrfToken"));
      }
      var a = Objects.requireNonNull(repo.findById(id));
      var b = Objects.requireNonNull(repo.findById(id));
      unavailable(() -> a.setAttribute("operationTokens", List.of(values.getFirst())));
      unavailable(() -> b.setAttribute("operationTokens", List.of(values.getFirst())));
      List<SessionOperationToken> preserved = b.getAttribute("operationTokens");
      assertEquals(10, preserved.size());
      assertEquals(new HashSet<>(values), new HashSet<>(preserved));
      var changed =
          new SessionOperationToken(
              "QDLREQ01", values.getFirst().token(), values.getFirst().issuedAt());
      assertThrows(
          IllegalArgumentException.class,
          () -> b.setAttribute("operationTokens", List.of(changed)));
      var stale = original;
      unavailable(() -> stale.setAttribute("operationTokens", List.of(changed)));
      a.setAttribute("operationTokens", values);
      var full = Objects.requireNonNull(repo.findById(id));
      var extra = new SessionOperationToken("QSBREQ01", new UUID(0, 99), NOW);
      unavailable(() -> original.setAttribute("operationTokens", List.of(extra)));
      assertEquals(
          new HashSet<>(values),
          new HashSet<>(full.<List<SessionOperationToken>>getAttribute("operationTokens")));
      repo.deleteById(id);
      unavailable(() -> full.setAttribute("operationTokens", List.of()));
      assertEquals(0, count());
    }
  }

  @Test
  void tokv208LegacyDeltaCannotCompleteRollbackOrResurrectRetiredToken() throws Exception {
    try (var f = new Fixture(db)) {
      var repo = adapter(f);
      var initial = repo.createSession();
      var values = SessionAttributeCodecTest.tokens(10);
      initial.setAttribute("operationTokens", values);
      var stale = Objects.requireNonNull(repo.findById(initial.getId()));
      var retiredStale = Objects.requireNonNull(repo.findById(initial.getId()));
      var id = WebSessionId.parse(initial.getId());
      var first = values.getFirst();
      var lifecycle =
          new SessionOperationTokenLifecycle(f.repository, f.clock, () -> new UUID(0, 99));
      var completed =
          lifecycle.completeVerified(
              id,
              first.purpose(),
              first.token(),
              dev.codex.schubert.nk.protocol.header.ResultCode.SUCCESS);
      assertEquals(Optional.of(NOW), completed.completedAt());
      stale.setAttribute("operationTokens", values);
      assertEquals(
          completed, f.repository.find(id).orElseThrow().attributes().operationTokens().getFirst());
      var completedSnapshot = Objects.requireNonNull(repo.findById(initial.getId()));
      var completedValues = new ArrayList<>(values);
      completedValues.set(0, completed);
      completedSnapshot.setAttribute("operationTokens", completedValues);
      unavailable(() -> completedSnapshot.removeAttribute("operationTokens"));
      var newToken = lifecycle.issue(id, "QDLREQ01");
      assertEquals(new UUID(0, 99), newToken.token());
      assertThrows(
          IllegalArgumentException.class, () -> stale.setAttribute("operationTokens", values));
      retiredStale.setAttribute("operationTokens", values);
      assertEquals(
          List.of(
              new UUID(0, 2),
              new UUID(0, 3),
              new UUID(0, 4),
              new UUID(0, 5),
              new UUID(0, 6),
              new UUID(0, 7),
              new UUID(0, 8),
              new UUID(0, 9),
              new UUID(0, 10),
              new UUID(0, 99)),
          f.repository.find(id).orElseThrow().attributes().operationTokens().stream()
              .map(SessionOperationToken::token)
              .toList());
      // Removing an already retired stale entry is a no-op; retaining it never re-inserts it.
      // Fresh retiredStale now contains current token99, so use the untouched initial snapshot
      // to omit only the already-retired UUID1 without omitting any current row tuple.
      initial.setAttribute("operationTokens", values.subList(1, 10));
      assertEquals(10, f.repository.find(id).orElseThrow().attributes().operationTokens().size());
      var forgedCompletion =
          new SessionOperationToken("QSBREQ01", new UUID(0, 200), NOW, Optional.of(NOW));
      assertThrows(
          IllegalArgumentException.class,
          () -> stale.setAttribute("operationTokens", List.of(forgedCompletion)));
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void web047RepositoryOwnershipExpiryAndFailuresReject() throws Exception {
    try (var f = new Fixture(db);
        var pool = Executors.newSingleThreadExecutor()) {
      var repo = adapter(f);
      var session = repo.createSession();
      assertThrows(
          NullPointerException.class, () -> new SpringEncryptedSessionRepository(null, f.clock));
      assertThrows(
          NullPointerException.class,
          () -> new SpringEncryptedSessionRepository(f.repository, null));
      assertThrows(NullPointerException.class, () -> repo.save(null));
      assertThrows(NullPointerException.class, () -> repo.findById(null));
      assertThrows(NullPointerException.class, () -> repo.deleteById(null));
      assertThrows(NullPointerException.class, () -> session.getAttribute(null));
      assertThrows(NullPointerException.class, () -> session.setAttribute(null, null));
      assertThrows(NullPointerException.class, () -> session.removeAttribute(null));
      assertThrows(NullPointerException.class, () -> session.setLastAccessedTime(null));
      assertThrows(NullPointerException.class, () -> session.setMaxInactiveInterval(null));
      assertThrows(NullPointerException.class, () -> new WebSessionFilterFactory().create(null));
      var snapshot = f.repository.create();
      assertThrows(
          NullPointerException.class,
          () -> new SpringWebSession(null, f.repository, f.clock, snapshot));
      assertThrows(
          NullPointerException.class, () -> new SpringWebSession(repo, null, f.clock, snapshot));
      assertThrows(
          NullPointerException.class,
          () -> new SpringWebSession(repo, f.repository, null, snapshot));
      assertThrows(
          NullPointerException.class,
          () -> new SpringWebSession(repo, f.repository, f.clock, null));
      assertThrows(IllegalArgumentException.class, () -> adapter(f).save(session));
      assertNull(repo.findById("bad"));
      repo.deleteById("bad");
      session.setMaxInactiveInterval(Duration.ofHours(8));
      for (Duration bad :
          List.of(
              Duration.ZERO,
              Duration.ofSeconds(-1),
              Duration.ofHours(9),
              Duration.ofHours(8).plusNanos(1)))
        assertThrows(IllegalArgumentException.class, () -> session.setMaxInactiveInterval(bad));
      session.setLastAccessedTime(NOW.plusSeconds(1).plusNanos(789));
      assertEquals(NOW.plusSeconds(1), session.getLastAccessedTime());
      f.clock.value = NOW.plusSeconds(28801).minusNanos(1000);
      assertFalse(session.isExpired());
      f.clock.value = NOW.plusSeconds(28801);
      assertTrue(session.isExpired());
      f.clock.value = f.clock.value.plusNanos(1000);
      assertTrue(session.isExpired());
      unavailable(() -> repo.save(session));
      assertNull(repo.findById(session.getId()));
      unavailable(session::changeSessionId);
      unavailable(() -> session.setLastAccessedTime(NOW));
      unavailable(() -> session.setAttribute("savedRequest", "/logs"));
      unavailable(() -> session.setAttribute("principal", PRINCIPAL));
      f.clock.value = NOW;
      var active = repo.createSession();
      synchronized (active) {
        assertEquals(active.getId(), pool.submit(active::getId).get(5, TimeUnit.SECONDS));
      }
      for (String fault : List.of("open", "connection.commit", "connection.close")) {
        f.failure = fault;
        unavailable(() -> repo.findById(active.getId()));
        unavailable(() -> repo.save(active));
        f.failure = "";
      }
      f.clock.value = null;
      assertThrows(NullPointerException.class, active::isExpired);
      f.clock.value = NOW;
      f.codec.close();
      unavailable(() -> repo.save(active));
    }
  }

  @Test
  void web048ServletFilterCookiesRestartAndFixation() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now().truncatedTo(ChronoUnit.MICROS);
      var repo = adapter(f);
      var filter = new WebSessionFilterFactory().create(repo);
      var first = new MockHttpServletResponse();
      filter.doFilter(
          request(null),
          first,
          (req, res) -> {
            var session = ((HttpServletRequest) req).getSession();
            session.setAttribute("savedRequest", "/logs?q=abc");
            session.setAttribute("operationTokens", SessionAttributeCodecTest.tokens(2));
            ((HttpServletResponse) res).setStatus(200);
          });
      Cookie cookie = Objects.requireNonNull(first.getCookie("SCHUBERT_NK_SESSION"));
      String original = cookie.getValue();
      assertEquals(43, original.length());
      assertEquals(32, Base64.getUrlDecoder().decode(original).length);
      assertTrue(cookie.getSecure());
      assertTrue(cookie.isHttpOnly());
      assertEquals("Lax", cookie.getAttribute("SameSite"));
      assertEquals("/", cookie.getPath());
      assertNull(cookie.getDomain());
      assertEquals(-1, cookie.getMaxAge());
      verifyStoredHash(original);
      var restarted = new WebSessionFilterFactory().create(adapter(f));
      var second = new MockHttpServletResponse();
      restarted.doFilter(
          request(cookie),
          second,
          (req, res) -> {
            var session = ((HttpServletRequest) req).getSession(false);
            assertNotNull(session);
            assertEquals(original, session.getId());
            assertEquals("/logs?q=abc", session.getAttribute("savedRequest"));
            session.setAttribute("principal", PRINCIPAL);
            assertNotEquals(original, session.getId());
            assertEquals(PRINCIPAL, session.getAttribute("principal"));
            assertEquals("04".repeat(32), session.getAttribute("csrfToken"));
          });
      var authenticated = Objects.requireNonNull(second.getCookie("SCHUBERT_NK_SESSION"));
      assertNotEquals(original, authenticated.getValue());
      assertNull(repo.findById(original));
      assertEquals(1, count());
      var third = new MockHttpServletResponse();
      restarted.doFilter(
          request(authenticated),
          third,
          (req, res) -> {
            var request = (HttpServletRequest) req;
            String before = request.getSession().getId();
            assertNotEquals(before, request.changeSessionId());
            assertEquals(PRINCIPAL, request.getSession().getAttribute("principal"));
            assertEquals(
                SessionAttributeCodecTest.tokens(2),
                request.getSession().getAttribute("operationTokens"));
          });
      assertNotEquals(
          authenticated.getValue(),
          Objects.requireNonNull(third.getCookie("SCHUBERT_NK_SESSION")).getValue());
    }
  }

  @Test
  void web049ServletInvalidationAndStaleCommitNeverResurrect() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now().truncatedTo(ChronoUnit.MICROS);
      var repo = adapter(f);
      var filter = new WebSessionFilterFactory().create(repo);
      var created = repo.createSession();
      var cookie = new Cookie("SCHUBERT_NK_SESSION", created.getId());
      var logout = new MockHttpServletResponse();
      filter.doFilter(
          request(cookie),
          logout,
          (req, res) -> ((HttpServletRequest) req).getSession().invalidate());
      assertEquals(0, count());
      assertEquals(0, Objects.requireNonNull(logout.getCookie("SCHUBERT_NK_SESSION")).getMaxAge());
      for (Cookie absent : List.of(cookie, new Cookie("SCHUBERT_NK_SESSION", "bad"))) {
        filter.doFilter(
            request(absent),
            new MockHttpServletResponse(),
            (req, res) -> assertNull(((HttpServletRequest) req).getSession(false)));
        assertEquals(0, count());
      }
      var active = repo.createSession();
      var response = new MockHttpServletResponse();
      unavailable(
          () ->
              filter.doFilter(
                  request(new Cookie("SCHUBERT_NK_SESSION", active.getId())),
                  response,
                  (req, res) -> {
                    var session = ((HttpServletRequest) req).getSession(false);
                    assertNotNull(session);
                    repo.deleteById(session.getId());
                    ((HttpServletResponse) res).flushBuffer();
                  }));
      assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
      assertEquals(0, count());
      var expired = repo.createSession();
      f.clock.value = f.clock.value.plusSeconds(28800);
      filter.doFilter(
          request(new Cookie("SCHUBERT_NK_SESSION", expired.getId())),
          new MockHttpServletResponse(),
          (req, res) -> assertNull(((HttpServletRequest) req).getSession(false)));
      assertEquals(0, count());
    }
  }

  private static SpringEncryptedSessionRepository adapter(Fixture f) {
    return new SpringEncryptedSessionRepository(f.repository, f.clock);
  }

  private static MockHttpServletRequest request(Cookie cookie) {
    var request = new MockHttpServletRequest("GET", "/logs");
    request.setSecure(true);
    if (cookie != null) request.setCookies(cookie);
    return request;
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void verifyStoredHash(String raw) throws Exception {
    String expected =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(raw.getBytes(java.nio.charset.StandardCharsets.US_ASCII)));
    try (var c = db.web();
        var s =
            c.prepareStatement(
                "select session_id_hash from schubert_web_session.web_http_sessions where session_id_hash=?")) {
      s.setString(1, expected);
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        assertEquals(expected, r.getString(1));
        assertFalse(r.next());
      }
    }
  }

  private static void unavailable(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(SessionStoreException.class, action);
    assertEquals("session storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
