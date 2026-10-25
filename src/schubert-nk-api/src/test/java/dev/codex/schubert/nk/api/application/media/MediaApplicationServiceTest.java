package dev.codex.schubert.nk.api.application.media;

import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.LAYOUTS;
import static dev.codex.schubert.nk.api.application.media.MediaStageFixture.NOW;
import static dev.codex.schubert.nk.api.application.media.MediaStageFixture.input;
import static dev.codex.schubert.nk.api.application.media.MediaStageFixture.invoke;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.AssetManifestLoader;
import dev.codex.schubert.nk.api.file.HeldMediaFileInspector;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionConsistency;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.MessageStageGuard;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestListener;
import dev.codex.schubert.nk.api.persistence.MediaRepository;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Message;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** Actual staged PostgreSQL/file/JMS orchestration. SS312/324/333; PT-MED-055..061. */
class MediaApplicationServiceTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  void med060BrokerRedeliverySendsOnlyAfterDatabaseCompletion() throws Exception {
    Path brokerRoot = root.resolve("broker");
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
        try (var h = new MediaStageFixture(database)) {
          h.seed();
          var request = input("MED");
          var listener = new SyncRequestListener(h.service, h.clock);
          if (point.equals("database")) h.fault = "open";
          var failing =
              (JMSContext)
                  Proxy.newProxyInstance(
                      JMSContext.class.getClassLoader(),
                      new Class<?>[] {JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals(point)) {
                          assertEquals(1, h.inboxCount());
                          assertEquals(0, h.live.get());
                          assertEquals(1, h.inspections.get());
                          throw new JMSRuntimeException("synthetic transport boundary failure");
                        }
                        return invoke(receiver, m, a);
                      });
          sendMedia(producer, requestQueue, request);
          Message first = requests.receive(5000);
          assertNotNull(first);
          assertEquals(1, first.getIntProperty("JMSXDeliveryCount"));
          if (point.equals("database")) temporary(() -> listener.onMessage(failing, first));
          else assertThrows(JMSRuntimeException.class, () -> listener.onMessage(failing, first));
          assertNull(replies.receive(250));
          assertEquals(point.equals("database") ? 0 : 1, h.inboxCount());
          h.fault = "none";
          Message retry = requests.receive(5000);
          assertNotNull(retry);
          assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
          listener.onMessage(receiver, retry);
          assertBrokerReply(
              replies.receive(5000),
              h.golden(
                  request,
                  point.equals("database") ? "0000" : "0200",
                  point.equals("database") ? 2 : 3));
          var frozen = h.stored(request);
          // A distinct broker message with the same business ID, without duplicate-cache hints.
          sendMedia(producer, requestQueue, request);
          Message duplicate = requests.receive(5000);
          assertNotNull(duplicate);
          assertEquals(1, duplicate.getIntProperty("JMSXDeliveryCount"));
          listener.onMessage(receiver, duplicate);
          assertBrokerReply(
              replies.receive(5000), h.golden(request, "0200", point.equals("database") ? 3 : 4));
          assertEquals(frozen, h.stored(request));
          assertEquals(1, h.inboxCount());
          assertEquals(point.equals("database") ? 2 : 3, h.inspections.get());
          assertEquals(0, h.live.get());
          assertNull(requests.receive(250));
          assertNull(replies.receive(250));
        }
      }
    } finally {
      broker.stop();
    }
  }

  private static void sendMedia(
      JMSContext context, ActiveMQQueue queue, WireMessage<FixedPayload> input)
      throws JMSException {
    byte[] body = new byte[328];
    Arrays.fill(body, (byte) 32);
    MediaRequestFixture.put(body, 0, "SCHBNK01001MEDREQ01001QS");
    MediaRequestFixture.put(body, 24, input.header().messageId().toString());
    MediaRequestFixture.put(body, 60, input.header().messageId().toString());
    MediaRequestFixture.put(body, 96, "20260908090100000");
    MediaRequestFixture.put(body, 113, "b".repeat(64));
    MediaRequestFixture.put(body, 177, "0256000072000000000000000000328");
    System.arraycopy(MediaRequestFixture.data("MEDREQ01"), 0, body, 256, 72);
    var message = context.createBytesMessage();
    message.writeBytes(body);
    message.setJMSCorrelationID(input.header().messageId().toString());
    message.setJMSReplyTo(new ActiveMQQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue()));
    message.setStringProperty("NKMessageID", input.header().messageId().toString());
    message.setStringProperty("NKLayoutID", "MEDREQ01");
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
    assertEquals("MEDRSP01", response.getStringProperty("NKLayoutID"));
    assertEquals("001", response.getStringProperty("NKProtocolVersion"));
    assertEquals(DeliveryMode.PERSISTENT, response.getJMSDeliveryMode());
    Arrays.fill(actual, (byte) 0);
  }

  @Test
  void med055EightQueriesCommitThenReplayFrozenBytes() throws Exception {
    for (String prefix : LAYOUTS) {
      try (var h = new MediaStageFixture(database)) {
        h.seed();
        var input = input(prefix);
        assertArrayEquals(h.golden(input, "0000", 2), h.service.process(input));
        var before = h.stored(input);
        assertEquals("COMPLETED", before.get(0));
        assertEquals("NONE", before.get(1));
        assertEquals("2026-09-09T00:01:00Z", before.get(4));
        assertEquals(List.of(true, false), h.modes);
        assertEquals(List.of("AUD", "VID", "MED").contains(prefix) ? 1 : 0, h.inspections.get());
        h.sql("update schubert.media_assets set title='changed-master'");
        h.now.set(NOW.plusSeconds(20));
        assertArrayEquals(h.golden(input, "0200", 3), h.service.process(input));
        assertEquals(before, h.stored(input));
        assertEquals(1, h.inboxCount());
        assertEquals(List.of(true, false, true, false), h.modes);
        assertEquals(0, h.live.get());
      }
    }
  }

  @Test
  void med056DefiniteMissingAndLimitsPersistWithoutInventedFiles() throws Exception {
    for (String prefix : LAYOUTS) {
      try (var h = new MediaStageFixture(database)) {
        h.seed();
        String code;
        if (List.of("AUD", "VID", "MED").contains(prefix)) {
          h.sql("truncate schubert.media_assets,schubert.audio_files cascade");
          code = "0104";
        } else {
          h.exceed(prefix);
          code = "9001";
        }
        var request = input(prefix);
        assertArrayEquals(h.golden(request, code, 2), h.service.process(request));
        var before = h.stored(request);
        assertEquals("ERROR", before.getFirst());
        assertEquals("NONE", before.get(1));
        assertEquals(0, h.inspections.get());
        assertArrayEquals(h.golden(request, code, 3), h.service.process(request));
        assertEquals(before, h.stored(request));
        assertEquals(1, h.inboxCount());
        assertEquals(0, h.inspections.get());
      }
    }
    try (var h = new MediaStageFixture(database)) {
      h.seed();
      h.fault = "query";
      temporary(() -> h.service.process(input("ANM")));
      assertEquals(0, h.inboxCount());
      assertEquals(0, h.inspections.get());
      assertEquals(0, h.live.get());
    }
  }

  @Test
  void med057PhysicalStageHasNoDatabaseLocksAndRechecksIdentity() throws Exception {
    try (var h = new MediaStageFixture(database);
        var assets = new Assets(root.resolve("assets"))) {
      h.seed();
      h.physical = assets.inspector;
      var request = input("MED");
      assertArrayEquals(h.golden(request, "0000", 2), h.service.process(request));
      var frozen = h.stored(request);
      Path file = assets.root.resolve("music/合成.ogg");
      mode(file, "rw-------");
      temporary(() -> h.service.process(request));
      assertEquals(frozen, h.stored(request));
      assertEquals(0100600, Files.getAttribute(file, "unix:mode"));
      mode(file, "rw-r-----");
      Path saved = assets.root.resolve("saved.ogg");
      Files.move(file, saved);
      temporary(() -> h.service.process(request));
      assertEquals(frozen, h.stored(request));
      Files.move(saved, file);
      h.sql("update schubert.media_assets set sha256=repeat('0',64) where logical_id='music-0'");
      temporary(() -> h.service.process(input("MED")));
      assertEquals(1, h.inboxCount());
      assertEquals(frozen, h.stored(request));
      // Replay validates the old saved hash, not the currently changed DB metadata.
      assertArrayEquals(h.golden(request, "0200", 3), h.service.process(request));
      assertEquals("abc", Files.readString(file));
      h.seed();
      h.physical =
          descriptor -> {
            throw new IOException("synthetic private file fault");
          };
      temporary(() -> h.service.process(input("AUD")));
      assertEquals(0, h.inboxCount());
    }
    for (String update :
        List.of(
            "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:01:00Z',revoke_reason='ADMIN'",
            "update schubert.auth_sessions set expires_at=issued_at",
            "update schubert.auth_sessions set user_id=102")) {
      try (var h = new MediaStageFixture(database)) {
        h.seed();
        h.duringFile = () -> h.sql(update);
        var request = input("MED");
        assertArrayEquals(h.golden(request, "0102", 1), h.service.process(request));
        assertEquals(0, h.inboxCount());
        assertEquals(1, h.inspections.get());
        assertEquals(0, h.live.get());
      }
    }
    try (var h = new MediaStageFixture(database)) {
      h.seed();
      h.duringFile =
          () -> {
            h.sql("update schubert.app_users set role='ADMIN' where id=101");
            h.now.set(NOW.plusSeconds(20));
          };
      var request = input("AUD");
      byte[] afterFile = h.service.process(request);
      assertArrayEquals(h.golden(request, "0000", 2), afterFile);
      assertEquals("2026-09-08T00:01:20Z", h.stored(request).get(3));
      assertEquals(1, h.inspections.get());
      assertEquals(List.of(true, false), h.modes);
      h.sql(
          "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:01:20Z',revoke_reason='ADMIN'");
      var before = h.stored(request);
      assertArrayEquals(h.golden(request, "0102", 3), h.service.process(request));
      assertEquals(before, h.stored(request));
      assertEquals(1, h.inspections.get()); // Initial auth rejection never opens an asset.
    }
  }

  @Test
  void med058ConcurrentDuplicateAndChangedRequestsKeepInboxIdentity() throws Exception {
    try (var h = new MediaStageFixture(database);
        var workers = Executors.newFixedThreadPool(10)) {
      h.seed();
      var request = input("MED");
      var start = new CountDownLatch(1);
      List<Future<byte[]>> tasks = new ArrayList<>();
      for (int i = 0; i < 100; i++)
        tasks.add(
            workers.submit(
                () -> {
                  await(start);
                  return h.service.process(request);
                }));
      start.countDown();
      var responseIds = new HashSet<Long>();
      int first = 0;
      int replay = 0;
      for (var task : tasks) {
        byte[] actual = task.get(30, TimeUnit.SECONDS);
        String code = ascii(actual, 208, 4);
        if (code.equals("0000")) first++;
        else {
          assertEquals("0200", code);
          replay++;
        }
        UUID id = UUID.fromString(ascii(actual, 24, 36));
        assertEquals(0, id.getMostSignificantBits());
        assertTrue(responseIds.add(id.getLeastSignificantBits()));
        assertArrayEquals(h.golden(request, code, id.getLeastSignificantBits()), actual);
      }
      assertEquals(1, first);
      assertEquals(99, replay);
      assertEquals(1, h.inboxCount());
      assertEquals(100, h.inspections.get());
      assertEquals(101, h.ids.get());
      for (long id = 2; id <= 101; id++) assertTrue(responseIds.contains(id));
      var frozen = h.stored(request);
      byte[] changed = MediaRequestFixture.data("MEDREQ01");
      MediaRequestFixture.put(changed, 64, "I");
      var otherMode = sameMessage(request, "MED", changed);
      assertThrows(PermanentProtocolException.class, () -> h.service.process(otherMode));
      var otherLayout = sameMessage(request, "ANM", new byte[0]);
      assertThrows(PermanentProtocolException.class, () -> h.service.process(otherLayout));
      h.sql("update schubert.auth_sessions set user_id=102");
      assertThrows(PermanentProtocolException.class, () -> h.service.process(request));
      h.sql("update schubert.auth_sessions set user_id=101");
      assertEquals(frozen, h.stored(request));
      assertEquals(100, h.inspections.get());
      var another = input("MED");
      assertArrayEquals(h.golden(another, "0000", 103), h.service.process(another));
      assertEquals(2, h.inboxCount());
      assertEquals(0, h.live.get());
    }
    try (var h = new MediaStageFixture(database);
        var workers = Executors.newVirtualThreadPerTaskExecutor()) {
      h.seed();
      var request = input("AUD");
      var held = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      h.duringFile =
          () -> {
            held.countDown();
            await(release);
          };
      var first = workers.submit(() -> h.service.process(request));
      await(held);
      var attempted = new CountDownLatch(1);
      var interrupted =
          new FutureTask<Boolean>(
              () -> {
                attempted.countDown();
                temporary(() -> h.service.process(request));
                return Thread.currentThread().isInterrupted();
              });
      Thread waiting = Thread.ofVirtual().unstarted(interrupted);
      waiting.start();
      try {
        await(attempted);
        waiting.interrupt();
        assertTrue(interrupted.get(10, TimeUnit.SECONDS));
        assertEquals(1, h.opens.get());
        assertEquals(0, h.live.get());
      } finally {
        release.countDown();
      }
      assertArrayEquals(h.golden(request, "0000", 2), first.get(10, TimeUnit.SECONDS));
      h.duringFile = () -> {};
      assertArrayEquals(h.golden(request, "0200", 3), h.service.process(request));
      assertEquals(1, h.inboxCount());
    }
  }

  @Test
  void med059JdbcKeyClockAndResourceFaultsRemainRecoverable() throws Exception {
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
              "rollback-close",
              "close")) {
        try (var h = new MediaStageFixture(database)) {
          h.seed();
          h.faultConnection = stage;
          h.fault = fault;
          var request = input("ANM");
          temporary(() -> h.service.process(request));
          boolean committed = stage == 2 && List.of("afterCommit", "close").contains(fault);
          assertEquals(committed ? 1 : 0, h.inboxCount(), fault);
          assertEquals(0, h.live.get());
          h.fault = "none";
          long nextId = h.ids.get() + (committed ? 1 : 2);
          assertArrayEquals(
              h.golden(request, committed ? "0200" : "0000", nextId), h.service.process(request));
          assertEquals(1, h.inboxCount());
        }
      }
    }
    for (String fault : List.of("close", "authRollback")) {
      try (var h = new MediaStageFixture(database)) {
        h.seed();
        h.sql(
            "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:01:00Z',revoke_reason='ADMIN'");
        h.fault = fault;
        temporary(() -> h.service.process(input("MED")));
        assertEquals(0, h.inboxCount());
        assertEquals(0, h.live.get());
      }
    }
    for (int stage = 1; stage <= 5; stage++) {
      for (boolean missing : List.of(false, true)) {
        try (var h = new MediaStageFixture(database)) {
          h.seed();
          h.clockFaultAt = stage;
          h.nullClock = missing;
          var request = input("ANM");
          temporary(() -> h.service.process(request));
          assertEquals(stage == 5 ? 1 : 0, h.inboxCount());
          h.clockFaultAt = 0;
          long next = h.ids.get() + (stage == 5 ? 1 : 2);
          assertArrayEquals(
              h.golden(request, stage == 5 ? "0200" : "0000", next), h.service.process(request));
        }
      }
    }
    for (int stage : new int[] {1, 2}) {
      for (boolean missing : List.of(false, true)) {
        try (var h = new MediaStageFixture(database)) {
          h.seed();
          h.identifierFaultAt = stage;
          h.nullIdentifier = missing;
          var request = input("ANM");
          temporary(() -> h.service.process(request));
          assertEquals(stage == 2 ? 1 : 0, h.inboxCount());
          h.identifierFaultAt = 0;
          long next = h.ids.get() + (stage == 2 ? 1 : 2);
          assertArrayEquals(
              h.golden(request, stage == 2 ? "0200" : "0000", next), h.service.process(request));
        }
      }
    }
    for (String closed :
        List.of("fingerprint-start", "snapshot-start", "fingerprint-file", "snapshot-file")) {
      try (var h = new MediaStageFixture(database)) {
        h.seed();
        if (closed.equals("fingerprint-start")) h.keys.close();
        if (closed.equals("snapshot-start")) h.snapshots.close();
        if (closed.equals("fingerprint-file")) h.duringFile = h.keys::close;
        if (closed.equals("snapshot-file")) h.duringFile = h.snapshots::close;
        temporary(() -> h.service.process(input("MED")));
        assertEquals(0, h.inboxCount());
        assertEquals(0, h.live.get());
      }
    }
    for (String change :
        List.of(
            "state",
            "ref",
            "layout",
            "version",
            "time",
            "key",
            "cipher",
            "missing",
            "fingerprintKey",
            "processing",
            "deleted")) {
      try (var h = new MediaStageFixture(database)) {
        h.seed();
        var request = input("MED");
        h.service.process(request);
        h.duringFile =
            () -> {
              String set =
                  switch (change) {
                    case "state" -> "processing_state='ERROR'";
                    case "ref" -> "result_ref_type='USER',result_ref_id=101";
                    case "layout" -> "response_layout_id='AUDRSP01'";
                    case "version" -> "response_version='002'";
                    case "time" -> "completed_at=completed_at+interval '1 microsecond'";
                    case "key" -> "response_key_version='other'";
                    case "cipher" -> "response_body_encrypted=decode(repeat('00',29),'hex')";
                    case "missing" -> "response_body_encrypted=null,response_key_version=null";
                    case "fingerprintKey" -> "fingerprint_key_version='unknown'";
                    case "processing" ->
                        "processing_state='PROCESSING',result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null";
                    default -> "";
                  };
              h.sql(
                  set.isEmpty()
                      ? "delete from schubert.request_inbox"
                      : "update schubert.request_inbox set " + set);
            };
        temporary(() -> h.service.process(request));
        assertEquals(change.equals("deleted") ? 0 : 1, h.inboxCount());
        assertEquals(0, h.live.get());
      }
    }
    try (var h = new MediaStageFixture(database)) {
      h.seed();
      var request = input("MED");
      h.service.process(request);
      h.sql(
          "update schubert.request_inbox set processing_state='PROCESSING',result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null");
      int before = h.inspections.get();
      temporary(() -> h.service.process(request));
      assertEquals(before, h.inspections.get());
      assertEquals(1, h.inboxCount());
    }
    try (var h = new MediaStageFixture(database)) {
      h.seed();
      var request = input("MED");
      h.service.process(request);
      byte[] changed = MediaRequestFixture.data("MEDREQ01");
      MediaRequestFixture.put(changed, 64, "I");
      var different = sameMessage(request, "MED", changed);
      h.faultConnection = h.opens.get() + 1;
      h.fault = "close";
      temporary(() -> h.service.process(different));
      assertEquals(1, h.inboxCount());
      assertEquals(0, h.live.get());
    }
    try (var h = new MediaStageFixture(database)) {
      h.seed();
      var request = input("MED");
      h.beforeOpen =
          () -> {
            if (h.opens.get() != 2) return;
            h.beforeOpen = () -> {};
            var competing =
                new MediaApplicationService(
                    h.source,
                    h.verifier,
                    new MediaRepository(),
                    h.inbox,
                    h.responses,
                    h.inspector,
                    h.clock,
                    () -> new UUID(0, h.ids.incrementAndGet()));
            assertEquals("0000", ascii(competing.process(request), 208, 4));
          };
      // Fault injection of a forbidden second service instance: never accept an unchecked winner.
      temporary(() -> h.service.process(request));
      assertEquals(1, h.inboxCount());
      assertEquals(0, h.live.get());
      assertArrayEquals(h.golden(request, "0200", 3), h.service.process(request));
    }
  }

  @Test
  void med061NullAndSharedStageContractsPreserveScenarioBehavior() throws Exception {
    try (var h = new MediaStageFixture(database)) {
      for (Executable action :
          List.<Executable>of(
              () ->
                  new MediaApplicationService(
                      null,
                      h.verifier,
                      new MediaRepository(),
                      h.inbox,
                      h.responses,
                      h.inspector,
                      h.clock),
              () ->
                  new MediaApplicationService(
                      h.source,
                      null,
                      new MediaRepository(),
                      h.inbox,
                      h.responses,
                      h.inspector,
                      h.clock),
              () ->
                  new MediaApplicationService(
                      h.source, h.verifier, null, h.inbox, h.responses, h.inspector, h.clock),
              () ->
                  new MediaApplicationService(
                      h.source,
                      h.verifier,
                      new MediaRepository(),
                      null,
                      h.responses,
                      h.inspector,
                      h.clock),
              () ->
                  new MediaApplicationService(
                      h.source,
                      h.verifier,
                      new MediaRepository(),
                      h.inbox,
                      null,
                      h.inspector,
                      h.clock),
              () ->
                  new MediaApplicationService(
                      h.source,
                      h.verifier,
                      new MediaRepository(),
                      h.inbox,
                      h.responses,
                      null,
                      h.clock),
              () ->
                  new MediaApplicationService(
                      h.source,
                      h.verifier,
                      new MediaRepository(),
                      h.inbox,
                      h.responses,
                      h.inspector,
                      null),
              () ->
                  new MediaApplicationService(
                      h.source,
                      h.verifier,
                      new MediaRepository(),
                      h.inbox,
                      h.responses,
                      h.inspector,
                      h.clock,
                      null),
              () -> h.service.process(null))) assertThrows(NullPointerException.class, action);
      assertEquals(0, h.opens.get());
      assertThrows(
          PermanentProtocolException.class,
          () -> h.service.process(MediaRequestFixture.message("GAMREQ01", new byte[0])));
      assertEquals(0, h.opens.get());
      h.seed();
      var publicService =
          MediaApplicationAssembly.create(h.source, h.keys, h.snapshots, h.inspector, h.clock);
      // PT-MED-ASSEMBLY-001/002: real staged SQL/golden path below uses production assembly.
      for (Executable missing :
          List.<Executable>of(
              () ->
                  MediaApplicationAssembly.create(null, h.keys, h.snapshots, h.inspector, h.clock),
              () ->
                  MediaApplicationAssembly.create(
                      h.source, null, h.snapshots, h.inspector, h.clock),
              () -> MediaApplicationAssembly.create(h.source, h.keys, null, h.inspector, h.clock),
              () -> MediaApplicationAssembly.create(h.source, h.keys, h.snapshots, null, h.clock),
              () ->
                  MediaApplicationAssembly.create(
                      h.source, h.keys, h.snapshots, h.inspector, null)))
        assertThrows(NullPointerException.class, missing);
      var request = input("ANM");
      byte[] actual = publicService.process(request);
      assertEquals("0000", ascii(actual, 208, 4));
      assertEquals("0010001002      ", ascii(actual, 256, 16));
      assertNotEquals(request.header().messageId(), UUID.fromString(ascii(actual, 24, 36)));
      assertEquals("2026-09-09T00:01:00Z", h.stored(request).get(4));
      for (String zone : List.of("UTC", "Asia/Tokyo")) {
        try (var c = database.api();
            var s = c.createStatement()) {
          s.execute("set time zone '" + zone + "'");
          try (var row =
              s.executeQuery(
                  "select timestamptz '2026-09-09T00:01:00Z',timestamptz '2026-09-09T09:01:00+09',timestamptz '2026-09-09T09:01:01+09'")) {
            assertTrue(row.next());
            Instant expected = Instant.parse("2026-09-09T00:01:00Z");
            assertEquals(expected, row.getObject(1, java.time.OffsetDateTime.class).toInstant());
            assertEquals(expected, row.getObject(2, java.time.OffsetDateTime.class).toInstant());
            assertEquals(
                expected.plusSeconds(1),
                row.getObject(3, java.time.OffsetDateTime.class).toInstant());
            assertNotEquals(
                row.getObject(2, java.time.OffsetDateTime.class).toInstant(),
                row.getObject(3, java.time.OffsetDateTime.class).toInstant());
          }
        }
      }
    }
    var encrypted = new EncryptedResponseSnapshot("test", new byte[29]);
    var value =
        new InboxCompletion(
            InboxCompletionState.COMPLETED,
            InboxResultReference.none(),
            "MEDRSP01",
            "001",
            Optional.of(encrypted),
            NOW);
    assertThrows(
        NullPointerException.class, () -> InboxCompletionConsistency.sameSaved(null, value));
    assertThrows(
        NullPointerException.class, () -> InboxCompletionConsistency.sameSaved(value, null));
    var copy =
        new InboxCompletion(
            value.state(),
            value.resultReference(),
            value.responseLayoutId(),
            value.responseVersion(),
            Optional.of(new EncryptedResponseSnapshot("test", new byte[29])),
            NOW);
    assertTrue(InboxCompletionConsistency.sameSaved(value, copy));
    for (var different :
        List.of(
            new InboxCompletion(
                InboxCompletionState.ERROR,
                value.resultReference(),
                "MEDRSP01",
                "001",
                value.responseSnapshot(),
                NOW),
            new InboxCompletion(
                value.state(),
                InboxResultReference.numeric(InboxResultReferenceType.USER, 101),
                "MEDRSP01",
                "001",
                value.responseSnapshot(),
                NOW),
            new InboxCompletion(
                value.state(),
                value.resultReference(),
                "AUDRSP01",
                "001",
                value.responseSnapshot(),
                NOW),
            new InboxCompletion(
                value.state(),
                value.resultReference(),
                "MEDRSP01",
                "002",
                value.responseSnapshot(),
                NOW),
            new InboxCompletion(
                value.state(),
                value.resultReference(),
                "MEDRSP01",
                "001",
                value.responseSnapshot(),
                NOW.plusSeconds(1)),
            new InboxCompletion(
                value.state(),
                value.resultReference(),
                "MEDRSP01",
                "001",
                Optional.of(new EncryptedResponseSnapshot("other", new byte[29])),
                NOW))) assertFalse(InboxCompletionConsistency.sameSaved(value, different));
    for (int i = 0; i < 29; i++) {
      byte[] altered = new byte[29];
      altered[i] = 1;
      var other =
          new InboxCompletion(
              value.state(),
              value.resultReference(),
              "MEDRSP01",
              "001",
              Optional.of(new EncryptedResponseSnapshot("test", altered)),
              NOW);
      assertFalse(InboxCompletionConsistency.sameSaved(value, other));
      assertEquals(1, altered[i]);
    }
    var missing =
        new InboxCompletion(
            value.state(), value.resultReference(), "MEDRSP01", "001", Optional.empty(), NOW);
    temporary(() -> InboxCompletionConsistency.sameSaved(value, missing));
    temporary(() -> InboxCompletionConsistency.sameSaved(missing, value));
    assertArrayEquals(new byte[29], encrypted.ciphertext());
    var guard = new MessageStageGuard();
    assertEquals(7, guard.execute(new UUID(0, 1), () -> 7));
    assertThrows(NullPointerException.class, () -> guard.execute(null, () -> 7));
    assertThrows(NullPointerException.class, () -> guard.execute(new UUID(0, 1), null));
  }

  private static WireMessage<FixedPayload> sameMessage(
      WireMessage<FixedPayload> original, String prefix, byte[] data) {
    var h = original.header();
    return new WireMessage<>(
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(prefix + "REQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            h.messageId(),
            h.correlationId(),
            h.sentAt(),
            h.authenticationContext(),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty()),
        new FixedPayload(data, 0, List.of()));
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(30, TimeUnit.SECONDS), "fixture coordination timeout");
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      throw new AssertionError(failure);
    }
  }

  private static String ascii(byte[] bytes, int offset, int length) {
    return new String(bytes, offset, length, StandardCharsets.US_ASCII);
  }

  private static void temporary(Executable action) {
    var failure = assertThrows(TemporaryInfrastructureException.class, action);
    assertEquals("request transaction is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void mode(Path path, String permissions) throws IOException {
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString(permissions));
  }

  private static final class Assets implements AutoCloseable {
    final Path root;
    final OwnedTransferDirectory held;
    final HeldMediaFileInspector inspector;

    Assets(Path root) throws Exception {
      this.root = Files.createDirectory(root);
      mode(root, "rwxr-x---");
      var attributes = Files.readAttributes(root, PosixFileAttributes.class);
      var identity =
          new StorageIdentity(attributes.owner().getName(), attributes.group().getName());
      StringBuilder lines = new StringBuilder();
      for (String path : List.of("scenario/合成.ogg", "video/合成.mp4", "music/合成.ogg")) {
        Path file = root.resolve(path);
        Files.createDirectory(file.getParent());
        mode(file.getParent(), "rwxr-x---");
        Files.writeString(file, "abc");
        mode(file, "rw-r-----");
        lines.append(MediaReplayFixture.SHA).append("  ").append(path).append('\n');
      }
      Path manifests = Files.createDirectory(root.resolve("manifests"));
      mode(manifests, "rwxr-x---");
      Path checksum = Files.writeString(manifests.resolve("master.sha256"), lines);
      mode(checksum, "rw-r-----");
      held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
      inspector =
          new HeldMediaFileInspector(
              held, identity, new AssetManifestLoader(held, identity).load(3));
    }

    @Override
    public void close() throws IOException {
      held.close();
    }
  }
}
