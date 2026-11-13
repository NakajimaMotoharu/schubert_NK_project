package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.Objects;
import java.util.function.IntConsumer;
import org.jspecify.annotations.NullMarked;

/**
 * External WEB entry, never a substitute for mandatory startup admission. No argv configuration
 * override is accepted. The unfinished native assembly is fail-closed, not a fixture-backed
 * service. NK-OPS-001; SYS-002/004; UI212/243/253; SS311/342/343; SSC-083; PG285;
 * PT-OPS-WEB-MAIN-001..004; 471 R1/D05.
 */
@NullMarked
public final class WebProcessMain {
  private final Map<String, String> environment;
  private final NonSecretConfigSource source;
  private final IntConsumer termination;
  private final WebTerminalCapture.Factory captures;

  public WebProcessMain() {
    this(System.getenv(), ServiceConfigFiles.production(), System::exit);
  }

  WebProcessMain(
      Map<String, String> environment, NonSecretConfigSource source, IntConsumer termination) {
    this(environment, source, termination, WebTerminalCapture::currentJvm);
  }

  WebProcessMain(
      Map<String, String> environment,
      NonSecretConfigSource source,
      IntConsumer termination,
      WebTerminalCapture.Factory captures) {
    this.environment = Map.copyOf(Objects.requireNonNull(environment, "environment"));
    this.source = Objects.requireNonNull(source, "source");
    this.termination = Objects.requireNonNull(termination, "termination");
    this.captures = Objects.requireNonNull(captures, "native PT captures");
  }

  @FunctionalInterface
  interface Startup {
    void execute(WebStartupInputs.Values inputs) throws IOException;
  }

  public void main(String[] arguments) throws IOException {
    Thread.currentThread().setUncaughtExceptionHandler(WebProcessMain::fatal);
    var coverage = captures.find(environment.get("INVOCATION_ID"));
    int status;
    if (coverage.isPresent()) {
      try (var hold = coverage.orElseThrow().open()) {
        hold.verifyOwner();
        status = run(arguments, environment, source);
        System.err.println("WEB process stopped");
        coverage.orElseThrow().capture();
        hold.verifyOwner();
        System.err.println("WEB fixed PT native capture complete");
      }
    } else {
      status = run(arguments, environment, source);
      System.err.println("WEB process stopped");
    }
    termination.accept(status);
  }

  int run(String[] arguments, Map<String, String> environment, NonSecretConfigSource source) {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(environment, "environment");
    Objects.requireNonNull(source, "non-secret source");
    if (arguments.length != 0) return 70;
    WebStartupInputs loader;
    try {
      loader = new WebStartupInputs(source, environment);
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
    WebStartupInputs.Values inputs;
    try {
      inputs = new WebStartupInputs(source, environment).load();
    } catch (IllegalArgumentException | NoSuchAlgorithmException failure) {
      SessionStoreException.preserveFatal(failure);
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
      WebStartupInputs loader, Map<String, String> environment, int[] failureCode)
      throws IOException {
    // One admitted owner: UNKNOWN never unwinds its DB/key/root callback frame.
    try (var lifetime = new WebProcessLifetime()) {
      lifetime.install();
      ServiceStartupAdmission.create(ServiceConfigFiles.Service.WEB, environment)
          .execute(
              () -> admittedConfiguration(loader, failureCode),
              (inputs, ready) ->
                  new ServiceProcessResources(
                          new ServiceProcessResources.Inputs(
                              ServiceConfigFiles.Service.WEB,
                              inputs.credentials(),
                              inputs.config().value("nk.db.url")),
                          source -> new WebJdbcPool().open(source))
                      .executeRetainingUnknown(
                          (pool, credentials) -> {
                            var runtime =
                                new WebNativeRuntime(
                                    pool, credentials, inputs.config(), ready, lifetime::stopping);
                            WebRuntimeExecution.execute(
                                runtime::start,
                                () -> lifetime.await(runtime::healthy),
                                lifetime::stop,
                                runtime::close);
                          }));
      System.err.println("WEB cleanup complete");
    }
  }

  static void fatal(Thread thread, Throwable failure) {
    System.err.println("WEB process failed");
  }

  /** PG-D378/WEB-REM006: original admission callback, no file/identity/factory override. */
  static ServiceStartupAdmission.Configuration<WebStartupInputs.Values> admittedConfiguration(
      WebStartupInputs loader, int[] failureCode) throws IOException {
    try {
      var inputs = loader.load();
      return new ServiceStartupAdmission.Configuration<>(inputs, inputs.config().canonicalSha256());
    } catch (IllegalArgumentException | NoSuchAlgorithmException failure) {
      SessionStoreException.preserveFatal(failure);
      failureCode[0] = 70;
      throw new IOException("non-secret configuration unavailable");
    }
  }
}
