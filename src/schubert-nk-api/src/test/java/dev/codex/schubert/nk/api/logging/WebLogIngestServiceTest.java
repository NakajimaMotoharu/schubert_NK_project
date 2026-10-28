package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.messaging.inbound.WebLogListener;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
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

/** PT-IDEM-012; independent SS323 wire offsets and SS331/351 SQL afterconditions. */
final class WebLogIngestServiceTest {
  private static final String FIXTURE_00000000_0000_0000_0000_000000000012_7E8766AA =
      "00000000-0000-0000-0000-000000000012";
  private static final String FIXTURE_GETCONNECTION_1DAA73DB = "getConnection";
  private static final String FIXTURE_PREPARESTATEMENT_CB987D1F = "prepareStatement";
  private static final String FIXTURE_EXECUTEUPDATE_5E0BBF58 = "executeUpdate";
  private static final String FIXTURE_RUNTIME_2D52CD90 = "runtime";
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

  @BeforeEach
  void reset() throws Exception {
    database.reset();
  }

  @Test
  void projectsExplicitColumnsAndDuplicateKeepsFirstRow() throws Exception {
    var service = new WebLogIngestService(source(database::api));
    byte[] wire = golden();
    assertTrue(service.ingest(event(wire)));
    field(wire, 105, 512, "Second delivery must not replace first");
    field(wire, 1043, 1024, "{}");
    assertFalse(service.ingest(event(wire)));
    try (var connection = database.api();
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select logged_at, service, category, level, action, message, request_id, message_id, correlation_id, source_message_id, actor_user_id, actor_username, http_method, request_uri, status_code, remote_address, duration_ms, security_hold_until, details = '{\"responseBytes\":42,\"truncated\":false,\"projectionStatus\":\"PENDING\",\"actorRole\":\"USER\"}'::jsonb as details_match from schubert.app_logs")) {
      assertTrue(rows.next());
      assertEquals(
          Instant.parse("2026-09-04T21:00:00Z"),
          rows.getObject("logged_at", java.time.OffsetDateTime.class).toInstant());
      assertEquals("WEB", rows.getString("service"));
      assertEquals("REQUEST", rows.getString("category"));
      assertEquals("INFO", rows.getString("level"));
      assertEquals("HTTP_REQUEST_COMPLETED", rows.getString("action"));
      assertEquals("Synthetic request complete", rows.getString("message"));
      assertEquals("00000000-0000-0000-0000-000000000099", rows.getString("request_id"));
      assertEquals(
          FIXTURE_00000000_0000_0000_0000_000000000012_7E8766AA, rows.getString("message_id"));
      assertEquals(
          FIXTURE_00000000_0000_0000_0000_000000000012_7E8766AA,
          rows.getString("source_message_id"));
      assertEquals("00000000-0000-0000-0000-000000000015", rows.getString("correlation_id"));
      assertNull(rows.getObject("actor_user_id"));
      assertNull(rows.getObject("security_hold_until"));
      assertEquals("synthetic-user", rows.getString("actor_username"));
      assertEquals("GET", rows.getString("http_method"));
      assertEquals("/login", rows.getString("request_uri"));
      assertEquals(200, rows.getInt("status_code"));
      assertEquals("127.0.0.1", rows.getString("remote_address"));
      assertEquals(12, rows.getLong("duration_ms"));
      assertTrue(rows.getBoolean("details_match"));
      assertFalse(rows.next());
    }
  }

  @Test
  void optionalFieldsIpv6AndConcurrentDuplicateAreSafe() throws Exception {
    byte[] wire = golden();
    field(wire, 41, 64, "");
    field(wire, 974, 64, "");
    field(wire, 1038, 5, "");
    field(wire, 1043, 1024, "");
    field(wire, 929, 45, "2001:db8::1");
    var service = new WebLogIngestService(source(database::api));
    var jobs = new java.util.ArrayList<Callable<Boolean>>();
    for (int index = 0; index < 100; index++) {
      jobs.add(() -> service.ingest(event(wire)));
    }
    try (var executor = Executors.newFixedThreadPool(8)) {
      int inserted = 0;
      for (var result : executor.invokeAll(jobs)) {
        if (result.get()) {
          inserted++;
        }
      }
      assertEquals(1, inserted);
    }
    try (var connection = database.api();
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select actor_username, action, details::text, remote_address = '2001:db8::1'::inet as ip_match from schubert.app_logs")) {
      assertTrue(rows.next());
      assertNull(rows.getString(1));
      assertEquals("HTTP_REQUEST_COMPLETED", rows.getString(2));
      assertEquals("{}", rows.getString(3));
      assertTrue(rows.getBoolean(4));
      assertFalse(rows.next());
    }
  }

  @Test
  void invalidWireAndNullNeverAcquireDatabase() {
    AtomicInteger opened = new AtomicInteger();
    var service =
        new WebLogIngestService(
            source(
                () -> {
                  opened.incrementAndGet();
                  throw new SQLException();
                }));
    assertThrows(NullPointerException.class, () -> new WebLogIngestService(null));
    assertThrows(NullPointerException.class, () -> service.ingest(null));
    for (var mutation :
        List.of(
            new Mutation(33, 8, "UNKNOWN"),
            new Mutation(17, 16, "ACTION"),
            new Mutation(41, 64, "LOGIN"),
            new Mutation(105, 512, ""),
            new Mutation(653, 8, "get"),
            new Mutation(661, 256, "relative"),
            new Mutation(661, 256, "//remote/path"),
            new Mutation(661, 256, "/?secret=1"),
            new Mutation(661, 256, "/#fragment"),
            new Mutation(929, 45, "localhost"),
            new Mutation(929, 45, "fe80::1%eth0"),
            new Mutation(917, 3, "600"),
            new Mutation(920, 9, "-1"),
            new Mutation(1038, 5, "ROOT"),
            new Mutation(1043, 1024, "{\"password\":\"synthetic-forbidden\"}"))) {
      byte[] wire = golden();
      field(wire, mutation.offset(), mutation.length(), mutation.text());
      assertThrows(
          PermanentProtocolException.class, () -> service.ingest(event(wire)), mutation.toString());
    }
    byte[] wrong = Arrays.copyOf(golden(), 320);
    ascii(wrong, 11, "QWKREQ01");
    ascii(wrong, 181, "000064");
    ascii(wrong, 199, "000000320");
    assertThrows(PermanentProtocolException.class, () -> service.ingest(event(wrong)));
    byte[] malformed = golden();
    ascii(malformed, 181, "002079");
    ascii(malformed, 199, "000002335");
    assertThrows(PermanentProtocolException.class, () -> service.ingest(event(malformed)));
    assertEquals(0, opened.get());
  }

  @Test
  void transactionFailuresNeverReportSuccessAndAlwaysReleaseConnection() throws Exception {
    for (String point :
        List.of(
            FIXTURE_GETCONNECTION_1DAA73DB,
            "setAutoCommit",
            FIXTURE_PREPARESTATEMENT_CB987D1F,
            FIXTURE_EXECUTEUPDATE_5E0BBF58,
            "commit",
            "close",
            FIXTURE_RUNTIME_2D52CD90)) {
      for (boolean rollbackFails : List.of(false, true)) {
        database.reset();
        AtomicInteger closed = new AtomicInteger();
        AtomicInteger rolledBack = new AtomicInteger();
        var service =
            new WebLogIngestService(
                source(
                    () -> {
                      if (point.equals(FIXTURE_GETCONNECTION_1DAA73DB)) {
                        throw new SQLException("synthetic-sensitive-driver-text");
                      }
                      Connection real = database.api();
                      return (Connection)
                          Proxy.newProxyInstance(
                              Connection.class.getClassLoader(),
                              new Class<?>[] {Connection.class},
                              (proxy, method, arguments) -> {
                                String name = method.getName();
                                if (name.equals("close")) {
                                  closed.incrementAndGet();
                                  real.close();
                                }
                                if (name.equals("rollback")) {
                                  rolledBack.incrementAndGet();
                                  real.rollback();
                                  if (rollbackFails) {
                                    throw new SQLException("synthetic-sensitive-rollback");
                                  }
                                }
                                if (name.equals(point)) {
                                  throw new SQLException("synthetic-sensitive-driver-text");
                                }
                                if (name.equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                                    && point.equals(FIXTURE_RUNTIME_2D52CD90)) {
                                  throw new IllegalStateException("synthetic runtime");
                                }
                                Object result = invoke(real, method, arguments);
                                if (name.equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                                    && point.equals(FIXTURE_EXECUTEUPDATE_5E0BBF58)) {
                                  var statement = (java.sql.PreparedStatement) result;
                                  return Proxy.newProxyInstance(
                                      Connection.class.getClassLoader(),
                                      new Class<?>[] {java.sql.PreparedStatement.class},
                                      (ignored, operation, args) -> {
                                        if (operation
                                            .getName()
                                            .equals(FIXTURE_EXECUTEUPDATE_5E0BBF58)) {
                                          throw new SQLException("synthetic-sensitive-bound-value");
                                        }
                                        return invoke(statement, operation, args);
                                      });
                                }
                                return result;
                              });
                    }));
        if (point.equals(FIXTURE_RUNTIME_2D52CD90)) {
          assertThrows(IllegalStateException.class, () -> service.ingest(event(golden())));
        } else {
          var failure =
              assertThrows(
                  LogProjectionDatabaseException.class,
                  () -> service.ingest(event(golden())),
                  point);
          assertEquals("DB request log projection was not confirmed", failure.getMessage());
          assertNull(failure.getCause());
          assertEquals(0, failure.getSuppressed().length);
        }
        assertEquals(point.equals(FIXTURE_GETCONNECTION_1DAA73DB) ? 0 : 1, closed.get(), point);
        assertEquals(
            List.of(
                        FIXTURE_PREPARESTATEMENT_CB987D1F,
                        FIXTURE_EXECUTEUPDATE_5E0BBF58,
                        "commit",
                        FIXTURE_RUNTIME_2D52CD90)
                    .contains(point)
                ? 1
                : 0,
            rolledBack.get(),
            point);
        assertEquals(point.equals("close") ? 1 : 0, count(), point);
      }
    }
    assertThrows(
        NullPointerException.class,
        () -> new WebLogIngestService(source(() -> null)).ingest(event(golden())));
  }

  @Test
  void databaseCommitSurvivesAckFailureAndBrokerCacheMiss(@TempDir Path brokerRoot)
      throws Exception {
    Configuration configuration;
    try (var input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(input);
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
    var queue = new ActiveMQQueue("nk.web.log::nk.web.log.q");
    var clock = Clock.fixed(Instant.parse("2026-09-07T00:00:00Z"), ZoneOffset.UTC);
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var consumerContext = factory.createContext(JMSContext.SESSION_TRANSACTED);
        var consumer = consumerContext.createConsumer(queue)) {
      var service = new WebLogIngestService(source(database::api));
      var listener = new WebLogListener(service, clock);
      var ackFailure =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (proxy, method, arguments) -> {
                    if (method.getName().equals("commit")) {
                      assertEquals(
                          1,
                          count(),
                          "DB commit must be visible on an independent connection before ACK");
                      throw new JMSRuntimeException("synthetic ACK failure");
                    }
                    return invoke(consumerContext, method, arguments);
                  });
      // No _AMQ_DUPL_ID: final DB UK must work even when broker duplicate cache has no entry.
      send(producer, queue);
      var first = consumer.receive(5000);
      assertNotNull(first);
      assertThrows(JMSRuntimeException.class, () -> listener.onMessage(ackFailure, first));
      assertEquals(1, count());
      var redelivered = consumer.receive(5000);
      assertNotNull(redelivered);
      assertEquals(2, redelivered.getIntProperty("JMSXDeliveryCount"));
      listener.onMessage(consumerContext, redelivered);
      assertEquals(1, count());
      send(producer, queue);
      var duplicate = consumer.receive(5000);
      assertNotNull(duplicate);
      assertEquals(1, duplicate.getIntProperty("JMSXDeliveryCount"));
      listener.onMessage(consumerContext, duplicate);
      assertEquals(1, count());
      assertNull(consumer.receive(250));

      database.reset();
      var unavailable =
          new WebLogListener(
              new WebLogIngestService(
                  source(
                      () -> {
                        throw new SQLException("synthetic DB outage");
                      })),
              clock);
      send(producer, queue);
      var beforeDb = consumer.receive(5000);
      assertNotNull(beforeDb);
      assertThrows(
          LogProjectionDatabaseException.class,
          () -> unavailable.onMessage(consumerContext, beforeDb));
      assertEquals(0, count());
      var retry = consumer.receive(5000);
      assertNotNull(retry);
      assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
      listener.onMessage(consumerContext, retry);
      assertEquals(1, count());
      assertNull(consumer.receive(250));
    } finally {
      broker.stop();
    }
  }

  private static void send(JMSContext context, ActiveMQQueue queue)
      throws jakarta.jms.JMSException {
    var message = context.createBytesMessage();
    message.writeBytes(golden());
    message.setStringProperty("NKMessageID", FIXTURE_00000000_0000_0000_0000_000000000012_7E8766AA);
    message.setStringProperty("NKLayoutID", "WLGEVT01");
    message.setStringProperty("NKProtocolVersion", "001");
    message.setJMSCorrelationID("00000000-0000-0000-0000-000000000015");
    context
        .createProducer()
        .setDeliveryMode(jakarta.jms.DeliveryMode.PERSISTENT)
        .setTimeToLive(0)
        .send(queue, message);
  }

  static int count() throws SQLException {
    try (var connection = database.api();
        var statement = connection.createStatement();
        var rows = statement.executeQuery("select count(*) from schubert.app_logs")) {
      assertTrue(rows.next());
      return rows.getInt(1);
    }
  }

  static WireMessage<FixedPayload> event(byte[] wire) {
    return new WireMessage<>(
        new HeaderCodec(LayoutRegistry.standard()).peek(wire),
        new FixedPayload(Arrays.copyOfRange(wire, 256, wire.length), 0, List.of()));
  }

  static byte[] golden() {
    byte[] wire = new byte[2336];
    Arrays.fill(wire, (byte) ' ');
    ascii(wire, 0, "SCHBNK01001WLGEVT01001EI");
    ascii(wire, 24, FIXTURE_00000000_0000_0000_0000_000000000012_7E8766AA);
    ascii(wire, 60, "00000000-0000-0000-0000-000000000015");
    ascii(wire, 96, "20260905060000000");
    ascii(wire, 177, "0256002080000000000000000002336");
    field(wire, 0, 17, "20260905060000000");
    field(wire, 17, 16, "REQUEST");
    field(wire, 33, 8, "INFO");
    field(wire, 41, 64, "HTTP_REQUEST_COMPLETED");
    field(wire, 105, 512, "Synthetic request complete");
    field(wire, 617, 36, "00000000-0000-0000-0000-000000000099");
    field(wire, 653, 8, "GET");
    field(wire, 661, 256, "/login");
    field(wire, 917, 3, "200");
    field(wire, 920, 9, "12");
    field(wire, 929, 45, "127.0.0.1");
    field(wire, 974, 64, "synthetic-user");
    field(wire, 1038, 5, "USER");
    field(
        wire,
        1043,
        1024,
        "{\"responseBytes\":42,\"truncated\":false,\"projectionStatus\":\"PENDING\"}");
    return wire;
  }

  static void field(byte[] wire, int offset, int length, String text) {
    Arrays.fill(wire, 256 + offset, 256 + offset + length, (byte) ' ');
    ascii(wire, 256 + offset, text);
  }

  static void ascii(byte[] wire, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(bytes, 0, wire, offset, bytes.length);
  }

  static Object invoke(Object target, java.lang.reflect.Method method, Object[] arguments)
      throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  static DataSource source(ConnectionFactory factory) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals(FIXTURE_GETCONNECTION_1DAA73DB)) {
                return factory.open();
              }
              throw new UnsupportedOperationException(method.getName());
            });
  }

  @FunctionalInterface
  interface ConnectionFactory {
    Connection open() throws SQLException;
  }

  private record Mutation(int offset, int length, String text) {}
}
