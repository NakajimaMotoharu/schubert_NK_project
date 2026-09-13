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
