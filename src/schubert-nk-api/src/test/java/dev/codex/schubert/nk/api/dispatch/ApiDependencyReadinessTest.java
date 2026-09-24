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
              throw new JMSRuntimeException("private-mq-password");
            },
            () -> context(false, 0, false, closes),
            () -> context(true, 1, false, closes),
            () -> context(true, 2, false, closes),
            () -> context(true, 0, true, closes))) {
      var failure =
          assertThrows(
              IllegalStateException.class, () -> new ApiDependencyReadiness(db, broker).verify());
      assertEquals("API Artemis receive queues unavailable", failure.getMessage());
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
          "API Artemis receive queues unavailable",
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
              if (method.getName().equals("getSessionMode")) throw inspection;
              if (method.getName().equals("close")) {
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
              if (method.getName().equals("getSessionMode")) throw inspection;
              if (method.getName().equals("close")) {
                closed.incrementAndGet();
                throw closeFailure;
              }
              throw new AssertionError(method.getName());
            });
    var observed =
        assertThrows(
            IllegalStateException.class,
            () -> new ApiDependencyReadiness(database, () -> context).verify());
    assertEquals("API Artemis receive queues unavailable", observed.getMessage());
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
              if (method.getName().equals("getSessionMode")) throw inspection;
              if (method.getName().equals("close")) {
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
                      if (method.getName().equals("close")) {
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
              case "close" -> {
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
              case "getSessionMode" ->
                  transacted ? JMSContext.SESSION_TRANSACTED : JMSContext.AUTO_ACKNOWLEDGE;
              case "createConsumer" -> {
                int index = attaches.incrementAndGet();
                assertEquals(
                    index == 1 ? "nk.sync.request::nk.sync.request.q" : "nk.web.log::nk.web.log.q",
                    ((jakarta.jms.Queue) arguments[0]).getQueueName());
                if (index == attachFailure) throw new JMSRuntimeException("private-mq-password");
                yield proxy(
                    JMSConsumer.class,
                    (consumer, called, args) -> {
                      if (called.getName().equals("close")) return null;
                      throw new AssertionError(called.getName());
                    });
              }
              case "close" -> {
                closes.incrementAndGet();
                if (closeFails) throw new JMSRuntimeException("private-mq-password");
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
