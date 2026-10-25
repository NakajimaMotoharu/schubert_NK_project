package dev.codex.schubert.nk.api.application.log;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;

/** Actual isolated PostgreSQL plus public JDBC boundary fault injection. PT-ADM-067..073. */
final class LogApplicationFixture implements AutoCloseable {
  final ApiLogDatabaseFixture db;
  final FingerprintKeyRing fingerprints = new FingerprintKeyRing("test", new byte[32], null, null);
  final ResponseSnapshotCodec snapshots =
      new ResponseSnapshotCodec("test", new byte[32], null, null);
  final AtomicInteger ids = new AtomicInteger();
  final AtomicInteger live = new AtomicInteger();
  final AtomicInteger commits = new AtomicInteger();
  final AtomicInteger rollbacks = new AtomicInteger();
  final JdbcInboxCoordinator inbox = new JdbcInboxCoordinator(fingerprints);
  final DataSource source;
  String connectionFault = "none";
  boolean rollbackFails;
  LogJdbcFaults sqlFault;
  Runnable afterCommit = () -> {};

  LogApplicationFixture(ApiLogDatabaseFixture db) throws Exception {
    this.db = db;
    source =
        (DataSource)
            Proxy.newProxyInstance(
                DataSource.class.getClassLoader(),
                new Class<?>[] {DataSource.class},
                (p, m, a) -> {
                  if (!m.getName().equals("getConnection"))
                    throw new AssertionError("unexpected DataSource operation");
                  if (connectionFault.equals("open"))
                    throw new SQLException("synthetic-private-provider");
                  if (connectionFault.equals("null")) return null;
                  Connection actual = db.api();
                  live.incrementAndGet();
                  Connection delegate = sqlFault == null ? actual : sqlFault.wrap(actual);
                  return Proxy.newProxyInstance(
                      Connection.class.getClassLoader(),
                      new Class<?>[] {Connection.class},
                      (cp, cm, ca) -> {
                        String name = cm.getName();
                        if (name.equals("rollback")) {
                          rollbacks.incrementAndGet();
                          if (rollbackFails) throw new SQLException("synthetic-private-rollback");
                        }
                        if (name.equals(connectionFault) && !name.equals("close"))
                          throw new SQLException("synthetic-private-provider");
                        Object result = invoke(delegate, cm, ca);
                        if (name.equals("commit")) {
                          commits.incrementAndGet();
                          afterCommit.run();
                        }
                        if (name.equals("close")) {
                          live.decrementAndGet();
                          if (connectionFault.equals("close"))
                            throw new SQLException("synthetic-private-close");
                        }
                        return result;
                      });
                });
  }

  void seed() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_users restart identity cascade");
    }
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) select i,'u'||i,'u'||i,'unusable-synthetic-hash',case when i<3 then 'ADMIN' else 'USER' end,'ACTIVE','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z' from (values(1),(2),(3))n(i)");
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("select setval('schubert.app_users_id_seq',3,true)");
    }
    for (int user : new int[] {1, 2, 3}) session(user, user);
    ids.set(0);
    commits.set(0);
    rollbacks.set(0);
  }

  void session(long user, int contextNumber) throws Exception {
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) values(?,?,?,decode(repeat('00',29),'hex'),'test','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T08:00:00Z','127.0.0.1',?)")) {
      s.setObject(1, new UUID(901, contextNumber));
      s.setLong(2, user);
      s.setString(
          3,
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256")
                      .digest(context(contextNumber).getBytes(StandardCharsets.US_ASCII))));
      s.setObject(4, new UUID(902, contextNumber));
      assertEquals(1, s.executeUpdate());
    }
  }

  static String context(int number) {
    return switch (number) {
      case 1 -> "b".repeat(64);
      case 2 -> "c".repeat(64);
      case 3 -> "d".repeat(64);
      default -> String.format(Locale.ROOT, "%064x", number);
    };
  }

  long scalar(String query) throws SQLException {
    try (var c = db.api();
        var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      long result = r.getLong(1);
      assertFalse(r.next());
      return result;
    }
  }

  String text(String query) throws SQLException {
    try (var c = db.api();
        var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String result = r.getString(1);
      assertFalse(r.next());
      return result;
    }
  }

  void sql(String sql) throws SQLException {
    try (var c = db.api();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  long inboxCount() throws SQLException {
    return scalar("select count(*) from schubert.request_inbox");
  }

  List<String> inboxMetadata() throws SQLException {
    try (var c = db.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select message_id,processing_state,result_ref_type,result_ref_id,response_layout_id,response_version,completed_at,expires_at,request_fingerprint_hmac,encode(response_body_encrypted,'hex') from schubert.request_inbox order by message_id")) {
      var result = new ArrayList<String>();
      while (r.next()) for (int i = 1; i <= 10; i++) result.add(r.getString(i));
      return result;
    }
  }

  static Object invoke(Object target, Method method, Object[] arguments) throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  @Override
  public void close() {
    assertEquals(0, live.get());
    fingerprints.close();
    snapshots.close();
  }
}
