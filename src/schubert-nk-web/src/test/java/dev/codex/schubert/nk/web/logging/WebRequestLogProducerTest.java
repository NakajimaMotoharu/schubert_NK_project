package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
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
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;

/** REQ005007009..014. Independent JSON/2336-byte/JCE/SQL postconditions; no deployed data. */
final class WebRequestLogProducerTest {
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_127_0_0_1_88270499 = "127.0.0.1";
  private static final String FIXTURE_LEVEL_06435E3C = "level";
  private static final String FIXTURE_DETAILS_521BCB5E = "details";
  private static final String FIXTURE_FAILED_7E8A57FE = "FAILED";
  private static final String FIXTURE_PROJECTIONSTATUS_B121730C = "projectionStatus";
  private static final String FIXTURE_COMMIT_5EA9C586 = "commit";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  static final Instant NOW = Instant.parse("2026-10-03T01:00:00.123987Z");
  static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);
  static final byte[] KEY = new byte[32]; // Public synthetic fixture, not a deployed key.
  static final byte[] NONCE = new byte[12];
  private static WebLogDatabaseFixture db;

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
    db.reset();
  }

  @Test
  void req010011012IndependentWholeJsonWireAndJceEnvelope() throws Exception {
    try (var fixture = new Fixture(source(db::web))) {
      var request = new MockHttpServletRequest();
      var trace = WebRequestTraceTest.trace(request, 1);
      trace.captureRoute("/login");
      fixture.producer.complete(
          trace, 200, 12999999, 3, FIXTURE_GET_04F32A7E, Optional.of("203.0.113.7"));
      String expected =
          "{\"timestamp\":\"2026-10-03T01:00:00.123Z\",\"service\":\"WEB\","
              + "\"appVersion\":\"pt-1\",\"configVersion\":\"cfg-1\",\"level\":\"INFO\",\"category\":\"REQUEST\","
              + "\"action\":\"HTTP_REQUEST_COMPLETED\",\"outcome\":\"SUCCESS\","
              + "\"messageId\":\"00000000-0000-0001-0000-000000000001\","
              + "\"correlationId\":\"00000000-0000-0001-0000-000000000001\","
              + "\"requestId\":\"00000000-0000-0000-0000-000000000001\","
              + "\"message\":\"HTTP request completed\",\"httpMethod\":\"GET\",\"path\":\"/login\","
              + "\"status\":200,\"elapsedMs\":12,\"remoteAddress\":\"203.0.113.7\","
              + "\"details\":{\"responseBytes\":3,\"projectionStatus\":\"PENDING\"}}";
      assertEquals(JsonParser.parseString(expected), fixture.logger.entries.getFirst().json());
      assertEquals(Level.INFO, fixture.logger.entries.getFirst().level());
      byte[] cipher = ciphertext(trace.eventId());
      byte[] golden = golden(trace.requestId(), trace.eventId(), trace.eventId());
      byte[] actualWire = independentDecrypt(trace.eventId(), trace.eventId(), cipher);
      assertArrayEquals(golden, actualWire);
      assertArrayEquals(envelope(trace.eventId(), trace.eventId(), golden), cipher);
      assertEquals(1, count());
      try (var connection = db.web();
          var statement = connection.createStatement();
          var rows =
              statement.executeQuery(
                  "select status,attempt_count,lease_owner,sent_at,"
                      + "extract(epoch from created_at) from schubert_web_session.web_log_outbox")) {
        assertTrue(rows.next());
        assertEquals("PENDING", rows.getString(1));
        assertEquals(0, rows.getInt(2));
        assertNull(rows.getString(3));
        assertNull(rows.getObject(4));
        assertEquals("1790989200.123000", rows.getBigDecimal(5).toPlainString());
        assertFalse(rows.next());
      }
      // Only this public synthetic fixture is exported. No key, ciphertext, session, token,
      // browser headers, actual runtime request or exception data is written to the PT proof.
      Path proof =
          Path.of(System.getProperty("nk.pt.repository"))
              .resolve("src/schubert-nk-web/target/request-log-proof");
      Files.createDirectories(proof);
      Files.write(proof.resolve("REQ010-wire.expected.bin"), golden);
      Files.write(proof.resolve("REQ010-wire.actual.bin"), actualWire);
      Files.writeString(proof.resolve("REQ010-json.expected.json"), expected + "\n");
      Files.writeString(
          proof.resolve("REQ010-json.actual.json"),
          fixture.logger.entries.getFirst().json() + "\n");
      Files.writeString(
          proof.resolve("REQ010-input.json"),
          "{\"testId\":\"PT-REQ-LOG010\",\"clock\":\"2026-10-03T01:00:00.123987Z\","
              + "\"requestUuid\":\"00000000-0000-0000-0000-000000000001\","
              + "\"eventUuid\":\"00000000-0000-0001-0000-000000000001\","
              + "\"route\":\"/login\",\"method\":\"GET\",\"status\":200,\"elapsedNs\":12999999,"
              + "\"responseBytes\":3,\"verifiedIp\":\"203.0.113.7\",\"actor\":null}"
              + "\n");
    }
  }

  @Test
  void req007009AllStatusMethodsActorAndNumericBoundaries() throws Exception {
    try (var fixture = new Fixture(source(db::web))) {
      int id = 10;
      for (String method :
          List.of(
              FIXTURE_GET_04F32A7E,
              "HEAD",
              "POST",
              "PUT",
              "PATCH",
              "DELETE",
              "OPTIONS",
              "TRACE",
              "CONNECT",
              "secret-method")) {
        var trace = WebRequestTraceTest.trace(new MockHttpServletRequest(), id++);
        fixture.producer.complete(trace, 200, 999999, 0, method, Optional.of("::1"));
        var json = fixture.logger.entries.getLast().json();
        assertEquals(
            method.equals("secret-method") ? "OTHER" : method,
            json.get("httpMethod").getAsString());
        assertEquals(0, json.get("elapsedMs").getAsLong());
        assertEquals("0:0:0:0:0:0:0:1", json.get("remoteAddress").getAsString());
        assertEquals("/**", json.get("path").getAsString());
        assertFalse(json.has("actorUsername"));
        assertFalse(json.has("actorRole"));
      }
      for (int status : new int[] {100, 399, 400, 499, 500, 599}) {
        var request = new MockHttpServletRequest();
        var trace = WebRequestTraceTest.trace(request, id++);
        WebRequestTrace.captureActor(
            request,
            Optional.of(
                new SessionPrincipal(
                    "équipe\u2028test",
                    UserRole.ADMIN,
                    AuthenticationContext.of("a".repeat(64)),
                    Instant.EPOCH)));
        fixture.producer.complete(
            trace, status, 1000000, 999999999999L, "POST", Optional.of(FIXTURE_127_0_0_1_88270499));
        var json = fixture.logger.entries.getLast().json();
        assertEquals(status, json.get("status").getAsInt());
        assertEquals(
            status >= 500 ? "ERROR" : status >= 400 ? "WARN" : "INFO",
            json.get(FIXTURE_LEVEL_06435E3C).getAsString());
        assertEquals(status >= 400 ? "FAILURE" : "SUCCESS", json.get("outcome").getAsString());
        assertEquals("équipe test", json.get("actorUsername").getAsString());
        assertEquals("ADMIN", json.get("actorRole").getAsString());
        assertFalse(json.getAsJsonObject(FIXTURE_DETAILS_521BCB5E).has("truncated"));
      }
      for (long[] input :
          new long[][] {
            {999999999000000L, 1},
            {1000000000000000L, 1},
            {Long.MAX_VALUE, Long.MAX_VALUE},
            {0, 1000000000000L}
          }) {
        var request = new MockHttpServletRequest();
        var trace = WebRequestTraceTest.trace(request, id++);
        WebRequestTrace.captureActor(
            request,
            Optional.of(
                new SessionPrincipal(
                    "\u2028",
                    UserRole.USER,
                    AuthenticationContext.of("b".repeat(64)),
                    Instant.EPOCH)));
        fixture.producer.complete(
            trace,
            200,
            input[0],
            input[1],
            FIXTURE_GET_04F32A7E,
            Optional.of(FIXTURE_127_0_0_1_88270499));
        var json = fixture.logger.entries.getLast().json();
        assertEquals(
            Math.min(input[0] / 1000000, 999999999999L), json.get("elapsedMs").getAsLong());
        assertEquals(
            Math.min(input[1], 999999999999L),
            json.getAsJsonObject(FIXTURE_DETAILS_521BCB5E).get("responseBytes").getAsLong());
        assertEquals(
            input[0] > 999999999000000L || input[1] > 999999999999L,
            json.getAsJsonObject(FIXTURE_DETAILS_521BCB5E).has("truncated"));
        assertFalse(json.has("actorUsername"));
        assertFalse(json.has("actorRole"));
        byte[] plain =
            independentDecrypt(trace.eventId(), trace.eventId(), ciphertext(trace.eventId()));
        assertEquals(
            input[0] == 0 ? "0        " : "999999999",
            new String(plain, 256 + 920, 9, StandardCharsets.US_ASCII));
      }
      assertEquals(20, count());
    }
  }

  @Test
  void req005009InvalidNumbersAndMissingTrustNeverInventWire() throws Exception {
    try (var fixture = new Fixture(source(db::web))) {
      var trace = WebRequestTraceTest.trace(new MockHttpServletRequest(), 40);
      for (long[] values : new long[][] {{99, 0, 0}, {600, 0, 0}, {200, -1, 0}, {200, 0, -1}}) {
        fixture.producer.complete(
            trace,
            (int) values[0],
            values[1],
            values[2],
            FIXTURE_GET_04F32A7E,
            Optional.of(FIXTURE_127_0_0_1_88270499));
        var json = fixture.logger.entries.getLast().json();
        assertEquals("SYSTEM", json.get("category").getAsString());
        assertEquals("UNKNOWN", json.get("outcome").getAsString());
        assertEquals("WEB_REQUEST_LOG_METADATA_INVALID", json.get("errorCode").getAsString());
        assertFalse(json.has("status"));
        assertFalse(json.has("remoteAddress"));
      }
      fixture.producer.complete(trace, 403, 0, 0, FIXTURE_GET_04F32A7E, Optional.empty());
      assertEquals(6, fixture.logger.entries.size());
      assertEquals(
          "WARN",
          fixture.logger.entries.getLast().json().get(FIXTURE_LEVEL_06435E3C).getAsString());
      assertEquals(Level.WARNING, fixture.logger.entries.getLast().level());
      assertEquals(
          FIXTURE_FAILED_7E8A57FE,
          fixture
              .logger
              .entries
              .getLast()
              .json()
              .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
              .get(FIXTURE_PROJECTIONSTATUS_B121730C)
              .getAsString());
      fixture.producer.complete(
          trace, 200, 0, 0, FIXTURE_GET_04F32A7E, Optional.of("not-an-ip-secret-canary"));
      assertEquals("UNKNOWN", fixture.logger.entries.getLast().json().get("outcome").getAsString());
      assertFalse(fixture.logger.entries.toString().contains("not-an-ip-secret-canary"));
      fixture.producer.complete(
          trace, 200, 0, 0, FIXTURE_GET_04F32A7E, Optional.of("127.0.0.1\r\nsecret"));
      assertFalse(fixture.logger.entries.toString().contains("secret"));
      assertEquals(0, count());
    }
  }

  @Test
  void req012DuplicateKeepsFirstCiphertextAndClosedCodecIsFailedNotSuccess() throws Exception {
    try (var fixture = new Fixture(source(db::web))) {
      var trace = WebRequestTraceTest.trace(new MockHttpServletRequest(), 41);
      fixture.producer.complete(
          trace, 200, 0, 0, FIXTURE_GET_04F32A7E, Optional.of(FIXTURE_127_0_0_1_88270499));
      byte[] first = ciphertext(trace.eventId());
      fixture.producer.complete(trace, 503, 0, 0, "POST", Optional.of(FIXTURE_127_0_0_1_88270499));
      assertArrayEquals(first, ciphertext(trace.eventId()));
      assertEquals(1, count());
      assertEquals(
          "ERROR",
          fixture.logger.entries.getLast().json().get(FIXTURE_LEVEL_06435E3C).getAsString());
      assertEquals(Level.ERROR, fixture.logger.entries.getLast().level());
      assertEquals(
          FIXTURE_FAILED_7E8A57FE,
          fixture
              .logger
              .entries
              .getLast()
              .json()
              .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
              .get(FIXTURE_PROJECTIONSTATUS_B121730C)
              .getAsString());
      fixture.codec.close();
      fixture.producer.complete(
          WebRequestTraceTest.trace(new MockHttpServletRequest(), 42),
          200,
          0,
          0,
          FIXTURE_GET_04F32A7E,
          Optional.of(FIXTURE_127_0_0_1_88270499));
      assertEquals(1, count());
      assertEquals(
          "WEB_REQUEST_LOG_PROJECTION_FAILED",
          fixture.logger.entries.getLast().json().get("errorCode").getAsString());
    }
  }

  @Test
  void req013AllSqlAndUnknownFailuresCloseRollbackAndPreserveSafeOutput() throws Exception {
    for (String stage :
        List.of(
            "get",
            "setAutoCommit",
            "prepareStatement",
            FIXTURE_COMMIT_5EA9C586,
            FIXTURE_CLOSE_97959247)) {
      for (boolean runtime : List.of(false, true)) {
        db.reset();
        var closed = new AtomicInteger();
        var rolled = new AtomicInteger();
        var sqlFailure = new SQLException("synthetic-private-provider-canary", "08006");
        var runtimeFailure = new IllegalStateException("synthetic-private-provider-canary");
        DataSource database =
            source(
                () -> {
                  if (stage.equals("get")) {
                    if (runtime) throw runtimeFailure;
                    throw sqlFailure;
                  }
                  Connection real = db.web();
                  return proxy(
                      Connection.class,
                      (instance, method, args) -> {
                        if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                          closed.incrementAndGet();
                          if (stage.equals(FIXTURE_CLOSE_97959247)) real.close();
                        }
                        if (method.getName().equals("rollback")) rolled.incrementAndGet();
                        if (method.getName().equals(stage)) {
                          if (runtime) throw runtimeFailure;
                          throw sqlFailure;
                        }
                        return invoke(real, method, args);
                      });
                });
        try (var fixture = new Fixture(database)) {
          fixture.producer.complete(
              WebRequestTraceTest.trace(new MockHttpServletRequest(), 50),
              200,
              0,
              0,
              FIXTURE_GET_04F32A7E,
              Optional.of(FIXTURE_127_0_0_1_88270499));
          assertEquals(2, fixture.logger.entries.size());
          var json = fixture.logger.entries.getLast().json();
          assertEquals("WARN", json.get(FIXTURE_LEVEL_06435E3C).getAsString());
          assertEquals(Level.WARNING, fixture.logger.entries.getLast().level());
          assertEquals(
              FIXTURE_FAILED_7E8A57FE,
              json.getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
                  .get(FIXTURE_PROJECTIONSTATUS_B121730C)
                  .getAsString());
          assertFalse(json.toString().contains("synthetic-private-provider-canary"));
          assertEquals(stage.equals("get") ? 0 : 1, closed.get());
          assertEquals(
              stage.equals("prepareStatement") || stage.equals(FIXTURE_COMMIT_5EA9C586) ? 1 : 0,
              rolled.get());
          assertEquals(stage.equals(FIXTURE_CLOSE_97959247) ? 1 : 0, count());
        }
      }
    }
  }

  @Test
  void req013RollbackUnknownAndFatalAreNotNormalizedAsSuccess() throws Exception {
    for (String cleanup : List.of("sql", "runtime", "same", "fatal")) {
      var primary = new SQLException("private-primary", "08006");
      var fatal = new AssertionError("synthetic-fatal");
      var closed = new AtomicInteger();
      DataSource database =
          source(
              () -> {
                Connection real = db.web();
                return proxy(
                    Connection.class,
                    (instance, method, args) -> {
                      if (method.getName().equals(FIXTURE_COMMIT_5EA9C586)) throw primary;
                      if (method.getName().equals("rollback")) {
                        switch (cleanup) {
                          case "sql" -> throw new SQLException("private-rollback");
                          case "runtime" -> throw new IllegalArgumentException("private-rollback");
                          case "same" -> throw primary;
                          default -> throw fatal;
                        }
                      }
                      if (method.getName().equals(FIXTURE_CLOSE_97959247)) closed.incrementAndGet();
                      return invoke(real, method, args);
                    });
              });
      try (var fixture = new Fixture(database)) {
        var trace = WebRequestTraceTest.trace(new MockHttpServletRequest(), 60);
        if (cleanup.equals("fatal")) {
          assertSame(
              fatal,
              assertThrows(
                  AssertionError.class,
                  () ->
                      fixture.producer.complete(
                          trace,
                          200,
                          0,
                          0,
                          FIXTURE_GET_04F32A7E,
                          Optional.of(FIXTURE_127_0_0_1_88270499))));
          assertArrayEquals(new Throwable[] {primary}, fatal.getSuppressed());
        } else {
          fixture.producer.complete(
              trace, 200, 0, 0, FIXTURE_GET_04F32A7E, Optional.of(FIXTURE_127_0_0_1_88270499));
          assertEquals(cleanup.equals("same") ? 0 : 1, primary.getSuppressed().length);
          assertEquals(
              FIXTURE_FAILED_7E8A57FE,
              fixture
                  .logger
                  .entries
                  .getLast()
                  .json()
                  .getAsJsonObject(FIXTURE_DETAILS_521BCB5E)
                  .get(FIXTURE_PROJECTIONSTATUS_B121730C)
                  .getAsString());
        }
        assertEquals(1, closed.get());
        assertEquals(0, count());
      }
    }
    var primary = new AssertionError("synthetic-primary-fatal");
    DataSource database =
        source(
            () -> {
              Connection real = db.web();
              return proxy(
                  Connection.class,
                  (instance, method, args) -> {
                    if (method.getName().equals(FIXTURE_COMMIT_5EA9C586)) throw primary;
                    return invoke(real, method, args);
                  });
            });
    try (var fixture = new Fixture(database)) {
      assertSame(
          primary,
          assertThrows(
              AssertionError.class,
              () ->
                  fixture.producer.complete(
                      WebRequestTraceTest.trace(new MockHttpServletRequest(), 61),
                      200,
                      0,
                      0,
                      FIXTURE_GET_04F32A7E,
                      Optional.of(FIXTURE_127_0_0_1_88270499))));
      assertEquals(0, count());
    }
  }

  @Test
  void req014LocalSinkFailureMarksOwnerTerminalAndNeverTouchesDb() {
    var opened = new AtomicInteger();
    var terminal = new AtomicInteger();
    try (var fixture =
        new Fixture(
            source(
                () -> {
                  opened.incrementAndGet();
                  throw new AssertionError("must not open");
                }))) {
      var producer =
          new WebRequestLogProducer(
              fixture.database,
              fixture.codec,
              new WebLogOutboxRepository(() -> 0),
              fixture.logger,
              CLOCK,
              UUID::randomUUID,
              "pt-1",
              "cfg-1",
              terminal::incrementAndGet);
      for (boolean disabled : List.of(false, true)) {
        fixture.logger.fail = !disabled;
        fixture.logger.enabled = !disabled;
        for (int status : new int[] {200, 400, 500})
          producer.complete(
              WebRequestTraceTest.trace(new MockHttpServletRequest(), 62),
              status,
              0,
              0,
              FIXTURE_GET_04F32A7E,
              Optional.of(FIXTURE_127_0_0_1_88270499));
        producer.metadataInvalid();
      }
      assertEquals(8, terminal.get());
      assertEquals(0, opened.get());
      assertTrue(fixture.logger.entries.isEmpty());
    }
  }

  @Test
  void req013IdenticalFatalRollbackIsNotSelfSuppressedOrSuccess() throws Exception {
    var fatal = new AssertionError("synthetic-identical-fatal");
    var closed = new AtomicInteger();
    DataSource database =
        source(
            () -> {
              Connection real = db.web();
              return proxy(
                  Connection.class,
                  (instance, method, args) -> {
                    if (method.getName().equals(FIXTURE_COMMIT_5EA9C586)
                        || method.getName().equals("rollback")) throw fatal;
                    if (method.getName().equals(FIXTURE_CLOSE_97959247)) closed.incrementAndGet();
                    return invoke(real, method, args);
                  });
            });
    try (var fixture = new Fixture(database)) {
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  fixture.producer.complete(
                      WebRequestTraceTest.trace(new MockHttpServletRequest(), 64),
                      200,
                      0,
                      0,
                      FIXTURE_GET_04F32A7E,
                      Optional.of(FIXTURE_127_0_0_1_88270499))));
      assertEquals(0, fatal.getSuppressed().length);
      assertEquals(1, closed.get());
      assertEquals(0, count());
      assertEquals(1, fixture.logger.entries.size()); // PENDING, never a success acknowledgement.
    }
  }

  @Test
  void req014ConstructorsAndBoundaryNullNeverBecomeSuccessfulAudit() {
    DataSource database =
        source(
            () -> {
              throw new AssertionError("must not open");
            });
    try (var fixture = new Fixture(database)) {
      var repo = new WebLogOutboxRepository(() -> 0);
      var logger = fixture.logger;
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  null, fixture.codec, repo, logger, CLOCK, UUID::randomUUID, "a", "b", () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database, null, repo, logger, CLOCK, UUID::randomUUID, "a", "b", () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database,
                  fixture.codec,
                  null,
                  logger,
                  CLOCK,
                  UUID::randomUUID,
                  "a",
                  "b",
                  () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database,
                  fixture.codec,
                  repo,
                  null,
                  CLOCK,
                  UUID::randomUUID,
                  "a",
                  "b",
                  () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database,
                  fixture.codec,
                  repo,
                  logger,
                  null,
                  UUID::randomUUID,
                  "a",
                  "b",
                  () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database, fixture.codec, repo, logger, CLOCK, null, "a", "b", () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database, fixture.codec, repo, logger, CLOCK, UUID::randomUUID, "a", "b", null));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database,
                  fixture.codec,
                  repo,
                  logger,
                  CLOCK,
                  UUID::randomUUID,
                  null,
                  "b",
                  () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              new WebRequestLogProducer(
                  database,
                  fixture.codec,
                  repo,
                  logger,
                  CLOCK,
                  UUID::randomUUID,
                  "a",
                  null,
                  () -> {}));
      for (String invalid : List.of("", "x".repeat(65), "secret\n", "a b", ".", "/private")) {
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new WebRequestLogProducer(
                    database,
                    fixture.codec,
                    repo,
                    logger,
                    CLOCK,
                    UUID::randomUUID,
                    invalid,
                    "b",
                    () -> {}));
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new WebRequestLogProducer(
                    database,
                    fixture.codec,
                    repo,
                    logger,
                    CLOCK,
                    UUID::randomUUID,
                    "a",
                    invalid,
                    () -> {}));
      }
      var trace = WebRequestTraceTest.trace(new MockHttpServletRequest(), 63);
      assertThrows(
          NullPointerException.class,
          () -> fixture.producer.complete(null, 200, 0, 0, FIXTURE_GET_04F32A7E, Optional.empty()));
      assertThrows(
          NullPointerException.class,
          () -> fixture.producer.complete(trace, 200, 0, 0, null, Optional.empty()));
      assertThrows(
          NullPointerException.class,
          () -> fixture.producer.complete(trace, 200, 0, 0, FIXTURE_GET_04F32A7E, null));
      Clock nullClock =
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
              return null;
            }
          };
      var producer =
          new WebRequestLogProducer(
              database,
              fixture.codec,
              repo,
              logger,
              nullClock,
              UUID::randomUUID,
              "a",
              "b",
              () -> {});
      assertThrows(NullPointerException.class, producer::metadataInvalid);
      assertThrows(
          NullPointerException.class,
          () -> producer.complete(trace, 200, 0, 0, FIXTURE_GET_04F32A7E, Optional.empty()));
      assertTrue(logger.entries.isEmpty());
    }
  }

  static final class Fixture implements AutoCloseable {
    final DataSource database;
    final RecordingLogger logger = new RecordingLogger();
    final WebLogPayloadCodec codec = new WebLogPayloadCodec("v1", KEY, null, null, new ZeroNonce());
    final WebRequestLogProducer producer;

    Fixture(DataSource database) {
      this.database = database;
      producer =
          new WebRequestLogProducer(
              database,
              codec,
              new WebLogOutboxRepository(() -> 0),
              logger,
              CLOCK,
              UUID::randomUUID,
              "pt-1",
              "cfg-1",
              () -> {
                throw new AssertionError("unexpected terminal");
              });
    }

    @Override
    public void close() {
      codec.close();
    }
  }

  record Entry(Level level, JsonObject json) {}

  static final class RecordingLogger implements Logger {
    final List<Entry> entries = new CopyOnWriteArrayList<>();
    volatile boolean fail;
    volatile boolean enabled = true;

    @Override
    public String getName() {
      return "independent-request-log";
    }

    @Override
    public boolean isLoggable(Level level) {
      return enabled;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable failure) {
      throw new AssertionError("primitive request log must not carry Throwable");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      if (fail) throw new IllegalStateException("synthetic-local-private-canary");
      assertNull(bundle);
      assertNull(parameters);
      entries.add(new Entry(level, JsonParser.parseString(format).getAsJsonObject()));
    }
  }

  private static final class ZeroNonce extends SecureRandom {
    private static final long serialVersionUID = 1L;

    @Override
    public void nextBytes(byte[] bytes) {
      assertEquals(12, bytes.length);
      Arrays.fill(bytes, (byte) 0);
    }
  }

  @FunctionalInterface
  interface OpenConnection {
    Connection open() throws SQLException;
  }

  static DataSource source(OpenConnection open) {
    return proxy(
        DataSource.class,
        (instance, method, args) -> {
          if (method.getName().equals("getConnection")) return open.open();
          throw new AssertionError("unexpected DataSource method");
        });
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static Object invoke(Object owner, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(owner, args);
    } catch (InvocationTargetException wrapped) {
      throw wrapped.getCause();
    }
  }

  static byte[] independentDecrypt(UUID event, UUID correlation, byte[] envelope) throws Exception {
    assertArrayEquals("NKENC1".getBytes(StandardCharsets.US_ASCII), Arrays.copyOf(envelope, 6));
    assertEquals(1, envelope[6]);
    assertEquals(2, envelope[7]);
    assertEquals("v1", new String(envelope, 8, 2, StandardCharsets.US_ASCII));
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE,
        new SecretKeySpec(KEY, "AES"),
        new GCMParameterSpec(128, Arrays.copyOfRange(envelope, 10, 22)));
    cipher.updateAAD(aad(event, correlation));
    return cipher.doFinal(Arrays.copyOfRange(envelope, 22, envelope.length));
  }

  private static byte[] envelope(UUID event, UUID correlation, byte[] plain) throws Exception {
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(KEY, "AES"), new GCMParameterSpec(128, NONCE));
    cipher.updateAAD(aad(event, correlation));
    var out = new ByteArrayOutputStream();
    out.write("NKENC1".getBytes(StandardCharsets.US_ASCII));
    out.write(new byte[] {1, 2, 'v', '1'});
    out.write(NONCE);
    out.write(cipher.doFinal(plain));
    return out.toByteArray();
  }

  private static byte[] aad(UUID event, UUID correlation) throws Exception {
    var out = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(out)) {
      for (byte[] field :
          List.of(
              "web-log-outbox".getBytes(StandardCharsets.US_ASCII),
              "schubert_web_session.web_log_outbox".getBytes(StandardCharsets.US_ASCII),
              HexFormat.of().parseHex(event.toString().replace("-", "")),
              HexFormat.of().parseHex(correlation.toString().replace("-", "")),
              new byte[] {1},
              "v1".getBytes(StandardCharsets.US_ASCII),
              "WLGEVT01".getBytes(StandardCharsets.US_ASCII),
              "001".getBytes(StandardCharsets.US_ASCII))) {
        data.writeInt(field.length);
        data.write(field);
      }
    }
    return out.toByteArray();
  }

  private static byte[] golden(UUID request, UUID event, UUID correlation) {
    byte[] wire = new byte[2336];
    Arrays.fill(wire, (byte) ' ');
    put(wire, 0, "SCHBNK01001WLGEVT01001EI");
    put(wire, 24, event.toString());
    put(wire, 60, correlation.toString());
    put(wire, 96, "20261003100000123");
    put(wire, 177, "0256002080000000000000000002336");
    put(wire, 256, "20261003100000123");
    put(wire, 273, "REQUEST");
    put(wire, 289, "INFO");
    put(wire, 297, "HTTP_REQUEST_COMPLETED");
    put(wire, 361, "HTTP request completed");
    put(wire, 873, request.toString());
    put(wire, 909, FIXTURE_GET_04F32A7E);
    put(wire, 917, "/login");
    put(wire, 1173, "200");
    put(wire, 1176, "12");
    put(wire, 1185, "203.0.113.7");
    put(wire, 1299, "{\"responseBytes\":3,\"projectionStatus\":\"PENDING\"}");
    return wire;
  }

  private static void put(byte[] wire, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(bytes, 0, wire, offset, bytes.length);
  }

  private static long count() throws SQLException {
    try (var connection = db.web();
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery("select count(*) from schubert_web_session.web_log_outbox")) {
      assertTrue(rows.next());
      return rows.getLong(1);
    }
  }

  private static byte[] ciphertext(UUID event) throws SQLException {
    try (var connection = db.web();
        var statement =
            connection.prepareStatement(
                "select payload_ciphertext from schubert_web_session.web_log_outbox where message_id=?")) {
      statement.setObject(1, event);
      try (var rows = statement.executeQuery()) {
        assertTrue(rows.next());
        byte[] result = rows.getBytes(1);
        assertFalse(rows.next());
        return result;
      }
    }
  }
}
