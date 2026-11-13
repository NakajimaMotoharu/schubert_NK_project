package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * External root Cleanup entry. Native 0/10 requires the genuine parent owner, actual Unit/DB
 * Inspector, committed deletion/Transfer and independent durable result readback. The legacy
 * read-only preflight test port never returns 0/10. No caller-supplied path, credential, run, URL
 * or test bypass. NK-OPS-001/NK-BAT-001; OPS009/BAK001/UI251/SS341/342/343/SSC104/PG334;
 * PT-OPS-CMAIN001 onward.
 */
@NullMarked
public final class CleanupProcessMain {
  @FunctionalInterface
  interface Preflight {
    BackupManifest verify() throws IOException;
  }

  @FunctionalInterface
  interface ExpiryWork {
    int execute() throws IOException;
  }

  private final ExpiryWork nativeCleanup;
  private final ExpiryWork nativeExpiry;
  private final java.util.function.IntConsumer termination;

  /** SSC299: standard Java25 noarg entry binds only the fixed native operations. */
  public CleanupProcessMain() {
    this(CleanupNativeExecution::execute, CleanupExpiryExecution::execute, System::exit);
  }

  CleanupProcessMain(
      ExpiryWork nativeCleanup,
      ExpiryWork nativeExpiry,
      java.util.function.IntConsumer termination) {
    this.nativeCleanup = Objects.requireNonNull(nativeCleanup, "native Cleanup operation");
    this.nativeExpiry = Objects.requireNonNull(nativeExpiry, "native Expiry operation");
    this.termination = Objects.requireNonNull(termination, "OS exit request");
  }

  public void main(String[] arguments) {
    Thread.currentThread().setUncaughtExceptionHandler(CleanupProcessMain::fatal);
    termination.accept(
        arguments.length == 1 && "--expiry".equals(arguments[0])
            ? runExpiry(arguments, nativeExpiry)
            : runNative(arguments, nativeCleanup));
  }

  static int runExpiry(String[] arguments, ExpiryWork work) {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(work, "genuine Expiry work");
    if (arguments.length != 1 || !"--expiry".equals(arguments[0])) return 70;
    try {
      int result = work.execute();
      return result == 0 || result == 10 || result == 30 ? result : 30;
    } catch (IOException
        | dev.codex.schubert.nk.batch.repository.BatchRepositoryException
        | dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessException
        | dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeException known) {
      if (!(known instanceof IOException)) StorageIoException.preserveFatal(known);
      return 30;
    }
  }

  static int runNative(String[] arguments, ExpiryWork work) {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(work, "genuine Cleanup work");
    if (arguments.length != 0) return 70;
    try {
      int result = work.execute();
      return result == 0 || result == 10 || result == 30 ? result : 30;
    } catch (IOException
        | dev.codex.schubert.nk.batch.repository.BatchRepositoryException
        | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException
        | dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoff.Failure known) {
      if (!(known instanceof IOException)) StorageIoException.preserveFatal(known);
      return 30;
    }
  }

  static int run(String[] arguments, Preflight preflight) {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(preflight, "native preflight");
    if (arguments.length != 0) return 70;
    try {
      Objects.requireNonNull(preflight.verify(), "verified backup observation");
      // An observation is not deletion, parent M/A, transfer or a durable completion record.
      return 30;
    } catch (IOException unavailable) {
      return 30;
    }
  }

  static void fatal(Thread thread, Throwable failure) {
    System.err.println("cleanup process failed");
  }
}
