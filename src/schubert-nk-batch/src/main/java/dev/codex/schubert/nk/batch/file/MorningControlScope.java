package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.MorningStopPass;
import dev.codex.schubert.nk.batch.platform.MorningUnitTerminals;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxFileLock;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Same-parent Morning M→fixed-eight stop→A→fresh-eight boundary. The supplied trusted work runs
 * only after A's fresh observation and remains inside both locks. This scope does not establish a
 * run original, invalidate current, prove clean Artemis journal, execute backup/Cleanup or issue a
 * startup permit. An unresolved stop-client attempt must not return from MorningStopPass; the
 * handle-less UNKNOWN and systemd hard-timeout recovery remain unaccepted. NK-OPS-001;
 * OPS009/UI251/253/SS341§4-5/343/SSC100-102/105; PG341/PT-OPS-MCTRL001-007.
 */
@NullMarked
final class MorningControlScope {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface Exclusive {
    <T> Optional<T> execute(LinuxFileLock.Operation<T> operation) throws IOException;
  }

  @FunctionalInterface
  interface StartupExclusive {
    <T> Optional<T> execute(LinuxFileLock.StartupOperation<T> operation) throws IOException;
  }

  @FunctionalInterface
  interface StopPass {
    void execute() throws IOException;
  }

  @FunctionalInterface
  interface Terminals {
    void requireAll() throws IOException;
  }

  private MorningControlScope() {}

  static <T> T execute(LinuxFileLock.Operation<T> trustedWork) throws IOException {
    Objects.requireNonNull(trustedWork, "trusted Morning work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    var maintenance = MaintenanceFileLock.create();
    var startup = StartupAdmissionFile.create();
    return execute(
        () -> root.recheck(snapshot),
        maintenance::tryExclusive,
        () -> MorningStopPass.create(root, snapshot).execute(),
        startup::tryExclusive,
        () -> MorningUnitTerminals.requireQuiescent(root, snapshot),
        trustedWork);
  }

  static <T> T execute(
      Gate root,
      Exclusive maintenance,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      LinuxFileLock.Operation<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(root, "Morning root gate");
    Objects.requireNonNull(maintenance, "fixed M lock");
    Objects.requireNonNull(stop, "fixed eight stop pass");
    Objects.requireNonNull(startup, "fixed A lock");
    Objects.requireNonNull(terminals, "fresh eight terminals");
    Objects.requireNonNull(trustedWork, "trusted Morning work");
    root.verify();
    Optional<T> afterMaintenance =
        maintenance.execute(
            () -> {
              root.verify();
              stop.execute();
              root.verify();
              Optional<T> afterStartup =
                  startup.execute(
                      borrowedDescriptor -> {
                        // A's reserved descriptor stays owned by StartupAdmissionFile. It is
                        // never exported to the work or used as a substitute for Unit proof.
                        root.verify();
                        terminals.requireAll();
                        root.verify();
                        T result =
                            Objects.requireNonNull(trustedWork.execute(), "Morning work result");
                        root.verify();
                        return result;
                      });
              if (afterStartup.isEmpty()) throw unavailable();
              root.verify();
              return afterStartup.orElseThrow();
            });
    if (afterMaintenance.isEmpty()) throw unavailable();
    root.verify();
    return afterMaintenance.orElseThrow();
  }

  private static IOException unavailable() {
    return new IOException("Morning control scope unavailable");
  }
}
