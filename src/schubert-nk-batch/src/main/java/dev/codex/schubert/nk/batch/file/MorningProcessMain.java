package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import java.io.IOException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fail-closed external Morning root entry while the remaining parent transaction is assembled. It
 * authenticates the fixed root actor, holds M and checks all eight effective stop policies via
 * MorningRootScope, but never stops a Unit, changes current, begins backup or grants a permit.
 * Returning 0/10 would misrepresent this read-only admission, so every valid invocation exits 30.
 * No raw diagnostic is printed. NK-OPS-001; OPS009/UI251/SS341/343/SSC100-102; PG339;
 * PT-OPS-MMAIN001-007.
 */
@NullMarked
public final class MorningProcessMain {
  @FunctionalInterface
  interface Admission {
    void verify(MorningParentBudget budget) throws IOException;
  }

  private MorningProcessMain() {}

  public static void main(String[] args) {
    System.exit(
        run(
            args,
            budget ->
                MorningRootScope.execute(
                    () -> {
                      budget.requireWithin();
                      return Boolean.TRUE;
                    })));
  }

  static int run(String[] args, Admission admission) {
    Objects.requireNonNull(args, "Morning arguments");
    Objects.requireNonNull(admission, "fixed Morning admission");
    if (args.length != 0) return 70;
    var budget = MorningParentBudget.create();
    try {
      budget.requireWithin();
      admission.verify(budget);
      budget.requireWithin();
      return 30;
    } catch (IOException | StopGateException known) {
      return 30;
    }
  }
}
