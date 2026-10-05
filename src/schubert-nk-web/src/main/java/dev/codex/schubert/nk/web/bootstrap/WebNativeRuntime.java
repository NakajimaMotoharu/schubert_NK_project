package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.*;
import dev.codex.schubert.nk.web.logging.*;
import dev.codex.schubert.nk.web.media.*;
import dev.codex.schubert.nk.web.messaging.*;
import dev.codex.schubert.nk.web.revocation.*;
import dev.codex.schubert.nk.web.security.*;
import dev.codex.schubert.nk.web.storage.LargeResultReader;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * One native ordinary Web partial owner, created before first acquisition. No callback unwind after
 * UNKNOWN; the entry retains this and its outer DB/key frame. NK-WEB-002/NK-OPS-001;
 * SYS002004/AUT002004/MQ003008/MON003/FIL001009; UI212223224226237243253; SS313314321342343352;
 * PG-D369; NATIVE-GRAPH/READY/STOP.
 */
@NullMarked
final class WebNativeRuntime implements AutoCloseable {
  private final DataSource database;
  private final ServiceCredentialSet credentials;
  private final WebNonSecretConfig config;
  private final ServiceStartupAdmission.Ready ready;
  private final Map<String, String> information;
  private final WebHttpAdmission admission;
  private final BooleanSupplier ownerStopping;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final Object ownerLock = new Object();
  private volatile @Nullable WebBrokerContexts broker;
  private volatile @Nullable WebNativeCodecs codecs;
  private volatile @Nullable OwnedTransferDirectory transfer;
  private volatile @Nullable OwnedTransferDirectory assets;
  private volatile @Nullable ArtemisReplyConsumers replies;
  private volatile @Nullable WebLogReplayWorker replay;
  private volatile @Nullable RevocationRetryWorker retry;
  private volatile @Nullable WebHttpServer http;
  private volatile @Nullable WebManagementServer management;
  private boolean startAttempted;
  private final WebRuntimeStop stop = new WebRuntimeStop(System::nanoTime);

  WebNativeRuntime(
      DataSource database,
      ServiceCredentialSet credentials,
      WebNonSecretConfig config,
      ServiceStartupAdmission.Ready ready,
      BooleanSupplier ownerStopping)
      throws IOException {
    this.database = Objects.requireNonNull(database, "Web database");
    this.credentials = Objects.requireNonNull(credentials, "Web credentials");
    this.config = Objects.requireNonNull(config, "Web config");
    this.ready = Objects.requireNonNull(ready, "Root admission ready");
    this.information = Map.copyOf(ready.information());
    this.ownerStopping = Objects.requireNonNull(ownerStopping, "Web stop notification");
    this.admission = new WebHttpAdmission(ownerStopping);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SS343 fixed Web runtime namespace under systemd ownership; no caller path or override")
  void start() throws IOException, org.apache.catalina.LifecycleException {
    synchronized (ownerLock) {
      if (startAttempted || stopping.get()) throw new IOException("Web startup unavailable");
      startAttempted = true;
      broker = WebBrokerContexts.create(credentials, config.value("nk.mq.url"));
      var currentBroker = Objects.requireNonNull(broker);
      new WebDependencyReadiness(database, currentBroker.contexts()).verify();
      codecs = WebNativeCodecs.create(credentials);
      var keys = Objects.requireNonNull(codecs);
      var directories = LinuxDirectoryCalls.create();
      transfer =
          OwnedTransferDirectory.open(
              directories, Path.of(config.value("nk.web.storage.transfer-root")));
      var transferRoot = Objects.requireNonNull(transfer);
      var transferIdentity = new StorageIdentity("schubert-api", "schubert-web");
      verify(transferRoot, transferIdentity);
      assets =
          OwnedTransferDirectory.open(
              directories, Path.of(config.value("nk.web.storage.asset-root")));
      var assetRoot = Objects.requireNonNull(assets);
      var assetIdentity = new StorageIdentity("schubert-data", "schubert-read");
      verify(assetRoot, assetIdentity);
      var clock = Clock.systemUTC();
      var timeout = replyTimeout(config);
      var client =
          new JmsRequestReplyClient(
              new ReplyCorrelationRegistry(Integer.parseInt(config.value("nk.web.mq.wait.max"))),
              clock,
              Integer.parseInt(config.value("nk.web.mq.wait.initial")));
      var sender = new ArtemisRequestSender(currentBroker.contexts());
      var outbox = new WebLogOutboxRepository();
      var dispatcher =
          new WebLogDispatcher(
              database,
              outbox,
              new WebLogMessageSender(keys.log(), currentBroker.contexts()),
              clock);
      replies = ArtemisReplyConsumers.bind(currentBroker.contexts());
      Objects.requireNonNull(replies)
          .start(
              new ArtemisReplyConsumer(
                  client, new JmsReplyDecoder(), new ArtemisReplyDlqSender(clock)),
              failure -> terminal.set(true));
      replay = WebLogReplayWorker.start(dispatcher, "native-web", 100, Duration.ofSeconds(1));
      var logout = new LogoutWireClient(client, sender, clock, UUID::randomUUID, timeout);
      retry =
          RevocationRetryWorker.start(
              new RevocationRetryCoordinator(database, keys.revoke(), logout, clock),
              Duration.ofSeconds(1));
      String app = Objects.requireNonNull(information.get("app"), "application version");
      String version = Objects.requireNonNull(information.get("config"), "configuration version");
      var audit =
          new WebSecurityAudit(System.getLogger("schubert.nk.web.security"), clock, app, version);
      var requestLog =
          new WebRequestLogProducer(
              database,
              keys.log(),
              outbox,
              System.getLogger("schubert.nk.web.request"),
              clock,
              UUID::randomUUID,
              app,
              version,
              () -> terminal.set(true));
      var assembly =
          new WebBusinessAssembly(
              client,
              sender,
              clock,
              UUID::randomUUID,
              audit,
              database,
              new LargeResultReader(transferRoot, transferIdentity),
              new MediaRangeService(
                  new DescriptorFileResolver(assetRoot, assetIdentity),
                  Integer.parseInt(config.value("nk.web.media.max-streams"))),
              new WebMediaAudit(System.getLogger("schubert.nk.web.media"), clock, app, version),
              requestLog,
              keys.revoke(),
              admission,
              timeout);
      var application =
          new WebApplication(
              database,
              currentBroker.contexts(),
              keys.session(),
              clock,
              new MqAuthenticationProvider(
                  new MqLoginClient(client, sender, clock, UUID::randomUUID, timeout),
                  new MqLoginContextProbe(client, sender, clock, UUID::randomUUID, timeout)),
              audit,
              UUID::randomUUID);
      application.startOwnedWithCoreSessionDependencies(
          Path.of("/run/schubert-nk/web"),
          Integer.parseInt(config.value("nk.web.http.port")),
          assembly::dependencies,
          owned -> http = owned,
          WebBusinessAssembly.configurations());
      if (!Objects.requireNonNull(http).mappedPaths().equals(REQUIRED_PATHS))
        throw new IOException("Web business mapping unavailable");
      management =
          WebManagementServer.bind(
              information,
              this::healthy,
              Integer.parseInt(config.value("nk.web.management.port")),
              com.sun.net.httpserver.HttpServer::create);
      var control = Objects.requireNonNull(management);
      control.start();
      control.promote(
          () -> {
            ready.release();
            admission.admit();
          });
    }
  }

  private static final Set<String> REQUIRED_PATHS =
      Set.of(
          "/",
          "/login",
          "/logout",
          "/error",
          "/search",
          "/logs",
          "/scenarios",
          "/scenarios/{id:[0-9]{1,12}}",
          "/scenarios/{game:NUKITASHI[12]}",
          "/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}",
          "/animation",
          "/animation/main",
          "/animation/ova",
          "/animation/opening",
          "/animation/videos/{id}",
          "/animation/media/{id}",
          "/music",
          "/music/{category}",
          "/music/{category}/{section}",
          "/music/media/{id}",
          "/music/download/{id}",
          "/audio/{id}",
          "/audio/{id}/download",
          "/admin/users",
          "/admin/users/new",
          "/admin/users/{id:[0-9]{1,12}}",
          "/questions",
          "/questions/new",
          "/questions/accepted/{receiptId}",
          "/questions/{id:[0-9]{1,12}}",
          "/notifications",
          "/notifications/{id:[0-9]{1,12}}");

  private static void verify(OwnedTransferDirectory root, StorageIdentity identity)
      throws StorageIoException {
    root.atDirectory(
        path -> {
          StorageAttributeGuard.directory(
              Files.readAttributes(path, "unix:owner,group,mode,nlink"), identity);
          return Boolean.TRUE;
        });
  }

  boolean healthy() {
    var reply = replies;
    var log = replay;
    var revoke = retry;
    var web = http;
    return WebRuntimeHealth.healthy(
        ownerStopping,
        stopping::get,
        terminal::get,
        reply,
        log,
        revoke,
        web,
        ArtemisReplyConsumers::ready,
        WebLogReplayWorker::running,
        RevocationRetryWorker::running);
  }

  boolean ready() {
    var control = management;
    return control != null && control.ready();
  }

  @Override
  public void close() throws IOException {
    synchronized (ownerLock) {
      if (stopping.compareAndSet(false, true)) stop.begin();
      admission.refuse();
      WebRuntimeStop.Step[] phases = {
        admission::drain,
        left -> {
          var value = http;
          if (value != null) value.close();
        },
        left -> {
          var value = retry;
          if (value != null) value.closeWithin(left);
        },
        left -> {
          var value = replay;
          if (value != null) value.closeWithin(left);
        },
        left -> {
          var value = replies;
          if (value != null) value.close();
        },
        left -> {
          var value = management;
          if (value != null) value.closeWithin(left);
        },
        left -> {
          var value = assets;
          if (value != null) value.close();
        },
        left -> {
          var value = transfer;
          if (value != null) value.close();
        },
        left -> {
          var value = codecs;
          if (value != null) value.close();
        },
        left -> {
          var value = broker;
          if (value != null) value.close();
        }
      };
      stop.close(phases);
    }
  }

  static Duration replyTimeout(WebNonSecretConfig config) {
    String value = Objects.requireNonNull(config, "Web config").value("nk.web.mq.reply-timeout");
    return value.endsWith("ms")
        ? Duration.ofMillis(Long.parseLong(value.substring(0, value.length() - 2)))
        : Duration.ofSeconds(Long.parseLong(value.substring(0, value.length() - 1)));
  }

  @Override
  public String toString() {
    return "WebNativeRuntime[REDACTED]";
  }
}
