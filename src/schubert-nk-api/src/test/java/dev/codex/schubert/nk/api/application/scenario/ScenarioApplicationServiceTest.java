package dev.codex.schubert.nk.api.application.scenario;

import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.message;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.put;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.search;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.spaces;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.ScenarioFileInspector;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestListener;
import dev.codex.schubert.nk.api.persistence.ScenarioRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.api.storage.RealScenarioFileFixture;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Message;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * SSC-027/PT-SCN-009-T01..T05. Real PG and independent SQL/wire/AES; publisher stub scope explicit.
 */
final class ScenarioApplicationServiceTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    sql("truncate schubert.app_logs");
    sql("truncate schubert.games cascade");
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.auth_sessions");
    sql("delete from schubert.app_users");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) "
            + "select id,'owner'||id,'key'||id,'unusable-fixture-hash','USER','ACTIVE','2026-09-08Z','2026-09-08Z','2026-09-08Z' from (values(101),(102)) t(id)");
    session("b", 1, 101);
  }

  @Test
  void successAuditIsAtomicAndNotRepeatedForSavedSearchAndDetail() throws Exception {
    master(2);
    try (var h = new Harness()) {
      for (String prefix : List.of("SRC", "SCN")) {
        var message = request(prefix);
        assertEquals(
            "0000", new String(h.service.process(message), 208, 4, StandardCharsets.US_ASCII));
        assertScenarioAudit(
            message, prefix.equals("SRC") ? "SCENARIO_SEARCHED" : "SCENARIO_VIEWED", 2);
        assertEquals(
            "0200", new String(h.service.process(message), 208, 4, StandardCharsets.US_ASCII));
        assertScenarioAudit(
            message, prefix.equals("SRC") ? "SCENARIO_SEARCHED" : "SCENARIO_VIEWED", 2);
      }
      assertEquals(2, count("schubert.app_logs"));
      assertEquals(2, count("schubert.request_inbox"));
    }
  }

  @Test
  void criticalAuditFailureRollsBackInboxAndCanBeRetried() throws Exception {
    master(2);
    sql(
        "create function schubert.fail_scenario_audit() returns trigger language plpgsql as $$ begin raise exception 'synthetic audit failure'; end $$");
    sql(
        "create trigger fail_scenario_audit before insert on schubert.app_logs for each row execute function schubert.fail_scenario_audit()");
    try (var h = new Harness()) {
      var message = request("SRC");
      try {
        assertThrows(TemporaryInfrastructureException.class, () -> h.service.process(message));
        assertEquals(0, count("schubert.request_inbox"));
        assertEquals(0, count("schubert.app_logs"));
        assertEquals(0, h.live.get());
      } finally {
        sql("drop trigger fail_scenario_audit on schubert.app_logs");
        sql("drop function schubert.fail_scenario_audit()");
      }
      assertEquals(
          "0000", new String(h.service.process(message), 208, 4, StandardCharsets.US_ASCII));
      assertScenarioAudit(message, "SCENARIO_SEARCHED", 2);
    }
  }

  @Test
  void concurrentSameMessageAuditsOnceAndDistinctMessagesAuditIndividually() throws Exception {
    master(2);
    try (var h = new Harness();
        var workers = Executors.newFixedThreadPool(12)) {
      var message = request("SRC");
      var start = new CountDownLatch(1);
      List<Future<String>> replies = new ArrayList<>();
      for (int n = 0; n < 24; n++)
        replies.add(
            workers.submit(
                () -> {
                  assertTrue(start.await(10, TimeUnit.SECONDS));
                  return ascii(h.service.process(message), 208, 4);
                }));
      start.countDown();
      List<String> codes = new ArrayList<>();
      for (var reply : replies) codes.add(reply.get(20, TimeUnit.SECONDS));
      assertEquals(1, Collections.frequency(codes, "0000"));
      assertEquals(23, Collections.frequency(codes, "0200"));
      assertScenarioAudit(message, "SCENARIO_SEARCHED", 2);
      var first = workers.submit(() -> ascii(h.service.process(request("SRC")), 208, 4));
      var second = workers.submit(() -> ascii(h.service.process(request("SRC")), 208, 4));
      assertEquals("0000", first.get(10, TimeUnit.SECONDS));
      assertEquals("0000", second.get(10, TimeUnit.SECONDS));
      assertEquals(3, count("schubert.app_logs"));
      assertEquals(3, count("schubert.request_inbox"));
    }
  }

  @Test
  void committedAuditRemainsExactlyOnceAfterUnknownResponse() throws Exception {
    for (String fault : List.of("afterCommit", "close")) {
      seed();
      master(2);
      try (var h = new Harness()) {
        var message = request("SRC");
        h.faultConnection = 2;
        h.fault = fault;
        assertThrows(TemporaryInfrastructureException.class, () -> h.service.process(message));
        assertScenarioAudit(message, "SCENARIO_SEARCHED", 2);
        assertEquals(1, count("schubert.request_inbox"));
        h.fault = "none";
        assertEquals("0200", ascii(h.service.process(message), 208, 4));
        assertScenarioAudit(message, "SCENARIO_SEARCHED", 2);
        assertEquals(0, h.live.get());
      }
    }
    seed();
    try (var h = new Harness()) {
      h.identifierFaultAt = 1;
      assertThrows(TemporaryInfrastructureException.class, () -> h.service.process(request("SRC")));
      assertEquals(0, count("schubert.app_logs"));
      assertEquals(0, count("schubert.request_inbox"));
    }
  }

  private static void assertScenarioAudit(
      WireMessage<FixedPayload> message, String action, int resultCount) throws Exception {
    try (var c = database.admin();
        var s =
            c.prepareStatement(
                "select service,category,level,action,message,actor_user_id,actor_username,correlation_id,logged_at,details::text from schubert.app_logs where message_id=?")) {
      s.setObject(1, message.header().messageId());
      try (var rows = s.executeQuery()) {
        assertTrue(rows.next(), "successful business action must have a committed critical audit");
        assertEquals("API", rows.getString(1));
        assertEquals("ACTION", rows.getString(2));
        assertEquals("INFO", rows.getString(3));
        assertEquals(action, rows.getString(4));
        assertEquals(action, rows.getString(5));
        assertEquals(101, rows.getLong(6));
        assertEquals("owner101", rows.getString(7));
        assertEquals(message.header().correlationId(), rows.getObject(8));
        assertEquals(NOW, rows.getObject(9, OffsetDateTime.class).toInstant());
        var details = com.google.gson.JsonParser.parseString(rows.getString(10)).getAsJsonObject();
        assertEquals(Set.of("layout", "resultCount"), details.keySet());
        assertEquals(message.header().layoutId().value(), details.get("layout").getAsString());
        assertEquals(resultCount, details.get("resultCount").getAsInt());
        assertFalse(rows.next(), "saved replay must not duplicate the business audit");
      }
    }
  }

  @Test
  void sixRequestsCommitFrozenResponsesAndReplayWithFreshHeaders() throws Exception {
    try (var h = new Harness()) {
      for (String prefix : ScenarioReplayFixture.LAYOUTS) {
        var request = request(prefix);
        String code = prefix.equals("SCN") ? "0104" : "0000";
        byte[] expected = golden(prefix, request, h, code, false, 0, 2);
        assertArrayEquals(expected, h.service.process(request));
        assertEquals(0, h.live.get());
        var before = stored(request);
        byte[] frozen =
            ScenarioReplayFixture.decrypt(ScenarioRequest.decode(request), cipher(request));
        assertArrayEquals(golden(prefix, request, h, code, false, 0, 1), frozen);
        assertArrayEquals(
            golden(prefix, request, h, prefix.equals("SCN") ? "0104" : "0200", false, 0, 3),
            h.service.process(request));
        assertEquals(before, stored(request));
        assertEquals(0, h.published.get());
        assertEquals(0, h.live.get());
        h.ids.set(0);
      }
      assertEquals(6, count("schubert.request_inbox"));
      assertEquals(1, count("schubert.app_logs")); // Only SRC succeeded; SCN0104 is not a view.
      try (var c = database.api();
          var s = c.createStatement();
          var r =
              s.executeQuery(
                  "select count(*) from schubert.request_inbox where created_at='2026-09-08T00:01:00Z' and completed_at=created_at and expires_at='2026-09-09T00:01:00Z'")) {
        assertTrue(r.next());
        assertEquals(6, r.getInt(1));
      }
    }
  }

  @Test
  void productionAssemblyUsesRealQueryInboxAndNullContract() throws Exception {
    try (var h = new Harness()) {
      var service =
          ScenarioApplicationAssembly.create(
              h.source, h.keys, h.snapshots, h.publisher, h.inspector, h.clock);
      var message = request("GAM");
      byte[] first = service.process(message);
      assertEquals("0000", new String(first, 208, 4, StandardCharsets.US_ASCII));
      assertEquals(1, count("schubert.request_inbox"));
      byte[] replay = service.process(message);
      assertEquals("0200", new String(replay, 208, 4, StandardCharsets.US_ASCII));
      assertEquals(1, count("schubert.request_inbox"));
      assertEquals(0, h.published.get());
      assertThrows(
          NullPointerException.class,
          () ->
              ScenarioApplicationAssembly.create(
                  null, h.keys, h.snapshots, h.publisher, h.inspector, h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              ScenarioApplicationAssembly.create(
                  h.source, null, h.snapshots, h.publisher, h.inspector, h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              ScenarioApplicationAssembly.create(
                  h.source, h.keys, null, h.publisher, h.inspector, h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              ScenarioApplicationAssembly.create(
                  h.source, h.keys, h.snapshots, null, h.inspector, h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              ScenarioApplicationAssembly.create(
                  h.source, h.keys, h.snapshots, h.publisher, null, h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              ScenarioApplicationAssembly.create(
                  h.source, h.keys, h.snapshots, h.publisher, h.inspector, null));
    }
  }

  @Test
  void detailBoundariesReleaseDatabaseBeforeFilesAndPreserveOriginalContent() throws Exception {
    master(501);
    sql(
        "insert into schubert.speakers(id,game_id,name,normalized_name,created_at) select n,1,'speaker'||n,'s'||n,'2026-09-08Z' from generate_series(1,501) t(n)");
    sql("update schubert.script_entries set speaker_id=id,entry_type='dialogue'");
    try (var h = new Harness()) {
      var request = request("SPK");
      assertArrayEquals(golden("SPK", request, h, "9001", false, 0, 2), h.service.process(request));
      assertEquals("ERROR", stored(request).get(0));
      assertEquals(0, h.published.get());
    }
    for (int count : new int[] {0, 200, 201, 10000, 10001}) {
      seed();
      master(count);
      try (var h = new Harness()) {
        var request = request("SCN");
        byte[] actual =
            assertDoesNotThrow(() -> h.service.process(request), "detail count=" + count);
        boolean file = count > 200 && count <= 10000;
        String code = count > 10000 ? "9001" : "0000";
        assertArrayEquals(golden("SCN", request, h, code, file, count, 2), actual);
        assertEquals(file ? 1 : 0, h.published.get());
        assertEquals(0, h.live.get());
        assertEquals(List.of(true, false), h.modes);
        if (count <= 10000) assertScenarioAudit(request, "SCENARIO_VIEWED", count);
        else assertEquals(0, count("schubert.app_logs"));
        var saved = stored(request);
        sql("update schubert.script_entries set body='changed after first response'");
        assertArrayEquals(
            golden("SCN", request, h, count > 10000 ? "9001" : "0200", file, count, 3),
            h.service.process(request));
        assertEquals(saved, stored(request));
        assertEquals(file ? 1 : 0, h.published.get());
        assertEquals(count <= 10000 ? 1 : 0, count("schubert.app_logs"));
      }
    }
    seed();
    master(201);
    try (var h = new Harness()) {
      h.publishAction =
          () -> {
            throw new CapacityExceededException();
          };
      var request = request("SCN");
      assertArrayEquals(golden("SCN", request, h, "9001", false, 0, 2), h.service.process(request));
      assertEquals("ERROR", stored(request).get(0));
    }
  }

  @Test
  void replayRegeneratesOnlyMissingOriginalFilesAndPreservesLifetime() throws Exception {
    master(201);
    try (var h = new Harness()) {
      var request = request("SCN");
      h.service.process(request);
      var first = stored(request);
      byte[] initial =
          ScenarioReplayFixture.decrypt(ScenarioRequest.decode(request), cipher(request));
      h.missing = true;
      h.now.set(NOW.plusSeconds(20));
      assertArrayEquals(
          golden("SCN", request, h, "0200", true, 201, 3), h.service.process(request));
      assertEquals(2, h.published.get());
      assertScenarioAudit(request, "SCENARIO_VIEWED", 201);
      var replaced = stored(request);
      assertEquals(first.subList(0, 5), replaced.subList(0, 5));
      byte[] after =
          ScenarioReplayFixture.decrypt(ScenarioRequest.decode(request), cipher(request));
      byte[] changed = initial.clone();
      put(changed, 256 + 1329, h.lastFile.fileId().toString());
      Arrays.fill(changed, 256 + 1365, 256 + 1621, (byte) 32);
      put(changed, 256 + 1365, h.lastFile.relativePath());
      assertArrayEquals(changed, after);
      assertNotEquals(first.get(5), replaced.get(5));
      for (String failure :
          List.of("master", "missingMaster", "queryCapacity", "capacity", "io", "invalidFile")) {
        h.publishAction = () -> {};
        h.inspectAction = () -> {};
        if (failure.equals("master")) sql("update schubert.script_entries set body='changed'");
        if (failure.equals("missingMaster")) sql("delete from schubert.script_entries");
        if (failure.equals("queryCapacity")) {
          sql("delete from schubert.script_entries");
          entries(10001);
        }
        if (failure.equals("capacity"))
          h.publishAction =
              () -> {
                throw new CapacityExceededException();
              };
        if (failure.equals("io"))
          h.publishAction =
              () -> {
                throw new IOException("synthetic file provider text");
              };
        if (failure.equals("invalidFile"))
          h.inspectAction =
              () -> {
                throw new IOException("invalid attributes/hash");
              };
        temporary(() -> h.service.process(request));
        assertEquals(replaced, stored(request));
        assertEquals(0, h.live.get());
        sql("delete from schubert.script_entries");
        entries(201);
      }
      sql("delete from schubert.script_entries");
      sql("delete from schubert.script_files");
      h.inspectAction = () -> {};
      temporary(() -> h.service.process(request));
      assertEquals(replaced, stored(request));
    }
  }

  @Test
  void oneHundredSameMessagesGenerateOnceAndFinalAuthenticationWins() throws Exception {
    master(201);
    try (var h = new Harness();
        var workers = Executors.newFixedThreadPool(16)) {
      var request = request("SCN");
      List<Future<byte[]>> replies = new ArrayList<>();
      for (int i = 0; i < 100; i++) replies.add(workers.submit(() -> h.service.process(request)));
      int initial = 0;
      var ids = new HashSet<String>();
      for (var reply : replies) {
        byte[] actual = reply.get(30, TimeUnit.SECONDS);
        String code = ascii(actual, 208, 4);
        if (code.equals("0000")) initial++;
        else assertEquals("0200", code);
        assertTrue(ids.add(ascii(actual, 24, 36)));
        assertEquals(request.header().messageId().toString(), ascii(actual, 60, 36));
        assertArrayEquals(
            Arrays.copyOfRange(golden("SCN", request, h, code, true, 201, 1), 256, 1984),
            Arrays.copyOfRange(actual, 256, actual.length));
      }
      assertEquals(1, initial);
      assertEquals(1, h.published.get());
      assertEquals(1, count("schubert.request_inbox"));
      assertEquals(0, h.live.get());
      session("d", 2, 101);
      var newContext = context(request, "d");
      assertArrayEquals(
          golden("SCN", newContext, h, "0200", true, 201, 102), h.service.process(newContext));
    }
    for (String change :
        List.of("revoked", "owner", "ownerClose", "role", "expiry", "regenerationOwner")) {
      seed();
      master(201);
      try (var h = new Harness()) {
        var request = request("SCN");
        if (change.equals("regenerationOwner")) {
          h.service.process(request);
          h.missing = true;
          h.inspectAction = () -> sql("update schubert.auth_sessions set user_id=102");
        } else
          h.publishAction =
              () -> {
                switch (change) {
                  case "revoked" ->
                      sql(
                          "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:01:01Z',revoke_reason='LOGOUT'");
                  case "owner", "ownerClose" -> {
                    sql("update schubert.auth_sessions set user_id=102");
                    if (change.equals("ownerClose")) {
                      h.fault = "close";
                      h.faultConnection = 2;
                    }
                  }
                  case "role" -> sql("update schubert.app_users set role='ADMIN' where id=101");
                  case "expiry" -> h.now.set(Instant.parse("2026-09-08T08:00:00Z"));
                  default -> throw new AssertionError(change);
                }
              };
        if (change.equals("ownerClose")) temporary(() -> h.service.process(request));
        else {
          byte[] actual = h.service.process(request);
          assertEquals(change.equals("role") ? "0000" : "0102", ascii(actual, 208, 4));
        }
        assertEquals(
            change.equals("role") || change.equals("regenerationOwner") ? 1 : 0,
            count("schubert.request_inbox"));
        assertEquals(0, h.live.get());
      }
    }
  }

  @Test
  void failuresAtEveryTransactionFileClockAndIdentityBoundaryNeverClaimSuccess() throws Exception {
    try (var h = new Harness()) {
      assertThrows(NullPointerException.class, () -> h.service.process(null));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  null,
                  h.verifier,
                  new ScenarioRepository(),
                  h.inbox,
                  h.responses,
                  h.publisher,
                  h.inspector,
                  h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  null,
                  new ScenarioRepository(),
                  h.inbox,
                  h.responses,
                  h.publisher,
                  h.inspector,
                  h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  h.verifier,
                  null,
                  h.inbox,
                  h.responses,
                  h.publisher,
                  h.inspector,
                  h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  h.verifier,
                  new ScenarioRepository(),
                  null,
                  h.responses,
                  h.publisher,
                  h.inspector,
                  h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  h.verifier,
                  new ScenarioRepository(),
                  h.inbox,
                  null,
                  h.publisher,
                  h.inspector,
                  h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  h.verifier,
                  new ScenarioRepository(),
                  h.inbox,
                  h.responses,
                  null,
                  h.inspector,
                  h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  h.verifier,
                  new ScenarioRepository(),
                  h.inbox,
                  h.responses,
                  h.publisher,
                  null,
                  h.clock));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  h.verifier,
                  new ScenarioRepository(),
                  h.inbox,
                  h.responses,
                  h.publisher,
                  h.inspector,
                  null));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioApplicationService(
                  h.source,
                  h.verifier,
                  new ScenarioRepository(),
                  h.inbox,
                  h.responses,
                  h.publisher,
                  h.inspector,
                  h.clock,
                  null));
      assertThrows(
          PermanentProtocolException.class,
          () -> h.service.process(message("GAMREQ01", spaces(1))));
      assertEquals(0, h.opens.get());
      var publicService =
          new ScenarioApplicationService(
              h.source,
              h.verifier,
              new ScenarioRepository(),
              h.inbox,
              h.responses,
              h.publisher,
              h.inspector,
              h.clock);
      assertEquals("0000", ascii(publicService.process(request("GAM")), 208, 4));
    }
    for (int stage : new int[] {1, 2}) {
      for (String fault :
          List.of(
              "open",
              "nullConnection",
              "setAutoCommit",
              "setReadOnly",
              "prepareStatement",
              "commit",
              "afterCommit",
              "rollback",
              "close")) {
        seed();
        try (var h = new Harness()) {
          h.fault = fault;
          h.faultConnection = stage;
          temporary(() -> h.service.process(request("GAM")));
          assertEquals(
              stage == 2 && List.of("afterCommit", "close").contains(fault) ? 1 : 0,
              count("schubert.request_inbox"),
              fault);
          assertEquals(0, h.live.get());
        }
      }
    }
    for (String fault : List.of("none", "close", "rollback")) {
      seed();
      sql(
          "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:00:30Z',revoke_reason='LOGOUT'");
      try (var h = new Harness()) {
        h.fault = fault;
        if (fault.equals("none"))
          assertEquals("0102", ascii(h.service.process(request("GAM")), 208, 4));
        else temporary(() -> h.service.process(request("GAM")));
        assertEquals(0, count("schubert.request_inbox"));
      }
    }
    for (int stage = 1; stage <= 5; stage++) {
      for (boolean nullValue : List.of(false, true)) {
        seed();
        try (var h = new Harness()) {
          h.clockFaultAt = stage;
          h.nullClock = nullValue;
          temporary(() -> h.service.process(request("GAM")));
          assertEquals(stage == 5 ? 1 : 0, count("schubert.request_inbox"));
        }
      }
    }
    for (int stage : new int[] {1, 2}) {
      for (boolean nullValue : List.of(false, true)) {
        seed();
        try (var h = new Harness()) {
          h.identifierFaultAt = stage;
          h.nullIdentifier = nullValue;
          temporary(() -> h.service.process(request("GAM")));
          assertEquals(stage == 2 ? 1 : 0, count("schubert.request_inbox"));
        }
      }
    }
    for (String corruption :
        List.of(
            "state",
            "ref",
            "layout",
            "version",
            "time",
            "key",
            "cipher",
            "missingCipher",
            "processing",
            "deleted")) {
      seed();
      try (var h = new Harness()) {
        var request = request("GAM");
        h.service.process(request);
        h.opens.set(0);
        h.beforeOpenAction =
            () -> {
              if (h.opens.get() != 2) return;
              String change =
                  switch (corruption) {
                    case "state" -> "processing_state='ERROR'";
                    case "ref" -> "result_ref_type='SCENARIO_FILE',result_ref_id=30";
                    case "layout" -> "response_layout_id='SPKRSP01'";
                    case "version" -> "response_version='002'";
                    case "time" -> "completed_at=completed_at+interval '1 microsecond'";
                    case "key" -> "response_key_version='other'";
                    case "cipher" -> "response_body_encrypted=decode(repeat('00',29),'hex')";
                    case "missingCipher" ->
                        "response_body_encrypted=null,response_key_version=null";
                    case "processing" ->
                        "processing_state='PROCESSING',result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null";
                    case "deleted" -> "";
                    default -> throw new AssertionError(corruption);
                  };
              sql(
                  change.isEmpty()
                      ? "delete from schubert.request_inbox"
                      : "update schubert.request_inbox set " + change);
            };
        temporary(() -> h.service.process(request));
        assertEquals(corruption.equals("deleted") ? 0 : 1, count("schubert.request_inbox"));
      }
    }
    seed();
    try (var h = new Harness()) {
      var request = request("GAM");
      h.beforeOpenAction =
          () -> {
            if (h.opens.get() == 2) {
              h.beforeOpenAction = () -> {};
              var other =
                  new ScenarioApplicationService(
                      h.source,
                      h.verifier,
                      new ScenarioRepository(),
                      h.inbox,
                      h.responses,
                      h.publisher,
                      h.inspector,
                      h.clock);
              assertEquals("0000", ascii(other.process(request), 208, 4));
            }
          };
      temporary(() -> h.service.process(request));
      assertEquals(1, count("schubert.request_inbox"));
    }
    for (String corrupt : List.of("identity", "identityClose", "fingerprintKey", "processing")) {
      seed();
      try (var h = new Harness()) {
        var request = request("GAM");
        h.service.process(request);
        sql(
            "update schubert.request_inbox set "
                + switch (corrupt) {
                  case "identity", "identityClose" ->
                      "correlation_id='00000000-0000-0000-0000-000000000999'";
                  case "fingerprintKey" -> "fingerprint_key_version='unknown'";
                  case "processing" ->
                      "processing_state='PROCESSING',result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null";
                  default -> throw new AssertionError(corrupt);
                });
        var before = stored(request);
        if (corrupt.equals("identityClose")) {
          h.fault = "close";
          h.faultConnection = 3;
        }
        if (corrupt.equals("identity")) {
          var error =
              assertThrows(PermanentProtocolException.class, () -> h.service.process(request));
          assertNull(error.getCause());
          assertEquals(0, error.getSuppressed().length);
        } else temporary(() -> h.service.process(request));
        assertEquals(before, stored(request));
      }
    }
    seed();
    master(201);
    try (var h = new Harness()) {
      h.publishAction =
          () -> {
            throw new IOException("synthetic failed publication");
          };
      temporary(() -> h.service.process(request("SCN")));
      assertEquals(0, count("schubert.request_inbox"));
      h.publishAction = () -> h.snapshots.close();
      temporary(() -> h.service.process(request("SCN")));
      assertEquals(
          1, h.published.get()); // Confirmed ready is retained by the provider, not deleted.
      assertEquals(0, count("schubert.request_inbox"));
    }
    seed();
    master(1);
    try (var h = new Harness()) {
      sql("update schubert.script_files set display_path='/invalid-display-path'");
      temporary(() -> h.service.process(request("SCN")));
      assertEquals(0, count("schubert.request_inbox"));
    }
  }

  @Test
  void brokerSendAndAckFailuresReplayOneCommittedResult(@TempDir Path brokerRoot) throws Exception {
    Configuration configuration;
    try (var file = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(file);
    }
    configuration
        .setPagingDirectory(brokerRoot.resolve("paging").toString())
        .setBindingsDirectory(brokerRoot.resolve("bindings").toString())
        .setJournalDirectory(brokerRoot.resolve("journal").toString())
        .setLargeMessagesDirectory(brokerRoot.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    var broker = new EmbeddedActiveMQ().setConfiguration(configuration).start();
    var requestQueue = new ActiveMQQueue(BrokerTopology.SYNC_REQUEST.fullyQualifiedQueue());
    var replyQueue = new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue());
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var receiver = factory.createContext(JMSContext.SESSION_TRANSACTED);
        var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var requests = receiver.createConsumer(requestQueue);
        var replies = observer.createConsumer(replyQueue)) {
      for (String point : List.of("createProducer", "commit", "database")) {
        seed();
        master(201);
        try (var h = new Harness()) {
          var input = request("SCN");
          var listener = new SyncRequestListener(h.service, h.clock);
          if (point.equals("database")) h.fault = "open";
          var failing =
              (JMSContext)
                  Proxy.newProxyInstance(
                      JMSContext.class.getClassLoader(),
                      new Class<?>[] {JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals(point)) {
                          assertEquals(1, count("schubert.request_inbox"));
                          assertEquals(0, h.live.get());
                          assertEquals(1, h.published.get());
                          throw new JMSRuntimeException("synthetic transport boundary failure");
                        }
                        return invoke(receiver, m, a);
                      });
          sendScenario(producer, requestQueue, input);
          Message first = requests.receive(5000);
          assertNotNull(first);
          assertEquals(1, first.getIntProperty("JMSXDeliveryCount"));
          if (point.equals("database")) temporary(() -> listener.onMessage(failing, first));
          else assertThrows(JMSRuntimeException.class, () -> listener.onMessage(failing, first));
          assertNull(replies.receive(250));
          assertEquals(point.equals("database") ? 0 : 1, count("schubert.request_inbox"));
          h.fault = "none";
          Message retry = requests.receive(5000);
          assertNotNull(retry);
          assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
          listener.onMessage(receiver, retry);
          assertBrokerReply(
              replies.receive(5000),
              golden(
                  "SCN",
                  input,
                  h,
                  point.equals("database") ? "0000" : "0200",
                  true,
                  201,
                  point.equals("database") ? 2 : 3));
          var frozen = stored(input);
          sendScenario(
              producer, requestQueue, input); // New broker message, no duplicate-cache property.
          Message duplicate = requests.receive(5000);
          assertNotNull(duplicate);
          assertEquals(1, duplicate.getIntProperty("JMSXDeliveryCount"));
          listener.onMessage(receiver, duplicate);
          assertBrokerReply(
              replies.receive(5000),
              golden("SCN", input, h, "0200", true, 201, point.equals("database") ? 3 : 4));
          assertEquals(frozen, stored(input));
          assertEquals(1, count("schubert.request_inbox"));
          assertEquals(1, h.published.get());
          assertEquals(0, h.live.get());
          assertNull(requests.receive(250));
          assertNull(replies.receive(250));
        }
      }
    } finally {
      broker.stop();
    }
  }

  private static void sendScenario(
      JMSContext context, ActiveMQQueue queue, WireMessage<FixedPayload> input)
      throws JMSException {
    byte[] body = spaces(268);
    put(body, 0, "SCHBNK01001SCNREQ01001QS");
    put(body, 24, input.header().messageId().toString());
    put(body, 60, input.header().messageId().toString());
    put(body, 96, "20260908090100000");
    put(body, 113, "b".repeat(64));
    put(body, 177, "0256000012000000000000000000268");
    put(body, 256, "000000000030");
    var message = context.createBytesMessage();
    message.writeBytes(body);
    message.setJMSCorrelationID(input.header().messageId().toString());
    message.setJMSReplyTo(new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue()));
    message.setStringProperty("NKMessageID", input.header().messageId().toString());
    message.setStringProperty("NKLayoutID", "SCNREQ01");
    message.setStringProperty("NKProtocolVersion", "001");
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(5000)
        .send(queue, message);
    Arrays.fill(body, (byte) 0);
  }

  private static void assertBrokerReply(Message received, byte[] expected) throws JMSException {
    var response = assertInstanceOf(BytesMessage.class, received);
    assertEquals(expected.length, response.getBodyLength());
    byte[] actual = new byte[expected.length];
    assertEquals(expected.length, response.readBytes(actual));
    assertArrayEquals(expected, actual);
    assertEquals(ascii(expected, 60, 36), response.getJMSCorrelationID());
    assertEquals(ascii(expected, 24, 36), response.getStringProperty("NKMessageID"));
    assertEquals("SCNRSP01", response.getStringProperty("NKLayoutID"));
    assertEquals("001", response.getStringProperty("NKProtocolVersion"));
    assertEquals(DeliveryMode.PERSISTENT, response.getJMSDeliveryMode());
    Arrays.fill(actual, (byte) 0);
  }

  @Test
  void realWriterInspectorAndDatabaseRegenerationShareExactFrozenBytes(
      @TempDir(factory = RealScenarioFileFixture.Ext4.class) Path directory) throws Exception {
    for (int count : new int[] {201, 10000}) {
      seed();
      master(count);
      Path filesRoot = Files.createDirectory(directory.resolve("count-" + count));
      try (var h = new Harness();
          var files = new RealScenarioFileFixture(filesRoot)) {
        ScenarioFilePublisher publisher =
            (records, time) -> {
              assertEquals(0, h.live.get());
              unlocked();
              h.published.incrementAndGet();
              h.lastFile = files.publisher().publish(records, time);
              return h.lastFile;
            };
        ScenarioFileInspector inspector =
            descriptor -> {
              assertEquals(0, h.live.get());
              unlocked();
              return files.inspector().inspect(descriptor);
            };
        var service =
            new ScenarioApplicationService(
                h.source,
                h.verifier,
                new ScenarioRepository(),
                h.inbox,
                h.responses,
                publisher,
                inspector,
                h.clock,
                () -> new UUID(0, h.ids.incrementAndGet()));
        var request = request("SCN");
        byte[] first = service.process(request);
        assertArrayEquals(golden("SCN", request, h, "0000", true, count, 2), first);
        Path original = filesRoot.resolve(h.lastFile.relativePath());
        assertRealFile(original, count);
        var saved = stored(request);
        assertArrayEquals(
            golden("SCN", request, h, "0200", true, count, 3), service.process(request));
        assertEquals(1, h.published.get());
        assertEquals(saved, stored(request));
        // Delete only this test's verified ready, simulating completed morning cleanup.
        Files.delete(original);
        byte[] regenerated = service.process(request);
        assertArrayEquals(golden("SCN", request, h, "0200", true, count, 4), regenerated);
        assertEquals(2, h.published.get());
        assertEquals(saved.subList(0, 5), stored(request).subList(0, 5));
        assertRealFile(filesRoot.resolve(h.lastFile.relativePath()), count);
        var failed = request("SCN");
        h.fault = "commit";
        h.faultConnection = h.opens.get() + 2;
        temporary(() -> service.process(failed));
        assertEquals(3, h.published.get());
        assertEquals(List.of(), stored(failed));
        Path retained = filesRoot.resolve(h.lastFile.relativePath());
        assertRealFile(retained, count);
        try (var children = Files.list(filesRoot.resolve("20260908"))) {
          assertEquals(2, children.count());
        }
        assertEquals(0, h.live.get());
      }
    }
  }

  private static void assertRealFile(Path path, int count) throws Exception {
    assertEquals(4800L * count, Files.size(path));
    assertEquals(0100640, Files.getAttribute(path, "unix:mode"));
    assertEquals(040750, Files.getAttribute(path.getParent(), "unix:mode"));
    assertEquals(
        "users",
        Files.readAttributes(path, java.nio.file.attribute.PosixFileAttributes.class)
            .group()
            .getName());
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var stream = Files.newInputStream(path)) {
      for (int n = 1; n <= count; n++) {
        byte[] expected = spaces(4800);
        ScenarioReplayFixture.number(expected, 0, 12, n);
        ScenarioReplayFixture.number(expected, 12, 6, n);
        ScenarioReplayFixture.number(expected, 18, 8, 1);
        put(expected, 26, "narration");
        put(expected, 164, "本文");
        ScenarioReplayFixture.number(expected, 4260, 3, 0);
        byte[] actual = stream.readNBytes(4800);
        assertArrayEquals(expected, actual);
        digest.update(actual);
      }
      assertEquals(-1, stream.read());
    }
    assertEquals(hash(count), HexFormat.of().formatHex(digest.digest()));
  }

  private static final class Harness implements AutoCloseable {
    final AtomicInteger live = new AtomicInteger();
    final AtomicInteger published = new AtomicInteger();
    final AtomicLong ids = new AtomicLong();
    final AtomicInteger opens = new AtomicInteger();
    final AtomicInteger clockCalls = new AtomicInteger();
    int faultConnection = 1;
    int clockFaultAt;
    int identifierFaultAt;
    String fault = "none";
    boolean nullClock;
    boolean nullIdentifier;
    final AtomicReference<Instant> now = new AtomicReference<>(NOW);
    final List<Boolean> modes = new CopyOnWriteArrayList<>();
    final FingerprintKeyRing keys =
        new FingerprintKeyRing("fp1", ScenarioReplayFixture.key(), null, null);
    final ResponseSnapshotCodec snapshots =
        new ResponseSnapshotCodec("fixture", ScenarioReplayFixture.key(), null, null);
    final AuthenticationContextVerifier verifier =
        new AuthenticationContextVerifier(new ContextHash());
    final JdbcInboxCoordinator inbox = new JdbcInboxCoordinator(keys);
    final ScenarioReplayService responses = new ScenarioReplayService(snapshots);
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
              throw new IllegalStateException("synthetic clock failure");
            }
            return now.get();
          }
        };
    boolean missing;
    Action publishAction = () -> {};
    Action inspectAction = () -> {};
    Action beforeOpenAction = () -> {};
    LargeResultDescriptor lastFile;
    final ScenarioFilePublisher publisher =
        (records, time) -> {
          assertEquals(0, live.get());
          unlocked();
          try {
            publishAction.run();
          } catch (SQLException failure) {
            throw new IOException(failure);
          }
          int number = published.incrementAndGet();
          UUID id = new UUID(0, 1000 + number);
          lastFile =
              new LargeResultDescriptor(
                  id,
                  "20260908/" + id + ".ready",
                  4800L * records.size(),
                  hash(records.size()),
                  records.size());
          return lastFile;
        };
    final ScenarioFileInspector inspector =
        descriptor -> {
          assertEquals(0, live.get());
          unlocked();
          try {
            inspectAction.run();
          } catch (SQLException failure) {
            throw new IOException(failure);
          }
          return missing
              ? ScenarioFileInspector.Availability.MISSING
              : ScenarioFileInspector.Availability.PRESENT;
        };
    final DataSource source =
        source(
            () -> {
              int stage = opens.incrementAndGet();
              try {
                beforeOpenAction.run();
              } catch (IOException failure) {
                throw new SQLException(failure);
              }
              boolean affected = stage == faultConnection;
              if (affected && fault.equals("open")) throw new SQLException("synthetic open");
              if (affected && fault.equals("nullConnection")) return null;
              Connection c = database.api();
              live.incrementAndGet();
              return (Connection)
                  Proxy.newProxyInstance(
                      Connection.class.getClassLoader(),
                      new Class<?>[] {Connection.class},
                      (p, m, a) -> {
                        if (m.getName().equals("setReadOnly")) modes.add((Boolean) a[0]);
                        if (m.getName().equals("close")) {
                          try {
                            Object result = invoke(c, m, a);
                            if (affected && fault.equals("close"))
                              throw new SQLException("synthetic close");
                            return result;
                          } finally {
                            live.decrementAndGet();
                          }
                        }
                        if (affected
                            && (m.getName().equals(fault)
                                || (m.getName().equals("prepareStatement")
                                    && fault.equals("rollback"))))
                          throw new SQLException("synthetic JDBC failure");
                        Object result = invoke(c, m, a);
                        if (affected && m.getName().equals("commit") && fault.equals("afterCommit"))
                          throw new SQLException("synthetic after commit");
                        return result;
                      });
            });
    final ScenarioApplicationService service =
        new ScenarioApplicationService(
            source,
            verifier,
            new ScenarioRepository(),
            inbox,
            responses,
            publisher,
            inspector,
            clock,
            () -> {
              long id = ids.incrementAndGet();
              if (id == identifierFaultAt) {
                if (nullIdentifier) return null;
                throw new IllegalStateException("synthetic UUID failure");
              }
              return new UUID(0, id);
            });

    Harness() throws Exception {}

    @Override
    public void close() {
      snapshots.close();
      keys.close();
      assertEquals(0, live.get());
    }
  }

  private static WireMessage<FixedPayload> request(String prefix) {
    byte[] data =
        switch (prefix) {
          case "GAM" -> new byte[0];
          case "SPK", "RTE" -> spaces(12);
          case "SCF" -> spaces(14);
          case "SRC" -> search();
          case "SCN" -> "000000000030".getBytes(StandardCharsets.US_ASCII);
          default -> throw new AssertionError(prefix);
        };
    if (List.of("SPK", "RTE", "SCF").contains(prefix)) put(data, 0, "NUKITASHI1");
    if (prefix.equals("SCF")) put(data, 12, "01");
    return message(prefix + "REQ01", data);
  }

  private static WireMessage<FixedPayload> context(WireMessage<FixedPayload> wire, String value) {
    var h = wire.header();
    return new WireMessage<>(
        new CommonHeader(
            h.protocolIdentifier(),
            h.headerVersion(),
            h.layoutId(),
            h.layoutVersion(),
            h.messageKind(),
            h.interactionKind(),
            h.messageId(),
            h.correlationId(),
            h.sentAt(),
            Optional.of(AuthenticationContext.of(value.repeat(64))),
            h.headerLength(),
            h.dataLength(),
            h.recordLength(),
            h.recordCount(),
            h.totalLength(),
            h.resultCode()),
        wire.payload());
  }

  private static byte[] golden(
      String prefix,
      WireMessage<FixedPayload> request,
      Harness h,
      String code,
      boolean file,
      int count,
      long response) {
    String timestamp =
        h.now.get().equals(NOW.plusSeconds(20)) ? "20260908090120000" : "20260908090100000";
    byte[] expected =
        ScenarioReplayFixture.wire(
            prefix,
            request.header().messageId(),
            new UUID(0, response),
            timestamp,
            request.header().authenticationContext().orElseThrow().wireValue(),
            code,
            file,
            count);
    if (prefix.equals("SCF") && (code.equals("0000") || code.equals("0200")))
      put(expected, 256 + 14, "共通ルート");
    if (file) {
      // Publisher's first descriptor is known before invocation; later calls use its public fixture
      // state.
      int publication = h.published.get() == 0 ? 1 : h.published.get();
      if (h.missing && h.now.get().equals(NOW.plusSeconds(20)) && publication == 1) publication = 2;
      UUID id = new UUID(0, 1000 + publication);
      put(expected, 256 + 1329, id.toString());
      Arrays.fill(expected, 256 + 1365, 256 + 1621, (byte) 32);
      put(expected, 256 + 1365, "20260908/" + id + ".ready");
      put(expected, 256 + 1633, hash(count));
    }
    return expected;
  }

  private static String hash(int count) {
    try {
      MessageDigest digest = MessageDigest.getInstance("SHA-256");
      byte[] record = spaces(4800);
      ScenarioReplayFixture.number(record, 18, 8, 1);
      put(record, 26, "narration");
      put(record, 164, "本文");
      ScenarioReplayFixture.number(record, 4260, 3, 0);
      for (int n = 1; n <= count; n++) {
        ScenarioReplayFixture.number(record, 0, 12, n);
        ScenarioReplayFixture.number(record, 12, 6, n);
        digest.update(record);
      }
      return HexFormat.of().formatHex(digest.digest());
    } catch (java.security.NoSuchAlgorithmException failure) {
      throw new AssertionError(failure);
    }
  }

  private static void master(int count) throws SQLException {
    sql("insert into schubert.games values(1,'NUKITASHI1','One',1,'2026-09-08Z')");
    sql(
        "insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at) "
            + "values(30,1,1,'scenario/01.txt','scenario/01.txt','01.txt','01_A','Chapter',repeat('a',64),1,'2026-09-08Z')");
    entries(count);
  }

  private static void entries(int count) throws SQLException {
    sql(
        "insert into schubert.script_entries(id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,body,raw_block,created_at) "
            + "select n,1,30,n,n,1,'narration','本文','synthetic','2026-09-08Z' from generate_series(1,"
            + count
            + ") t(n)");
  }

  private static void session(String raw, int id, int owner) throws Exception {
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

  private static void sql(String sql) throws SQLException {
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  private static int count(String table) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from " + table)) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static List<String> stored(WireMessage<FixedPayload> request) throws SQLException {
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "select processing_state,result_ref_type,created_at,completed_at,expires_at,encode(response_body_encrypted,'hex'),response_key_version from schubert.request_inbox where message_id=?")) {
      s.setObject(1, request.header().messageId());
      try (var r = s.executeQuery()) {
        var values = new ArrayList<String>();
        if (r.next()) for (int col = 1; col <= 7; col++) values.add(r.getString(col));
        assertFalse(r.next());
        return values;
      }
    }
  }

  private static EncryptedResponseSnapshot cipher(WireMessage<FixedPayload> request)
      throws SQLException {
    var values = stored(request);
    return new EncryptedResponseSnapshot(values.get(6), HexFormat.of().parseHex(values.get(5)));
  }

  private static void unlocked() throws IOException {
    try (var c = database.transaction();
        var s = c.createStatement()) {
      s.executeQuery("select id from schubert.app_users for update nowait").close();
      s.executeQuery("select id from schubert.auth_sessions for update nowait").close();
      s.executeQuery("select message_id from schubert.request_inbox for update nowait").close();
      c.rollback();
    } catch (SQLException failure) {
      throw new IOException(failure);
    }
  }

  private static String ascii(byte[] bytes, int offset, int length) {
    return new String(bytes, offset, length, StandardCharsets.US_ASCII);
  }

  private static void temporary(org.junit.jupiter.api.function.Executable operation) {
    var error = assertThrows(TemporaryInfrastructureException.class, operation);
    assertEquals("request transaction is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  @FunctionalInterface
  private interface Action {
    void run() throws IOException, SQLException;
  }

  @FunctionalInterface
  private interface SqlOpen {
    Connection open() throws SQLException;
  }

  private static DataSource source(SqlOpen open) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (p, m, a) -> {
              if (m.getName().equals("getConnection")) return open.open();
              throw new UnsupportedOperationException(m.getName());
            });
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}
