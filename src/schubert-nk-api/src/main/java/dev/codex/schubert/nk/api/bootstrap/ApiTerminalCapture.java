package dev.codex.schubert.nk.api.bootstrap;

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
 * NK-OPS-001/SS342343352/PG-D412/API-TAIL005. Fixed native capture; package-local test boundary
 * only.
 */
@NullMarked
final class ApiTerminalCapture {
  @FunctionalInterface
  interface Factory {
    Optional<ApiTerminalCapture> find(@Nullable String invocation) throws IOException;
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
    private final T owner;
    private final Operation<T> verify;
    private final Operation<T> close;

    Owner(T owner, Operation<T> verify, Operation<T> close) {
      this.owner = Objects.requireNonNull(owner, "native PT stop owner");
      this.verify = Objects.requireNonNull(verify, "native PT owner verification");
      this.close = Objects.requireNonNull(close, "native PT owner close");
    }

    void verifyOwner() throws IOException {
      verify.run(owner);
    }

    @Override
    public void close() throws IOException {
      close.run(owner);
    }
  }

  private final Open open;
  private final Capture capture;

  ApiTerminalCapture(Open open, Capture capture) {
    this.open = Objects.requireNonNull(open, "native PT open");
    this.capture = Objects.requireNonNull(capture, "native PT capture");
  }

  static Optional<ApiTerminalCapture> currentJvm(@Nullable String invocation) throws IOException {
    return FixedNativeCoverageCheckpoint.fromCurrentJvm(
            ServiceConfigFiles.Service.API, FixedNativeCoverageProfile.Phase.ORDINARY, invocation)
        .map(
            checkpoint ->
                new ApiTerminalCapture(
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
    return Objects.requireNonNull(open.get(), "native PT owner");
  }

  void capture() throws IOException {
    capture.run(FixedNativeCoverageCheckpoint.Point.TERMINAL);
  }
}
