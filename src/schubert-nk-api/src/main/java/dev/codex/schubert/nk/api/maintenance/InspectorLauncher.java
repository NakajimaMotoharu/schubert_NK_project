package dev.codex.schubert.nk.api.maintenance;

import dev.codex.schubert.nk.api.file.InspectorApplication;
import dev.codex.schubert.nk.api.file.InspectorCredentialException;
import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageProfile;
import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageTerminal;
import java.io.IOException;
import java.io.PrintStream;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Private receipt producer; the required OS wrapper owns process exit mapping. NK-DAT-001;
 * DAT-009/OPS-009; UI212/241/251; SS343 6.8/341/342/352; QA-046/SSC-049/PG-D-144;
 * PT-DB-INBOX-225..232.
 */
@NullMarked
public final class InspectorLauncher {
  private static final Factory NATIVE =
      settings -> new InspectorApplication(settings)::executeNative;

  @FunctionalInterface
  interface Factory {
    Operation create(InspectorSettings settings);
  }

  @FunctionalInterface
  interface Operation {
    InspectionExecution execute(InspectionRun run) throws IOException, NoSuchAlgorithmException;
  }

  public static void main(String[] arguments) throws IOException {
    Thread.currentThread().setUncaughtExceptionHandler(InspectorLauncher::fatal);
    var measurement =
        new FixedNativeCoverageTerminal(
            FixedNativeCoverageProfile.TerminalRole.INSPECTOR, System.getenv("INVOCATION_ID"));
    completeAndClose(
        arguments,
        System.getenv(),
        System.out,
        NATIVE,
        measurement::terminal,
        measurement::closing,
        System.err);
  }

  /** PG-D401: an internal measurement callback only, not an Inspector admission/owner grant. */
  @FunctionalInterface
  interface Capture {
    boolean run() throws IOException;
  }

  /** PT-DB-INBOX-669001..004: receipt must be durable at the stream before terminal capture. */
  static void complete(
      String @Nullable [] arguments,
      @Nullable Map<String, String> environment,
      @Nullable PrintStream output,
      @Nullable Factory factory,
      @Nullable Capture capture,
      @Nullable PrintStream diagnostics)
      throws IOException {
    if (arguments == null
        || environment == null
        || output == null
        || factory == null
        || capture == null
        || diagnostics == null) throw new IllegalArgumentException("inspector entry required");
    new InspectorLauncher().write(arguments, environment, output, factory);
    if (capture.run()) diagnostics.println("Inspector fixed PT native capture complete");
  }

  /** SSC234: completed receipt/terminal callback returns before the finite closing point. */
  static void completeAndClose(
      String @Nullable [] arguments,
      @Nullable Map<String, String> environment,
      @Nullable PrintStream output,
      @Nullable Factory factory,
      @Nullable Capture capture,
      @Nullable Capture closing,
      @Nullable PrintStream diagnostics)
      throws IOException {
    if (closing == null || diagnostics == null)
      throw new IllegalArgumentException("inspector closing required");
    complete(arguments, environment, output, factory, capture, diagnostics);
    if (closing.run()) diagnostics.println("Inspector fixed PT native closing complete");
  }

  /** Returns an internal code, not an OS/parent-gate certificate. */
  public int run(String[] arguments, Map<String, String> environment) {
    return run(arguments, environment, NATIVE);
  }

  int run(String[] arguments, Map<String, String> environment, Factory factory) {
    Objects.requireNonNull(factory, "inspector factory");
    try {
      var configuration = InspectorLaunchConfiguration.read(arguments, environment);
      var operation =
          Objects.requireNonNull(factory.create(configuration.settings()), "inspector operation");
      return Objects.requireNonNull(operation.execute(configuration.run()), "inspection result")
          .exitCode();
    } catch (InspectorLaunchConfiguration.Invalid
        | InspectorCredentialException
        | NoSuchAlgorithmException failure) {
      return 70;
    } catch (IOException failure) {
      return 50;
    }
  }

  void write(
      String[] arguments, Map<String, String> environment, PrintStream output, Factory factory)
      throws IOException {
    Objects.requireNonNull(output, "receipt output");
    int status = run(arguments, environment, factory);
    output.print("NKINSPECTOR1 " + status + "\n");
    if (output.checkError()) throw new IOException("inspector receipt unavailable");
  }

  private static void fatal(Thread thread, Throwable failure) {
    System.err.println("inspector failed");
  }
}
