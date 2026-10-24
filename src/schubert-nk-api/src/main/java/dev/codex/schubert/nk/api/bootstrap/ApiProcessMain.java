package dev.codex.schubert.nk.api.bootstrap;

import com.zaxxer.hikari.HikariDataSource;
import dev.codex.schubert.nk.api.application.question.QuestionWorkerService;
import dev.codex.schubert.nk.api.application.question.StubAnswerProvider;
import dev.codex.schubert.nk.api.dispatch.ApiDependencyReadiness;
import dev.codex.schubert.nk.api.dispatch.ApiSyncRequestDispatcher;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.api.logging.WebLogIngestService;
import dev.codex.schubert.nk.api.messaging.config.ApiBrokerContexts;
import dev.codex.schubert.nk.api.messaging.inbound.ApiMessagingRuntime;
import dev.codex.schubert.nk.api.monitoring.ApiMetricContext;
import dev.codex.schubert.nk.api.monitoring.ApiServiceMetricBinding;
import dev.codex.schubert.nk.api.storage.ApiApplicationPreparation;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.Objects;
import java.util.function.BooleanSupplier;
import java.util.function.IntConsumer;
import org.jspecify.annotations.NullMarked;

/**
 * External API entry, never a substitute for mandatory startup admission. No argv configuration
 * override is accepted. The complete graph is borrowed inside its admitted owners; component PT
 * cannot substitute for native readiness. NK-OPS-001; SYS-002/004; UI212/243/253; SS311/342/343;
 * SSC-083/158/161; PG285/D334/336; PT-OPS-API-MAIN-001..004/READY001..008; 471 R1/D05.
 */
@NullMarked
public final class ApiProcessMain {
  private static final int EXPECTED_FAILURE_STATUS_COUNT = 1;

  private final Map<String, String> environment;
  private final NonSecretConfigSource source;
  private final IntConsumer termination;
  private final ApiTerminalCapture.Factory captures;

  public ApiProcessMain() {
    this(System.getenv(), ServiceConfigFiles.production(), System::exit);
  }

  ApiProcessMain(
      Map<String, String> environment, NonSecretConfigSource source, IntConsumer termination) {
    this(environment, source, termination, ApiTerminalCapture::currentJvm);
  }

  ApiProcessMain(
      Map<String, String> environment,
      NonSecretConfigSource source,
      IntConsumer termination,
      ApiTerminalCapture.Factory captures) {
    this.environment = Map.copyOf(Objects.requireNonNull(environment, "environment"));
    this.source = Objects.requireNonNull(source, "source");
    this.termination = Objects.requireNonNull(termination, "termination");
    this.captures = Objects.requireNonNull(captures, "native PT captures");
  }

  @FunctionalInterface
  interface Startup {
    void execute(ApiStartupInputs.Values inputs) throws IOException;
  }

  /** SSC301: non-secret data only; never a startup admission or resource capability. */
  @FunctionalInterface
  interface ConfigurationLoad {
    ApiStartupInputs.Values load() throws IOException, NoSuchAlgorithmException;
  }

  /** PT-OPS-API-CONFIG-SSC301001..008; called only inside the admitted configuration callback. */
  static ServiceStartupAdmission.Configuration<ApiStartupInputs.Values> admittedConfiguration(
      ConfigurationLoad input, int[] failureCode) throws IOException {
    Objects.requireNonNull(input, "configuration input");
    Objects.requireNonNull(failureCode, "configuration failure status");
    if (failureCode.length != EXPECTED_FAILURE_STATUS_COUNT)
      throw new IllegalArgumentException("one configuration failure status required");
    try {
      var inputs = Objects.requireNonNull(input.load(), "startup inputs");
      return new ServiceStartupAdmission.Configuration<>(inputs, inputs.config().canonicalSha256());
    } catch (IllegalArgumentException | NoSuchAlgorithmException failure) {
      failureCode[0] = 70;
      throw new IOException("non-secret configuration unavailable");
    }
  }

  public void main(String[] arguments) throws IOException {
    Thread.currentThread().setUncaughtExceptionHandler(ApiProcessMain::fatal);
    var coverage = captures.find(environment.get("INVOCATION_ID"));
    int status;
    if (coverage.isPresent()) {
      try (var hold = coverage.orElseThrow().open()) {
        hold.verifyOwner();
        status = run(arguments, environment, source);
        System.err.println("API process stopped");
        coverage.orElseThrow().capture();
        hold.verifyOwner();
        System.err.println("API fixed PT native capture complete");
      }
    } else {
      status = run(arguments, environment, source);
      System.err.println("API process stopped");
    }
    termination.accept(status);
  }

  int run(String[] arguments, Map<String, String> environment, NonSecretConfigSource source) {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(environment, "environment");
    Objects.requireNonNull(source, "non-secret source");
    if (arguments.length != 0) return 70;
    ApiStartupInputs loader;
    try {
      loader = new ApiStartupInputs(source, environment);
      loader.validateEnvironment(); // No file IO; keep existing argv/environment 70 contract.
    } catch (IllegalArgumentException failure) {
      return 70;
    }
    int[] failureCode = {50};
    try {
      startNative(loader, environment, failureCode);
      return 0;
    } catch (IOException failure) {
      return failureCode[0];
    }
  }

  int run(
      String[] arguments,
      Map<String, String> environment,
      NonSecretConfigSource source,
      Startup startup) {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(environment, "environment");
    Objects.requireNonNull(source, "non-secret source");
    Objects.requireNonNull(startup, "startup");
    if (arguments.length != 0) return 70;
    ApiStartupInputs.Values inputs;
    try {
      inputs = new ApiStartupInputs(source, environment).load();
    } catch (IllegalArgumentException | NoSuchAlgorithmException failure) {
      return 70;
    } catch (IOException failure) {
      return 50;
    }
    try {
      startup.execute(inputs);
      return 0;
    } catch (IOException failure) {
      return 50;
    }
  }

  private static void startNative(
      ApiStartupInputs loader, Map<String, String> environment, int[] failureCode)
      throws IOException {
    try (var lifetime = new ApiProcessLifetime()) {
      lifetime.install();
      System.err.println("API startup entered ADMISSION");
      ServiceStartupAdmission.create(ServiceConfigFiles.Service.API, environment)
          .execute(
              () -> {
                System.err.println("API startup entered CONFIGURATION");
                return admittedConfiguration(loader::load, failureCode);
              },
              (inputs, ready) -> {
                System.err.println("API startup entered PROCESS_RESOURCES");
                new ServiceProcessResources(
                        new ServiceProcessResources.Inputs(
                            ServiceConfigFiles.Service.API,
                            inputs.credentials(),
                            inputs.config().value("nk.db.url")),
                        source -> new ApiJdbcPool().open(source))
                    .executeRetainingUnknown(
                        (pool, credentials) -> {
                          System.err.println("API startup entered BROKER");
                          ResourceScope.acquire(
                              () ->
                                  ApiBrokerContexts.createRetainingUnknown(
                                      credentials, inputs.config().value("nk.mq.url")),
                              ServiceProcessResources.ownedRelease(ApiBrokerContexts::close, true),
                              broker -> {
                                System.err.println("API startup entered DEPENDENCY_READINESS");
                                new ApiDependencyReadiness(
                                        pool, broker.sync(), broker.webLog(), broker.async())
                                    .verify();
                                System.err.println("API startup entered APPLICATION_PREPARATION");
                                ApiApplicationPreparation.executeRetainingUnknown(
                                    pool,
                                    credentials,
                                    java.nio.file.Path.of(
                                        inputs.config().value("nk.api.storage.transfer-root")),
                                    java.nio.file.Path.of(
                                        inputs.config().value("nk.api.storage.asset-root")),
                                    Integer.parseInt(
                                        inputs
                                            .config()
                                            .value("nk.api.storage.asset-manifest-entries")),
                                    java.time.Clock.systemUTC(),
                                    broker.async()::get,
                                    (processors, outbox) -> {
                                      var sync = new ApiSyncRequestDispatcher(processors);
                                      var clock = java.time.Clock.systemUTC();
                                      var worker =
                                          new QuestionWorkerService(
                                              pool,
                                              new StubAnswerProvider(clock),
                                              outbox::wake,
                                              lifetime::stopping,
                                              clock);
                                      System.err.println("API startup entered READY_INFORMATION");
                                      var information = ready.information();
                                      System.err.println("API startup entered OUTBOX_START");
                                      outbox.start();
                                      var groupsReady =
                                          new java.util.concurrent.atomic.AtomicBoolean();
                                      System.err.println("API startup entered MANAGEMENT");
                                      ResourceScope
                                          .<ApiMetricContext<ApiServiceMetricBinding>, Boolean,
                                              IOException>
                                              acquire(
                                                  () ->
                                                      ApiServiceMetricBinding.prepareContext(
                                                          inputs
                                                              .config()
                                                              .value("nk.monitoring.mode"),
                                                          () ->
                                                              HikariDataSource.class
                                                                  .cast(pool)
                                                                  .getHikariPoolMXBean(),
                                                          () ->
                                                              HikariDataSource.class
                                                                  .cast(pool)
                                                                  .getHikariConfigMXBean()),
                                                  ServiceProcessResources.ownedRelease(
                                                      metrics -> metrics.close(), true),
                                                  metrics -> {
                                                    metrics.initialize();
                                                    return ResourceScope.acquire(
                                                        () ->
                                                            ApiManagementServer.bind(
                                                                information,
                                                                applicationReadiness(
                                                                    groupsReady::get,
                                                                    lifetime::stopping,
                                                                    outbox::healthy),
                                                                metrics),
                                                        ServiceProcessResources.ownedRelease(
                                                            ApiManagementServer::close, true),
                                                        management -> {
                                                          management.start();
                                                          System.err.println(
                                                              "API startup entered CONSUMERS");
                                                          return ResourceScope.acquire(
                                                              () ->
                                                                  ApiMessagingRuntime
                                                                      .startRetainingUnknown(
                                                                          broker.sync(),
                                                                          broker.webLog(),
                                                                          broker.async(),
                                                                          lifetime.guardSync(sync),
                                                                          lifetime.guardEvent(
                                                                              new WebLogIngestService(
                                                                                  pool)),
                                                                          lifetime.guardEvent(
                                                                              worker),
                                                                          clock,
                                                                          lifetime
                                                                              .committedFailureHandler(),
                                                                          lifetime::fail),
                                                              ServiceProcessResources.ownedRelease(
                                                                  ApiMessagingRuntime::close, true),
                                                              runtime -> {
                                                                try {
                                                                  groupsReady.set(true);
                                                                  System.err.println(
                                                                      "API startup entered ADMISSION_RELEASE");
                                                                  management.promote(ready);
                                                                  lifetime.await(
                                                                      runtimeReadiness(
                                                                          runtime::ready,
                                                                          outbox::healthy));
                                                                  return Boolean.TRUE;
                                                                } finally {
                                                                  lifetime.stop();
                                                                  groupsReady.set(false);
                                                                }
                                                              });
                                                        });
                                                  });
                                    });
                                return Boolean.TRUE;
                              });
                        });
              });
      // Exact normal whole-cleanup marker; generic stopped diagnostics are not success evidence.
      System.err.println("API cleanup complete");
    }
  }

  // PG-D389/PT-OPS-API-HEALTH001..003. These read-only predicates neither admit nor promote.
  // Bind once, sample on each request, preserve short-circuit order and exact supplier failure.
  static BooleanSupplier applicationReadiness(
      BooleanSupplier groupsReady, BooleanSupplier stopping, BooleanSupplier outboxHealthy) {
    Objects.requireNonNull(groupsReady, "consumer groups readiness");
    Objects.requireNonNull(stopping, "process stop state");
    Objects.requireNonNull(outboxHealthy, "outbox health");
    return () ->
        groupsReady.getAsBoolean() && !stopping.getAsBoolean() && outboxHealthy.getAsBoolean();
  }

  static BooleanSupplier runtimeReadiness(
      BooleanSupplier consumersReady, BooleanSupplier outboxHealthy) {
    Objects.requireNonNull(consumersReady, "consumers readiness");
    Objects.requireNonNull(outboxHealthy, "outbox health");
    return () -> consumersReady.getAsBoolean() && outboxHealthy.getAsBoolean();
  }

  static void fatal(Thread thread, Throwable failure) {
    System.err.println("API process failed");
  }
}
