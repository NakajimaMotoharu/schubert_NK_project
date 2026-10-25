package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Queue;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** SS312/342/354; SSC330/BUG1593/YKT1346; PT-WEB-READY-GRAPH330001..003; no I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class WebReadinessFailureGraph330Test {
  @Test
  void ready330001DbGraphsPreserveFatalAfterOneCloseAndNeverOpenJms() {
    for (boolean closeOnly : new boolean[] {false, true}) {
      var fixture = new Fixture();
      var fatal = new AssertionError("PUBLIC fatal");
      var primary = new SQLException("PUBLIC database");
      if (!closeOnly) primary.initCause(fatal);
      fixture.databaseFailure = primary;
      if (closeOnly) fixture.databaseClosing = new IllegalStateException("PUBLIC close", fatal);
      assertSame(fatal, assertThrows(AssertionError.class, fixture::verify));
      fixture.assertCounts(true, 0);
    }
  }

  @Test
  void ready330002JmsLinkedAndBothCloseGraphsPreserveFatalAfterCleanup() {
    for (int mode = 0; mode < 3; mode++) {
      var fixture = new Fixture();
      var fatal = new AssertionError("PUBLIC fatal");
      if (mode == 0) {
        var linked = new SQLException("PUBLIC linked");
        linked.setNextException(new SQLException("PUBLIC next", fatal));
        var jms = new JMSException("PUBLIC jms");
        jms.setLinkedException(linked);
        fixture.jmsFailure = new IllegalStateException("PUBLIC outer", jms);
      } else if (mode == 1) {
        fixture.jmsFailure = new IllegalStateException("PUBLIC primary");
        fixture.jmsClosing = new IllegalStateException("PUBLIC close", fatal);
      } else {
        fixture.consumerClosing = new IllegalStateException("PUBLIC consumer close", fatal);
      }
      assertSame(fatal, assertThrows(AssertionError.class, fixture::verify));
      fixture.assertCounts(false, mode == 2 ? 1 : 0);
    }
  }

  @Test
  void ready330003DirectFatalPriorityAndOrdinaryCyclicCatalogStayFixed() {
    for (boolean primaryFatal : new boolean[] {false, true}) {
      var fixture = new Fixture();
      var first = new AssertionError("PUBLIC primary");
      var closing = new AssertionError("PUBLIC close");
      fixture.jmsFailure = primaryFatal ? first : new IllegalStateException("PUBLIC primary");
      fixture.jmsClosing = closing;
      assertSame(
          primaryFatal ? first : closing, assertThrows(AssertionError.class, fixture::verify));
      fixture.assertCounts(false, 0);
    }
    var fixture = new Fixture();
    var sql = new SQLException("PUBLIC sql");
    var jms = new JMSException("PUBLIC jms");
    var root = new IllegalStateException("PUBLIC outer", jms);
    jms.setLinkedException(sql);
    sql.initCause(root);
    sql.setNextException(sql);
    fixture.jmsFailure = root;
    fixture.jmsClosing = new IllegalArgumentException("PUBLIC ordinary close");
    var actual = assertThrows(WebStartupException.class, fixture::verify);
    assertEquals("Web Artemis reply Queue is unavailable", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
    fixture.assertCounts(false, 0);
  }

  private static final class Fixture {
    @Nullable Throwable databaseFailure;
    @Nullable Throwable databaseClosing;
    @Nullable Throwable jmsFailure;
    @Nullable Throwable jmsClosing;
    @Nullable Throwable consumerClosing;
    int databaseOpens;
    int databaseCloses;
    int brokerOpens;
    int contextCloses;
    int consumerCloses;

    void verify() {
      Connection connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("isValid")) {
                      assertEquals(2, args[0]);
                      if (databaseFailure != null) throw databaseFailure;
                      return true;
                    }
                    if (method.getName().equals("close")) {
                      databaseCloses++;
                      if (databaseClosing != null) throw databaseClosing;
                      return null;
                    }
                    throw new UnsupportedOperationException("unexpected connection fixture call");
                  });
      DataSource source =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (proxy, method, args) -> {
                    if (!method.getName().equals("getConnection"))
                      throw new UnsupportedOperationException("unexpected source fixture call");
                    databaseOpens++;
                    return connection;
                  });
      JMSConsumer consumer =
          (JMSConsumer)
              Proxy.newProxyInstance(
                  JMSConsumer.class.getClassLoader(),
                  new Class<?>[] {JMSConsumer.class},
                  (proxy, method, args) -> {
                    if (!method.getName().equals("close"))
                      throw new UnsupportedOperationException("unexpected consumer fixture call");
                    consumerCloses++;
                    if (consumerClosing != null) throw consumerClosing;
                    return null;
                  });
      Queue queue =
          (Queue)
              Proxy.newProxyInstance(
                  Queue.class.getClassLoader(),
                  new Class<?>[] {Queue.class},
                  (proxy, method, args) -> {
                    if (!method.getName().equals("getQueueName"))
                      throw new UnsupportedOperationException("unexpected queue fixture call");
                    return "PUBLIC";
                  });
      JMSContext context =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (proxy, method, args) -> {
                    return switch (method.getName()) {
                      case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                      case "createQueue" -> queue;
                      case "createConsumer" -> {
                        if (jmsFailure != null) throw jmsFailure;
                        yield consumer;
                      }
                      case "close" -> {
                        contextCloses++;
                        if (jmsClosing != null) throw jmsClosing;
                        yield null;
                      }
                      default ->
                          throw new UnsupportedOperationException(
                              "unexpected context fixture call");
                    };
                  });
      new WebDependencyReadiness(
              source,
              () -> {
                brokerOpens++;
                return context;
              })
          .verify();
    }

    void assertCounts(boolean databaseFailed, int expectedConsumerCloses) {
      assertEquals(1, databaseOpens);
      assertEquals(1, databaseCloses);
      assertEquals(databaseFailed ? 0 : 1, brokerOpens);
      assertEquals(databaseFailed ? 0 : 1, contextCloses);
      assertEquals(expectedConsumerCloses, consumerCloses);
    }
  }
}
