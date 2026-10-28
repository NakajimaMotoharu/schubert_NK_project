package dev.codex.schubert.nk.api.dispatch;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import java.io.InputStream;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG234/266/PT-JMS-019/022: borrowed API DB/JMS admission, not broker management readiness. */
final class ApiDependencyReadinessTest {
  private static final String FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85 =
      "nk.sync.request::nk.sync.request.q";
  private static final String FIXTURE_NK_WEB_LOG_NK_WEB_LOG_Q_BD49E4FA = "nk.web.log::nk.web.log.q";
  private static final String FIXTURE_API_ARTEMIS_RECEIVE_QUEUES_UNAVAILABLE_949A1CD8 =
      "API Artemis receive queues unavailable";
  private static final String FIXTURE_PRIVATE_MQ_PASSWORD_36C97947 = "private-mq-password";
  private static final String FIXTURE_GETSESSIONMODE_BF25AD1A = "getSessionMode";
  private static final String FIXTURE_CLOSE_97959247 = "close";

  @Test
  void thirdProfileProbesOnlyFixedAsyncQueueAndEveryNullPortIsRejected() {
    var closes = new AtomicInteger();
    var attaches = new AtomicInteger();
    var db = source(() -> connection(true, false, false, new AtomicInteger()));
    java.util.function.Supplier<JMSContext> sync =
        () ->
            singleQueueContext(
                FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85,
                false,
                new AtomicInteger(),
                new AtomicInteger());
    java.util.function.Supplier<JMSContext> log =
        () ->
            singleQueueContext(
                FIXTURE_NK_WEB_LOG_NK_WEB_LOG_Q_BD49E4FA,
                false,
                new AtomicInteger(),
                new AtomicInteger());
    java.util.function.Supplier<JMSContext> async =
        () -> singleQueueContext("nk.async.work::nk.async.work.q", false, attaches, closes);
    new ApiDependencyReadiness(db, sync, log, async).verify();
    assertEquals(1, attaches.get());
    assertEquals(1, closes.get());
    assertThrows(
        NullPointerException.class, () -> new ApiDependencyReadiness(null, sync, log, async));
    assertThrows(
        NullPointerException.class, () -> new ApiDependencyReadiness(db, null, log, async));
    assertThrows(
        NullPointerException.class, () -> new ApiDependencyReadiness(db, sync, null, async));
    assertThrows(NullPointerException.class, () -> new ApiDependencyReadiness(db, sync, log, null));
    var rejected =
        new ApiDependencyReadiness(
            db,
            sync,
            log,
            () -> singleQueueContext("nk.async.work::nk.async.work.q", true, attaches, closes));
    assertThrows(IllegalStateException.class, rejected::verify);
    assertEquals(2, attaches.get());
    assertEquals(2, closes.get());
  }

  @TempDir Path root;

  @Test
  void realPostgresAndBothReceiveQueuesCloseAfterProbe() throws Exception {
    var fixture = new ApiLogDatabaseFixture(Files.createDirectory(root.resolve("postgres")));
    EmbeddedActiveMQ broker = startBroker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0")) {
      assertDoesNotThrow(
          () ->
              new ApiDependencyReadiness(
                      source(fixture::api),
                      () -> factory.createContext(JMSContext.SESSION_TRANSACTED))
                  .verify());
      assertDoesNotThrow(
          () ->
              new ApiDependencyReadiness(
                      source(fixture::api),
                      () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                      () -> factory.createContext(JMSContext.SESSION_TRANSACTED))
                  .verify());
      assertEquals(
          0,
          broker
              .getActiveMQServer()
              .locateQueue(
                  org.apache.activemq.artemis.api.core.SimpleString.of("nk.sync.request.q"))
              .getConsumerCount());
      assertEquals(
          0,
          broker
              .getActiveMQServer()
              .locateQueue(org.apache.activemq.artemis.api.core.SimpleString.of("nk.web.log.q"))
              .getConsumerCount());
    } finally {
      broker.stop();
      fixture.stop();
    }
  }

  @Test
  void separateProfilesProbeOnlyTheirOwnQueuesAndCloseBothContexts() {
    var syncCloses = new AtomicInteger();
    var logCloses = new AtomicInteger();
    var syncAttaches = new AtomicInteger();
    var logAttaches = new AtomicInteger();
    var db = source(() -> connection(true, false, false, new AtomicInteger()));
    var admission =
        new ApiDependencyReadiness(
            db,
            () ->
                singleQueueContext(
                    FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85,
                    false,
                    syncAttaches,
                    syncCloses),
            () ->
                singleQueueContext(
                    FIXTURE_NK_WEB_LOG_NK_WEB_LOG_Q_BD49E4FA, false, logAttaches, logCloses));
    assertDoesNotThrow(admission::verify);
    assertEquals(1, syncAttaches.get());
    assertEquals(1, logAttaches.get());
    assertEquals(1, syncCloses.get());
    assertEquals(1, logCloses.get());
  }

  @Test
  void separateWebLogAttachFailureLeavesNoContextAndIsRedacted() {
    var syncCloses = new AtomicInteger();
    var logCloses = new AtomicInteger();
    var syncAttaches = new AtomicInteger();
    var logAttaches = new AtomicInteger();
    var db = source(() -> connection(true, false, false, new AtomicInteger()));
    var admission =
        new ApiDependencyReadiness(
            db,
            () ->
                singleQueueContext(
                    FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85,
                    false,
                    syncAttaches,
                    syncCloses),
            () ->
                singleQueueContext(
                    FIXTURE_NK_WEB_LOG_NK_WEB_LOG_Q_BD49E4FA, true, logAttaches, logCloses));
    var failure = assertThrows(IllegalStateException.class, admission::verify);
    assertEquals(FIXTURE_API_ARTEMIS_RECEIVE_QUEUES_UNAVAILABLE_949A1CD8, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(1, syncAttaches.get());
    assertEquals(1, logAttaches.get());
    assertEquals(1, syncCloses.get());
    assertEquals(1, logCloses.get());
  }

  @Test
  void nullAndInvalidDatabaseFailBeforeBroker() {
    var brokerCalls = new AtomicInteger();
    java.util.function.Supplier<JMSContext> broker =
        () -> {
          brokerCalls.incrementAndGet();
          return null;
        };
    assertThrows(NullPointerException.class, () -> new ApiDependencyReadiness(null, broker));
    assertThrows(
        NullPointerException.class, () -> new ApiDependencyReadiness(source(() -> null), null));
    for (DataSource source :
        new DataSource[] {
          source(() -> null),
          source(() -> connection(false, false, false, new AtomicInteger())),
          source(
              () -> {
                throw new SQLException("private-db-password");
              })
        }) {
      var failure =
          assertThrows(
              IllegalStateException.class,
              () -> new ApiDependencyReadiness(source, broker).verify());
      assertEquals("API database unavailable", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertEquals(0, brokerCalls.get());
  }

  @Test
  void jdbcInspectionAndCloseFailuresAreRedacted() {
    var closes = new AtomicInteger();
    for (DataSource source :
        new DataSource[] {
          source(() -> connection(true, true, false, closes)),
          source(() -> connection(true, false, true, closes))
        }) {
      var failure =
          assertThrows(
              IllegalStateException.class,
              () -> new ApiDependencyReadiness(source, () -> null).verify());
      assertEquals("API database unavailable", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertEquals(2, closes.get());
  }

  @Test
  void brokerNullModeAttachAndCloseFailuresAreRedacted() {
    var db = source(() -> connection(true, false, false, new AtomicInteger()));
    var closes = new AtomicInteger();
    for (java.util.function.Supplier<JMSContext> broker :
        java.util.List.of(
            (java.util.function.Supplier<JMSContext>) () -> null,
            () -> {
              throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
            },
            () -> context(false, 0, false, closes),
            () -> context(true, 1, false, closes),
            () -> context(true, 2, false, closes),
            () -> context(true, 0, true, closes))) {
      var failure =
          assertThrows(
              IllegalStateException.class, () -> new ApiDependencyReadiness(db, broker).verify());
      assertEquals(FIXTURE_API_ARTEMIS_RECEIVE_QUEUES_UNAVAILABLE_949A1CD8, failure.getMessage());
      assertNull(failure.getCause());
    }
    assertEquals(4, closes.get());
  }

  @Test
  void stoppedBrokerCannotPassConnectivity() throws Exception {
    var broker = startBroker(Files.createDirectory(root.resolve("stopped")));
    broker.stop();
    try (var factory = new ActiveMQConnectionFactory("vm://0")) {
      var db = source(() -> connection(true, false, false, new AtomicInteger()));
      assertEquals(
          FIXTURE_API_ARTEMIS_RECEIVE_QUEUES_UNAVAILABLE_949A1CD8,
          assertThrows(
                  IllegalStateException.class,
                  () ->
                      new ApiDependencyReadiness(
                              db, () -> factory.createContext(JMSContext.SESSION_TRANSACTED))
                          .verify())
              .getMessage());
    }
  }

  @Test
  void apiReadinessFatalBrokerCloseCannotBeDowngradedToOrdinaryUnavailable() {
    RuntimeException inspection = new JMSRuntimeException("synthetic inspection failure");
    AssertionError fatal = new AssertionError("synthetic owned context close failure");
    var closed = new AtomicInteger();
    var database = source(() -> connection(true, false, false, new AtomicInteger()));
    JMSContext context =
        proxy(
            JMSContext.class,
            (ignored, method, args) -> {
              if (method.getName().equals(FIXTURE_GETSESSIONMODE_BF25AD1A)) throw inspection;
              if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                closed.incrementAndGet();
                throw fatal;
              }
              throw new AssertionError(method.getName());
            });
    AssertionError observed =
        assertThrows(
            AssertionError.class,
            () -> new ApiDependencyReadiness(database, () -> context).verify());
    assertSame(fatal, observed);
    assertEquals(1, closed.get());
  }

  @Test
  void apiReadinessOrdinaryInspectionAndCloseFailuresRemainRedacted() {
    RuntimeException inspection = new JMSRuntimeException("synthetic inspection failure");
    RuntimeException closeFailure = new JMSRuntimeException("synthetic close failure");
    var closed = new AtomicInteger();
    var database = source(() -> connection(true, false, false, new AtomicInteger()));
    JMSContext context =
        proxy(
            JMSContext.class,
            (ignored, method, args) -> {
              if (method.getName().equals(FIXTURE_GETSESSIONMODE_BF25AD1A)) throw inspection;
              if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                closed.incrementAndGet();
                throw closeFailure;
              }
              throw new AssertionError(method.getName());
            });
    var observed =
        assertThrows(
            IllegalStateException.class,
            () -> new ApiDependencyReadiness(database, () -> context).verify());
    assertEquals(FIXTURE_API_ARTEMIS_RECEIVE_QUEUES_UNAVAILABLE_949A1CD8, observed.getMessage());
    assertNull(observed.getCause());
    assertEquals(1, closed.get());
  }

  @Test
  void apiReadinessFatalInspectionRetainsIdentityEvenWhenCloseAlsoFatal() {
    AssertionError inspection = new AssertionError("synthetic inspection failure");
    AssertionError closeFailure = new AssertionError("synthetic close failure");
    var closed = new AtomicInteger();
    var database = source(() -> connection(true, false, false, new AtomicInteger()));
    JMSContext context =
        proxy(
            JMSContext.class,
            (ignored, method, args) -> {
              if (method.getName().equals(FIXTURE_GETSESSIONMODE_BF25AD1A)) throw inspection;
              if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                closed.incrementAndGet();
                throw closeFailure;
              }
              throw new AssertionError(method.getName());
            });
    AssertionError observed =
        assertThrows(
            AssertionError.class,
            () -> new ApiDependencyReadiness(database, () -> context).verify());
    assertSame(inspection, observed);
    assertEquals(1, closed.get());
  }

  @Test
  void apiReadinessFatalDatabaseCloseCannotBeDowngradedToOrdinaryUnavailable() {
    SQLException inspection = new SQLException("synthetic private database failure");
    AssertionError fatal = new AssertionError("synthetic owned database close failure");
    var closed = new AtomicInteger();
    var brokerCalls = new AtomicInteger();
    var database =
        source(
            () ->
                proxy(
                    Connection.class,
                    (ignored, method, args) -> {
                      if (method.getName().equals("isValid")) throw inspection;
                      if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                        closed.incrementAndGet();
                        throw fatal;
                      }
                      throw new AssertionError(method.getName());
                    }));
    AssertionError observed =
        assertThrows(
            AssertionError.class,
            () ->
                new ApiDependencyReadiness(
                        database,
                        () -> {
                          brokerCalls.incrementAndGet();
                          return null;
                        })
                    .verify());
    assertSame(fatal, observed);
    assertEquals(1, closed.get());
    assertEquals(0, brokerCalls.get());
  }

  @Test
  void apiReadinessOrdinaryDatabaseInspectionAndCloseFailuresRemainRedacted() {
    SQLException inspection = new SQLException("synthetic private database failure");
    SQLException closeFailure = new SQLException("synthetic private close failure");
    var closed = new AtomicInteger();
    var database = source(() -> failingDatabase(inspection, closeFailure, closed));
    var observed =
        assertThrows(
            IllegalStateException.class,
            () -> new ApiDependencyReadiness(database, () -> null).verify());
    assertEquals("API database unavailable", observed.getMessage());
    assertNull(observed.getCause());
    assertEquals(1, closed.get());
  }

  @Test
  void apiReadinessFatalDatabaseInspectionRetainsIdentityEvenWhenCloseAlsoFatal() {
    AssertionError inspection = new AssertionError("synthetic database inspection failure");
    AssertionError closeFailure = new AssertionError("synthetic database close failure");
    var closed = new AtomicInteger();
    var database = source(() -> failingDatabase(inspection, closeFailure, closed));
    AssertionError observed =
        assertThrows(
            AssertionError.class, () -> new ApiDependencyReadiness(database, () -> null).verify());
    assertSame(inspection, observed);
    assertEquals(1, closed.get());
  }

  private static Connection failingDatabase(
      Throwable inspection, Throwable closeFailure, AtomicInteger closed) {
    return proxy(
        Connection.class,
        (ignored, method, args) -> {
          if (method.getName().equals("isValid")) throw inspection;
          if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
            closed.incrementAndGet();
            throw closeFailure;
          }
          throw new AssertionError(method.getName());
        });
  }

  private static Connection connection(
      boolean valid, boolean inspectFails, boolean closeFails, AtomicInteger closes) {
    return proxy(
        Connection.class,
        (ignored, method, arguments) ->
            switch (method.getName()) {
              case "isValid" -> {
                assertEquals(2, arguments[0]);
                if (inspectFails) throw new SQLException("private-db-password");
                yield valid;
              }
              case FIXTURE_CLOSE_97959247 -> {
                closes.incrementAndGet();
                if (closeFails) throw new SQLException("private-db-password");
                yield null;
              }
              default -> throw new AssertionError(method.getName());
            });
  }

  private static JMSContext context(
      boolean transacted, int attachFailure, boolean closeFails, AtomicInteger closes) {
    var attaches = new AtomicInteger();
    return proxy(
        JMSContext.class,
        (ignored, method, arguments) ->
            switch (method.getName()) {
              case FIXTURE_GETSESSIONMODE_BF25AD1A ->
                  transacted ? JMSContext.SESSION_TRANSACTED : JMSContext.AUTO_ACKNOWLEDGE;
              case "createConsumer" -> {
                int index = attaches.incrementAndGet();
                assertEquals(
                    index == 1
                        ? FIXTURE_NK_SYNC_REQUEST_NK_SYNC_REQUEST_Q_D0778F85
                        : FIXTURE_NK_WEB_LOG_NK_WEB_LOG_Q_BD49E4FA,
                    ((jakarta.jms.Queue) arguments[0]).getQueueName());
                if (index == attachFailure)
                  throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
                yield proxy(
                    JMSConsumer.class,
                    (consumer, called, args) -> {
                      if (called.getName().equals(FIXTURE_CLOSE_97959247)) return null;
                      throw new AssertionError(called.getName());
                    });
              }
              case FIXTURE_CLOSE_97959247 -> {
                closes.incrementAndGet();
                if (closeFails) throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
                yield null;
              }
              default -> throw new AssertionError(method.getName());
            });
  }

  private static JMSContext singleQueueContext(
      String expected, boolean attachFails, AtomicInteger attaches, AtomicInteger closes) {
    return proxy(
        JMSContext.class,
        (ignored, method, arguments) ->
            switch (method.getName()) {
              case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
              case "createConsumer" -> {
                assertEquals(expected, ((jakarta.jms.Queue) arguments[0]).getQueueName());
                attaches.incrementAndGet();
                if (attachFails)
                  throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
                yield proxy(
                    JMSConsumer.class,
                    (consumer, called, args) -> {
                      if (called.getName().equals(FIXTURE_CLOSE_97959247)) return null;
                      throw new AssertionError(called.getName());
                    });
              }
              case FIXTURE_CLOSE_97959247 -> {
                closes.incrementAndGet();
                yield null;
              }
              default -> throw new AssertionError(method.getName());
            });
  }

  private static DataSource source(SqlOpen open) {
    return proxy(
        DataSource.class,
        (ignored, method, arguments) -> {
          if (method.getName().equals("getConnection")) return open.get();
          throw new AssertionError(method.getName());
        });
  }

  @SuppressWarnings("unchecked")
  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return (T) Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler);
  }

  private static EmbeddedActiveMQ startBroker(Path root) throws Exception {
    Configuration config;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      config = new FileConfigurationParser().parseMainConfig(input);
    }
    config
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large-messages").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(config).start();
  }

  @FunctionalInterface
  private interface SqlOpen {
    Connection get() throws SQLException;
  }
}
