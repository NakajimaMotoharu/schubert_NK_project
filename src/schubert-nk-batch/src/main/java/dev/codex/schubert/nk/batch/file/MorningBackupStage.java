package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.time.Clock;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Production parent bridge from the continuously held M/A/original/DB scope to committed backup
 * begins and new-only request publication. The work callback remains within all owners and must
 * itself prove worker start/full termination, archives and later parent gates; this bridge alone
 * never marks a backup successful. NK-OPS-001; OPS009/BAK001/UI251/SS341§5-6/343§6.15;
 * SSC089/092/094/104/105; PG349/PT-OPS-MBSTAGE001-004.
 */
@NullMarked
final class MorningBackupStage {
  interface Scope {
    <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation) throws IOException;
  }

  private MorningBackupStage() {}

  static <T> T fresh(MorningBackupPreparation.Continuation<T> work) throws IOException {
    Objects.requireNonNull(work, "fresh backup work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    return execute(
        MorningControlScope::executeOwned,
        MorningBackupRequestPublication.create(root, snapshot),
        Clock.systemUTC(),
        false,
        UUID.randomUUID(),
        work);
  }

  static <T> T resume(UUID runId, MorningBackupPreparation.Continuation<T> work)
      throws IOException {
    Objects.requireNonNull(runId, "explicit resume run");
    Objects.requireNonNull(work, "resume backup work");
    var root = RootStartupContext.create();
    var snapshot = root.capture(RootStartupContext.Service.MORNING);
    Scope scope =
        new Scope() {
          @Override
          public <R> R execute(MorningNewRunAdmission.OwnedContinuation<R> continuation)
              throws IOException {
            return MorningControlScope.executeResumeOwned(runId, continuation);
          }
        };
    return execute(
        scope,
        MorningBackupRequestPublication.create(root, snapshot),
        Clock.systemUTC(),
        true,
        UUID.randomUUID(),
        work);
  }

  static <T> T execute(
      Scope scope,
      MorningBackupPreparation.Publisher publisher,
      Clock clock,
      boolean recoverAbandoned,
      UUID part,
      MorningBackupPreparation.Continuation<T> work)
      throws IOException {
    Objects.requireNonNull(scope, "owned Morning control scope");
    Objects.requireNonNull(publisher, "root request publication");
    Objects.requireNonNull(clock, "UTC backup clock");
    Objects.requireNonNull(part, "new request part");
    Objects.requireNonNull(work, "same-owner backup work");
    return Objects.requireNonNull(
        scope.execute(
            (state, database) ->
                MorningBackupPreparation.execute(
                    state, database, clock, recoverAbandoned, publisher, part, work)),
        "Morning backup stage result");
  }
}
