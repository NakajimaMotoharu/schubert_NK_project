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
public final class ResourceScope {
  private ResourceScope() {}

  @FunctionalInterface
  public interface Action<T extends @Nullable Object> {
    T run() throws IOException;
  }

  /** SSC308/PT-IOFACT-001..005: all ports exist before this acquisition is invoked. */
  @FunctionalInterface
  public interface Acquire<R, E extends IOException> {
    @Nullable R open() throws E;
  }

  @FunctionalInterface
  public interface Release<R> {
    void close(R resource) throws IOException;
  }

  @FunctionalInterface
  public interface OwnedAction<R, T extends @Nullable Object> {
    T run(R resource) throws IOException;
  }

  /**
   * SSC308/PT-IOFACT-001..012: factory failures retain E/identity; owned failures follow use's
   * explicit IO precedence. No callback or wrapper is allocated after ownership starts.
   */
  public static <R, T extends @Nullable Object, E extends IOException> T acquire(
      Acquire<R, E> acquire, Release<R> release, OwnedAction<R, T> action)
      throws E, StorageIoException {
    Objects.requireNonNull(acquire, "resource acquire");
    Objects.requireNonNull(release, "resource release");
    Objects.requireNonNull(action, "resource action");
    @Nullable R resource = acquire.open();
    if (resource == null) throw new NullPointerException("acquired resource");
    try {
      T result;
      try {
        result = action.run(resource);
      } catch (IOException | RuntimeException | Error primary) {
        try {
          release.close(resource);
        } catch (IOException | RuntimeException | Error secondary) {
          if (primary instanceof IOException && !(secondary instanceof IOException))
            throw secondary;
          primary.addSuppressed(new StorageIoException(StorageIoException.Reason.UNAVAILABLE));
        }
        throw primary;
      }
      release.close(resource);
      return result;
    } catch (IOException failure) {
      throw new StorageIoException(
          failure instanceof StorageIoException storage && failure.getSuppressed().length == 0
              ? storage.reason()
              : StorageIoException.Reason.UNAVAILABLE);
    }
  }

  public static <T extends @Nullable Object> T use(Closeable release, Action<T> action)
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
