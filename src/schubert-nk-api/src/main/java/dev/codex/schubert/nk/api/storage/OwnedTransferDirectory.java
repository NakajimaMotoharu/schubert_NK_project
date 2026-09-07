package dev.codex.schubert.nk.api.storage;

import java.io.IOException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Objects;
import java.util.UUID;

/**
 * API writer's owned directory capability; path replacement never redirects an operation.
 * NK-SCN-001; RD FIL-001..009; UI237; SS333 §7.3; SSC-019; PT-SCN-008-F02. Package-only callbacks
 * must finish all path operations before returning; never export their path. Root
 * ownership/permission/filesystem readiness admission is a separate, mandatory caller gate.
 */
final class OwnedTransferDirectory implements AutoCloseable {
  private final DirectoryCalls calls;
  private int descriptor;

  @FunctionalInterface
  interface FileOperation<T> {
    T execute(Path capabilityPath) throws IOException;
  }

  private OwnedTransferDirectory(DirectoryCalls calls, int descriptor) {
    this.calls = calls;
    this.descriptor = descriptor;
  }

  /** Open every absolute path segment NOFOLLOW; never creates or chmods the configured root. */
  static OwnedTransferDirectory open(DirectoryCalls calls, Path root) throws StorageIoException {
    Objects.requireNonNull(calls, "calls");
    Objects.requireNonNull(root, "root");
    if (!root.isAbsolute() || root.getNameCount() == 0 || !root.equals(root.normalize())) {
      throw new IllegalArgumentException("invalid transfer root");
    }
    // JDK Path parsing has already rejected NUL; native calls recheck each segment before use.
    try (OwnedTransferDirectory current = new OwnedTransferDirectory(calls, calls.openRoot())) {
      for (Path segment : root) {
        int next = calls.openDirectory(current.descriptor, segment.toString());
        int previous = current.descriptor;
        current.descriptor = next;
        calls.close(previous);
      }
      OwnedTransferDirectory result = new OwnedTransferDirectory(calls, current.descriptor);
      current.descriptor = -1; // Ownership transfer; the lexical resource has nothing to close.
      return result;
    }
  }

  /** New or existing date child, never follows a symlink; child owns an independent FD. */
  synchronized OwnedTransferDirectory openDate(LocalDate date) throws StorageIoException {
    Objects.requireNonNull(date, "date");
    requireOpen();
    if (date.getYear() < 1 || date.getYear() > 9999) {
      throw new IllegalArgumentException("invalid transfer date");
    }
    String name = date.format(DateTimeFormatter.BASIC_ISO_DATE);
    try {
      calls.createDirectory(descriptor, name);
      calls.sync(descriptor);
    } catch (StorageIoException ex) {
      if (ex.reason() != StorageIoException.Reason.COLLISION) {
        throw ex;
      }
      // EEXIST proves no type/ownership: openDirectory still performs O_DIRECTORY|O_NOFOLLOW.
    }
    return new OwnedTransferDirectory(calls, calls.openDirectory(descriptor, name));
  }

  synchronized <T> T atPart(UUID id, FileOperation<T> operation) throws StorageIoException {
    return atFile(id, ".part", operation);
  }

  synchronized <T> T atReady(UUID id, FileOperation<T> operation) throws StorageIoException {
    return atFile(id, ".ready", operation);
  }

  private <T> T atFile(UUID id, String suffix, FileOperation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(id, "id");
    Objects.requireNonNull(operation, "operation");
    requireOpen();
    Path capability = Path.of("/proc/self/fd", Integer.toString(descriptor), id + suffix);
    try {
      return operation.execute(capability);
    } catch (FileAlreadyExistsException ex) {
      throw new StorageIoException(StorageIoException.Reason.COLLISION);
    } catch (NoSuchFileException ex) {
      throw new StorageIoException(StorageIoException.Reason.MISSING);
    } catch (IOException ex) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  /** Atomic no-replace publication, then directory durability; never unlinks ready on failure. */
  synchronized void publish(UUID id) throws StorageIoException {
    Objects.requireNonNull(id, "id");
    requireOpen();
    calls.publish(descriptor, id + ".part", id + ".ready");
    calls.sync(descriptor);
  }

  /** Only a writer-owned part may be removed; no ready/root/directory deletion API exists. */
  synchronized void deletePart(UUID id) throws StorageIoException {
    Objects.requireNonNull(id, "id");
    requireOpen();
    calls.unlink(descriptor, id + ".part");
  }

  private void requireOpen() throws StorageIoException {
    if (descriptor < 0) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  /** Consume ownership before close: even an interrupted/failed close must not reuse the FD. */
  @Override
  public synchronized void close() throws StorageIoException {
    if (descriptor >= 0) {
      int previous = descriptor;
      descriptor = -1;
      calls.close(previous);
    }
  }
}
