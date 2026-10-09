package dev.codex.schubert.nk.bootstrap;

import java.io.IOException;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC234 same-main finite measurement lifecycle, not business admission/termination authority.
 * NK-OPS-001/TST004/OPS009/UI251/SS342343354/451/PT-OPS-CLOSE743001..004.
 */
@NullMarked
public final class FixedNativeCoverageTerminal {
  @FunctionalInterface
  interface Factory {
    @Nullable Optional<FixedNativeCoverageCheckpoint> open() throws IOException;
  }

  private final Thread owner = Thread.currentThread();
  private final Factory factory;
  private Optional<FixedNativeCoverageCheckpoint> checkpoint = Optional.empty();
  private boolean terminalAttempted;
  private boolean terminalReturned;
  private boolean closingAttempted;

  public FixedNativeCoverageTerminal(
      FixedNativeCoverageProfile.@Nullable TerminalRole role, @Nullable String invocation) {
    if (role == null) throw new IllegalArgumentException("fixed PT terminal role required");
    factory = () -> FixedNativeCoverageCheckpoint.fromCurrentTerminalJvm(role, invocation);
  }

  FixedNativeCoverageTerminal(@Nullable Factory factory) {
    if (factory == null) throw new IllegalArgumentException("fixed PT terminal factory required");
    this.factory = factory;
  }

  public boolean terminal() throws IOException {
    FixedNativeCoverageCheckpoint.require(Thread.currentThread() == owner);
    FixedNativeCoverageCheckpoint.require(!terminalAttempted);
    terminalAttempted = true;
    var opened = factory.open();
    // The nullable factory observation is validated before storing the invariant.
    if (opened == null) throw FixedNativeCoverageCheckpoint.unavailable();
    checkpoint = opened;
    if (checkpoint.isPresent())
      checkpoint.orElseThrow().capture(FixedNativeCoverageCheckpoint.Point.TERMINAL);
    terminalReturned = true;
    return checkpoint.isPresent();
  }

  public boolean closing() throws IOException {
    FixedNativeCoverageCheckpoint.require(Thread.currentThread() == owner);
    FixedNativeCoverageCheckpoint.require(!closingAttempted);
    closingAttempted = true;
    FixedNativeCoverageCheckpoint.require(terminalReturned);
    if (checkpoint.isEmpty()) return false;
    checkpoint.orElseThrow().capture(FixedNativeCoverageCheckpoint.Point.CLOSING);
    return true;
  }
}
