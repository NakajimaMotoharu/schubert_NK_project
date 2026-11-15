package dev.codex.schubert.nk.storage;

import java.io.Closeable;
import java.io.IOException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * One owned I/O release with explicit compound failure precedence, never a TWR self-suppression.
 * NK-OPS-001/OPS009/FIL001..009/UI237/251/SS333; SSC063/PG170; RSCOPE001..008. Arguments are
 * validated before ownership is accepted. Callback null values stay explicit.
 */
@NullMarked
public interface ResourceScope {

  @FunctionalInterface
  interface Action<T extends @Nullable Object> {
    T run() throws IOException;
  }

  /** SSC308/PT-IOFACT-001..005: all ports exist before this acquisition is invoked. */
  @FunctionalInterface
  interface Acquire<R, E extends IOException> {
    @Nullable R open() throws E;
  }

  @FunctionalInterface
  interface Release<R> {
    void close(R resource) throws IOException;
  }

  @FunctionalInterface
  interface OwnedAction<R, T extends @Nullable Object> {
    T run(R resource) throws IOException;
  }

  /**
   * Builds a complete, nonnull owner before transferring responsibility for R
   * (SSC308/IOFACT013-018). All state and callbacks precede acquisition. Factory failures preserve
   * E; incomplete assembly releases R once with acquire's existing compound precedence. A returned
   * owner, not this helper, then owns R. A nullable T bound permits testing rejected null assembly,
   * never a null owner result.
   */
  static <R, T extends @Nullable Object, E extends IOException> T handoff(
      Acquire<R, E> acquire, Release<R> release, OwnedAction<R, T> assemble)
      throws E, StorageIoException {
    Objects.requireNonNull(acquire, "resource acquire");
    Objects.requireNonNull(release, "resource release");
    Objects.requireNonNull(assemble, "complete owner assembly");
    boolean[] transferred = new boolean[1];
    return ResourceScope.<R, T, E>acquire(
        acquire,
        resource -> {
          if (!transferred[0]) release.close(resource);
        },
        resource -> {
          T complete = Objects.requireNonNull(assemble.run(resource), "complete resource owner");
          transferred[0] = true;
          return complete;
        });
  }

  /**
   * SSC308/PT-IOFACT-001..012: factory failures retain E/identity; owned failures follow use's
   * explicit IO precedence. No callback or wrapper is allocated after ownership starts.
   */
  static <R, T extends @Nullable Object, E extends IOException> T acquire(
      Acquire<R, E> acquire, Release<R> release, OwnedAction<R, T> action)
      throws E, StorageIoException {
    Objects.requireNonNull(acquire, "resource acquire");
    Objects.requireNonNull(release, "resource release");
    Objects.requireNonNull(action, "resource action");
    @Nullable R resource = acquire.open();
    try {
      T result;
      R owned;
      try {
        owned = Objects.requireNonNull(resource, "acquired resource");
        result = action.run(owned);
      } catch (IOException | RuntimeException | Error primary) {
        if (resource != null) {
          try {
            release.close(resource);
          } catch (IOException | RuntimeException | Error secondary) {
            if (primary instanceof IOException && !(secondary instanceof IOException))
              throw secondary;
            primary.addSuppressed(new StorageIoException(StorageIoException.Reason.UNAVAILABLE));
          }
        }
        throw primary;
      }
      release.close(owned);
      return result;
    } catch (IOException failure) {
      throw new StorageIoException(
          failure instanceof StorageIoException storage && failure.getSuppressed().length == 0
              ? storage.reason()
              : StorageIoException.Reason.UNAVAILABLE);
    }
  }

  static <T extends @Nullable Object> T use(Closeable release, Action<T> action)
      throws StorageIoException {
    Objects.requireNonNull(release, "resource release");
    Objects.requireNonNull(action, "resource action");
    try {
      T result;
      try {
        result = action.run();
      } catch (IOException | RuntimeException | Error primary) {
        try {
          release.close();
        } catch (IOException | RuntimeException | Error secondary) {
          if (primary instanceof IOException && !(secondary instanceof IOException))
            throw secondary;
          primary.addSuppressed(new StorageIoException(StorageIoException.Reason.UNAVAILABLE));
        }
        throw primary;
      }
      release.close();
      return result;
    } catch (IOException failure) {
      throw new StorageIoException(
          failure instanceof StorageIoException storage && failure.getSuppressed().length == 0
              ? storage.reason()
              : StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
