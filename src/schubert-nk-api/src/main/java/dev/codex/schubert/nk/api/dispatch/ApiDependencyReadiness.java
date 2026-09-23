package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSContext;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Objects;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;

/**
 * Borrowed DB/JMS connectivity admission before API consumers start. A JMS consumer attachment can
 * be lazy: SS321 management verification of topology, ACL, journal, disk and queue thresholds is a
 * separate mandatory gate. Trace: NK-MSG-001/002; RD MQ-001/003/006/008, SYS-004; UI212/231/252;
 * SS311/312/321/342; PG234/PT-JMS-019.
 */
public final class ApiDependencyReadiness {
  private final DataSource database;
  private final Supplier<JMSContext> broker;

  public ApiDependencyReadiness(DataSource database, Supplier<JMSContext> broker) {
    this.database = Objects.requireNonNull(database, "database");
    this.broker = Objects.requireNonNull(broker, "broker");
  }

  /** Neither a DB mutation nor JMS message consumption; all borrowed resources close on failure. */
  public void verify() {
    try (Connection connection =
        Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      if (!connection.isValid(2)) throw new IllegalStateException("invalid JDBC connection");
    } catch (SQLException | RuntimeException failure) {
      throw new IllegalStateException("API database unavailable");
    }
    try (JMSContext context = Objects.requireNonNull(broker.get(), "JMS context")) {
      if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new IllegalStateException("non-transacted JMS context");
      }
      Objects.requireNonNull(
              context.createConsumer(
                  new ActiveMQQueue(BrokerTopology.SYNC_REQUEST.fullyQualifiedQueue())),
              "sync consumer")
          .close();
      Objects.requireNonNull(
              context.createConsumer(
                  new ActiveMQQueue(BrokerTopology.WEB_LOG.fullyQualifiedQueue())),
              "Web Log consumer")
          .close();
    } catch (RuntimeException failure) {
      throw new IllegalStateException("API Artemis receive queues unavailable");
    }
  }
}
