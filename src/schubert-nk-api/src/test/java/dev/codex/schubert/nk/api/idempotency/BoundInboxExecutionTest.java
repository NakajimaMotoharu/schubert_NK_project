package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Real PostgreSQL, independent SQL/LP/HMAC/body expectations. SSC-033/PT-IDEM-B01..B04. */
final class BoundInboxExecutionTest {
  private static final String FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC =
      "delete from schubert.request_inbox";
  private static final String FIXTURE_USTREQ01_D6E6CD9B = "USTREQ01";
  private static final String FIXTURE_USER_3_2B58DC49 = "USER:3";
  private static final String FIXTURE_WRONG_PK_A0157D1B = "wrong-pk";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final UUID ORIGINAL = new UUID(0x5800000000000000L, 1);
  private static final UUID RETRY = new UUID(0x5800000000000000L, 2);
  private static final UUID TOKEN = new UUID(0x5800000000000000L, 3);
  private static final Instant RECEIVED = Instant.parse("2026-09-08T01:00:00Z");
  private static final Instant FINISHED = RECEIVED.plusSeconds(2);
  private static final byte[] BODY = "000000000003000000001   ".getBytes(StandardCharsets.US_ASCII);
  private static final InboxHandler NEVER =
      ignored -> {
        throw new AssertionError("replay executed handler");
      };
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
    sql("delete from schubert.app_users");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(1,'owner','owner','synthetic-test-hash','USER','ACTIVE','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z')");
  }

  @Test
  void boundFirstMessageAndOperationTokenKeepOriginalAadIdentity() throws Exception {
    try (var keys = keys();
        var crypto = crypto();
        var canonical = canonical(FIXTURE_USTREQ01_D6E6CD9B, FIXTURE_USER_3_2B58DC49);
        var c = database.transaction()) {
      var coordinator = new JdbcInboxCoordinator(keys);
      var completion = completion(crypto.encrypt(identity(ORIGINAL), BODY));
      var calls = new AtomicInteger();
      var first =
          coordinator.executeBound(
              c,
              request(ORIGINAL, canonical),
              ignored -> {
                calls.incrementAndGet();
                return completion;
              });
      assertEquals(ORIGINAL, first.sourceMessageId());
      assertEquals(InboxExecutionStatus.EXECUTED, first.execution().status());
      assertEquals(completion, first.execution().completion().orElseThrow());
      assertEquals(0, count()); // Coordinator does not commit caller's work.
      c.commit();
      var stored = metadata();
      for (UUID message : List.of(ORIGINAL, RETRY)) {
        var replay = coordinator.executeBound(c, request(message, canonical), NEVER);
        assertEquals(ORIGINAL, replay.sourceMessageId());
        assertEquals(InboxExecutionStatus.REPLAY, replay.execution().status());
        var saved = replay.execution().completion().orElseThrow();
        assertEquals(3, saved.resultReference().numericId().orElseThrow());
        assertEquals(FINISHED, saved.completedAt());
        assertArrayEquals(
            BODY,
            crypto.decrypt(
                identity(replay.sourceMessageId()), saved.responseSnapshot().orElseThrow()));
        assertThrows(
            ResponseSnapshotException.class,
            () -> crypto.decrypt(identity(RETRY), saved.responseSnapshot().orElseThrow()));
        assertSameResult(
            replay.execution(), coordinator.execute(c, request(message, canonical), NEVER));
        c.commit();
        assertEquals(stored, metadata());
      }
      assertEquals(1, calls.get());
      assertEquals(1, count());
      assertEquals("BoundInboxExecution[REDACTED]", first.toString());
      assertFalse(first.toString().contains(ORIGINAL.toString()));
    }
  }

  @Test
  void boundNullCorruptIdentityAndSqlFaultsNeverProduceReplay() throws Exception {
    try (var keys = keys();
        var canonical = canonical(FIXTURE_USTREQ01_D6E6CD9B, FIXTURE_USER_3_2B58DC49);
        var c = database.transaction()) {
      var coordinator = new JdbcInboxCoordinator(keys);
      var request = request(ORIGINAL, canonical);
      assertThrows(
          NullPointerException.class,
          () -> new BoundInboxExecution(null, InboxExecution.inProgress()));
      assertThrows(NullPointerException.class, () -> new BoundInboxExecution(ORIGINAL, null));
      assertThrows(
          NullPointerException.class, () -> coordinator.executeBound(null, request, NEVER));
      assertThrows(NullPointerException.class, () -> coordinator.executeBound(c, null, NEVER));
      assertThrows(NullPointerException.class, () -> coordinator.executeBound(c, request, null));
      try (var auto = database.api()) {
        assertEquals(
            InboxException.Reason.TRANSACTION_REQUIRED,
            assertThrows(InboxException.class, () -> coordinator.executeBound(auto, request, NEVER))
                .reason());
      }
      seedProcessing(request);
      for (String fault :
          List.of(
              "null-pk", FIXTURE_WRONG_PK_A0157D1B, "query", "result-close", "statement-close")) {
        Exception failure =
            assertThrows(
                Exception.class,
                () ->
                    coordinator.executeBound(fault(c, fault, new AtomicInteger()), request, NEVER));
        if (fault.equals("null-pk"))
          assertEquals(
              "22004", assertInstanceOf(java.sql.SQLDataException.class, failure).getSQLState());
        else if (fault.equals(FIXTURE_WRONG_PK_A0157D1B))
          assertEquals(InboxException.Reason.MESSAGE_ID_REUSE, ((InboxException) failure).reason());
        else assertInstanceOf(SQLException.class, failure);
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        c.rollback();
        assertEquals(1, count());
      }
      for (String change :
          List.of(
              "fingerprint_key_version='unknown'",
              "request_fingerprint_hmac='" + "ff".repeat(32) + "'")) {
        sql("update schubert.request_inbox set " + change);
        assertThrows(InboxException.class, () -> coordinator.executeBound(c, request, NEVER));
        c.rollback();
        sql(
            "update schubert.request_inbox set fingerprint_key_version='fp1',request_fingerprint_hmac='"
                + hmac(canonical)
                + "'");
      }
      try (var read = database.transaction()) {
        read.setReadOnly(true);
        assertEquals(
            InboxException.Reason.MESSAGE_ID_REUSE,
            assertThrows(
                    InboxException.class,
                    () ->
                        coordinator.inspectMessage(
                            fault(read, FIXTURE_WRONG_PK_A0157D1B, new AtomicInteger()), request))
                .reason());
        read.rollback();
        assertFalse(read.isClosed());
        assertTrue(read.isReadOnly());
      }
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      assertThrows(
          SQLException.class,
          () ->
              coordinator.executeBound(
                  c,
                  request,
                  ignored -> {
                    throw new SQLException("synthetic handler failure");
                  }));
      assertEquals(0, count());
      c.rollback();
      assertEquals(0, count());
    }
  }

  @Test
  void boundConcurrentInsertRecoveryAndProcessingUseStoredMessage() throws Exception {
    try (var keys = keys();
        var canonical = canonical(FIXTURE_USTREQ01_D6E6CD9B, FIXTURE_USER_3_2B58DC49)) {
      var coordinator = new JdbcInboxCoordinator(keys);
      for (UUID incoming : List.of(ORIGINAL, RETRY)) {
        sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
        try (var c = database.transaction()) {
          var injected = afterSavepoint(c, () -> seedProcessing(request(ORIGINAL, canonical)));
          var result = coordinator.executeBound(injected, request(incoming, canonical), NEVER);
          assertEquals(ORIGINAL, result.sourceMessageId());
          assertEquals(InboxExecutionStatus.IN_PROGRESS, result.execution().status());
          assertTrue(result.execution().completion().isEmpty());
          c.commit();
          assertEquals(result, coordinator.executeBound(c, request(incoming, canonical), NEVER));
          c.commit();
          assertEquals(1, count());
        }
      }
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      var calls = new AtomicInteger();
      try (var workers = Executors.newFixedThreadPool(10)) {
        var results = new ArrayList<java.util.concurrent.Future<BoundInboxExecution>>();
        for (int n = 0; n < 100; n++) {
          UUID message = new UUID(0x5900000000000000L, n);
          results.add(
              workers.submit(
                  () -> {
                    try (var local = canonical(FIXTURE_USTREQ01_D6E6CD9B, FIXTURE_USER_3_2B58DC49);
                        var c = database.transaction()) {
                      var result =
                          coordinator.executeBound(
                              c,
                              request(message, local),
                              ignored -> {
                                calls.incrementAndGet();
                                return completion(
                                    new EncryptedResponseSnapshot("test", new byte[29]));
                              });
                      c.commit();
                      return result;
                    }
                  }));
        }
        var completed = new ArrayList<BoundInboxExecution>();
        for (var future : results) completed.add(future.get(20, TimeUnit.SECONDS));
        assertEquals(100, completed.size());
        assertEquals(
            1,
            completed.stream()
                .filter(r -> r.execution().status() == InboxExecutionStatus.EXECUTED)
                .count());
        assertEquals(
            99,
            completed.stream()
                .filter(r -> r.execution().status() == InboxExecutionStatus.REPLAY)
                .count());
        assertEquals(
            1, completed.stream().map(BoundInboxExecution::sourceMessageId).distinct().count());
        assertEquals(completed.getFirst().sourceMessageId().toString(), metadata().getFirst());
      }
      assertEquals(1, calls.get());
      assertEquals(1, count());
    }
  }

  @Test
  void boundCompatibilityPreservesReadOnlyAndSnapshotReplacement() throws Exception {
    try (var keys = keys();
        var canonical = canonical("SCNREQ01", "30");
        var c = database.transaction()) {
      var coordinator = new JdbcInboxCoordinator(keys);
      var request = request(ORIGINAL, canonical);
      var old = scenario(1);
      var next = scenario(2);
      assertEquals(InboxExecution.executed(old), coordinator.execute(c, request, ignored -> old));
      c.commit();
      var before = metadata();
      assertEquals(ORIGINAL, coordinator.executeBound(c, request, NEVER).sourceMessageId());
      coordinator.replaceScenarioSnapshot(c, request, old, next);
      c.rollback();
      assertArrayEquals(
          old.responseSnapshot().orElseThrow().ciphertext(),
          coordinator
              .execute(c, request, NEVER)
              .completion()
              .orElseThrow()
              .responseSnapshot()
              .orElseThrow()
              .ciphertext());
      coordinator.replaceScenarioSnapshot(c, request, old, next);
      c.commit();
      assertEquals(before, metadata());
      var rebound = coordinator.executeBound(c, request, NEVER);
      assertEquals(ORIGINAL, rebound.sourceMessageId());
      assertArrayEquals(
          next.responseSnapshot().orElseThrow().ciphertext(),
          rebound
              .execution()
              .completion()
              .orElseThrow()
              .responseSnapshot()
              .orElseThrow()
              .ciphertext());
      c.commit();
      try (var read = database.transaction()) {
        read.setReadOnly(true);
        var queries = new AtomicInteger();
        assertSameResult(
            rebound.execution(),
            coordinator.inspectMessage(fault(read, "none", queries), request).orElseThrow());
        assertEquals(1, queries.get());
        assertTrue(read.isReadOnly());
        assertFalse(read.isClosed());
        read.commit();
      }
      assertEquals(before, metadata());
      // Bound metadata from a USER fixture conveys no current ADMIN authorization.
      try (var read = database.api();
          var s = read.createStatement();
          var r = s.executeQuery("select role from schubert.app_users where id=1")) {
        assertTrue(r.next());
        assertEquals("USER", r.getString(1));
        assertFalse(r.next());
      }
    }
  }

  private static FingerprintKeyRing keys() {
    return new FingerprintKeyRing("fp1", new byte[32], null, null);
  }

  private static void assertSameResult(InboxExecution a, InboxExecution b) {
    assertEquals(a.status(), b.status());
    var left = a.completion().orElseThrow();
    var right = b.completion().orElseThrow();
    assertEquals(left.state(), right.state());
    assertEquals(left.resultReference(), right.resultReference());
    assertEquals(left.responseLayoutId(), right.responseLayoutId());
    assertEquals(left.responseVersion(), right.responseVersion());
    assertEquals(left.completedAt(), right.completedAt());
    assertEquals(
        left.responseSnapshot().orElseThrow().keyVersion(),
        right.responseSnapshot().orElseThrow().keyVersion());
    assertArrayEquals(
        left.responseSnapshot().orElseThrow().ciphertext(),
        right.responseSnapshot().orElseThrow().ciphertext());
  }

  private static ResponseSnapshotCodec crypto() {
    return new ResponseSnapshotCodec("test", new byte[32], null, null);
  }

  private static ResponseSnapshotIdentity identity(UUID message) {
    return ResponseSnapshotIdentity.authenticated(message, "USTRSP01", FIXTURE_001_A3FEAA64, 1);
  }

  private static CanonicalRequest canonical(String layout, String target) {
    return new CanonicalRequest("1", layout, FIXTURE_001_A3FEAA64, target, List.of());
  }

  private static InboxRequest request(UUID message, CanonicalRequest canonical) {
    return new InboxRequest(
        message,
        message,
        OptionalLong.of(1),
        canonical.layoutId().equals(FIXTURE_USTREQ01_D6E6CD9B)
            ? Optional.of(TOKEN)
            : Optional.empty(),
        canonical,
        RECEIVED,
        RECEIVED.plusSeconds(86400));
  }

  private static InboxCompletion completion(EncryptedResponseSnapshot snapshot) {
    return new InboxCompletion(
        InboxCompletionState.COMPLETED,
        InboxResultReference.numeric(InboxResultReferenceType.USER, 3),
        "USTRSP01",
        FIXTURE_001_A3FEAA64,
        Optional.of(snapshot),
        FINISHED);
  }

  private static InboxCompletion scenario(int value) {
    byte[] bytes = new byte[29];
    java.util.Arrays.fill(bytes, (byte) value);
    return new InboxCompletion(
        InboxCompletionState.COMPLETED,
        InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 30),
        "SCNRSP01",
        FIXTURE_001_A3FEAA64,
        Optional.of(new EncryptedResponseSnapshot("test", bytes)),
        FINISHED);
  }

  private static void sql(String sql) throws Exception {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  private static int count() throws Exception {
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert.request_inbox")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static List<String> metadata() throws Exception {
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select message_id,correlation_id,request_layout_id,owner_user_id,processing_state,result_ref_type,result_ref_id,response_layout_id,response_version,completed_at,expires_at from schubert.request_inbox")) {
      assertTrue(r.next());
      var values = new ArrayList<String>();
      for (int i = 1; i <= 11; i++) values.add(r.getString(i));
      assertEquals(FINISHED, r.getObject(10, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          FINISHED.plusSeconds(86400), r.getObject(11, java.time.OffsetDateTime.class).toInstant());
      assertFalse(r.next());
      return values;
    }
  }

  private static String hmac(CanonicalRequest canonical) throws Exception {
    var buffer = new ByteArrayOutputStream();
    try (var stream = new DataOutputStream(buffer)) {
      stream.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
      for (String value :
          List.of("1", canonical.layoutId(), FIXTURE_001_A3FEAA64, canonical.target())) {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        stream.writeInt(bytes.length);
        stream.write(bytes);
      }
      stream.writeInt(0);
    }
    var mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(new byte[32], "HmacSHA256"));
    return HexFormat.of().formatHex(mac.doFinal(buffer.toByteArray()));
  }

  private static void seedProcessing(InboxRequest request) throws Exception {
    try (var c = database.transaction();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,created_at,expires_at) values(?,?,?,'001',1,?,?,'fp1','PROCESSING',?,?)")) {
      s.setObject(1, request.messageId());
      s.setObject(2, request.correlationId());
      s.setString(3, request.canonicalRequest().layoutId());
      s.setObject(4, request.operationToken().orElse(null));
      s.setString(5, hmac(request.canonicalRequest()));
      s.setObject(6, RECEIVED.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(7, RECEIVED.plusSeconds(86400).atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
      c.commit();
    }
  }

  private interface SqlAction {
    void run() throws Exception;
  }

  private static Connection afterSavepoint(Connection c, SqlAction action) {
    var calls = new AtomicInteger();
    return (Connection)
        Proxy.newProxyInstance(
            BoundInboxExecutionTest.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              Object result = invoke(c, m, a);
              if (m.getName().equals("setSavepoint")
                  && m.getParameterCount() == 0
                  && calls.getAndIncrement() == 0) action.run();
              return result;
            });
  }

  private static Connection fault(Connection c, String mode, AtomicInteger queries) {
    return (Connection)
        Proxy.newProxyInstance(
            BoundInboxExecutionTest.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              Object result = invoke(c, m, a);
              if (m.getName().equals("prepareStatement")
                  && a[0].toString().startsWith("select correlation_id")) {
                queries.incrementAndGet();
                var statement = (PreparedStatement) result;
                return Proxy.newProxyInstance(
                    BoundInboxExecutionTest.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (sp, sm, sa) -> {
                      if (sm.getName().equals("executeQuery") && mode.equals("query"))
                        throw new SQLException("synthetic query fault");
                      Object sr = invoke(statement, sm, sa);
                      if (sm.getName().equals("close") && mode.equals("statement-close"))
                        throw new SQLException("synthetic close fault");
                      if (sm.getName().equals("executeQuery")) {
                        var rows = (ResultSet) sr;
                        return Proxy.newProxyInstance(
                            BoundInboxExecutionTest.class.getClassLoader(),
                            new Class<?>[] {ResultSet.class},
                            (rp, rm, ra) -> {
                              if (rm.getName().equals("getObject") && "message_id".equals(ra[0])) {
                                if (mode.equals("null-pk")) return null;
                                if (mode.equals(FIXTURE_WRONG_PK_A0157D1B)) return RETRY;
                              }
                              Object rr = invoke(rows, rm, ra);
                              if (rm.getName().equals("close") && mode.equals("result-close"))
                                throw new SQLException("synthetic close fault");
                              return rr;
                            });
                      }
                      return sr;
                    });
              }
              return result;
            });
  }

  private static Object invoke(Object target, Method method, Object[] arguments) throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}
