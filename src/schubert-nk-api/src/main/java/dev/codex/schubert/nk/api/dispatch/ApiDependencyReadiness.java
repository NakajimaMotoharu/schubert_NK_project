package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSContext;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Objects;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed DB/JMS connectivity admission before API consumers start. A JMS consumer attachment can
 * be lazy: SS321 management verification of topology, ACL, journal, disk and queue thresholds is a
 * separate mandatory gate. Trace: NK-MSG-001/002; RD MQ-001/003/006/008, SYS-004; UI212/231/252;
 * SS311/312/321/342; PG234/266/268, PT-JMS-019/022/023, BUG-248/249.
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
    try {
      Connection connection = Objects.requireNonNull(database.getConnection(), "JDBC connection");
      @Nullable Throwable primary = null;
      try {
        if (!connection.isValid(2)) throw new IllegalStateException("invalid JDBC connection");
      } catch (SQLException | RuntimeException | Error failure) {
        primary = failure;
        throw failure;
      } finally {
        try {
          connection.close();
        } catch (SQLException | RuntimeException | Error closing) {
          // The DB probe has the same owned-resource fatal precedence as the JMS probe below.
          if (primary == null || closing instanceof Error && !(primary instanceof Error)) {
            throw closing;
          }
        }
      }
    } catch (SQLException | RuntimeException failure) {
      throw new IllegalStateException("API database unavailable");
    }
    try {
      JMSContext context = Objects.requireNonNull(broker.get(), "JMS context");
      @Nullable Throwable primary = null;
      try {
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
      } catch (RuntimeException | Error failure) {
        primary = failure;
        throw failure;
      } finally {
        try {
          context.close();
        } catch (RuntimeException | Error closing) {
          // Readiness exposes no provider detail. A fatal close must not be hidden behind an
          // ordinary inspection failure; otherwise the primary failure keeps precedence.
          // No suppression is needed for this fixed/redacted startup boundary.
          if (primary == null || closing instanceof Error && !(primary instanceof Error)) {
            throw closing;
          }
        }
      }
    } catch (RuntimeException failure) {
      throw new IllegalStateException("API Artemis receive queues unavailable");
    }
  }
}
