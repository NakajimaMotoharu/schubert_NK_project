package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
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
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS324 §7.1/333 §6.1; SSC-027; PT-IDEM-SR01..SR03. Real PG, independent SQL/HMAC. */
final class JdbcScenarioSnapshotReplacementTest {
  private static final String FIXTURE_SCNREQ01_2CFBA57E = "SCNREQ01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_SNAPSHOT1_AA1B72D1 = "snapshot1";
  private static final String FIXTURE_SCNRSP01_DD42C8D5 = "SCNRSP01";
  private static final String FIXTURE_EXECUTEUPDATE_5E0BBF58 = "executeUpdate";
  private static final UUID MESSAGE = new UUID(0x5700000000000000L, 1);
  private static final Instant RECEIVED = Instant.parse("2026-09-08T00:00:00Z");
  private static final Instant COMPLETED = Instant.parse("2026-09-08T00:00:01.123456Z");
  private static final InboxResultReference FILE =
      InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 30);
  private static final String METADATA =
      "message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,"
          + "request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,"
          + "result_ref_id,result_ref_uuid,response_layout_id,response_version,created_at,completed_at,expires_at";
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
  void users() throws Exception {
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.app_users");
    for (int id : new int[] {101, 102})
      sql(
          "insert into schubert.app_users(id,username,username_key,password_hash,role,status,"
              + "password_changed_at,created_at,updated_at) values("
              + id
              + ",'owner"
              + id
              + "','key"
              + id
              + "','{pbkdf2-v1}public-test-hash','USER','ACTIVE',"
              + "'2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z')");
    seed();
  }

  @Test
  void replacementCommitsOnlyCiphertextAndKeyWithoutExtendingLifetime() throws Exception {
    var request = request(FIXTURE_SCNREQ01_2CFBA57E, FIXTURE_001_A3FEAA64, 101, MESSAGE, "30");
    var canonical = request.canonicalRequest();
    try (canonical;
        var keys = keys()) {
      var coordinator = new JdbcInboxCoordinator(keys);
      var before = metadata();
      assertEquals(MESSAGE.toString(), before.get(0));
      assertEquals("101", before.get(4));
      assertEquals(hmac(), before.get(6));
      assertEquals("SCENARIO_FILE", before.get(9));
      assertEquals("30", before.get(10));
      try (var connection = database.transaction()) {
        coordinator.replaceScenarioSnapshot(connection, request, old(), next());
        assertFalse(connection.isClosed());
        assertFalse(connection.getAutoCommit());
        assertFalse(connection.isReadOnly());
        assertStored(
            FIXTURE_SNAPSHOT1_AA1B72D1,
            bytes(0)); // Another connection cannot see uncommitted bytes.
        connection.rollback();
        assertStored(FIXTURE_SNAPSHOT1_AA1B72D1, bytes(0));
        coordinator.replaceScenarioSnapshot(connection, request, old(), next());
        connection.commit();
        assertStored("snapshot2", bytes(7));
        assertEquals(before, metadata());
        assertTimes();
        assertEquals(
            InboxException.Reason.STATE_CORRUPT,
            assertThrows(
                    InboxException.class,
                    () -> coordinator.replaceScenarioSnapshot(connection, request, old(), next()))
                .reason());
        connection.rollback();
      }
      seed();
      var ready = new CountDownLatch(2);
      var release = new CountDownLatch(1);
      try (var workers = Executors.newFixedThreadPool(2)) {
        var results = new ArrayList<java.util.concurrent.Future<Boolean>>();
        for (int n = 0; n < 2; n++) {
          final int candidate = 7 + n;
          results.add(
              workers.submit(
                  () -> {
                    try (var connection = database.transaction()) {
                      ready.countDown();
                      assertTrue(release.await(10, TimeUnit.SECONDS));
                      try {
                        coordinator.replaceScenarioSnapshot(
                            connection,
                            request,
                            old(),
                            completion(
                                InboxCompletionState.COMPLETED,
                                FILE,
                                FIXTURE_SCNRSP01_DD42C8D5,
                                FIXTURE_001_A3FEAA64,
                                Optional.of(
                                    new EncryptedResponseSnapshot(
                                        "snapshot" + candidate, bytes(candidate))),
                                COMPLETED));
                        connection.commit();
                        return true;
                      } catch (InboxException stale) {
                        assertEquals(InboxException.Reason.STATE_CORRUPT, stale.reason());
                        connection.rollback();
                        return false;
                      }
                    }
                  }));
        }
        assertTrue(ready.await(10, TimeUnit.SECONDS));
        release.countDown();
        int successes = 0;
        for (var result : results) if (result.get(15, TimeUnit.SECONDS)) successes++;
        assertEquals(1, successes);
      }
      try (var c = database.api();
          var s = c.createStatement();
          var r =
              s.executeQuery(
                  "select response_key_version,response_body_encrypted from schubert.request_inbox")) {
        assertTrue(r.next());
        assertTrue(List.of("snapshot7", "snapshot8").contains(r.getString(1)));
        assertArrayEquals(bytes(r.getString(1).equals("snapshot7") ? 7 : 8), r.getBytes(2));
        assertFalse(r.next());
      }
      assertEquals(before, metadata());
      assertTimes();
    }
  }

  @Test
  void invalidMetadataIdentityAndStoredStateRejectBeforeReplacement() throws Exception {
    var request = request(FIXTURE_SCNREQ01_2CFBA57E, FIXTURE_001_A3FEAA64, 101, MESSAGE, "30");
    var canonical = request.canonicalRequest();
    try (canonical;
        var keys = keys()) {
      var coordinator = new JdbcInboxCoordinator(keys);
      var before = metadata();
      List<InboxCompletion> malformed =
          List.of(
              completion(
                  InboxCompletionState.ERROR,
                  FILE,
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  old().responseSnapshot(),
                  COMPLETED),
              completion(
                  InboxCompletionState.COMPLETED,
                  InboxResultReference.none(),
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  old().responseSnapshot(),
                  COMPLETED),
              completion(
                  InboxCompletionState.COMPLETED,
                  FILE,
                  "GAMRSP01",
                  FIXTURE_001_A3FEAA64,
                  old().responseSnapshot(),
                  COMPLETED),
              completion(
                  InboxCompletionState.COMPLETED,
                  FILE,
                  FIXTURE_SCNRSP01_DD42C8D5,
                  "002",
                  old().responseSnapshot(),
                  COMPLETED),
              completion(
                  InboxCompletionState.COMPLETED,
                  FILE,
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  Optional.empty(),
                  COMPLETED),
              completion(
                  InboxCompletionState.COMPLETED,
                  FILE,
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  old().responseSnapshot(),
                  COMPLETED.plusNanos(1000)));
      for (var invalid : malformed) {
        reject(coordinator, request, invalid, next());
        reject(coordinator, request, old(), invalid);
      }
      for (var invalid :
          List.of(
              request("GAMREQ01", FIXTURE_001_A3FEAA64, 101, MESSAGE, "30"),
              request(FIXTURE_SCNREQ01_2CFBA57E, "002", 101, MESSAGE, "30"),
              request(FIXTURE_SCNREQ01_2CFBA57E, FIXTURE_001_A3FEAA64, 102, MESSAGE, "30"),
              request(FIXTURE_SCNREQ01_2CFBA57E, FIXTURE_001_A3FEAA64, 101, new UUID(0, 99), "30"),
              request(FIXTURE_SCNREQ01_2CFBA57E, FIXTURE_001_A3FEAA64, 101, MESSAGE, "31"))) {
        var invalidCanonical = invalid.canonicalRequest();
        try (invalidCanonical) {
          reject(coordinator, invalid, old(), next());
        }
      }
      reject(
          coordinator,
          request,
          completion(
              InboxCompletionState.COMPLETED,
              FILE,
              FIXTURE_SCNRSP01_DD42C8D5,
              FIXTURE_001_A3FEAA64,
              Optional.of(new EncryptedResponseSnapshot("unknown", bytes(0))),
              COMPLETED),
          next());
      for (int index = 0; index < 29; index++) {
        byte[] altered = bytes(0);
        altered[index] = 1;
        reject(
            coordinator,
            request,
            completion(
                InboxCompletionState.COMPLETED,
                FILE,
                FIXTURE_SCNRSP01_DD42C8D5,
                FIXTURE_001_A3FEAA64,
                Optional.of(new EncryptedResponseSnapshot(FIXTURE_SNAPSHOT1_AA1B72D1, altered)),
                COMPLETED),
            next());
      }
      assertEquals(before, metadata());
      for (String mutation :
          List.of(
              "processing_state='ERROR'",
              "processing_state='PROCESSING',result_ref_type=null,result_ref_id=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null",
              "result_ref_id=31",
              "response_layout_id='GAMRSP01'",
              "response_version='002'",
              "completed_at=completed_at+interval '1 microsecond'",
              "response_body_encrypted=null,response_key_version=null",
              "response_key_version='unknown'",
              "fingerprint_key_version='unknown'",
              "request_fingerprint_hmac=repeat('0',64)")) {
        sql("update schubert.request_inbox set " + mutation);
        var mutatedMetadata = metadata();
        reject(coordinator, request, old(), next());
        assertEquals(mutatedMetadata, metadata());
        seed();
      }
      try (var c = database.transaction()) {
        var fault = new JdbcFault("nullColumn");
        assertThrows(
            SQLDataException.class,
            () -> coordinator.replaceScenarioSnapshot(fault.connection(c), request, old(), next()));
        c.rollback();
      }
      sql("delete from schubert.request_inbox");
      reject(coordinator, request, old(), next());
      assertEquals(List.of(), metadata());
    }
  }

  @Test
  void nullTransactionAndJdbcFaultsPreserveOwnershipAndClearBindings() throws Exception {
    var request = request(FIXTURE_SCNREQ01_2CFBA57E, FIXTURE_001_A3FEAA64, 101, MESSAGE, "30");
    var canonical = request.canonicalRequest();
    try (canonical;
        var keys = keys();
        var c = database.transaction()) {
      var coordinator = new JdbcInboxCoordinator(keys);
      assertThrows(
          NullPointerException.class,
          () -> coordinator.replaceScenarioSnapshot(null, request, old(), next()));
      assertThrows(
          NullPointerException.class,
          () -> coordinator.replaceScenarioSnapshot(c, null, old(), next()));
      assertThrows(
          NullPointerException.class,
          () -> coordinator.replaceScenarioSnapshot(c, request, null, next()));
      assertThrows(
          NullPointerException.class,
          () -> coordinator.replaceScenarioSnapshot(c, request, old(), null));
      c.setAutoCommit(true);
      assertEquals(
          InboxException.Reason.TRANSACTION_REQUIRED,
          assertThrows(
                  InboxException.class,
                  () -> coordinator.replaceScenarioSnapshot(c, request, old(), next()))
              .reason());
      c.setAutoCommit(false);
      c.setReadOnly(true);
      assertEquals(
          InboxException.Reason.TRANSACTION_REQUIRED,
          assertThrows(
                  InboxException.class,
                  () -> coordinator.replaceScenarioSnapshot(c, request, old(), next()))
              .reason());
      c.rollback();
      c.setReadOnly(false);
      for (String point :
          List.of(
              "getAutoCommit",
              "isReadOnly",
              "prepareUpdate",
              "setBytes",
              "setString",
              "setObject",
              "zero",
              "two",
              FIXTURE_EXECUTEUPDATE_5E0BBF58,
              "afterUpdate",
              "close",
              "executeAndClose")) {
        var fault = new JdbcFault(point);
        var replacement = next();
        assertThrows(
            SQLException.class,
            () ->
                coordinator.replaceScenarioSnapshot(
                    fault.connection(c), request, old(), replacement),
            point);
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        c.rollback();
        assertStored(FIXTURE_SNAPSHOT1_AA1B72D1, bytes(0));
        for (byte[] binding : fault.bindings) assertArrayEquals(new byte[29], binding, point);
        assertArrayEquals(bytes(7), replacement.responseSnapshot().orElseThrow().ciphertext());
      }
      var observed = new JdbcFault("none");
      coordinator.replaceScenarioSnapshot(observed.connection(c), request, old(), next());
      assertEquals(1, observed.bindings.size());
      assertArrayEquals(new byte[29], observed.bindings.getFirst());
      c.rollback();
      assertStored(FIXTURE_SNAPSHOT1_AA1B72D1, bytes(0));
      assertTimes();
    }
  }

  private static void reject(
      JdbcInboxCoordinator coordinator,
      InboxRequest request,
      InboxCompletion expected,
      InboxCompletion replacement)
      throws Exception {
    var before = storedRow();
    try (var connection = database.transaction()) {
      assertThrows(
          InboxException.class,
          () -> coordinator.replaceScenarioSnapshot(connection, request, expected, replacement));
      assertFalse(connection.isClosed());
      connection.rollback();
    }
    assertEquals(before, storedRow());
  }

  private static List<String> storedRow() throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select "
                    + METADATA
                    + ",encode(response_body_encrypted,'hex'),response_key_version from schubert.request_inbox")) {
      var result = new ArrayList<String>();
      if (r.next()) for (int col = 1; col <= 19; col++) result.add(r.getString(col));
      assertFalse(r.next());
      return result;
    }
  }

  private static InboxRequest request(
      String layout, String version, long owner, UUID correlation, String id) {
    return new InboxRequest(
        MESSAGE,
        correlation,
        OptionalLong.of(owner),
        Optional.empty(),
        new CanonicalRequest(
            Long.toString(owner),
            layout,
            version,
            "REQUEST:" + layout,
            List.of(
                new CanonicalField("scriptFileId", "N1", id.getBytes(StandardCharsets.US_ASCII)))),
        RECEIVED,
        RECEIVED.plusSeconds(86400));
  }

  private static InboxCompletion old() {
    return completion(
        InboxCompletionState.COMPLETED,
        FILE,
        FIXTURE_SCNRSP01_DD42C8D5,
        FIXTURE_001_A3FEAA64,
        Optional.of(new EncryptedResponseSnapshot(FIXTURE_SNAPSHOT1_AA1B72D1, bytes(0))),
        COMPLETED);
  }

  private static InboxCompletion next() {
    return completion(
        InboxCompletionState.COMPLETED,
        FILE,
        FIXTURE_SCNRSP01_DD42C8D5,
        FIXTURE_001_A3FEAA64,
        Optional.of(new EncryptedResponseSnapshot("snapshot2", bytes(7))),
        COMPLETED);
  }

  private static InboxCompletion completion(
      InboxCompletionState state,
      InboxResultReference ref,
      String layout,
      String version,
      Optional<EncryptedResponseSnapshot> snapshot,
      Instant time) {
    return new InboxCompletion(state, ref, layout, version, snapshot, time);
  }

  private static byte[] bytes(int value) {
    byte[] result = new byte[29];
    Arrays.fill(result, (byte) value);
    return result;
  }

  private static byte[] key() {
    byte[] result = new byte[32];
    Arrays.fill(result, (byte) 11);
    return result;
  }

  private static FingerprintKeyRing keys() {
    return new FingerprintKeyRing("fp1", key(), null, null);
  }

  private static String hmac() throws Exception {
    var bytes = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(bytes)) {
      data.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
      for (String value :
          List.of("101", FIXTURE_SCNREQ01_2CFBA57E, FIXTURE_001_A3FEAA64, "REQUEST:SCNREQ01"))
        lp(data, value);
      data.writeInt(1);
      for (String value : List.of("scriptFileId", "N1", "30")) lp(data, value);
    }
    var mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(key(), "HmacSHA256"));
    return HexFormat.of().formatHex(mac.doFinal(bytes.toByteArray()));
  }

  private static void lp(DataOutputStream data, String value) throws Exception {
    byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
    data.writeInt(encoded.length);
    data.write(encoded);
  }

  private static void seed() throws Exception {
    sql("delete from schubert.request_inbox");
    // Literal DDL oracle; ciphertext is storage-only, not an AES validity claim.
    sql(
        "insert into schubert.request_inbox("
            + METADATA
            + ",response_body_encrypted,response_key_version) values('"
            + MESSAGE
            + "','"
            + MESSAGE
            + "','SCNREQ01','001',101,null,'"
            + hmac()
            + "','fp1','COMPLETED','SCENARIO_FILE',30,null,'SCNRSP01','001',"
            + "'2026-09-08T00:00:00Z','2026-09-08T00:00:01.123456Z','2026-09-09T00:00:01.123456Z',"
            + "decode(repeat('00',29),'hex'),'snapshot1')");
  }

  private static void sql(String sql) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  private static List<String> metadata() throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery("select " + METADATA + " from schubert.request_inbox")) {
      var values = new ArrayList<String>();
      if (r.next()) for (int col = 1; col <= 17; col++) values.add(r.getString(col));
      assertFalse(r.next());
      return values;
    }
  }

  private static void assertStored(String version, byte[] bytes) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select response_key_version,response_body_encrypted from schubert.request_inbox")) {
      assertTrue(r.next());
      assertEquals(version, r.getString(1));
      assertArrayEquals(bytes, r.getBytes(2));
      assertFalse(r.next());
    }
  }

  private static void assertTimes() throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select created_at,completed_at,expires_at from schubert.request_inbox")) {
      assertTrue(r.next());
      assertEquals(RECEIVED, r.getObject(1, java.time.OffsetDateTime.class).toInstant());
      assertEquals(COMPLETED, r.getObject(2, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-09T00:00:01.123456Z"),
          r.getObject(3, java.time.OffsetDateTime.class).toInstant());
      assertFalse(r.next());
    }
  }

  /** Public JDBC boundary fault injection; no private production reflection or alternate SQL. */
  private static final class JdbcFault {
    private final String point;
    private final List<byte[]> bindings = new ArrayList<>();

    private JdbcFault(String point) {
      this.point = point;
    }

    private Connection connection(Connection delegate) {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (method.getName().equals(point))
                  throw new SQLException("synthetic provider failure", "08006");
                if (method.getName().equals("prepareStatement")) {
                  boolean update = ((String) args[0]).startsWith("update ");
                  if (update && point.equals("prepareUpdate"))
                    throw new SQLException("synthetic prepare");
                  return statement((PreparedStatement) invoke(delegate, method, args), update);
                }
                return invoke(delegate, method, args);
              });
    }

    private PreparedStatement statement(PreparedStatement delegate, boolean update) {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (update && name.equals("setBytes")) bindings.add((byte[]) args[1]);
                if (update
                    && (name.equals(point)
                        || (name.equals(FIXTURE_EXECUTEUPDATE_5E0BBF58)
                            && point.equals("executeAndClose")))) {
                  if (name.equals("close")) delegate.close();
                  throw new SQLException("synthetic JDBC failure", "08006");
                }
                if (update && name.equals(FIXTURE_EXECUTEUPDATE_5E0BBF58) && point.equals("zero"))
                  return 0;
                if (update && name.equals(FIXTURE_EXECUTEUPDATE_5E0BBF58) && point.equals("two"))
                  return 2;
                Object result = invoke(delegate, method, args);
                if (update
                    && name.equals(FIXTURE_EXECUTEUPDATE_5E0BBF58)
                    && point.equals("afterUpdate"))
                  throw new SQLException("synthetic after update");
                if (update && name.equals("close") && point.equals("executeAndClose"))
                  throw new SQLException("synthetic close");
                if (name.equals("executeQuery") && point.equals("nullColumn"))
                  return Proxy.newProxyInstance(
                      ResultSet.class.getClassLoader(),
                      new Class<?>[] {ResultSet.class},
                      (p, m, a) ->
                          m.getName().equals("getString") && "response_layout_id".equals(a[0])
                              ? null
                              : invoke(result, m, a));
                return result;
              });
    }

    private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
      try {
        return method.invoke(target, args);
      } catch (InvocationTargetException exception) {
        throw exception.getCause();
      }
    }
  }
}
