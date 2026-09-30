package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import java.io.IOException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * External root Cleanup entry. Until the parent-owned M/A, terminal-unit, DELETE, transfer and
 * durable result contract is joined, this entry always refuses 0/10 and blocks Artemis Requires. No
 * caller-supplied path, credential, run, URL or test bypass. NK-OPS-001/NK-BAT-001;
 * OPS009/BAK001/UI251/SS341/342/343/SSC104/PG334; PT-OPS-CMAIN001 onward.
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

  private CleanupProcessMain() {}

  public static void main(String[] arguments) {
    Thread.currentThread().setUncaughtExceptionHandler(CleanupProcessMain::fatal);
    System.exit(
        arguments.length == 1 && "--expiry".equals(arguments[0])
            ? runExpiry(arguments, CleanupExpiryExecution::execute)
            : run(arguments, CleanupNativePreflight::verify));
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
