package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.api.file.ServiceProcessResources;
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
 * override is accepted. The unfinished native assembly is fail-closed, not a fixture-backed
 * service. NK-OPS-001; SYS-002/004; UI212/243/253; SS311/342/343; SSC-083; PG285;
 * PT-OPS-API-MAIN-001..004; 471 R1/D05.
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
    return run(arguments, environment, source, ApiProcessMain::startNative);
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

  private static void startNative(ApiStartupInputs.Values inputs) throws IOException {
    // R1 incremental entry only. D01-D04 are mandatory and are not yet wired. Never expose an
    // HTTP/JMS fixture or report readiness until the real process graph satisfies every gate.
    new ServiceProcessResources(
            new ServiceProcessResources.Inputs(
                ServiceConfigFiles.Service.API,
                inputs.credentials(),
                inputs.config().value("nk.db.url")),
            source -> new ApiJdbcPool().open(source))
        .execute(ServiceProcessResources.unassembledStartup());
  }

  static void fatal(Thread thread, Throwable failure) {
    System.err.println("API process failed");
  }
}
