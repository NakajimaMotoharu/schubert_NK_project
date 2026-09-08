package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Scoped read-only file-adapter capability, not authentication or root admission. NK-MED-001; RD
 * FIL-006/007; UI237/243; SS311/333; SSC-028; PG-D-074; PT-MED-021..025. Caller owns an admitted
 * root and supplies already logically validated segments. No root or file is repaired.
 */
public final class ExistingFileAccess {
  private final OwnedTransferDirectory root;
  private final StorageIdentity identity;
  private final Io io;

  /**
   * Trusted file-adapter callback; finish all I/O here and never export channel/path references.
   */
  @FunctionalInterface
  public interface ReadOperation<T> {
    T execute(SeekableByteChannel channel) throws IOException;
  }

  interface Io {
    Map<String, Object> attributes(Path heldPath) throws IOException;

    SeekableByteChannel openReadOnly(Path heldPath) throws IOException;
  }

  public ExistingFileAccess(OwnedTransferDirectory root, StorageIdentity identity) {
    this(root, identity, new NioIo());
  }

  ExistingFileAccess(OwnedTransferDirectory root, StorageIdentity identity, Io io) {
    this.root = Objects.requireNonNull(root, "root");
    this.identity = Objects.requireNonNull(identity, "identity");
    this.io = Objects.requireNonNull(io, "io");
  }

  /**
   * Read one exact positive-size inode. The result must contain no live I/O capability. Media's
   * N12/prefix/NFC/UTF-8 restrictions and manifest validation remain the caller's prior gates.
   */
  public <T> T read(List<String> segments, long expectedSize, ReadOperation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(segments, "segments");
    Objects.requireNonNull(operation, "operation");
    if (segments.isEmpty() || segments.size() > 256 || expectedSize < 1) {
      throw new IllegalArgumentException("invalid existing file request");
    }
    List<String> names = List.copyOf(segments);
    try {
      return walk(root, names, 0, expectedSize, operation);
    } catch (StorageIoException | UnsupportedOperationException failure) {
      // Even missing/close failures are integrity-unavailable, never logical ID absence or success.
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  private <T> T walk(
      OwnedTransferDirectory directory,
      List<String> names,
      int index,
      long expectedSize,
      ReadOperation<T> operation)
      throws StorageIoException {
    directory.atDirectory(
        handle -> {
          StorageAttributeGuard.directory(io.attributes(handle), identity);
          return Boolean.TRUE;
        });
    String name = names.get(index);
    if (index == names.size() - 1) {
      return directory.atExistingEntryHandle(
          name,
          handle -> {
            StorageAttributeGuard.existingFile(io.attributes(handle), identity, expectedSize);
            try (SeekableByteChannel channel = io.openReadOnly(handle)) {
              requireSize(channel, expectedSize);
              T result = operation.execute(channel);
              requireSize(channel, expectedSize);
              StorageAttributeGuard.existingFile(io.attributes(handle), identity, expectedSize);
              return result;
            }
          });
    }
    try (OwnedTransferDirectory child = directory.openExistingChild(name)) {
      return walk(child, names, index + 1, expectedSize, operation);
    }
  }

  private static void requireSize(SeekableByteChannel channel, long expectedSize)
      throws IOException {
    if (channel.size() != expectedSize) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  private static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path heldPath) throws IOException {
      // Intentional follow of an owned kernel FD, not a replaceable caller path.
      return Files.readAttributes(heldPath, "unix:owner,group,mode,nlink,size");
    }

    @Override
    public SeekableByteChannel openReadOnly(Path heldPath) throws IOException {
      return FileChannel.open(heldPath, StandardOpenOption.READ);
    }
  }
}
