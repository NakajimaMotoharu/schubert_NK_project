package dev.codex.schubert.nk.web.storage;

import java.io.IOException;

/**
 * Fixed internal classification; no original/suppressed physical path or content. NK-SCN-001; RD
 * FIL-006/007; UI237; SS333 §6; PT-SCN-008-RD04/RD05.
 */
final class FileIntegrityException extends IOException {
  private static final long serialVersionUID = 1L;

  FileIntegrityException() {
    super("FILE_INTEGRITY_MISMATCH");
  }
}
