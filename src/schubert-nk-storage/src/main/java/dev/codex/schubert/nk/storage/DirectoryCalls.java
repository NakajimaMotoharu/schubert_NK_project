package dev.codex.schubert.nk.storage;

/** Owned directory FD operations; names are single segments. SS333 §7.3; PT-SCN-008-F01..F03. */
public interface DirectoryCalls {
  int openRoot() throws StorageIoException;

  int openDirectory(int parent, String name) throws StorageIoException;

  /**
   * O_PATH inode capability, including symlink itself; validate type before any actual file I/O.
   */
  int openEntry(int parent, String name) throws StorageIoException;

  /** Atomically create and own a new 0640 file; never opens/replaces an existing name. */
  int createFile(int parent, String name) throws StorageIoException;

  void createDirectory(int parent, String name) throws StorageIoException;

  void publish(int directory, String part, String ready) throws StorageIoException;

  void unlink(int directory, String name) throws StorageIoException;

  void sync(int directory) throws StorageIoException;

  /** Consumes the FD even on failure; callers must not retry close after possible FD reuse. */
  void close(int directory) throws StorageIoException;
}
