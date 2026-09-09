package dev.codex.schubert.nk.storage;

import java.nio.file.Path;

/**
 * File-adapter-only retained inode metadata SPI, no file content or authorization. NK-DAT-001;
 * DAT-009/OPS-009/FIL-006; UI212/241/251; SS311/343 6.3; QA-046/SSC-049/PG-D-133;
 * PT-DB-INBOX-121..128.
 */
public interface InodeSecurityCalls {
  /**
   * ACL non-retrieval is empty, not proof of absence or permission; caller must apply its policy.
   */
  byte[] accessAcl(Path held, int maximumBytes) throws StorageIoException;

  boolean readOnlyFilesystem(Path held) throws StorageIoException;

  long effectiveUid();
}
