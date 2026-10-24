package dev.codex.schubert.nk.web.bootstrap;

import com.zaxxer.hikari.HikariDataSource;
import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import dev.codex.schubert.nk.web.logging.WebLogDispatcher;
import dev.codex.schubert.nk.web.logging.WebLogMessageSender;
import dev.codex.schubert.nk.web.logging.WebLogOutboxRepository;
import dev.codex.schubert.nk.web.logging.WebLogReplayWorker;
import dev.codex.schubert.nk.web.logging.WebMediaAudit;
import dev.codex.schubert.nk.web.logging.WebRequestLogProducer;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.media.DescriptorFileResolver;
import dev.codex.schubert.nk.web.media.MediaRangeService;
import dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumer;
import dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumers;
import dev.codex.schubert.nk.web.messaging.ArtemisReplyDlqSender;
import dev.codex.schubert.nk.web.messaging.ArtemisRequestSender;
import dev.codex.schubert.nk.web.messaging.CommittedFatalReplyException;
import dev.codex.schubert.nk.web.messaging.JmsReplyDecoder;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.messaging.WebBrokerContexts;
import dev.codex.schubert.nk.web.monitoring.WebMetricContext;
import dev.codex.schubert.nk.web.monitoring.WebServiceMetricBinding;
import dev.codex.schubert.nk.web.revocation.RevocationRetryCoordinator;
import dev.codex.schubert.nk.web.revocation.RevocationRetryWorker;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.MqLoginClient;
import dev.codex.schubert.nk.web.security.MqLoginContextProbe;
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
import java.util.function.BiFunction;
import java.util.function.BooleanSupplier;
import java.util.function.ToIntBiFunction;
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
  private static final String CONFIG_DESCRIPTION = "Web config";
  private final DataSource database;
  private final ServiceCredentialSet credentials;
  private final WebNonSecretConfig config;
  private final ServiceStartupAdmission.Ready retainedReady;
  private final Map<String, String> information;
  private final WebHttpAdmission admission;
  private final BooleanSupplier ownerStopping;
  private final ResourceScope.Acquire<DirectoryCalls, StorageIoException> directories;
  private final BiFunction<WebNonSecretConfig, String, Path> paths;
  private final ToIntBiFunction<WebNonSecretConfig, String> ports;
  private final ResourceScope.OwnedAction<
          Map.Entry<OwnedTransferDirectory, StorageIdentity>, @Nullable Boolean>
      directoryProof;
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final WebRuntimeFailureSignal<CommittedFatalReplyException> failureSignal =
      new WebRuntimeFailureSignal<>(terminal);
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final Object ownerLock = new Object();
  private @Nullable WebBrokerContexts broker;
  private @Nullable WebNativeCodecs codecs;
  private @Nullable OwnedTransferDirectory transfer;
  private @Nullable OwnedTransferDirectory assets;
  private volatile @Nullable ArtemisReplyConsumers replies;
  private volatile @Nullable WebLogReplayWorker replay;
  private volatile @Nullable RevocationRetryWorker retry;
  private volatile @Nullable WebHttpServer http;
  private volatile @Nullable WebManagementServer management;
  private @Nullable WebMetricContext<WebServiceMetricBinding> metrics;
  private boolean startAttempted;
  private final WebRuntimeStop stop = new WebRuntimeStop(System::nanoTime);

  WebNativeRuntime(
      DataSource database,
      ServiceCredentialSet credentials,
      WebNonSecretConfig config,
      ServiceStartupAdmission.Ready ready,
      BooleanSupplier ownerStopping)
      throws IOException {
    this(
        database,
        credentials,
        config,
        ready,
        ownerStopping,
        LinuxDirectoryCalls::create,
        WebNativeRuntime::nativePath,
        WebNativeRuntime::nativePort,
        WebNativeRuntime::nativeVerify);
  }

  /** SSC327/PG-D482: internal ports only; Production retains the fixed five-argument binding. */
  WebNativeRuntime(
      DataSource database,
      ServiceCredentialSet credentials,
      WebNonSecretConfig config,
      ServiceStartupAdmission.Ready ready,
      BooleanSupplier ownerStopping,
      ResourceScope.Acquire<DirectoryCalls, StorageIoException> directories,
      BiFunction<WebNonSecretConfig, String, Path> paths,
      ToIntBiFunction<WebNonSecretConfig, String> ports,
      ResourceScope.OwnedAction<
              Map.Entry<OwnedTransferDirectory, StorageIdentity>, @Nullable Boolean>
          directoryProof)
      throws IOException {
    this.database = Objects.requireNonNull(database, "Web database");
    this.credentials = Objects.requireNonNull(credentials, "Web credentials");
    this.config = Objects.requireNonNull(config, CONFIG_DESCRIPTION);
    this.retainedReady = Objects.requireNonNull(ready, "Root admission ready");
    this.information = Map.copyOf(ready.information());
    this.ownerStopping = Objects.requireNonNull(ownerStopping, "Web stop notification");
    this.directories = Objects.requireNonNull(directories, "Web directory acquire");
    this.paths = Objects.requireNonNull(paths, "Web internal paths");
    this.ports = Objects.requireNonNull(ports, "Web internal ports");
    this.directoryProof = Objects.requireNonNull(directoryProof, "Web directory proof");
    this.admission = new WebHttpAdmission(ownerStopping);
  }

  void start() throws IOException, org.apache.catalina.LifecycleException {
    synchronized (ownerLock) {
      if (startAttempted || stopping.get()) throw new IOException("Web startup unavailable");
      startAttempted = true;
      broker = WebBrokerContexts.createRetainingUnknown(credentials, config.value("nk.mq.url"));
      var currentBroker = Objects.requireNonNull(broker);
      new WebDependencyReadiness(database, currentBroker.contexts()).verify();
      codecs = WebNativeCodecs.create(credentials);
      var keys = Objects.requireNonNull(codecs);
      var directoryCalls = Objects.requireNonNull(directories.open(), "Web directory calls");
      transfer =
          OwnedTransferDirectory.open(
              directoryCalls, paths.apply(config, "nk.web.storage.transfer-root"));
      var transferRoot = Objects.requireNonNull(transfer);
      var transferIdentity = new StorageIdentity("schubert-api", "schubert-web");
      if (!Boolean.TRUE.equals(directoryProof.run(Map.entry(transferRoot, transferIdentity))))
        throw new IOException("Web directory proof unavailable");
      assets =
          OwnedTransferDirectory.open(
              directoryCalls, paths.apply(config, "nk.web.storage.asset-root"));
      var assetRoot = Objects.requireNonNull(assets);
      var assetIdentity = new StorageIdentity("schubert-data", "schubert-read");
      if (!Boolean.TRUE.equals(directoryProof.run(Map.entry(assetRoot, assetIdentity))))
        throw new IOException("Web directory proof unavailable");
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
              failureSignal,
              failureSignal);
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
              failureSignal);
      metrics =
          WebServiceMetricBinding.prepareContext(
              config.value("nk.monitoring.mode"),
              () -> HikariDataSource.class.cast(database).getHikariPoolMXBean(),
              () -> HikariDataSource.class.cast(database).getHikariConfigMXBean(),
              failureSignal);
      var metricOwner = Objects.requireNonNull(metrics);
      metricOwner.initialize();
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
          paths.apply(config, "runtime"),
          ports.applyAsInt(config, "nk.web.http.port"),
          (core, sessions) -> {
            var dependencies = assembly.dependencies(core, sessions);
            var binding = metricOwner.bindings();
            return binding.isPresent()
                ? binding.orElseThrow().withHttpObserver(dependencies)
                : dependencies;
          },
          owned -> http = owned,
          WebBusinessAssembly.configurations());
      requireMappings(Objects.requireNonNull(http).mappedPaths());
      management =
          WebManagementServer.bind(
              information,
              this::healthy,
              ports.applyAsInt(config, "nk.web.management.port"),
              com.sun.net.httpserver.HttpServer::create,
              metricOwner);
      var control = Objects.requireNonNull(management);
      control.start();
      control.promote(
          () -> {
            retainedReady.release();
            admission.admit();
          });
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SS343 fixed Web runtime namespace under systemd ownership; no caller path or override")
  static Path nativePath(WebNonSecretConfig config, String key) {
    Objects.requireNonNull(config, CONFIG_DESCRIPTION);
    return switch (Objects.requireNonNull(key, "Web internal path key")) {
      case "runtime" -> Path.of("/run/schubert-nk/web");
      case "nk.web.storage.transfer-root", "nk.web.storage.asset-root" ->
          Path.of(config.value(key));
      default -> throw new IllegalArgumentException("Web internal path unavailable");
    };
  }

  static int nativePort(WebNonSecretConfig config, String key) {
    Objects.requireNonNull(config, CONFIG_DESCRIPTION);
    return switch (Objects.requireNonNull(key, "Web internal port key")) {
      case "nk.web.http.port", "nk.web.management.port" -> Integer.parseInt(config.value(key));
      default -> throw new IllegalArgumentException("Web internal port unavailable");
    };
  }

  static Boolean nativeVerify(Map.Entry<OwnedTransferDirectory, StorageIdentity> entry)
      throws StorageIoException {
    Objects.requireNonNull(entry, "Web directory proof entry");
    verify(
        Objects.requireNonNull(entry.getKey(), "Web directory"),
        Objects.requireNonNull(entry.getValue(), "Web directory identity"));
    return Boolean.TRUE;
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

  /** PG-D378/WEB-REM003: exact route set check, no new configuration or repair. */
  static void requireMappings(Set<String> paths) throws IOException {
    if (!paths.equals(REQUIRED_PATHS)) throw new IOException("Web business mapping unavailable");
  }

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
    return WebRuntimeHealth.ready(control, WebManagementServer::ready);
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
          var value = metrics;
          if (value != null) value.close();
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
    String value =
        Objects.requireNonNull(config, CONFIG_DESCRIPTION).value("nk.web.mq.reply-timeout");
    return value.endsWith("ms")
        ? Duration.ofMillis(Long.parseLong(value.substring(0, value.length() - 2)))
        : Duration.ofSeconds(Long.parseLong(value.substring(0, value.length() - 1)));
  }

  @Override
  public String toString() {
    return "WebNativeRuntime[REDACTED]";
  }
}
