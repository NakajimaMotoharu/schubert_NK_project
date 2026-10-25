package dev.codex.schubert.nk.api.application.media;

import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.SHA;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.codec;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.key;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.maximum;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.wire;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.data;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.message;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.put;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.MediaFileInspector;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.persistence.MediaRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;

/** Real PG roles/transactions, independent SQL postconditions and UI232/235 expected bytes. */
final class MediaStageFixture implements AutoCloseable {
  static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  final ApiLogDatabaseFixture database;
  final AtomicInteger live = new AtomicInteger();
  final AtomicInteger opens = new AtomicInteger();
  final AtomicInteger inspections = new AtomicInteger();
  final AtomicLong ids = new AtomicLong();
  final AtomicInteger clockCalls = new AtomicInteger();
  final AtomicReference<Instant> now = new AtomicReference<>(NOW);
  final List<Boolean> modes = new CopyOnWriteArrayList<>();
  int faultConnection = 1;
  int clockFaultAt;
  int identifierFaultAt;
  String fault = "none";
  boolean nullClock;
  boolean nullIdentifier;
  Action beforeOpen = () -> {};
  Action duringFile = () -> {};
  MediaFileInspector physical = descriptor -> {};
  final FingerprintKeyRing keys = new FingerprintKeyRing("fp1", key(), null, null);
  final ResponseSnapshotCodec snapshots = codec();
  final AuthenticationContextVerifier verifier =
      new AuthenticationContextVerifier(new ContextHash());
  final JdbcInboxCoordinator inbox = new JdbcInboxCoordinator(keys);
  final MediaReplayService responses = new MediaReplayService(snapshots);
  final Clock clock =
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
          if (clockCalls.incrementAndGet() == clockFaultAt) {
            if (nullClock) return null;
            throw new IllegalStateException("synthetic clock fault");
          }
          return now.get();
        }
      };
  final DataSource source;
  final MediaFileInspector inspector;
  final MediaApplicationService service;

  MediaStageFixture(ApiLogDatabaseFixture database) throws java.security.NoSuchAlgorithmException {
    this.database = database;
    source =
        (DataSource)
            Proxy.newProxyInstance(
                DataSource.class.getClassLoader(),
                new Class<?>[] {DataSource.class},
                (p, m, a) -> {
                  if (!m.getName().equals("getConnection"))
                    throw new AssertionError("unexpected datasource method");
                  int stage = opens.incrementAndGet();
                  beforeOpen.run();
                  boolean affected = stage == faultConnection;
                  if (affected && fault.equals("open"))
                    throw new SQLException("synthetic open fault");
                  if (affected && fault.equals("nullConnection")) return null;
                  Connection connection = database.api();
                  live.incrementAndGet();
                  return Proxy.newProxyInstance(
                      Connection.class.getClassLoader(),
                      new Class<?>[] {Connection.class},
                      (proxy, method, args) -> {
                        String name = method.getName();
                        if (name.equals("setReadOnly")) modes.add((Boolean) args[0]);
                        if (name.equals("close")) {
                          try {
                            Object result = invoke(connection, method, args);
                            if (affected && fault.contains("close"))
                              throw new SQLException("synthetic close fault");
                            return result;
                          } finally {
                            live.decrementAndGet();
                          }
                        }
                        if (affected
                            && (name.equals(fault)
                                || (name.equals("prepareStatement")
                                    && fault.equals("query")
                                    && ((String) args[0]).contains("schubert.media_assets"))
                                || (name.equals("prepareStatement") && fault.startsWith("rollback"))
                                || (name.equals("rollback")
                                    && (fault.startsWith("rollback")
                                        || fault.equals("authRollback")))))
                          throw new SQLException("synthetic JDBC fault");
                        Object result = invoke(connection, method, args);
                        if (affected && name.equals("commit") && fault.equals("afterCommit"))
                          throw new SQLException("synthetic uncertain commit");
                        return result;
                      });
                });
    inspector =
        descriptor -> {
          assertEquals(0, live.get(), "no connection during physical work");
          unlocked();
          inspections.incrementAndGet();
          try {
            duringFile.run();
          } catch (SQLException failure) {
            throw new IOException("synthetic file stage SQL fault");
          }
          physical.verify(descriptor);
        };
    service =
        new MediaApplicationService(
            source,
            verifier,
            new MediaRepository(),
            inbox,
            responses,
            inspector,
            clock,
            () -> {
              long id = ids.incrementAndGet();
              if (id == identifierFaultAt) {
                if (nullIdentifier) return null;
                throw new IllegalStateException("synthetic identifier fault");
              }
              return new UUID(0, id);
            });
  }

  @Override
  public void close() {
    snapshots.close();
    keys.close();
    assertEquals(0, live.get());
  }

  @FunctionalInterface
  interface Action {
    void run() throws SQLException, IOException;
  }

  static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  static WireMessage<FixedPayload> input(String prefix) {
    return message(prefix + "REQ01", data(prefix + "REQ01"));
  }

  void sql(String value) throws SQLException {
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute(value);
    }
  }

  void seed() throws Exception {
    sql("truncate schubert.games,schubert.media_assets cascade");
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.auth_sessions");
    sql("delete from schubert.app_users");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) select id,'owner'||id,'key'||id,'unusable-fixture-hash','USER','ACTIVE','2026-09-08Z','2026-09-08Z','2026-09-08Z' from (values(101),(102)) t(id)");
    session("b", 1, 101);
    sql("insert into schubert.games values(1,'NUKITASHI1','One',1,'2026-09-08Z')");
    sql(
        "insert into schubert.audio_files(id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,byte_size,sha256,created_at) values(700,1,'scenario/合成.ogg','表示/a.ogg','表示.ogg','700','voice',3,'"
            + SHA
            + "','2026-09-08Z')");
    asset(
        1,
        "video-0",
        "VIDEO",
        "動画0",
        "MAIN",
        "",
        "video/main.mp4",
        "表示/a.mp4",
        "表示.mp4",
        "video/mp4");
    asset(
        2,
        "opening",
        "VIDEO",
        "動画",
        "OPENING",
        "",
        "video/合成.mp4",
        "表示/動画.mp4",
        "表示.mp4",
        "video/mp4");
    asset(
        3,
        "music-0",
        "MUSIC",
        "曲0",
        "BGM",
        "ゲーム",
        "music/合成.ogg",
        "表示/a.ogg",
        "表示.ogg",
        "audio/ogg");
  }

  void asset(
      int id,
      String logical,
      String type,
      String title,
      String category,
      String section,
      String path,
      String display,
      String name,
      String mime)
      throws SQLException {
    try (var c = database.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.media_assets(id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,pair_role,display_order,created_at) values(?,?,?,?,?,?,?,?,?,3,?,?,?,1,'2026-09-08Z')")) {
      s.setInt(1, id);
      s.setString(2, logical);
      s.setString(3, type);
      s.setString(4, title);
      s.setString(5, category);
      s.setString(6, section.isEmpty() ? null : section);
      s.setString(7, path);
      s.setString(8, display);
      s.setString(9, name);
      s.setString(10, SHA);
      s.setString(11, mime);
      s.setString(12, type.equals("MUSIC") ? "N" : null);
      assertEquals(1, s.executeUpdate());
    }
  }

  void session(String raw, int id, int owner) throws Exception {
    String hash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(raw.repeat(64).getBytes(StandardCharsets.US_ASCII)));
    sql(
        "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) values('"
            + new UUID(0, id)
            + "',"
            + owner
            + ",'"
            + hash
            + "',decode(repeat('00',29),'hex'),'fixture','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T08:00:00Z','127.0.0.1','"
            + new UUID(1, id)
            + "')");
  }

  void exceed(String prefix) throws SQLException {
    sql("truncate schubert.media_assets cascade");
    int count = prefix.equals("ANM") ? 1000 : maximum(prefix) + 1;
    boolean video = prefix.equals("ANM") || prefix.equals("ANL");
    String category = video ? "'MAIN'" : prefix.equals("MCT") ? "'分類'||i" : "'BGM'";
    String section = video ? "NULL" : prefix.equals("MCS") ? "'区分'||i" : "'ゲーム'";
    String pathRoot = video ? "video/" : "music/";
    String suffix = video ? ".mp4" : ".ogg";
    sql(
        "insert into schubert.media_assets(id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,pair_role,display_order,created_at) select i,'id-'||i,'"
            + (video ? "VIDEO" : "MUSIC")
            + "','title',"
            + category
            + ","
            + section
            + ",'"
            + pathRoot
            + "'||i||'"
            + suffix
            + "','表示/'||i||'"
            + suffix
            + "','file"
            + suffix
            + "',3,'"
            + SHA
            + "','"
            + (video ? "video/mp4" : "audio/ogg")
            + "',"
            + (video ? "NULL" : "'N'")
            + ",i,'2026-09-08Z' from generate_series(1,"
            + count
            + ") t(i)");
  }

  void unlocked() throws IOException {
    try (var c = database.transaction();
        var s = c.createStatement()) {
      s.executeQuery("select id from schubert.app_users for update nowait").close();
      s.executeQuery("select id from schubert.auth_sessions for update nowait").close();
      s.executeQuery("select message_id from schubert.request_inbox for update nowait").close();
      c.rollback();
    } catch (SQLException failure) {
      throw new IOException("DB locked during file stage");
    }
  }

  List<String> stored(WireMessage<FixedPayload> request) throws SQLException {
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "select processing_state,result_ref_type,created_at,completed_at,expires_at,encode(response_body_encrypted,'hex'),response_key_version from schubert.request_inbox where message_id=?")) {
      s.setObject(1, request.header().messageId());
      try (var row = s.executeQuery()) {
        List<String> result = new ArrayList<>();
        if (row.next())
          for (int i = 1; i <= 7; i++)
            result.add(
                i >= 3 && i <= 5
                    ? row.getObject(i, java.time.OffsetDateTime.class).toInstant().toString()
                    : row.getString(i));
        assertFalse(row.next());
        return result;
      }
    }
  }

  int inboxCount() throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var row = s.executeQuery("select count(*) from schubert.request_inbox")) {
      assertTrue(row.next());
      return row.getInt(1);
    }
  }

  byte[] golden(WireMessage<FixedPayload> request, String code, long responseId) {
    String prefix = request.header().layoutId().value().substring(0, 3);
    int count = maximum(prefix) > 0 ? 1 : 0;
    byte[] expected =
        wire(
            prefix,
            MediaRequest.decode(request),
            new UUID(0, responseId),
            now.get().equals(NOW.plusSeconds(20)) ? "20260908090120000" : "20260908090100000",
            request.header().authenticationContext().orElseThrow().wireValue(),
            code,
            count,
            prefix.equals("VID") ? "mp4" : "ogg",
            prefix.equals("VID") ? "I" : "A");
    if (!code.equals("0000") && !code.equals("0200")) return expected;
    switch (prefix) {
      case "ANM" -> put(expected, 256, "0010001002");
      case "ANL" -> put(expected, 264 + 924, "0001");
      case "MCT" -> {
        Arrays.fill(expected, 264, 328, (byte) 32);
        put(expected, 264, "BGM");
      }
      case "MCS" -> {
        Arrays.fill(expected, 264, 392, (byte) 32);
        put(expected, 264, "ゲーム");
      }
      case "MTR" -> {
        Arrays.fill(expected, 272, 336, (byte) 32);
        put(expected, 272, "music-0");
        put(expected, 272 + 1293, "0001");
      }
      default -> {}
    }
    return expected;
  }
}
