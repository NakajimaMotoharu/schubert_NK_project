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
 * Same-parent Morning M→dedicated DB/advisory→original→fixed-eight stop→A→fresh-eight boundary. The
 * supplied trusted work runs only after A's fresh observation and remains inside M, A, DB and the
 * original scope. This does not invalidate current, prove clean Artemis journal, execute
 * backup/Cleanup or issue a startup permit. An unresolved stop-client must not return from
 * MorningStopPass; handle-less UNKNOWN/hard-timeout recovery remain unaccepted. NK-OPS-001;
 * OPS009/UI251/253/SS341§3-5/343/SSC094/100-102/105; PG341/343/PT-OPS-MCTRL001-009.
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

  interface Original {
    <T> T execute(MorningNewRunAdmission.Continuation<T> continuation) throws IOException;
  }

  @FunctionalInterface
  interface Terminals {
    void requireAll() throws IOException;
  }

  private MorningControlScope() {}

  static <T> T execute(MorningNewRunAdmission.Continuation<T> trustedWork) throws IOException {
    Objects.requireNonNull(trustedWork, "trusted Morning work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    var maintenance = MaintenanceFileLock.create();
    var startup = StartupAdmissionFile.create();
    return execute(
        () -> root.recheck(snapshot),
        maintenance::tryExclusive,
        new Original() {
          @Override
          public <T> T execute(MorningNewRunAdmission.Continuation<T> continuation)
              throws IOException {
            // Fresh release/BOM admission and the dedicated DB owner are constructed only under M.
            return MorningNewRunAdmission.create(root, snapshot).execute(continuation);
          }
        },
        () -> MorningStopPass.create(root, snapshot).execute(),
        startup::tryExclusive,
        () -> MorningUnitTerminals.requireQuiescent(root, snapshot),
        trustedWork);
  }

  static <T> T execute(
      Gate root,
      Exclusive maintenance,
      Original original,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      MorningNewRunAdmission.Continuation<T> trustedWork)
      throws IOException {
    Objects.requireNonNull(original, "dedicated DB and durable original");
    Objects.requireNonNull(stop, "fixed eight stop pass");
    Objects.requireNonNull(startup, "fixed A lock");
    Objects.requireNonNull(terminals, "fresh eight terminals");
    Objects.requireNonNull(trustedWork, "same-run Morning work");
    return executeStopAndStartup(
        root,
        maintenance,
        () ->
            original.execute(
                state -> {
                  root.verify();
                  return afterOriginal(
                      root, stop, startup, terminals, () -> trustedWork.execute(state));
                }));
  }

  static <T> T execute(
      Gate root,
      Exclusive maintenance,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      LinuxFileLock.Operation<T> trustedWork)
      throws IOException {
    // Isolated PT port for the PG341 stop/A boundary. The native factory above always uses the
    // original-owning overload; this overload alone is never a Production Morning entry.
    Objects.requireNonNull(stop, "fixed eight stop pass");
    Objects.requireNonNull(startup, "fixed A lock");
    Objects.requireNonNull(terminals, "fresh eight terminals");
    Objects.requireNonNull(trustedWork, "trusted Morning work");
    return executeStopAndStartup(
        root, maintenance, () -> afterOriginal(root, stop, startup, terminals, trustedWork));
  }

  private static <T> T executeStopAndStartup(
      Gate root, Exclusive maintenance, LinuxFileLock.Operation<T> afterMaintenance)
      throws IOException {
    Objects.requireNonNull(root, "Morning root gate");
    Objects.requireNonNull(maintenance, "fixed M lock");
    Objects.requireNonNull(afterMaintenance, "owned Morning work");
    root.verify();
    Optional<T> completed =
        maintenance.execute(
            () -> {
              root.verify();
              T result =
                  Objects.requireNonNull(afterMaintenance.execute(), "Morning M work result");
              root.verify();
              return result;
            });
    if (completed.isEmpty()) throw unavailable();
    root.verify();
    return completed.orElseThrow();
  }

  private static <T> T afterOriginal(
      Gate root,
      StopPass stop,
      StartupExclusive startup,
      Terminals terminals,
      LinuxFileLock.Operation<T> trustedWork)
      throws IOException {
    stop.execute();
    root.verify();
    Optional<T> afterStartup =
        startup.execute(
            borrowedDescriptor -> {
              // A's reserved descriptor stays owned by StartupAdmissionFile. It is never exported
              // to the work or used as a substitute for Unit proof.
              root.verify();
              terminals.requireAll();
              root.verify();
              T result = Objects.requireNonNull(trustedWork.execute(), "Morning work result");
              root.verify();
              return result;
            });
    if (afterStartup.isEmpty()) throw unavailable();
    return afterStartup.orElseThrow();
  }

  private static IOException unavailable() {
    return new IOException("Morning control scope unavailable");
  }
}
