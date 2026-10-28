package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.zip.Deflater;
import java.util.zip.DeflaterOutputStream;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-009..016. Independent wire/AAD/JCE and SQL fixtures, no Production capture. */
final class AuthenticationInboxInspectorTest {
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_0101_F2D4F761 = "0101";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final UUID REQUEST = new UUID(0, 101);
  private static final UUID SESSION = new UUID(0, 104);
  private static final ResponseSnapshotIdentity LOGIN =
      ResponseSnapshotIdentity.anonymous(REQUEST, "LGNRSP01", FIXTURE_001_A3FEAA64);
  private static final ResponseSnapshotIdentity LOGOUT =
      ResponseSnapshotIdentity.authenticated(REQUEST, "LOGRSP01", FIXTURE_001_A3FEAA64, 7);

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.api();
        var s = c.createStatement()) {
      s.execute("delete from schubert.app_logs");
      s.execute("delete from schubert.auth_sessions");
      s.execute("delete from schubert.app_users");
      s.execute(
          "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values (7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09'),(8,'Other','other','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09')");
    }
  }

  @Test
  void loginOriginalAndLaterAccountState() throws Exception {
    try (var f = new Fixture();
        var c = db.transaction()) {
      f.seed(c, false);
      var saved = f.saved(LOGIN, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      assertTrue(f.inspector.isConsistent(c, LOGIN, saved));
      try (var s = c.createStatement()) {
        s.execute(
            "update schubert.app_users set username='Changed',role='ADMIN',status='DISABLED' where id=7");
        s.execute(
            "update schubert.auth_sessions set last_accessed_at=issued_at+interval '1 hour',expires_at=issued_at+interval '9 hours',revoked=true,revoked_at=issued_at+interval '2 hours',revoke_reason='ADMIN'");
      }
      assertTrue(f.inspector.isConsistent(c, LOGIN, saved));
      assertEquals(
          "2026-09-09T00:00:00.123Z|2026-09-09T01:00:00.123Z|2026-09-09T09:00:00.123Z|true|0",
          state(c));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      String unchanged = state(c);
      try (var statement = c.createStatement()) {
        statement.execute("set local timezone='UTC'");
      }
      assertEquals(unchanged, state(c));
      assertTrue(f.inspector.isConsistent(c, LOGIN, saved));
      try (var statement = c.createStatement()) {
        statement.execute("set local timezone='Asia/Tokyo'");
      }
      assertEquals(unchanged, state(c));
      c.rollback();
    }
  }

  @Test
  void logoutOwnerAndRevokedReference() throws Exception {
    try (var f = new Fixture();
        var c = db.transaction()) {
      f.seed(c, true);
      for (String code : List.of(FIXTURE_0000_876EEFE0, "0200"))
        assertTrue(
            f.inspector.isConsistent(
                c, LOGOUT, f.saved(LOGOUT, code, InboxResultReference.authSession(SESSION))));
      var saved = f.saved(LOGOUT, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      for (String change :
          List.of(
              "user_id=8",
              "context_hash=repeat('0',64)",
              "revoked_at=revoked_at+interval '1 millisecond'",
              "revoked=false,revoked_at=null,revoke_reason=null")) {
        var point = c.setSavepoint();
        try (var s = c.createStatement()) {
          s.execute("update schubert.auth_sessions set " + change);
        }
        assertFalse(f.inspector.isConsistent(c, LOGOUT, saved));
        c.rollback(point);
        c.releaseSavepoint(point);
      }
      assertFalse(
          f.inspector.isConsistent(
              c,
              LOGOUT,
              f.saved(
                  LOGOUT,
                  FIXTURE_0000_876EEFE0,
                  InboxResultReference.authSession(new UUID(0, 999)))));
      assertEquals(
          "2026-09-09T00:00:00.123Z|2026-09-09T00:00:00.123Z|2026-09-09T08:00:00.123Z|true|0",
          state(c));
      c.rollback();
    }
  }

  @Test
  void deterministicErrorReferences() throws Exception {
    try (var f = new Fixture();
        var c = db.transaction()) {
      for (String code : List.of(FIXTURE_0101_F2D4F761, "0106")) {
        assertTrue(
            f.inspector.isConsistent(c, LOGIN, f.saved(LOGIN, code, InboxResultReference.none())));
        assertFalse(
            f.inspector.isConsistent(
                c, LOGIN, f.saved(LOGIN, code, InboxResultReference.authSession(SESSION))));
      }
      assertTrue(
          f.inspector.isConsistent(
              c, LOGOUT, f.saved(LOGOUT, "0102", InboxResultReference.none())));
      byte[] invalidFiller = f.wire(LOGOUT, "0102");
      Arrays.fill(invalidFiller, 256, 273, (byte) ' ');
      assertFalse(
          f.inspector.isConsistent(
              c,
              LOGOUT,
              f.savedBytes(
                  LOGOUT, invalidFiller, InboxCompletionState.ERROR, InboxResultReference.none())));
      assertFalse(
          f.inspector.isConsistent(
              c, LOGOUT, f.saved(LOGOUT, "0102", InboxResultReference.authSession(SESSION))));
      assertFalse(
          f.inspector.isConsistent(
              c, LOGOUT, f.saved(LOGOUT, FIXTURE_0101_F2D4F761, InboxResultReference.none())));
      assertFalse(
          f.inspector.isConsistent(c, LOGIN, f.saved(LOGIN, "9000", InboxResultReference.none())));
      try (var s = c.createStatement();
          var rows = s.executeQuery("select count(*) from schubert.auth_sessions")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getInt(1));
      }
      c.rollback();
    }
  }

  @Test
  void missingAndInconsistentLoginRows() throws Exception {
    try (var f = new Fixture();
        var c = db.transaction()) {
      f.seed(c, false);
      var saved = f.saved(LOGIN, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      for (String change :
          List.of(
              "user_id=8",
              "created_message_id='00000000-0000-0000-0000-000000000999'",
              "context_hash=repeat('0',64)",
              "key_version='unknown'",
              "context_ciphertext=decode(repeat('00',100),'hex')",
              "issued_at=issued_at-interval '1 millisecond'")) {
        var point = c.setSavepoint();
        try (var s = c.createStatement()) {
          s.execute("update schubert.auth_sessions set " + change);
        }
        assertFalse(f.inspector.isConsistent(c, LOGIN, saved));
        c.rollback(point);
        c.releaseSavepoint(point);
      }
      assertTrue(f.inspector.isConsistent(c, LOGIN, saved));
      try (var s = c.createStatement()) {
        s.execute("delete from schubert.auth_sessions");
      }
      assertFalse(f.inspector.isConsistent(c, LOGIN, saved));
      c.rollback();
    }
  }

  @Test
  void identityStructureAndNullContracts() throws Exception {
    try (var f = new Fixture();
        var c = db.transaction()) {
      var saved = f.saved(LOGIN, FIXTURE_0101_F2D4F761, InboxResultReference.none());
      assertFalse(
          f.inspector.isConsistent(
              c,
              ResponseSnapshotIdentity.authenticated(REQUEST, "GAMRSP01", FIXTURE_001_A3FEAA64, 7),
              saved));
      assertFalse(
          f.inspector.isConsistent(
              c,
              ResponseSnapshotIdentity.authenticated(REQUEST, "LGNRSP01", FIXTURE_001_A3FEAA64, 7),
              saved));
      assertFalse(
          f.inspector.isConsistent(
              c,
              ResponseSnapshotIdentity.anonymous(REQUEST, "LOGRSP01", FIXTURE_001_A3FEAA64),
              saved));
      assertFalse(f.inspector.isConsistent(c, LOGOUT, saved));
      byte[] broken = f.wire(LOGIN, FIXTURE_0101_F2D4F761);
      broken[0] = 'X';
      assertFalse(
          f.inspector.isConsistent(
              c,
              LOGIN,
              f.savedBytes(
                  LOGIN, broken, InboxCompletionState.ERROR, InboxResultReference.none())));
      assertFalse(
          f.inspector.isConsistent(
              c,
              LOGIN,
              f.savedBytes(
                  LOGIN,
                  f.wire(LOGIN, FIXTURE_0101_F2D4F761),
                  InboxCompletionState.COMPLETED,
                  InboxResultReference.none())));
      assertThrows(
          NullPointerException.class,
          () -> new AuthenticationInboxInspector(null, f.contexts, new ContextHash()));
      assertThrows(
          NullPointerException.class,
          () -> new AuthenticationInboxInspector(f.snapshots, null, new ContextHash()));
      assertThrows(
          NullPointerException.class,
          () -> new AuthenticationInboxInspector(f.snapshots, f.contexts, null));
      assertThrows(NullPointerException.class, () -> f.inspector.isConsistent(null, LOGIN, saved));
      assertThrows(NullPointerException.class, () -> f.inspector.isConsistent(c, null, saved));
      assertThrows(NullPointerException.class, () -> f.inspector.isConsistent(c, LOGIN, null));
      c.rollback();
    }
  }

  @Test
  void databaseFaultsAndTransactionOwnership() throws Exception {
    try (var f = new Fixture();
        var c = db.transaction()) {
      f.seed(c, false);
      var saved = f.saved(LOGIN, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      for (String method : List.of("getAutoCommit", "prepareStatement")) {
        assertFalse(f.inspector.isConsistent(proxy(c, method, () -> {}), LOGIN, saved));
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
      }
      assertTrue(f.inspector.isConsistent(proxy(c, "", () -> {}), LOGIN, saved));
      assertEquals(
          "2026-09-09T00:00:00.123Z|2026-09-09T00:00:00.123Z|2026-09-09T08:00:00.123Z|false|0",
          state(c));
      c.rollback();
      var auto = db.api();
      try (auto) {
        assertFalse(f.inspector.isConsistent(auto, LOGIN, saved));
      }
      assertFalse(f.inspector.isConsistent(auto, LOGIN, saved));
    }
  }

  @Test
  void keyRotationAndClosedLifetimes() throws Exception {
    try (var f = new Fixture();
        var c = db.transaction()) {
      f.seed(c, true);
      var login = f.saved(LOGIN, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      var logout =
          f.saved(LOGOUT, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      byte[] newKey = random(32);
      try (var s = new ResponseSnapshotCodec("s2", newKey, "s1", f.key);
          var a = new AuthContextCodec("a2", newKey, "a1", f.contextKey)) {
        var rotated = new AuthenticationInboxInspector(s, a, new ContextHash());
        assertTrue(rotated.isConsistent(c, LOGIN, login));
        assertTrue(rotated.isConsistent(c, LOGOUT, logout));
      }
      try (var wrong = new AuthContextCodec("a1", newKey, null, null)) {
        assertFalse(
            new AuthenticationInboxInspector(f.snapshots, wrong, new ContextHash())
                .isConsistent(c, LOGIN, login));
      }
      f.contexts.close();
      assertFalse(f.inspector.isConsistent(c, LOGIN, login));
      assertFalse(
          f.inspector.isConsistent(proxy(c, "afterStructure", f.snapshots::close), LOGOUT, logout));
      assertFalse(f.inspector.isConsistent(c, LOGOUT, logout));
      Arrays.fill(newKey, (byte) 0);
      c.rollback();
    }
  }

  @Test
  void concurrentReferencesDoNotCross() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      try (var c = db.transaction()) {
        f.seed(c, true);
        c.commit();
      }
      var saved = f.saved(LOGIN, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      var logout =
          f.saved(LOGOUT, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(SESSION));
      var wrong =
          f.saved(LOGIN, FIXTURE_0000_876EEFE0, InboxResultReference.authSession(new UUID(0, 999)));
      byte[] before = saved.responseSnapshot().orElseThrow().ciphertext();
      var jobs = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              try (var c = db.transaction()) {
                assertTrue(f.inspector.isConsistent(c, LOGIN, saved));
                assertTrue(f.inspector.isConsistent(c, LOGOUT, logout));
                assertFalse(f.inspector.isConsistent(c, LOGIN, wrong));
                c.rollback();
                return true;
              }
            });
      for (var result : pool.invokeAll(jobs)) assertTrue(result.get());
      assertArrayEquals(before, saved.responseSnapshot().orElseThrow().ciphertext());
      try (var c = db.api()) {
        assertEquals(
            "2026-09-09T00:00:00.123Z|2026-09-09T00:00:00.123Z|2026-09-09T08:00:00.123Z|true|0",
            state(c));
      }
    }
  }

  private static String state(Connection c) throws SQLException {
    try (var s = c.createStatement();
        var r =
            s.executeQuery(
                "select issued_at,last_accessed_at,expires_at,revoked,(select count(*) from schubert.app_logs) from schubert.auth_sessions")) {
      assertTrue(r.next());
      String result =
          r.getObject(1, java.time.OffsetDateTime.class).toInstant()
              + "|"
              + r.getObject(2, java.time.OffsetDateTime.class).toInstant()
              + "|"
              + r.getObject(3, java.time.OffsetDateTime.class).toInstant()
              + "|"
              + r.getBoolean(4)
              + "|"
              + r.getLong(5);
      assertFalse(r.next());
      return result;
    }
  }

  private static Connection proxy(Connection c, String fault, Runnable afterStructure) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (object, method, args) -> {
              if (List.of("commit", "rollback", "close").contains(method.getName()))
                throw new AssertionError("inspector changed transaction ownership");
              if (method.getName().equals(fault))
                throw new SQLException("synthetic private provider text");
              if (fault.equals("afterStructure") && method.getName().equals("getAutoCommit"))
                afterStructure.run();
              try {
                return method.invoke(c, args);
              } catch (InvocationTargetException failure) {
                throw failure.getCause();
              }
            });
  }

  private static byte[] random(int size) {
    byte[] bytes = new byte[size];
    new SecureRandom().nextBytes(bytes);
    return bytes;
  }

  private static byte[] ascii(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  private static byte[] uuid(UUID id) {
    return ByteBuffer.allocate(16)
        .putLong(id.getMostSignificantBits())
        .putLong(id.getLeastSignificantBits())
        .array();
  }

  private static void put(byte[] bytes, int offset, String text) {
    byte[] value = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(value, 0, bytes, offset, value.length);
  }

  private static byte[] lp(List<byte[]> fields) throws Exception {
    var bytes = new ByteArrayOutputStream();
    try (var out = new DataOutputStream(bytes)) {
      for (byte[] field : fields) {
        out.writeInt(field.length);
        out.write(field);
      }
    }
    return bytes.toByteArray();
  }

  private static byte[] envelope(byte[] key, String version, byte[] aad, byte[] plain)
      throws Exception {
    byte[] nonce = random(12);
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad);
    byte[] encrypted = cipher.doFinal(plain);
    return ByteBuffer.allocate(20 + version.length() + encrypted.length)
        .put(ascii("NKENC1"))
        .put((byte) 1)
        .put((byte) version.length())
        .put(ascii(version))
        .put(nonce)
        .put(encrypted)
        .array();
  }

  // Shared independent wire/JCE input fixture for limited-role SQL PT017..024.
  static final class Fixture implements AutoCloseable {
    final byte[] key = random(32);
    final byte[] contextKey = random(32);
    final String raw = HexFormat.of().formatHex(random(32));
    final ResponseSnapshotCodec snapshots = new ResponseSnapshotCodec("s1", key, null, null);
    final AuthContextCodec contexts = new AuthContextCodec("a1", contextKey, null, null);
    final AuthenticationInboxInspector inspector =
        new AuthenticationInboxInspector(snapshots, contexts, new ContextHash());

    Fixture() throws java.security.NoSuchAlgorithmException {}

    void seed(Connection c, boolean revoked) throws Exception {
      byte[] aad =
          lp(
              List.of(
                  ascii("SCHUBERT-NK-AUTHCTX-v1"),
                  ascii("schubert.auth_sessions"),
                  ascii(SESSION.toString()),
                  ascii("7"),
                  ascii("1"),
                  ascii("a1")));
      byte[] cipher = envelope(contextKey, "a1", aad, ascii(raw));
      try (var s =
          c.prepareStatement(
              "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,revoked,revoked_at,revoke_reason,client_address,created_message_id) values (?,7,?,?,'a1','2026-09-09T00:00:00.123Z','2026-09-09T00:00:00.123Z','2026-09-09T08:00:00.123Z',?,?,?,'127.0.0.1',?)")) {
        s.setObject(1, SESSION);
        s.setString(
            2, HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(ascii(raw))));
        s.setBytes(3, cipher);
        s.setBoolean(4, revoked);
        s.setObject(5, revoked ? TIME.atOffset(java.time.ZoneOffset.UTC) : null);
        s.setString(6, revoked ? "LOGOUT" : null);
        s.setObject(7, REQUEST);
        assertEquals(1, s.executeUpdate());
      } finally {
        Arrays.fill(cipher, (byte) 0);
      }
    }

    byte[] wire(ResponseSnapshotIdentity id, String code) {
      boolean login = id.responseLayoutId().equals("LGNRSP01");
      boolean success = code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200");
      byte[] bytes = new byte[login ? 688 : 280];
      Arrays.fill(bytes, (byte) ' ');
      put(bytes, 0, "SCHBNK01001" + id.responseLayoutId() + "001SS");
      put(bytes, 24, new UUID(0, 102).toString());
      put(bytes, 60, REQUEST.toString());
      put(bytes, 96, "20260909090000123");
      if (!login) put(bytes, 113, raw);
      put(
          bytes,
          177,
          login ? "0256000432000000000000000000688" : "0256000024000000000000000000280");
      put(bytes, 208, code);
      if (login) {
        put(bytes, 423, code.equals("0106") ? "000900000" : "000000000");
        if (success) {
          put(bytes, 256, "Learner");
          put(bytes, 320, "USER");
          put(bytes, 325, raw);
          put(bytes, 389, "20260909090000123");
          put(bytes, 406, "20260909170000123");
        } else put(bytes, 432, "Synthetic error");
      } else put(bytes, 256, success ? "20260909090000123" : "00000000000000000");
      return bytes;
    }

    InboxCompletion saved(ResponseSnapshotIdentity id, String code, InboxResultReference ref)
        throws Exception {
      return savedBytes(
          id,
          wire(id, code),
          code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200")
              ? InboxCompletionState.COMPLETED
              : InboxCompletionState.ERROR,
          ref);
    }

    InboxCompletion savedBytes(
        ResponseSnapshotIdentity id,
        byte[] wire,
        InboxCompletionState state,
        InboxResultReference ref)
        throws Exception {
      var compressed = new ByteArrayOutputStream();
      var deflater = new Deflater(3);
      try (var zip = new DeflaterOutputStream(compressed, deflater)) {
        zip.write(wire);
      } finally {
        deflater.end();
        Arrays.fill(wire, (byte) 0);
      }
      byte[] aad =
          lp(
              List.of(
                  ascii("api-inbox-response"),
                  ascii("schubert.request_inbox"),
                  uuid(id.requestMessageId()),
                  new byte[] {1},
                  ascii("s1"),
                  ascii(id.responseLayoutId()),
                  ascii(id.responseVersion()),
                  id.ownerUserId().isPresent()
                      ? ByteBuffer.allocate(8).putLong(id.ownerUserId().getAsLong()).array()
                      : new byte[0]));
      byte[] encrypted = envelope(key, "s1", aad, compressed.toByteArray());
      return new InboxCompletion(
          state,
          ref,
          id.responseLayoutId(),
          id.responseVersion(),
          Optional.of(new EncryptedResponseSnapshot("s1", encrypted)),
          TIME);
    }

    @Override
    public void close() {
      snapshots.close();
      contexts.close();
      Arrays.fill(key, (byte) 0);
      Arrays.fill(contextKey, (byte) 0);
    }
  }
}
