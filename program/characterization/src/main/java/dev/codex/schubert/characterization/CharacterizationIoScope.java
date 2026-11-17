package dev.codex.schubert.characterization;

import java.io.IOException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Nonnull operation-owned IO, no adapter/baseline/permission authority. PG-D-1171/SS355. */
@NullMarked
final class CharacterizationIoScope {
  @FunctionalInterface
  interface Open<R> {
    R acquire() throws IOException;
  }

  @FunctionalInterface
  interface Release<R> {
    void close(R resource) throws IOException;
  }

  @FunctionalInterface
  interface Work<R, T> {
    T apply(R resource) throws IOException;
  }

  private CharacterizationIoScope() {
    throw new AssertionError("CharacterizationIoScope is a static tool");
  }

  /** All callbacks exist and are checked before acquisition; no unowned post-open handoff. */
  static <R, T> T acquire(Open<R> factory, Release<R> release, Work<R, T> work) throws IOException {
    Objects.requireNonNull(factory, "IO factory");
    Objects.requireNonNull(release, "IO release");
    Objects.requireNonNull(work, "IO work");
    R resource = Objects.requireNonNull(factory.acquire(), "nonnull IO resource");
    T result;
    try {
      result = Objects.requireNonNull(work.apply(resource), "nonnull IO result");
    } catch (IOException | RuntimeException | Error primary) {
      try {
        release.close(resource);
      } catch (IOException | RuntimeException | Error secondary) {
        if (primary != secondary) primary.addSuppressed(secondary);
      }
      throw primary;
    }
    release.close(resource);
    return result;
  }
}
