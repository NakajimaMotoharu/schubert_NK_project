package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Shared file-adapter directory capability; path replacement never redirects an operation.
 * NK-SCN-001; RD FIL-001..009; UI237; SS333 §7.3; SSC-019/021; PT-SCN-008-F02/LIB01.
 * File-adapter-only callbacks must finish all path operations before returning; never export their
 * path. Root ownership/permission/filesystem readiness admission is a separate, mandatory caller
 * gate.
 */
public final class OwnedTransferDirectory implements AutoCloseable {
  private static final java.lang.String LITERAL_OPERATION = "operation";

  private static final java.lang.String LITERAL_PART = ".part";

  // BUG-036/YKT-032: caller monitors must not control internal state/resource lifetime.
  private final ReentrantLock stateLock = new ReentrantLock();
  private final DirectoryCalls calls;
  private int descriptor;

  @FunctionalInterface
  public interface FileOperation<T> {
    T execute(Path capabilityPath) throws IOException, NoSuchAlgorithmException;
  }

  private OwnedTransferDirectory(DirectoryCalls calls, int descriptor) {
    this.calls = calls;
    this.descriptor = descriptor;
  }

  /** SSC308/PT-DIRFACT-001..003: wrap the existing root FD only after all Java state exists. */
  public static OwnedTransferDirectory openRoot(DirectoryCalls calls) throws StorageIoException {
    Objects.requireNonNull(calls, "calls");
    var owned = new OwnedTransferDirectory(calls, -1);
    owned.descriptor = calls.openRoot();
    return owned;
  }

  /** Open every absolute path segment NOFOLLOW; never creates or chmods the configured root. */
  public static OwnedTransferDirectory open(DirectoryCalls calls, Path root)
      throws StorageIoException {
    Objects.requireNonNull(calls, "calls");
    Objects.requireNonNull(root, "root");
    if (!root.isAbsolute() || root.getNameCount() == 0 || !root.equals(root.normalize())) {
      throw new IllegalArgumentException("invalid transfer root");
    }
    // JDK Path parsing has already rejected NUL; native calls recheck each segment before use.
    return ResourceScope.acquire(
        () -> openRoot(calls),
        OwnedTransferDirectory::close,
        current -> {
          for (Path segment : root) {
            int next = calls.openDirectory(current.descriptor, segment.toString());
            int previous = current.descriptor;
            current.descriptor = next;
            calls.close(previous);
          }
          OwnedTransferDirectory result = new OwnedTransferDirectory(calls, current.descriptor);
          current.descriptor = -1; // Ownership transfer; the lexical resource has nothing to close.
          return result;
        });
  }

  /**
   * Existing child only; reader never creates, initializes, syncs or repairs a date. RD01/SS333.
   */
  public OwnedTransferDirectory openExistingDate(LocalDate date) throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(date, "date");
      requireOpen();
      if (date.getYear() < 1 || date.getYear() > 9999) {
        throw new IllegalArgumentException("invalid transfer date");
      }
      var owned = new OwnedTransferDirectory(calls, -1);
      owned.descriptor =
          calls.openDirectory(descriptor, date.format(DateTimeFormatter.BASIC_ISO_DATE));
      return owned;
    } finally {
      stateLock.unlock();
    }
  }

  /** Existing Asset child only. NK-MED-001; UI237/243; SS333; SSC-028; PT-MED-018/019. */
  public OwnedTransferDirectory openExistingChild(String name) throws StorageIoException {
    stateLock.lock();
    try {
      requireSegment(name);
      requireOpen();
      var owned = new OwnedTransferDirectory(calls, -1);
      owned.descriptor = calls.openDirectory(descriptor, name);
      return owned;
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Hold an existing Asset inode without following its final symlink. The callback must validate
   * its Unix type/attributes before reading, finish all I/O here and never export the capability.
   */
  public <T> T atExistingEntryHandle(String name, FileOperation<T> operation)
      throws StorageIoException {
    stateLock.lock();
    try {
      requireSegment(name);
      Objects.requireNonNull(operation, LITERAL_OPERATION);
      requireOpen();
      return withEntry(() -> calls.openEntry(descriptor, name), operation);
    } finally {
      stateLock.unlock();
    }
  }

  private static void requireSegment(String name) {
    Objects.requireNonNull(name, "name");
    if (name.isEmpty()
        || name.equals(".")
        || name.equals("..")
        || name.indexOf('/') >= 0
        || name.indexOf('\0') >= 0) {
      throw new IllegalArgumentException("invalid storage segment");
    }
  }

  /** New or existing date child, never follows a symlink; child owns an independent FD. */
  public OwnedTransferDirectory openDate(LocalDate date) throws StorageIoException {
    return openDate(date, handle -> Boolean.TRUE);
  }

  /** Initialize only the directory this call created; never repairs an existing date. */
  public OwnedTransferDirectory openDate(LocalDate date, FileOperation<Boolean> initialize)
      throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(date, "date");
      Objects.requireNonNull(initialize, "initialize");
      requireOpen();
      if (date.getYear() < 1 || date.getYear() > 9999) {
        throw new IllegalArgumentException("invalid transfer date");
      }
      String name = date.format(DateTimeFormatter.BASIC_ISO_DATE);
      boolean created;
      try {
        calls.createDirectory(descriptor, name);
        calls.sync(descriptor);
        created = true;
      } catch (StorageIoException ex) {
        if (ex.reason() != StorageIoException.Reason.COLLISION) {
          throw ex;
        }
        // EEXIST proves no type/ownership: openDirectory still performs O_DIRECTORY|O_NOFOLLOW.
        created = false;
      }
      final boolean initializeCreated = created;
      return ResourceScope.acquire(
          () -> openExistingChild(name),
          OwnedTransferDirectory::close,
          child -> {
            if (initializeCreated) {
              child.atDirectory(initialize);
              calls.sync(child.descriptor);
            }
            var result = new OwnedTransferDirectory(calls, child.descriptor);
            child.descriptor = -1;
            return result;
          });
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * New-only 0700 child, with child/parent durability before transferring ownership. Caller
   * authenticates namespace/owner under exclusion; no repair or deletion on failure.
   * NK-OPS-001/BAK/BKO/UI251/SS333 7.6/341 6.1/343; SSC068/PG186; CDIR001..008.
   */
  public OwnedTransferDirectory createPrivateChild(String name) throws StorageIoException {
    stateLock.lock();
    try {
      requireSegment(name);
      requireOpen();
      calls.createPrivateDirectory(descriptor, name);
      return ResourceScope.acquire(
          () -> openExistingChild(name),
          OwnedTransferDirectory::close,
          child -> {
            calls.sync(child.descriptor);
            calls.sync(descriptor);
            var result = new OwnedTransferDirectory(calls, child.descriptor);
            child.descriptor = -1;
            return result;
          });
    } finally {
      stateLock.unlock();
    }
  }

  /** Inspect this held directory, not its replaceable configured path; never export the path. */
  public <T> T atDirectory(FileOperation<T> operation) throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(operation, LITERAL_OPERATION);
      requireOpen();
      return execute(Path.of("/proc/self/fd", Integer.toString(descriptor)), operation);
    } finally {
      stateLock.unlock();
    }
  }

  public <T> T atPart(UUID id, FileOperation<T> operation) throws StorageIoException {
    stateLock.lock();
    try {
      return atFile(id, LITERAL_PART, operation);
    } finally {
      stateLock.unlock();
    }
  }

  public <T> T atReady(UUID id, FileOperation<T> operation) throws StorageIoException {
    stateLock.lock();
    try {
      return atFile(id, ".ready", operation);
    } finally {
      stateLock.unlock();
    }
  }

  private <T> T atFile(UUID id, String suffix, FileOperation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(id, "id");
    Objects.requireNonNull(operation, LITERAL_OPERATION);
    requireOpen();
    Path capability = Path.of("/proc/self/fd", Integer.toString(descriptor), id + suffix);
    return execute(capability, operation);
  }

  /** Hold the part inode; caller must validate its Unix attributes before any read. */
  public <T> T atPartHandle(UUID id, FileOperation<T> operation) throws StorageIoException {
    stateLock.lock();
    try {
      return atHandle(id, LITERAL_PART, operation);
    } finally {
      stateLock.unlock();
    }
  }

  /** Hold the ready inode; a replaced name cannot redirect the scoped capability. */
  public <T> T atReadyHandle(UUID id, FileOperation<T> operation) throws StorageIoException {
    stateLock.lock();
    try {
      return atHandle(id, ".ready", operation);
    } finally {
      stateLock.unlock();
    }
  }

  private <T> T atHandle(UUID id, String suffix, FileOperation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(id, "id");
    Objects.requireNonNull(operation, LITERAL_OPERATION);
    requireOpen();
    return withEntry(() -> calls.openEntry(descriptor, id + suffix), operation);
  }

  /** CREATE_NEW and own the actual inode before starting any writer callback. */
  public <T> T createPart(UUID id, FileOperation<T> operation) throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(id, "id");
      Objects.requireNonNull(operation, LITERAL_OPERATION);
      requireOpen();
      return withEntry(() -> calls.createFile(descriptor, id + LITERAL_PART), operation);
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Own a new 0600 part inode. NK-OPS-001; OPS-009/UI251/SS333/343 §6.10; PG-D-153;
   * PT-OPS-PFILE-001/003/004/005. Caller validates metadata/ACL and forces written content.
   */
  public <T> T createPrivatePart(UUID id, FileOperation<T> operation) throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(id, "id");
      Objects.requireNonNull(operation, LITERAL_OPERATION);
      requireOpen();
      return withEntry(() -> calls.createPrivateFile(descriptor, id + LITERAL_PART), operation);
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * SSC193: one admitted new-only 0600 entry, held O_EXCL/NOFOLLOW/CLOEXEC inode throughout I/O. No
   * arbitrary path, existing-file recovery, deletion or implicit directory sync. The caller
   * authenticates namespace/owner/ACL and forces content, then syncs and closes the owned
   * directory. NK-OPS-001 / OPS009,TST004 / UI251 / SS333343451 / PT-OPS-NFILE193001..004.
   */
  public <T> T createPrivateEntry(String name, FileOperation<T> operation)
      throws StorageIoException {
    stateLock.lock();
    try {
      if (name == null || operation == null)
        throw new IllegalArgumentException("private entry name and operation required");
      requireSegment(name);
      requireOpen();
      return withEntry(() -> calls.createPrivateFile(descriptor, name), operation);
    } finally {
      stateLock.unlock();
    }
  }

  @FunctionalInterface
  private interface EntryOpen {
    int open() throws StorageIoException;
  }

  private <T> T withEntry(EntryOpen open, FileOperation<T> operation) throws StorageIoException {
    // The JVM allocates EntryHandle before evaluating open.open(); its constructor only stores.
    return ResourceScope.acquire(
        () -> new EntryHandle(calls, open.open()),
        EntryHandle::close,
        entry -> execute(Path.of("/proc/self/fd", Integer.toString(entry.descriptor)), operation));
  }

  private static <T> T execute(Path capability, FileOperation<T> operation)
      throws StorageIoException {
    try {
      return operation.execute(capability);
    } catch (FileAlreadyExistsException ex) {
      StorageIoException.preserveFatal(ex);
      throw new StorageIoException(StorageIoException.Reason.COLLISION);
    } catch (NoSuchFileException ex) {
      StorageIoException.preserveFatal(ex);
      throw new StorageIoException(StorageIoException.Reason.MISSING);
    } catch (IOException | NoSuchAlgorithmException ex) {
      StorageIoException.preserveFatal(ex);
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  /** Operation-local only, never returned or shared; one lexical close consumes the native FD. */
  private static final class EntryHandle implements AutoCloseable {
    private final DirectoryCalls calls;
    private final int descriptor;

    private EntryHandle(DirectoryCalls calls, int descriptor) {
      this.calls = calls;
      this.descriptor = descriptor;
    }

    @Override
    public void close() throws StorageIoException {
      calls.close(descriptor);
    }
  }

  /** Atomic no-replace publication, then directory durability; never unlinks ready on failure. */
  public void publish(UUID id) throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(id, "id");
      requireOpen();
      calls.publish(descriptor, id + LITERAL_PART, id + ".ready");
      calls.sync(descriptor);
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Only writer-owned part cleanup; ordinary callers never delete ready/root/directory. SSC-022's
   * exclusive diagnostic cleanup is a separate scoped file-adapter policy.
   */
  public void deletePart(UUID id) throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(id, "id");
      requireOpen();
      calls.unlink(descriptor, id + LITERAL_PART);
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * No-replace publication of an owned part under one admitted name, then directory sync.
   * NK-OPS-001; SS333/343 §6.10; PG-D-153; PT-OPS-PFILE-002/004..007. A sync failure does not undo
   * the rename; callers must reconcile the uncertain result under their exclusive lock.
   */
  public void publishAs(UUID id, String name) throws StorageIoException {
    stateLock.lock();
    try {
      Objects.requireNonNull(id, "id");
      requireSegment(name);
      requireOpen();
      calls.publish(descriptor, id + LITERAL_PART, name);
      calls.sync(descriptor);
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Unlink one caller-admitted owned entry and sync. NK-OPS-001; SS343 §6.10; PG-D-153;
   * PT-OPS-PFILE-004..006. Does not itself establish run ownership, stable namespace or child stop.
   */
  public void unlinkEntry(String name) throws StorageIoException {
    stateLock.lock();
    try {
      requireSegment(name);
      requireOpen();
      calls.unlink(descriptor, name);
      calls.sync(descriptor);
    } finally {
      stateLock.unlock();
    }
  }

  /** Admitted empty child only; Root/M+A/identity gates belong to the cleanup caller. SSC118. */
  public void removeEmptyChild(String name) throws StorageIoException {
    stateLock.lock();
    try {
      requireSegment(name);
      requireOpen();
      calls.removeEmptyDirectory(descriptor, name);
      calls.sync(descriptor);
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Publish one existing directory under the same retained parent, never replacing a target.
   * NK-OPS-001; BAK/BKO/OPS009/UI251/SS333 7.5/341 6.9; SSC065/PG176; PDIR001..008. Caller retains
   * exclusion, authenticates the original/final inode and forces all contents. This capability
   * alone does not certify a backup. Partial publication is never undone.
   */
  public void publishChild(String pending, String ready) throws StorageIoException {
    stateLock.lock();
    try {
      requireSegment(pending);
      requireSegment(ready);
      if (pending.equals(ready)) throw new IllegalArgumentException("identical directory names");
      requireOpen();
      ResourceScope.acquire(
          () -> openExistingChild(pending),
          OwnedTransferDirectory::close,
          child -> {
            calls.publish(descriptor, pending, ready);
            calls.sync(descriptor);
            return Boolean.TRUE;
          });
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Durability barrier for owned startup-probe cleanup; never a reader operation. SS333 §7.4;
   * SSC-022; PT-SCN-008-P01/P03 and BUG-036 monitor regression.
   */
  public void sync() throws StorageIoException {
    stateLock.lock();
    try {
      requireOpen();
      calls.sync(descriptor);
    } finally {
      stateLock.unlock();
    }
  }

  private void requireOpen() throws StorageIoException {
    if (descriptor < 0) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  /** Consume ownership before close: even an interrupted/failed close must not reuse the FD. */
  @Override
  public void close() throws StorageIoException {
    stateLock.lock();
    try {
      if (descriptor >= 0) {
        int previous = descriptor;
        descriptor = -1;
        calls.close(previous);
      }
    } finally {
      stateLock.unlock();
    }
  }
}
