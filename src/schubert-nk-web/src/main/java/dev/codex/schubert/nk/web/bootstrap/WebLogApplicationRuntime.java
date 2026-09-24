package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.web.config.LogMvcConfiguration;
import dev.codex.schubert.nk.web.config.ScenarioLogMvcConfiguration;
import dev.codex.schubert.nk.web.logging.WebLogDispatcher;
import dev.codex.schubert.nk.web.logging.WebLogReplayWorker;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumer;
import dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumers;
import dev.codex.schubert.nk.web.messaging.ArtemisReplyDlqSender;
import dev.codex.schubert.nk.web.messaging.ArtemisRequestSender;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import dev.codex.schubert.nk.web.messaging.JmsReplyDecoder;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogSearchWireClient;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.MqLoginClient;
import dev.codex.schubert.nk.web.security.MqLoginContextProbe;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;
import java.util.function.IntSupplier;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.apache.catalina.LifecycleException;
import org.jspecify.annotations.Nullable;

/**
 * Owns the Log-path Web reply consumer, outbox replay worker, and secured HTTP server. Supplied DB,
 * broker factory, codecs, dispatcher, and audit remain caller-owned. The outer process still owns
 * credential loading, broker-management readiness and nonzero exit on terminal reply. Trace:
 * NK-WEB-002/NK-MSG-001/002; RD MQ-003..008/AUT-002/MON-003; UI225/226/231/232/235; SS311/313/
 * 314/321/324/342/352; PG231/PT-SCR127..130.
 */
public final class WebLogApplicationRuntime implements AutoCloseable {
  private final AutoCloseable http;
  private final AutoCloseable replay;
  private final AutoCloseable replies;
  private final IntSupplier port;
  private final BooleanSupplier replyReady;
  private final BooleanSupplier replayRunning;
  private final AtomicBoolean terminal;
  private final AtomicBoolean closed = new AtomicBoolean();

  /** Package-local lifecycle seam for deterministic close-failure PT. */
  WebLogApplicationRuntime(
      AutoCloseable http,
      AutoCloseable replay,
      AutoCloseable replies,
      IntSupplier port,
      BooleanSupplier replyReady,
      BooleanSupplier replayRunning,
      AtomicBoolean terminal) {
    this.http = Objects.requireNonNull(http, "http");
    this.replay = Objects.requireNonNull(replay, "replay");
    this.replies = Objects.requireNonNull(replies, "replies");
    this.port = Objects.requireNonNull(port, "port");
    this.replyReady = Objects.requireNonNull(replyReady, "replyReady");
    this.replayRunning = Objects.requireNonNull(replayRunning, "replayRunning");
    this.terminal = Objects.requireNonNull(terminal, "terminal");
  }

  /** Starts the shared reply registry before any Login/Log request can enter HTTP. */
  public static WebLogApplicationRuntime start(
      Path runtimeDirectory,
      int port,
      DataSource database,
      JmsContextFactory broker,
      SessionPayloadCodec sessionCodec,
      Clock clock,
      WebSecurityAudit audit,
      Supplier<UUID> identifiers,
      WebLogDispatcher logDispatcher,
      String logWorker,
      int logBatchLimit,
      Duration logInterval,
      Consumer<dev.codex.schubert.nk.web.messaging.CommittedFatalReplyException> onTerminal)
      throws LifecycleException {
    return startPath(
        runtimeDirectory,
        port,
        database,
        broker,
        sessionCodec,
        clock,
        audit,
        identifiers,
        logDispatcher,
        logWorker,
        logBatchLimit,
        logInterval,
        onTerminal,
        false);
  }

  /** Registers Scenario and Log MVC together; the outer process still owns full readiness. */
  public static WebLogApplicationRuntime startWithScenario(
      Path runtimeDirectory,
      int port,
      DataSource database,
      JmsContextFactory broker,
      SessionPayloadCodec sessionCodec,
      Clock clock,
      WebSecurityAudit audit,
      Supplier<UUID> identifiers,
      WebLogDispatcher logDispatcher,
      String logWorker,
      int logBatchLimit,
      Duration logInterval,
      Consumer<dev.codex.schubert.nk.web.messaging.CommittedFatalReplyException> onTerminal)
      throws LifecycleException {
    return startPath(
        runtimeDirectory,
        port,
        database,
        broker,
        sessionCodec,
        clock,
        audit,
        identifiers,
        logDispatcher,
        logWorker,
        logBatchLimit,
        logInterval,
        onTerminal,
        true);
  }

  private static WebLogApplicationRuntime startPath(
      Path runtimeDirectory,
      int port,
      DataSource database,
      JmsContextFactory broker,
      SessionPayloadCodec sessionCodec,
      Clock clock,
      WebSecurityAudit audit,
      Supplier<UUID> identifiers,
      WebLogDispatcher logDispatcher,
      String logWorker,
      int logBatchLimit,
      Duration logInterval,
      Consumer<dev.codex.schubert.nk.web.messaging.CommittedFatalReplyException> onTerminal,
      boolean scenario)
      throws LifecycleException {
    Class<?> configuration =
        scenario ? ScenarioLogMvcConfiguration.class : LogMvcConfiguration.class;
    WebHttpServer.validateConfiguration(runtimeDirectory, port, new Class<?>[] {configuration});
    Objects.requireNonNull(database, "database");
    Objects.requireNonNull(broker, "broker");
    Objects.requireNonNull(sessionCodec, "sessionCodec");
    Objects.requireNonNull(clock, "clock");
    Objects.requireNonNull(audit, "audit");
    Objects.requireNonNull(identifiers, "identifiers");
    Objects.requireNonNull(logDispatcher, "logDispatcher");
    Objects.requireNonNull(logWorker, "logWorker");
    Objects.requireNonNull(logInterval, "logInterval");
    Objects.requireNonNull(onTerminal, "onTerminal");

    var client = new JmsRequestReplyClient();
    var sender = new ArtemisRequestSender(broker);
    var authentication =
        new MqAuthenticationProvider(
            new MqLoginClient(client, sender, clock, identifiers, Duration.ofSeconds(2)),
            new MqLoginContextProbe(client, sender, clock, identifiers, Duration.ofSeconds(2)));
    var application =
        new WebApplication(
            database, broker, sessionCodec, clock, authentication, audit, identifiers);
    var terminal = new AtomicBoolean();
    ArtemisReplyConsumers replies =
        ArtemisReplyConsumers.start(
            broker,
            new ArtemisReplyConsumer(
                client, new JmsReplyDecoder(), new ArtemisReplyDlqSender(clock)),
            failure -> {
              terminal.set(true);
              onTerminal.accept(failure);
            });
    WebLogReplayWorker replay = null;
    try {
      replay = WebLogReplayWorker.start(logDispatcher, logWorker, logBatchLimit, logInterval);
      WebHttpServer http =
          application.startWithSessionDependencies(
              runtimeDirectory,
              port,
              sessions -> {
                var logClient =
                    new LogSearchWireClient(
                        client, sender, clock, identifiers, Duration.ofSeconds(2));
                var invalid = new ApiSessionInvalidHandler(sessions, audit);
                if (scenario) {
                  return Map.<Class<?>, Object>of(
                      LogSearchWireClient.class,
                      logClient,
                      ScenarioWireClient.class,
                      new ScenarioWireClient(
                          client, sender, clock, identifiers, Duration.ofSeconds(2)),
                      ApiSessionInvalidHandler.class,
                      invalid);
                }
                return Map.<Class<?>, Object>of(
                    LogSearchWireClient.class, logClient,
                    ApiSessionInvalidHandler.class, invalid);
              },
              configuration);
      return new WebLogApplicationRuntime(
          http, replay, replies, http::port, replies::ready, replay::running, terminal);
    } catch (LifecycleException | RuntimeException failure) {
      closeAfterFailure(failure, replay, replies);
      throw failure;
    }
  }

  public int port() {
    if (closed.get()) {
      throw new IllegalStateException("Web Log runtime is closed");
    }
    return port.getAsInt();
  }

  /** Local ownership health, not full deployment or API readiness. */
  public boolean ready() {
    return !closed.get()
        && !terminal.get()
        && replyReady.getAsBoolean()
        && replayRunning.getAsBoolean();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  @Override
  public void close() {
    if (!closed.compareAndSet(false, true)) {
      return;
    }
    Exception failure = null;
    for (AutoCloseable resource : new AutoCloseable[] {http, replay, replies}) {
      try {
        resource.close();
      } catch (Exception closing) {
        if (failure == null) failure = closing;
        else if (failure != closing) failure.addSuppressed(closing);
      }
    }
    if (failure != null) {
      throw new IllegalStateException("Web Log runtime stop failed", failure);
    }
  }

  static void closeAfterFailure(
      Exception startupFailure, @Nullable AutoCloseable replay, AutoCloseable replies) {
    for (AutoCloseable resource : new AutoCloseable[] {replay, replies}) {
      if (resource != null) {
        try {
          resource.close();
        } catch (Exception closing) {
          if (startupFailure != closing) startupFailure.addSuppressed(closing);
        }
      }
    }
  }
}
