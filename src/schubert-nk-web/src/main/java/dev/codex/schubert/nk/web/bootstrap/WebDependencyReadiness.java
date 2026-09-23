package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Web-only DB/broker admission before opening HTTP. JMS consumer construction is not proof that a
 * Queue exists; the SS321 management readiness check remains a separate mandatory startup gate.
 * This proves transport connectivity, not full API/business dispatch or actual NK Characterization.
 * NK-WEB-002; SYS-001/002/004,MQ-001/002; UI211/212/231/252; SS311/321/342; PG221/PT-SCR113..116.
 */
public final class WebDependencyReadiness {
  private final DataSource database;
  private final JmsContextFactory broker;

  public WebDependencyReadiness(DataSource database, JmsContextFactory broker) {
    this.database = Objects.requireNonNull(database, "database");
    this.broker = Objects.requireNonNull(broker, "broker");
  }

  /** Borrows/returns both resources; no DB mutation and no JMS message consumption. */
  public void verify() {
    try (Connection connection = Objects.requireNonNull(database.getConnection())) {
      if (!connection.isValid(2)) throw new WebStartupException("Web technical database");
    } catch (SQLException | RuntimeException failure) {
      throw new WebStartupException("Web technical database");
    }
    try (var context = Objects.requireNonNull(broker.open())) {
      var reply = context.createQueue(BrokerTopology.SYNC_REPLY_WEB.fullyQualifiedQueue());
      // Do not infer Queue existence from this call: some JMS providers attach lazily.
      Objects.requireNonNull(context.createConsumer(reply)).close();
    } catch (RuntimeException failure) {
      throw new WebStartupException("Web Artemis reply Queue");
    }
  }
}
