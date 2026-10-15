package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint;
import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageProfile;
import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageStopHold;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * NK-OPS-001/SS342343352/PG-D378/WEB-REM005. Fixed native capture; package-local test boundary
 * only.
 */
@NullMarked
final class WebTerminalCapture {
  @FunctionalInterface
  interface Factory {
    Optional<WebTerminalCapture> find(@Nullable String invocation) throws IOException;
  }

  @FunctionalInterface
  interface Open {
    Owner<?> get() throws IOException;
  }

  @FunctionalInterface
  interface Capture {
    void run(FixedNativeCoverageCheckpoint.Point point) throws IOException;
  }

  @FunctionalInterface
  interface Operation<T> {
    void run(T owner) throws IOException;
  }

  static final class Owner<T> implements AutoCloseable {
    private final T retainedOwner;
    private final Operation<T> verify;
    private final Operation<T> retainedClose;

    Owner(T owner, Operation<T> verify, Operation<T> close) {
      this.retainedOwner = Objects.requireNonNull(owner, "native PT stop owner");
      this.verify = Objects.requireNonNull(verify, "native PT owner verification");
      this.retainedClose = Objects.requireNonNull(close, "native PT owner close");
    }

    void verifyOwner() throws IOException {
      verify.run(retainedOwner);
    }

    @Override
    public void close() throws IOException {
      retainedClose.run(retainedOwner);
    }
  }

  private final Open retainedOpen;
  private final Capture retainedCapture;

  WebTerminalCapture(Open open, Capture capture) {
    this.retainedOpen = Objects.requireNonNull(open, "native PT open");
    this.retainedCapture = Objects.requireNonNull(capture, "native PT capture");
  }

  static Optional<WebTerminalCapture> currentJvm(@Nullable String invocation) throws IOException {
    return FixedNativeCoverageCheckpoint.fromCurrentJvm(
            ServiceConfigFiles.Service.WEB, FixedNativeCoverageProfile.Phase.ORDINARY, invocation)
        .map(
            checkpoint ->
                new WebTerminalCapture(
                    () -> {
                      var hold = FixedNativeCoverageStopHold.open();
                      return new Owner<>(
                          hold,
                          FixedNativeCoverageStopHold::verifyOwner,
                          FixedNativeCoverageStopHold::close);
                    },
                    checkpoint::capture));
  }

  Owner<?> open() throws IOException {
    return Objects.requireNonNull(retainedOpen.get(), "native PT owner");
  }

  void capture() throws IOException {
    retainedCapture.run(FixedNativeCoverageCheckpoint.Point.TERMINAL);
  }
}
