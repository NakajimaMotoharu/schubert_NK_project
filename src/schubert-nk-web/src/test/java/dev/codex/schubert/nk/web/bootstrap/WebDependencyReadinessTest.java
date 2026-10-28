package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Queue;
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

/** PG221/PT-SCR113..116. No deployed DB/broker or credentials are used. */
final class WebDependencyReadinessTest {
  private static final String FIXTURE_PRIVATE_DB_PASSWORD_AD3D4CC0 = "private-db-password";
  private static final String FIXTURE_WEB_ARTEMIS_REPLY_QUEUE_IS_UNAVAILABLE_B15CBB0F =
      "Web Artemis reply Queue is unavailable";
  private static final String FIXTURE_PRIVATE_MQ_PASSWORD_36C97947 = "private-mq-password";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  @TempDir Path root;

  @Test
  void scr113RealPostgresAndApprovedBrokerQueue() throws Exception {
    var pgRoot = Files.createDirectory(root.resolve("pg"));
    var fixture = new WebLogDatabaseFixture(pgRoot);
    var broker = start(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0")) {
      DataSource database = source(fixture::web);
      assertDoesNotThrow(
          () ->
              new WebDependencyReadiness(
                      database, () -> factory.createContext(JMSContext.SESSION_TRANSACTED))
                  .verify());
    } finally {
      broker.stop();
      fixture.stop();
    }
  }

  @Test
  void scr114NullAndInvalidDatabaseStopBeforeJms() throws Exception {
    var connection = connection(false, false, false, new AtomicInteger());
    var brokerCalls = new AtomicInteger();
    assertThrows(NullPointerException.class, () -> new WebDependencyReadiness(null, () -> null));
    assertThrows(
        NullPointerException.class, () -> new WebDependencyReadiness(source(() -> null), null));
    var missing =
        new WebDependencyReadiness(
            source(() -> null),
            () -> {
              brokerCalls.incrementAndGet();
              return null;
            });
    assertEquals(
        "Web technical database is unavailable",
        assertThrows(WebStartupException.class, missing::verify).getMessage());
    var invalid =
        new WebDependencyReadiness(
            source(() -> connection),
            () -> {
              brokerCalls.incrementAndGet();
              return null;
            });
    assertThrows(WebStartupException.class, invalid::verify);
    assertEquals(0, brokerCalls.get());
  }

  @Test
  void scr115ProviderFailuresAreRedactedAndBorrowedResourcesClose() throws Exception {
    var closes = new AtomicInteger();
    for (var database :
        new DataSource[] {
          source(
              () -> {
                throw new SQLException(FIXTURE_PRIVATE_DB_PASSWORD_AD3D4CC0);
              }),
          source(() -> connection(true, true, false, closes)),
          source(() -> connection(true, false, true, closes))
        }) {
      var failure =
          assertThrows(
              WebStartupException.class,
              () -> new WebDependencyReadiness(database, () -> null).verify());
      assertEquals("Web technical database is unavailable", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertEquals(2, closes.get());

    var db = source(() -> connection(true, false, false, closes));
    var noContext =
        assertThrows(
            WebStartupException.class, () -> new WebDependencyReadiness(db, () -> null).verify());
    assertEquals(FIXTURE_WEB_ARTEMIS_REPLY_QUEUE_IS_UNAVAILABLE_B15CBB0F, noContext.getMessage());
    var provider =
        assertThrows(
            WebStartupException.class,
            () ->
                new WebDependencyReadiness(
                        db,
                        () -> {
                          throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
                        })
                    .verify());
    assertNull(provider.getCause());
    var brokerCloses = new AtomicInteger();
    var attach =
        assertThrows(
            WebStartupException.class,
            () ->
                new WebDependencyReadiness(db, () -> context(true, false, brokerCloses)).verify());
    assertEquals(FIXTURE_WEB_ARTEMIS_REPLY_QUEUE_IS_UNAVAILABLE_B15CBB0F, attach.getMessage());
    var close =
        assertThrows(
            WebStartupException.class,
            () ->
                new WebDependencyReadiness(db, () -> context(false, true, brokerCloses)).verify());
    assertEquals(FIXTURE_WEB_ARTEMIS_REPLY_QUEUE_IS_UNAVAILABLE_B15CBB0F, close.getMessage());
    assertEquals(2, brokerCloses.get());
  }

  @Test
  void scr116UnavailableBrokerCannotBecomeReady() throws Exception {
    var broker = start(Files.createDirectory(root.resolve("broker-stopped")));
    broker.stop();
    try (var factory = new ActiveMQConnectionFactory("vm://0")) {
      var db = source(() -> connection(true, false, false, new AtomicInteger()));
      var failure =
          assertThrows(
              WebStartupException.class,
              () ->
                  new WebDependencyReadiness(
                          db, () -> factory.createContext(JMSContext.SESSION_TRANSACTED))
                      .verify());
      assertEquals(FIXTURE_WEB_ARTEMIS_REPLY_QUEUE_IS_UNAVAILABLE_B15CBB0F, failure.getMessage());
    }
  }

  @Test
  void scr136FatalDatabaseCloseCannotBeDowngraded() {
    var closes = new AtomicInteger();
    var brokerCalls = new AtomicInteger();
    var fatal = new AssertionError("fatal-db-close-marker");
    Connection connection =
        proxy(
            Connection.class,
            (instance, method, args) -> {
              switch (method.getName()) {
                case "isValid" -> throw new SQLException(FIXTURE_PRIVATE_DB_PASSWORD_AD3D4CC0);
                case FIXTURE_CLOSE_97959247 -> {
                  closes.incrementAndGet();
                  throw fatal;
                }
                default -> throw new AssertionError("unexpected JDBC call " + method.getName());
              }
            });
    var readiness =
        new WebDependencyReadiness(
            source(() -> connection),
            () -> {
              brokerCalls.incrementAndGet();
              throw new AssertionError("broker must not be acquired");
            });
    assertSame(fatal, assertThrows(AssertionError.class, readiness::verify));
    assertEquals(1, closes.get());
    assertEquals(0, brokerCalls.get());

    var ordinaryCloses = new AtomicInteger();
    var ordinary =
        new WebDependencyReadiness(
            source(
                () ->
                    compoundConnection(
                        new SQLException("synthetic inspection"),
                        new SQLException("synthetic close"),
                        ordinaryCloses)),
            () -> {
              brokerCalls.incrementAndGet();
              throw new AssertionError("broker must not be acquired");
            });
    var fixed = assertThrows(WebStartupException.class, ordinary::verify);
    assertEquals("Web technical database is unavailable", fixed.getMessage());
    assertNull(fixed.getCause());
    assertEquals(1, ordinaryCloses.get());
    assertEquals(0, brokerCalls.get());

    var primaryFatal = new AssertionError("fatal-db-inspection-marker");
    var fatalCloses = new AtomicInteger();
    var bothFatal =
        new WebDependencyReadiness(
            source(() -> compoundConnection(primaryFatal, fatal, fatalCloses)),
            () -> {
              brokerCalls.incrementAndGet();
              throw new AssertionError("broker must not be acquired");
            });
    assertSame(primaryFatal, assertThrows(AssertionError.class, bothFatal::verify));
    assertEquals(1, fatalCloses.get());
    assertEquals(0, brokerCalls.get());
  }

  @Test
  void scr137FatalBrokerCloseCannotBeDowngraded() {
    var dbCloses = new AtomicInteger();
    var brokerCloses = new AtomicInteger();
    var fatal = new AssertionError("fatal-broker-close-marker");
    JMSContext context =
        proxy(
            JMSContext.class,
            (instance, method, args) ->
                switch (method.getName()) {
                  case "createQueue" ->
                      proxy(
                          Queue.class,
                          (queue, called, parameters) -> {
                            if (called.getName().equals("getQueueName"))
                              return "nk.sync.reply.web.q";
                            throw new AssertionError("unexpected Queue call " + called.getName());
                          });
                  case "createConsumer" ->
                      throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
                  case FIXTURE_CLOSE_97959247 -> {
                    brokerCloses.incrementAndGet();
                    throw fatal;
                  }
                  default -> throw new AssertionError("unexpected JMS call " + method.getName());
                });
    var readiness =
        new WebDependencyReadiness(
            source(() -> connection(true, false, false, dbCloses)), () -> context);
    assertSame(fatal, assertThrows(AssertionError.class, readiness::verify));
    assertEquals(1, dbCloses.get());
    assertEquals(1, brokerCloses.get());

    var ordinaryCloses = new AtomicInteger();
    var ordinary =
        new WebDependencyReadiness(
            source(() -> connection(true, false, false, dbCloses)),
            () ->
                compoundContext(
                    new JMSRuntimeException("synthetic inspection"),
                    new JMSRuntimeException("synthetic close"),
                    ordinaryCloses));
    var fixed = assertThrows(WebStartupException.class, ordinary::verify);
    assertEquals(FIXTURE_WEB_ARTEMIS_REPLY_QUEUE_IS_UNAVAILABLE_B15CBB0F, fixed.getMessage());
    assertNull(fixed.getCause());
    assertEquals(1, ordinaryCloses.get());

    var primaryFatal = new AssertionError("fatal-broker-inspection-marker");
    var fatalCloses = new AtomicInteger();
    var bothFatal =
        new WebDependencyReadiness(
            source(() -> connection(true, false, false, dbCloses)),
            () -> compoundContext(primaryFatal, fatal, fatalCloses));
    assertSame(primaryFatal, assertThrows(AssertionError.class, bothFatal::verify));
    assertEquals(1, fatalCloses.get());
    assertEquals(3, dbCloses.get());
  }

  private static Connection compoundConnection(
      Throwable inspection, Throwable closing, AtomicInteger closes) {
    return proxy(
        Connection.class,
        (instance, method, args) -> {
          switch (method.getName()) {
            case "isValid" -> throw inspection;
            case FIXTURE_CLOSE_97959247 -> {
              closes.incrementAndGet();
              throw closing;
            }
            default -> throw new AssertionError("unexpected JDBC call " + method.getName());
          }
        });
  }

  private static JMSContext compoundContext(
      Throwable inspection, Throwable closing, AtomicInteger closes) {
    return proxy(
        JMSContext.class,
        (instance, method, args) -> {
          switch (method.getName()) {
            case "createQueue" -> {
              return proxy(
                  Queue.class,
                  (queue, called, parameters) -> {
                    if (called.getName().equals("getQueueName")) return "nk.sync.reply.web.q";
                    throw new AssertionError("unexpected Queue call " + called.getName());
                  });
            }
            case "createConsumer" -> throw inspection;
            case FIXTURE_CLOSE_97959247 -> {
              closes.incrementAndGet();
              throw closing;
            }
            default -> throw new AssertionError("unexpected JMS call " + method.getName());
          }
        });
  }

  private static Connection connection(
      boolean valid, boolean inspectionFails, boolean closeFails, AtomicInteger closes) {
    return proxy(
        Connection.class,
        (instance, method, args) ->
            switch (method.getName()) {
              case "isValid" -> {
                assertEquals(2, args[0]);
                if (inspectionFails) throw new SQLException(FIXTURE_PRIVATE_DB_PASSWORD_AD3D4CC0);
                yield valid;
              }
              case FIXTURE_CLOSE_97959247 -> {
                closes.incrementAndGet();
                if (closeFails) throw new SQLException(FIXTURE_PRIVATE_DB_PASSWORD_AD3D4CC0);
                yield null;
              }
              default -> throw new AssertionError("unexpected JDBC call " + method.getName());
            });
  }

  private static DataSource source(SqlOpen open) {
    return proxy(
        DataSource.class,
        (instance, method, args) -> {
          if (method.getName().equals("getConnection")) return open.get();
          throw new AssertionError("unexpected DataSource call " + method.getName());
        });
  }

  private static JMSContext context(boolean attachFails, boolean closeFails, AtomicInteger closes) {
    return proxy(
        JMSContext.class,
        (instance, method, args) ->
            switch (method.getName()) {
              case "createQueue" -> {
                assertEquals("nk.sync.reply.web::nk.sync.reply.web.q", args[0]);
                yield proxy(
                    Queue.class,
                    (queue, called, parameters) -> {
                      if (called.getName().equals("getQueueName")) return "nk.sync.reply.web.q";
                      throw new AssertionError("unexpected Queue call " + called.getName());
                    });
              }
              case "createConsumer" -> {
                if (attachFails)
                  throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
                yield proxy(
                    JMSConsumer.class,
                    (consumer, called, parameters) -> {
                      if (called.getName().equals(FIXTURE_CLOSE_97959247)) return null;
                      throw new AssertionError("unexpected consumer call " + called.getName());
                    });
              }
              case FIXTURE_CLOSE_97959247 -> {
                closes.incrementAndGet();
                if (closeFails) throw new JMSRuntimeException(FIXTURE_PRIVATE_MQ_PASSWORD_36C97947);
                yield null;
              }
              default -> throw new AssertionError("unexpected JMS call " + method.getName());
            });
  }

  @SuppressWarnings("unchecked")
  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return (T) Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler);
  }

  private static EmbeddedActiveMQ start(Path root) throws Exception {
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
