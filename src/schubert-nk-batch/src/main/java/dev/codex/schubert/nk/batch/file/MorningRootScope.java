package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClient;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxFileLock;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed Morning root/M ownership boundary. All eight effective stop policies must be deployable
 * before the trusted continuation may issue any stop or change. The continuation remains inside M;
 * it must retain an unresolved stop-client attempt instead of returning on UNKNOWN. This boundary
 * neither acquires A nor stops a Unit, begins backup, issues a permit or grants startup authority.
 * NK-OPS-001; OPS009/UI251/SS341§3-5/343/SSC100-102; PG336/PT-OPS-MROOT001-006.
 */
@NullMarked
final class MorningRootScope {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface Exclusive {
    <T> Optional<T> execute(LinuxFileLock.Operation<T> operation) throws IOException;
  }

  @FunctionalInterface
  interface Policy {
    void preflight() throws IOException;
  }

  private MorningRootScope() {}

  static <T> T execute(LinuxFileLock.Operation<T> continuation) throws IOException {
    Objects.requireNonNull(continuation, "trusted Morning continuation");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    var lock = MaintenanceFileLock.create();
    return execute(
        () -> root.recheck(snapshot),
        lock::tryExclusive,
        () -> MaintenanceUnitStopClient.create(root, snapshot).preflightAll(),
        continuation);
  }

  static <T> T execute(
      Gate root, Exclusive lock, Policy policy, LinuxFileLock.Operation<T> continuation)
      throws IOException {
    Objects.requireNonNull(root, "Morning root identity");
    Objects.requireNonNull(lock, "fixed M owner");
    Objects.requireNonNull(policy, "fixed eight-Unit policy");
    Objects.requireNonNull(continuation, "trusted Morning continuation");
    root.verify();
    Optional<T> result =
        lock.execute(
            () -> {
              root.verify();
              policy.preflight();
              root.verify();
              T value = Objects.requireNonNull(continuation.execute(), "Morning result");
              root.verify();
              return value;
            });
    if (result.isEmpty()) throw new IOException("Morning root admission unavailable");
    root.verify();
    return result.orElseThrow();
  }
}
