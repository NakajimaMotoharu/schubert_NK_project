package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
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
 * SS311/312/321/342; PG234/266/268/361, PT-JMS-019/022/023/025, BUG-248/249/321.
 */
public final class ApiDependencyReadiness {
  private final DataSource database;
  private final Supplier<JMSContext> broker;
  private final @Nullable Supplier<JMSContext> webLog;
  private final @Nullable Supplier<JMSContext> async;

  // Compatibility for package-local PT of the original single-context behavior only.
  ApiDependencyReadiness(DataSource database, Supplier<JMSContext> broker) {
    this.database = Objects.requireNonNull(database, "database");
    this.broker = Objects.requireNonNull(broker, "broker");
    this.webLog = null;
    this.async = null;
  }

  public ApiDependencyReadiness(
      DataSource database, Supplier<JMSContext> sync, Supplier<JMSContext> webLog) {
    this.database = Objects.requireNonNull(database, "database");
    this.broker = Objects.requireNonNull(sync, "sync broker");
    this.webLog = Objects.requireNonNull(webLog, "Web Log broker");
    this.async = null;
  }

  public ApiDependencyReadiness(
      DataSource database,
      Supplier<JMSContext> sync,
      Supplier<JMSContext> webLog,
      Supplier<JMSContext> async) {
    this.database = Objects.requireNonNull(database, "database");
    this.broker = Objects.requireNonNull(sync, "sync broker");
    this.webLog = Objects.requireNonNull(webLog, "Web Log broker");
    this.async = Objects.requireNonNull(async, "async broker");
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
          TemporaryInfrastructureException.attachSecondary(primary, closing);
        }
      }
    } catch (SQLException | RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new IllegalStateException("API database unavailable");
    }
    probe(broker, BrokerTopology.SYNC_REQUEST, webLog == null);
    if (webLog != null) probe(webLog, BrokerTopology.WEB_LOG, false);
    if (async != null) probe(async, BrokerTopology.ASYNC_WORK, false);
  }

  private static void probe(
      Supplier<JMSContext> supplier, BrokerTopology topology, boolean legacyWebLog) {
    try {
      JMSContext context = Objects.requireNonNull(supplier.get(), "JMS context");
      @Nullable Throwable primary = null;
      try {
        if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
          throw new IllegalStateException("non-transacted JMS context");
        }
        Objects.requireNonNull(
                context.createConsumer(new ActiveMQQueue(topology.fullyQualifiedQueue())),
                "receive consumer")
            .close();
        if (legacyWebLog)
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
          // Retain only in the transient primary graph until the fixed catalog is classified.
          if (primary == null || closing instanceof Error && !(primary instanceof Error)) {
            throw closing;
          }
          TemporaryInfrastructureException.attachSecondary(primary, closing);
        }
      }
    } catch (RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new IllegalStateException("API Artemis receive queues unavailable");
    }
  }
}
