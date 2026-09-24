package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.WebLogIngestService;
import dev.codex.schubert.nk.api.messaging.inbound.ApiMessagingRuntime;
import dev.codex.schubert.nk.api.messaging.inbound.CommittedFatalInboundException;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.LoginApplicationAssembly;
import jakarta.jms.JMSContext;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Supplier;
import javax.sql.DataSource;

/**
 * Owns the API receive groups for the initial Login→Game-context→Log path. The outer process must
 * provide {@code LoginInboxService::execute}, {@code ScenarioApplicationService} and {@code
 * LogQueryApplicationService}. Login alone uses an outer JDBC transaction, whereas Scenario and Log
 * services own their staged transactions. This is a path runtime, not complete API readiness: the
 * outer process must validate all broker resources/credentials and register all layouts before
 * exposure. Trace: NK-MSG-001/002, NK-AUT-001, NK-ADM-001; RD FUN-001/008, AUT-001/002,
 * MQ-003/006/008; UI225/226/231/232/235; SS311/312/314/321/323/324; PG233/PT-JMS-018.
 */
public final class ApiLogPathApplicationRuntime implements AutoCloseable {
  private final ApiMessagingRuntime messaging;
  private final SyncRequestProcessor processor;

  private ApiLogPathApplicationRuntime(
      ApiMessagingRuntime messaging, SyncRequestProcessor processor) {
    this.messaging = messaging;
    this.processor = processor;
  }

  /**
   * Connects the real Login transaction graph to the receive group. Key-bearing codecs remain
   * caller-owned and must outlive this runtime. Game-context and Log search are separate staged
   * processors and must also be Production implementations before process readiness. PG254;
   * PT-AUT-INBOX-009; SS311/312/314/324.
   */
  public static ApiLogPathApplicationRuntime startWithLogin(
      Supplier<JMSContext> factory,
      DataSource database,
      FingerprintKeyRing fingerprints,
      AuthContextCodec contexts,
      ResponseSnapshotCodec snapshots,
      SyncRequestProcessor gameContext,
      SyncRequestProcessor logSearch,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal)
      throws NoSuchAlgorithmException {
    var login = LoginApplicationAssembly.create(fingerprints, contexts, snapshots, clock);
    return start(factory, database, login::execute, gameContext, logSearch, clock, onTerminal);
  }

  public static ApiLogPathApplicationRuntime start(
      Supplier<JMSContext> factory,
      DataSource database,
      TransactionalRequestHandler login,
      SyncRequestProcessor gameContext,
      SyncRequestProcessor logSearch,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal) {
    Objects.requireNonNull(factory, "factory");
    Objects.requireNonNull(database, "database");
    Objects.requireNonNull(login, "login");
    Objects.requireNonNull(gameContext, "gameContext");
    Objects.requireNonNull(logSearch, "logSearch");
    Objects.requireNonNull(clock, "clock");
    Objects.requireNonNull(onTerminal, "onTerminal");
    new ApiDependencyReadiness(database, factory).verify();
    var processor =
        new LogPathSyncRequestProcessor(
            new JdbcSyncRequestProcessor(database, login, clock), gameContext, logSearch);
    var messaging =
        ApiMessagingRuntime.start(
            factory, processor, new WebLogIngestService(database), clock, onTerminal);
    return new ApiLogPathApplicationRuntime(messaging, processor);
  }

  public boolean ready() {
    return messaging.ready();
  }

  public boolean terminalFailureObserved() {
    return messaging.terminalFailureObserved();
  }

  SyncRequestProcessor processor() {
    return processor;
  }

  @Override
  public void close() {
    messaging.close();
  }
}
