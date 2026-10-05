package dev.codex.schubert.nk.web.bootstrap;

import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import org.jspecify.annotations.NullMarked;

/**
 * NK-WEB-002/SS313342352/PG-D378/WEB-REM002. Same captured terminal flag; no close or diagnostic.
 */
@NullMarked
final class WebRuntimeFailureSignal<T extends Throwable> implements Runnable, Consumer<T> {
  private final AtomicBoolean terminal;

  WebRuntimeFailureSignal(AtomicBoolean terminal) {
    this.terminal = Objects.requireNonNull(terminal, "Web terminal flag");
  }

  @Override
  public void run() {
    terminal.set(true);
  }

  @Override
  public void accept(T ignored) {
    terminal.set(true);
  }
}
