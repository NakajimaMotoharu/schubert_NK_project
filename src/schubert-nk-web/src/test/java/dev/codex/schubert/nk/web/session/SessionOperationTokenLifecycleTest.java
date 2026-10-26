package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** QA049/PG-D356/UI226/SS314; TOKV207208 real JDBC and literal order/time/count oracle. */
class SessionOperationTokenLifecycleTest {
  private static final int EXPECTED_PENDING_TOKEN_CAPACITY = 10;

  private static final String FIXTURE_SUBMIT_REQUEST = "QSBREQ01";
  private static final String FIXTURE_STATE_REQUEST = "USTREQ01";
  private static final String FIXTURE_ROLE_REQUEST = "URLREQ01";
  private static final String FIXTURE_CONNECTION_CLOSE = "connection.close";
  private static final String FIXTURE_CANCEL_REQUEST = "NTCREQ01";

  static final Instant NOW = Instant.parse("2026-10-04T00:00:00Z");
  static WebLogDatabaseFixture db;

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

  static SessionAttributes tokens(SessionAttributes current, List<SessionOperationToken> values) {
    return new SessionAttributes(
        current.principal(), current.csrfToken(), current.savedRequest(), values);
  }

  static List<SessionOperationToken> pending(int count) {
    var result = new ArrayList<SessionOperationToken>();
    for (int n = 1; n <= count; n++)
      result.add(new SessionOperationToken(FIXTURE_SUBMIT_REQUEST, new UUID(0, n), NOW));
    return result;
  }

  static SessionOperationTokenLifecycle service(Fixture f, AtomicInteger calls) {
    return new SessionOperationTokenLifecycle(
        f.repository, f.clock, () -> new UUID(0, 100 + calls.incrementAndGet()));
  }

  @Test
  void tokv209aExactCapacityNeverPartiallyPublishesOrGeneratesUuid() throws Exception {
    for (int before = 0; before <= EXPECTED_PENDING_TOKEN_CAPACITY; before++)
      for (int count = 1; count <= 4; count++)
        try (var f = new Fixture(db)) {
          reset(); // BUG640: fixed identity/nonce fixture requires independent subcase rows.
          f.clock.value = NOW;
          var session = f.repository.create();
          var original = pending(before);
          f.repository.mutate(session.sessionId(), current -> tokens(current, original));
          var calls = new AtomicInteger();
          var lifecycle = service(f, calls);
          var purposes =
              List.of(FIXTURE_STATE_REQUEST, FIXTURE_ROLE_REQUEST, "UPWREQ01", "ULKREQ01")
                  .subList(0, count);
          if (before + count <= EXPECTED_PENDING_TOKEN_CAPACITY) {
            var issued = lifecycle.issueForForms(session.sessionId(), purposes);
            assertEquals(purposes, issued.stream().map(SessionOperationToken::purpose).toList());
            assertEquals(count, calls.get());
            assertEquals(
                before + count,
                f.repository
                    .find(session.sessionId())
                    .orElseThrow()
                    .attributes()
                    .operationTokens()
                    .size());
            assertThrows(UnsupportedOperationException.class, issued::clear);
          } else {
            assertThrows(
                OperationTokenConflictException.class,
                () -> lifecycle.issueForForms(session.sessionId(), purposes));
            assertEquals(0, calls.get());
            assertEquals(
                original,
                f.repository
                    .find(session.sessionId())
                    .orElseThrow()
                    .attributes()
                    .operationTokens());
          }
          assertEquals(0, f.live.get());
        }
  }

  @Test
  void tokv209bOnlyRequiredConsumedOldestWithStableTieOrderRetire() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var original = new ArrayList<>(pending(5));
      for (int n = 6; n <= 10; n++) {
        int seconds =
            switch (n) {
              case 6 -> 3;
              case 7, 8 -> 2;
              case 9 -> 1;
              default -> 4;
            };
        original.add(
            new SessionOperationToken(
                FIXTURE_SUBMIT_REQUEST,
                new UUID(0, n),
                NOW,
                Optional.of(NOW.plusSeconds(seconds))));
      }
      f.repository.mutate(session.sessionId(), current -> tokens(current, original));
      f.clock.value = NOW.plusSeconds(5);
      var calls = new AtomicInteger();
      var issued =
          service(f, calls)
              .issueForForms(
                  session.sessionId(),
                  List.of(FIXTURE_STATE_REQUEST, FIXTURE_ROLE_REQUEST, "UPWREQ01", "ULKREQ01"));
      assertEquals(
          List.of(101L, 102L, 103L, 104L),
          issued.stream().map(t -> t.token().getLeastSignificantBits()).toList());
      assertTrue(
          issued.stream()
              .allMatch(t -> t.issuedAt().equals(NOW.plusSeconds(5)) && t.completedAt().isEmpty()));
      var retained =
          f.repository.find(session.sessionId()).orElseThrow().attributes().operationTokens();
      assertEquals(
          List.of(1L, 2L, 3L, 4L, 5L, 10L, 101L, 102L, 103L, 104L),
          retained.stream().map(t -> t.token().getLeastSignificantBits()).toList());
      assertEquals(original.getLast(), retained.get(5));
      assertEquals(4, calls.get());
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void tokv209cOriginalAndGroupUuidCollisionsRollbackWholeList() throws Exception {
    for (long duplicate : List.of(1L, 101L))
      try (var f = new Fixture(db)) {
        reset();
        f.clock.value = NOW;
        var session = f.repository.create();
        var original = pending(1);
        f.repository.mutate(session.sessionId(), current -> tokens(current, original));
        var calls = new AtomicInteger();
        var lifecycle =
            new SessionOperationTokenLifecycle(
                f.repository,
                f.clock,
                () -> new UUID(0, calls.incrementAndGet() == 1 ? 101 : duplicate));
        assertThrows(
            SessionStoreException.class,
            () ->
                lifecycle.issueForForms(
                    session.sessionId(), List.of(FIXTURE_STATE_REQUEST, FIXTURE_ROLE_REQUEST)));
        assertEquals(2, calls.get());
        assertEquals(
            original,
            f.repository.find(session.sessionId()).orElseThrow().attributes().operationTokens());
        assertEquals(0, f.live.get());
      }
    for (String failure : List.of("connection.commit", FIXTURE_CONNECTION_CLOSE))
      try (var f = new Fixture(db)) {
        reset();
        f.clock.value = NOW;
        var session = f.repository.create();
        var calls = new AtomicInteger();
        f.failure = failure;
        assertThrows(
            SessionStoreException.class,
            () ->
                service(f, calls)
                    .issueForForms(
                        session.sessionId(), List.of(FIXTURE_STATE_REQUEST, FIXTURE_ROLE_REQUEST)));
        assertTrue(f.hit);
        f.failure = "";
        assertEquals(
            failure.equals(FIXTURE_CONNECTION_CLOSE) ? 2 : 0,
            f.repository
                .find(session.sessionId())
                .orElseThrow()
                .attributes()
                .operationTokens()
                .size());
        assertEquals(0, f.live.get());
      }
  }

  @Test
  void tokv209dOneHundredCompetingGroupsRespectSameRowAtomicCapacity() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      try (var executor = Executors.newFixedThreadPool(8)) {
        var jobs = new ArrayList<Callable<Boolean>>();
        for (int n = 0; n < 100; n++)
          jobs.add(
              () -> {
                try {
                  lifecycle.issueForForms(
                      session.sessionId(), List.of(FIXTURE_STATE_REQUEST, FIXTURE_ROLE_REQUEST));
                  return true;
                } catch (OperationTokenConflictException capacity) {
                  return false;
                }
              });
        int accepted = 0;
        for (var result : executor.invokeAll(jobs, 30, TimeUnit.SECONDS)) {
          assertFalse(result.isCancelled());
          if (result.get()) accepted++;
        }
        assertEquals(5, accepted);
      }
      var retained =
          f.repository.find(session.sessionId()).orElseThrow().attributes().operationTokens();
      assertEquals(10, retained.size());
      assertEquals(10, retained.stream().map(SessionOperationToken::token).distinct().count());
      assertEquals(10, calls.get());
      assertTrue(retained.stream().allMatch(t -> t.completedAt().isEmpty()));
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void tokv209eNullMissingAndUnknownGroupBoundariesBeforeUuid() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      assertThrows(
          NullPointerException.class, () -> lifecycle.issueForForms(session.sessionId(), null));
      assertThrows(
          NullPointerException.class,
          () -> lifecycle.issueForForms(session.sessionId(), Arrays.asList((String) null)));
      assertThrows(
          IllegalArgumentException.class,
          () -> lifecycle.issueForForms(session.sessionId(), List.of()));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              lifecycle.issueForForms(
                  session.sessionId(), Collections.nCopies(11, FIXTURE_STATE_REQUEST)));
      assertThrows(
          IllegalArgumentException.class,
          () -> lifecycle.issueForForms(session.sessionId(), List.of("UNKNOWN")));
      assertThrows(
          NullPointerException.class,
          () -> lifecycle.issueForForms(null, List.of(FIXTURE_STATE_REQUEST)));
      f.repository.invalidate(session.sessionId());
      assertThrows(
          OperationTokenConflictException.class,
          () ->
              lifecycle.issueForForms(
                  session.sessionId(), List.of(FIXTURE_STATE_REQUEST, FIXTURE_ROLE_REQUEST)));
      assertEquals(0, calls.get());
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void tokv207IssueRequireCompleteFirstWriteAndAllSuccessCodes() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      var issued = lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST);
      assertEquals(new UUID(0, 101), issued.token());
      assertEquals(NOW, issued.issuedAt());
      assertEquals(Optional.empty(), issued.completedAt());
      assertEquals(
          issued, lifecycle.require(session.sessionId(), FIXTURE_SUBMIT_REQUEST, issued.token()));
      f.clock.value = NOW.plusSeconds(1);
      var completed =
          lifecycle.completeVerified(
              session.sessionId(), FIXTURE_SUBMIT_REQUEST, issued.token(), ResultCode.SUCCESS);
      assertEquals(Optional.of(NOW.plusSeconds(1)), completed.completedAt());
      f.clock.value = NOW.plusSeconds(2);
      assertEquals(
          completed,
          lifecycle.completeVerified(
              session.sessionId(),
              FIXTURE_SUBMIT_REQUEST,
              issued.token(),
              ResultCode.IDEMPOTENT_SUCCESS));
      assertEquals(
          completed,
          lifecycle.require(session.sessionId(), FIXTURE_SUBMIT_REQUEST, issued.token()));
      assertEquals(1, calls.get());
      assertEquals(0, f.live.get());
      for (var code : ResultCode.values())
        if (!(code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS))
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  lifecycle.completeVerified(
                      session.sessionId(), FIXTURE_SUBMIT_REQUEST, issued.token(), code));
      var second = lifecycle.issue(session.sessionId(), FIXTURE_CANCEL_REQUEST);
      assertEquals(
          Optional.of(NOW.plusSeconds(2)),
          lifecycle
              .completeVerified(
                  session.sessionId(),
                  FIXTURE_CANCEL_REQUEST,
                  second.token(),
                  ResultCode.IDEMPOTENT_SUCCESS)
              .completedAt());
      assertThrows(
          OperationTokenConflictException.class,
          () -> lifecycle.require(session.sessionId(), FIXTURE_CANCEL_REQUEST, issued.token()));
      try (var c = db.web();
          var s = c.createStatement();
          var rows =
              s.executeQuery(
                  "select count(*),min(version),max(version) from"
                      + " schubert_web_session.web_http_sessions")) {
        assertTrue(rows.next());
        assertEquals(1, rows.getInt(1));
        assertEquals(8, rows.getInt(2));
        assertEquals(8, rows.getInt(3));
      }
    }
  }

  @Test
  void tokv207FullPendingRejectsBeforeUuidAndRetiresOnlyOldestConsumedTie() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      var values = pending(10);
      f.repository.mutate(session.sessionId(), current -> tokens(current, values));
      var rejected =
          assertThrows(
              OperationTokenConflictException.class,
              () -> lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST));
      assertEquals(409, rejected.httpStatus());
      assertEquals(0, calls.get());
      assertEquals(
          values,
          f.repository.find(session.sessionId()).orElseThrow().attributes().operationTokens());
      values.set(
          0,
          new SessionOperationToken(
              FIXTURE_SUBMIT_REQUEST, new UUID(0, 1), NOW, Optional.of(NOW.plusSeconds(2))));
      values.set(
          2,
          new SessionOperationToken(
              FIXTURE_SUBMIT_REQUEST, new UUID(0, 3), NOW, Optional.of(NOW.plusSeconds(1))));
      values.set(
          4,
          new SessionOperationToken(
              FIXTURE_SUBMIT_REQUEST, new UUID(0, 5), NOW, Optional.of(NOW.plusSeconds(1))));
      f.repository.mutate(session.sessionId(), current -> tokens(current, values));
      f.clock.value = NOW.plusSeconds(3);
      var retiredCollision =
          new SessionOperationTokenLifecycle(f.repository, f.clock, () -> new UUID(0, 3));
      assertThrows(
          SessionStoreException.class,
          () -> retiredCollision.issue(session.sessionId(), "QDLREQ01"));
      assertEquals(
          values,
          f.repository.find(session.sessionId()).orElseThrow().attributes().operationTokens());
      var added = lifecycle.issue(session.sessionId(), "QDLREQ01");
      assertEquals(new UUID(0, 101), added.token());
      assertEquals(1, calls.get());
      List<UUID> expected =
          List.of(
              new UUID(0, 1),
              new UUID(0, 2),
              new UUID(0, 4),
              new UUID(0, 5),
              new UUID(0, 6),
              new UUID(0, 7),
              new UUID(0, 8),
              new UUID(0, 9),
              new UUID(0, 10),
              new UUID(0, 101));
      assertEquals(
          expected,
          f
              .repository
              .find(session.sessionId())
              .orElseThrow()
              .attributes()
              .operationTokens()
              .stream()
              .map(SessionOperationToken::token)
              .toList());
      assertThrows(
          OperationTokenConflictException.class,
          () -> lifecycle.require(session.sessionId(), FIXTURE_SUBMIT_REQUEST, new UUID(0, 3)));
      assertThrows(
          OperationTokenConflictException.class,
          () ->
              lifecycle.completeVerified(
                  session.sessionId(), FIXTURE_SUBMIT_REQUEST, new UUID(0, 3), ResultCode.SUCCESS));
      assertEquals(1, calls.get());
    }
  }

  @Test
  void tokv208HundredConcurrentCompletionsKeepFirstStampAndFreshList() throws Exception {
    try (var f = new Fixture(db);
        var pool = Executors.newFixedThreadPool(10)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      var issued = lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST);
      f.clock.value = NOW.plusSeconds(1);
      var jobs = new ArrayList<Callable<SessionOperationToken>>();
      for (int n = 0; n < 100; n++)
        jobs.add(
            () ->
                lifecycle.completeVerified(
                    session.sessionId(),
                    FIXTURE_SUBMIT_REQUEST,
                    issued.token(),
                    ResultCode.SUCCESS));
      for (var future : pool.invokeAll(jobs))
        assertEquals(
            Optional.of(NOW.plusSeconds(1)), future.get(30, TimeUnit.SECONDS).completedAt());
      assertEquals(1, calls.get());
      var result = f.repository.find(session.sessionId()).orElseThrow();
      assertEquals(1, result.attributes().operationTokens().size());
      assertEquals(102, result.row().version());
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void tokv208HundredConcurrentIssuesReserveExactlyTenWithoutReplacingPending() throws Exception {
    try (var f = new Fixture(db);
        var pool = Executors.newFixedThreadPool(10)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      var jobs = new ArrayList<Callable<Optional<SessionOperationToken>>>();
      for (int n = 0; n < 100; n++)
        jobs.add(
            () -> {
              try {
                return Optional.of(lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST));
              } catch (OperationTokenConflictException capacity) {
                assertEquals(409, capacity.httpStatus());
                return Optional.empty();
              }
            });
      var accepted = new HashSet<UUID>();
      int rejected = 0;
      for (var future : pool.invokeAll(jobs)) {
        var result = future.get(30, TimeUnit.SECONDS);
        if (result.isPresent()) assertTrue(accepted.add(result.orElseThrow().token()));
        else rejected++;
      }
      assertEquals(
          Set.of(
              new UUID(0, 101),
              new UUID(0, 102),
              new UUID(0, 103),
              new UUID(0, 104),
              new UUID(0, 105),
              new UUID(0, 106),
              new UUID(0, 107),
              new UUID(0, 108),
              new UUID(0, 109),
              new UUID(0, 110)),
          accepted);
      assertEquals(90, rejected);
      assertEquals(10, calls.get());
      var persisted = f.repository.find(session.sessionId()).orElseThrow();
      assertEquals(101, persisted.row().version());
      assertEquals(10, persisted.attributes().operationTokens().size());
      assertEquals(
          accepted,
          new HashSet<>(
              persisted.attributes().operationTokens().stream()
                  .map(SessionOperationToken::token)
                  .toList()));
      assertTrue(
          persisted.attributes().operationTokens().stream()
              .allMatch(value -> value.completedAt().isEmpty() && value.issuedAt().equals(NOW)));
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void tokv208DeletedExpiredAndFaultsNeverRecreateOrReturnUnknownSuccess() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      f.repository.invalidate(session.sessionId());
      assertThrows(
          OperationTokenConflictException.class,
          () -> lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST));
      assertThrows(
          OperationTokenConflictException.class,
          () -> lifecycle.require(session.sessionId(), FIXTURE_SUBMIT_REQUEST, new UUID(0, 1)));
      assertThrows(
          OperationTokenConflictException.class,
          () ->
              lifecycle.completeVerified(
                  session.sessionId(), FIXTURE_SUBMIT_REQUEST, new UUID(0, 1), ResultCode.SUCCESS));
      assertEquals(0, calls.get());
      var expiring = f.repository.create();
      f.clock.value = NOW.plusSeconds(28800);
      assertThrows(
          OperationTokenConflictException.class,
          () -> lifecycle.issue(expiring.sessionId(), FIXTURE_SUBMIT_REQUEST));
      assertEquals(0, calls.get());
      try (var c = db.web();
          var s = c.createStatement();
          var rows =
              s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getInt(1));
      }
    }
    for (String fault : List.of("connection.commit", FIXTURE_CONNECTION_CLOSE))
      try (var f = new Fixture(db)) {
        f.clock.value = NOW;
        var session = f.repository.create();
        var lifecycle = service(f, new AtomicInteger());
        var issued = lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST);
        f.clock.value = NOW.plusSeconds(1);
        f.failure = fault;
        assertThrows(
            SessionStoreException.class,
            () ->
                lifecycle.completeVerified(
                    session.sessionId(),
                    FIXTURE_SUBMIT_REQUEST,
                    issued.token(),
                    ResultCode.SUCCESS));
        assertTrue(f.hit);
        f.failure = "";
        var reread = lifecycle.require(session.sessionId(), FIXTURE_SUBMIT_REQUEST, issued.token());
        assertEquals(
            fault.equals(FIXTURE_CONNECTION_CLOSE)
                ? Optional.of(NOW.plusSeconds(1))
                : Optional.empty(),
            reread.completedAt());
        assertEquals(0, f.live.get());
        f.repository.invalidate(session.sessionId());
      }
  }

  @Test
  void tokv208NullUnknownClockCollisionAndMissingTokenRemainClosed() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = NOW;
      var session = f.repository.create();
      var calls = new AtomicInteger();
      var lifecycle = service(f, calls);
      assertThrows(
          NullPointerException.class, () -> new SessionOperationTokenLifecycle(null, f.clock));
      assertThrows(
          NullPointerException.class, () -> new SessionOperationTokenLifecycle(f.repository, null));
      assertThrows(
          NullPointerException.class,
          () -> new SessionOperationTokenLifecycle(f.repository, f.clock, null));
      assertThrows(
          IllegalArgumentException.class, () -> lifecycle.issue(session.sessionId(), "UNKNOWN"));
      assertThrows(NullPointerException.class, () -> lifecycle.issue(session.sessionId(), null));
      assertThrows(
          NullPointerException.class,
          () -> lifecycle.require(session.sessionId(), FIXTURE_SUBMIT_REQUEST, null));
      assertThrows(
          NullPointerException.class,
          () -> lifecycle.require(null, FIXTURE_SUBMIT_REQUEST, new UUID(0, 1)));
      assertThrows(
          NullPointerException.class,
          () ->
              lifecycle.completeVerified(
                  session.sessionId(), FIXTURE_SUBMIT_REQUEST, new UUID(0, 1), null));
      assertThrows(
          OperationTokenConflictException.class,
          () ->
              lifecycle.completeVerified(
                  session.sessionId(), FIXTURE_SUBMIT_REQUEST, new UUID(0, 1), ResultCode.SUCCESS));
      assertEquals(0, calls.get());
      var issued = lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST);
      var duplicate = new SessionOperationTokenLifecycle(f.repository, f.clock, issued::token);
      assertThrows(
          SessionStoreException.class,
          () -> duplicate.issue(session.sessionId(), FIXTURE_CANCEL_REQUEST));
      var nullId = new SessionOperationTokenLifecycle(f.repository, f.clock, () -> null);
      assertThrows(
          SessionStoreException.class,
          () -> nullId.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST));
      f.clock.value = null;
      assertThrows(
          SessionStoreException.class,
          () -> lifecycle.issue(session.sessionId(), FIXTURE_SUBMIT_REQUEST));
      f.clock.value = NOW.minusNanos(1);
      assertThrows(
          SessionStoreException.class,
          () ->
              lifecycle.completeVerified(
                  session.sessionId(), FIXTURE_SUBMIT_REQUEST, issued.token(), ResultCode.SUCCESS));
      f.clock.value = NOW;
      var defaultService =
          new SessionOperationTokenLifecycle(f.repository, Clock.fixed(NOW, ZoneOffset.UTC));
      assertEquals(
          NOW, defaultService.issue(session.sessionId(), FIXTURE_CANCEL_REQUEST).issuedAt());
      assertEquals(
          2,
          f.repository
              .find(session.sessionId())
              .orElseThrow()
              .attributes()
              .operationTokens()
              .size());
    }
  }
}
