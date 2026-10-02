package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.api.application.question.QuestionWorkerService;
import dev.codex.schubert.nk.api.application.question.StubAnswerProvider;
import dev.codex.schubert.nk.api.dispatch.ApiDependencyReadiness;
import dev.codex.schubert.nk.api.dispatch.ApiSyncRequestDispatcher;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.api.logging.WebLogIngestService;
import dev.codex.schubert.nk.api.messaging.config.ApiBrokerContexts;
import dev.codex.schubert.nk.api.messaging.inbound.ApiMessagingRuntime;
import dev.codex.schubert.nk.api.storage.ApiApplicationPreparation;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.Objects;
import java.util.function.IntConsumer;
import org.jspecify.annotations.NullMarked;

/**
 * External API entry, never a substitute for mandatory startup admission. No argv configuration
 * override is accepted. The complete graph is borrowed inside its admitted owners; component PT
 * cannot substitute for native readiness. NK-OPS-001; SYS-002/004; UI212/243/253; SS311/342/343;
 * SSC-083/158; PG285/D334; PT-OPS-API-MAIN-001..004/READY001..008; 471 R1/D05.
 */
@NullMarked
public final class ApiProcessMain {
  private final Map<String, String> environment;
  private final NonSecretConfigSource source;
  private final IntConsumer termination;

  public ApiProcessMain() {
    this(System.getenv(), ServiceConfigFiles.production(), System::exit);
  }

  ApiProcessMain(
      Map<String, String> environment, NonSecretConfigSource source, IntConsumer termination) {
    this.environment = Map.copyOf(Objects.requireNonNull(environment, "environment"));
    this.source = Objects.requireNonNull(source, "source");
    this.termination = Objects.requireNonNull(termination, "termination");
  }

  @FunctionalInterface
  interface Startup {
    void execute(ApiStartupInputs.Values inputs) throws IOException;
  }

  public void main(String[] arguments) {
    Thread.currentThread().setUncaughtExceptionHandler(ApiProcessMain::fatal);
    int status = run(arguments, environment, source);
    System.err.println("API process stopped");
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
      ServiceStartupAdmission.create(ServiceConfigFiles.Service.API, environment)
          .execute(
              () -> {
                try {
                  var inputs = loader.load();
                  return new ServiceStartupAdmission.Configuration<>(
                      inputs, inputs.config().canonicalSha256());
                } catch (IllegalArgumentException | NoSuchAlgorithmException failure) {
                  failureCode[0] = 70;
                  throw new IOException("non-secret configuration unavailable");
                }
              },
              (inputs, ready) ->
                  new ServiceProcessResources(
                          new ServiceProcessResources.Inputs(
                              ServiceConfigFiles.Service.API,
                              inputs.credentials(),
                              inputs.config().value("nk.db.url")),
                          source -> new ApiJdbcPool().open(source))
                      .execute(
                          (pool, credentials) -> {
                            try (var broker =
                                ApiBrokerContexts.create(
                                    credentials, inputs.config().value("nk.mq.url"))) {
                              new ApiDependencyReadiness(
                                      pool, broker.sync(), broker.webLog(), broker.async())
                                  .verify();
                              ApiApplicationPreparation.execute(
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
                                    var information = ready.information();
                                    outbox.start();
                                    var groupsReady =
                                        new java.util.concurrent.atomic.AtomicBoolean();
                                    try (var management =
                                        ApiManagementServer.open(
                                            information,
                                            () ->
                                                groupsReady.get()
                                                    && !lifetime.stopping()
                                                    && outbox.healthy())) {
                                      try (var runtime =
                                          ApiMessagingRuntime.start(
                                              broker.sync(),
                                              broker.webLog(),
                                              broker.async(),
                                              lifetime.guardSync(sync),
                                              lifetime.guardEvent(new WebLogIngestService(pool)),
                                              lifetime.guardEvent(worker),
                                              clock,
                                              failure -> lifetime.fail(),
                                              lifetime::fail)) {
                                        try {
                                          groupsReady.set(true);
                                          management.promote(ready);
                                          lifetime.await(() -> runtime.ready() && outbox.healthy());
                                        } finally {
                                          lifetime.stop();
                                          groupsReady.set(false);
                                        }
                                      }
                                    }
                                  });
                            }
                          }));
      // Exact normal whole-cleanup marker; generic stopped diagnostics are not success evidence.
      System.err.println("API cleanup complete");
    }
  }

  static void fatal(Thread thread, Throwable failure) {
    System.err.println("API process failed");
  }
}
