package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.WebSecurityFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepository;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
import java.nio.file.Path;
import java.time.Clock;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.apache.catalina.LifecycleException;

/**
 * Restricted production Web composition: DB/JMS transport readiness precedes HTTP binding, then the
 * approved encrypted-session security chain owns all requests. The caller owns every supplied
 * dependency and the returned server; credential loading, broker management readiness, API dispatch
 * and NK Characterization are separate startup gates. NK-WEB-002;
 * SYS-001/002/004,AUT-001,MQ-001/002; UI211/212/226/252; SS311/314/321/342/352/362;
 * PG222/PT-SCR117..119.
 */
public final class WebApplication {
  private final DataSource database;
  private final JmsContextFactory broker;
  private final SessionPayloadCodec codec;
  private final Clock clock;
  private final MqAuthenticationProvider authentication;
  private final WebSecurityAudit audit;
  private final Supplier<UUID> requestIds;

  public WebApplication(
      DataSource database,
      JmsContextFactory broker,
      SessionPayloadCodec codec,
      Clock clock,
      MqAuthenticationProvider authentication,
      WebSecurityAudit audit,
      Supplier<UUID> requestIds) {
    this.database = Objects.requireNonNull(database, "database");
    this.broker = Objects.requireNonNull(broker, "broker");
    this.codec = Objects.requireNonNull(codec, "codec");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.audit = Objects.requireNonNull(audit, "audit");
    this.requestIds = Objects.requireNonNull(requestIds, "requestIds");
  }

  public WebHttpServer start(Path runtimeDirectory, int port, Class<?>... featureConfigurations)
      throws LifecycleException {
    // Validate the local path/port/configuration before borrowing DB or broker resources.
    WebHttpServer.validateConfiguration(runtimeDirectory, port, featureConfigurations);
    new WebDependencyReadiness(database, broker).verify();
    var sessions =
        new SpringEncryptedSessionRepository(
            new EncryptedWebSessionRepository(database, codec, clock), clock);
    var security =
        new WebSecurityFilterFactory().create(sessions, authentication, audit, requestIds);
    return WebHttpServer.start(runtimeDirectory, port, security, featureConfigurations);
  }
}
