package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator;
import dev.codex.schubert.nk.api.security.AuthSessionRevocationService;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.api.security.PasswordHasher;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import javax.sql.DataSource;

/** Actual isolated PostgreSQL plus public JDBC boundary fault injection. PT-ADM-033..039. */
final class UserApplicationFixture implements AutoCloseable {
  static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  static final UUID MESSAGE = new UUID(90, 1);
  static final UUID TOKEN = new UUID(90, 2);
  static final String PASSWORD = "Synthetic-Password-12";
  final ApiLogDatabaseFixture db;
  final FingerprintKeyRing fingerprints = new FingerprintKeyRing("test", new byte[32], null, null);
  final ResponseSnapshotCodec snapshots =
      new ResponseSnapshotCodec("test", new byte[32], null, null);
  final AtomicInteger ids = new AtomicInteger();
  final AtomicInteger live = new AtomicInteger();
  final AtomicInteger commits = new AtomicInteger();
  final AtomicInteger rollbacks = new AtomicInteger();
  final AdminCommandAuthenticator authentication;
  final UserCommandService commands;
  final JdbcInboxCoordinator inbox = new JdbcInboxCoordinator(fingerprints);
  final UserMutationReplayService responses = new UserMutationReplayService(snapshots);
  UserMutationApplicationService service;
  final DataSource source;
  String connectionFault = "none";
  boolean rollbackFails;
  UserCommandFaults sqlFault;
  Runnable afterCommit = () -> {};

  UserApplicationFixture(ApiLogDatabaseFixture db) throws Exception {
    this.db = db;
    authentication = new AdminCommandAuthenticator(new ContextHash());
    commands =
        new UserCommandService(
            new PasswordHasher(), new AuthSessionRevocationService(new ContextHash()));
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
    service = build(Clock.fixed(NOW, ZoneOffset.UTC), () -> new UUID(900, ids.incrementAndGet()));
  }

  UserMutationApplicationService build(Clock clock, Supplier<UUID> identifiers) {
    return new UserMutationApplicationService(
        source, authentication, inbox, commands, responses, clock, identifiers);
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

  static WireMessage<FixedPayload> input(
      String layout, long target, long version, boolean flag, UUID message, UUID token, int owner) {
    return input(layout, target, version, flag, message, token, owner, "New", PASSWORD);
  }

  static WireMessage<FixedPayload> input(
      String layout,
      long target,
      long version,
      boolean flag,
      UUID message,
      UUID token,
      int owner,
      String name,
      String password) {
    byte[] data =
        UserMutationRequestTest.data(layout, target, version, flag, name, password, token);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            message,
            message,
            NOW,
            Optional.of(AuthenticationContext.of(context(owner))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }

  static void reply(
      byte[] actual,
      WireMessage<FixedPayload> request,
      String code,
      long target,
      long version,
      long responseId) {
    byte[] expected =
        UserMutationReplayServiceTest.wire(
            request.header().layoutId().value(),
            request.header().messageId(),
            new UUID(900, responseId),
            NOW,
            request.header().authenticationContext().orElseThrow().wireValue(),
            code,
            target,
            version);
    assertArrayEquals(expected, actual);
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

  long version(long user) throws SQLException {
    return scalar("select version from schubert.app_users where id=" + user);
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
