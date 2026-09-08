package dev.codex.schubert.nk.api.file;

import java.io.IOException;

/**
 * Fixed temporary integrity failure, never a logical-ID not-found result. SS333; PT-MED-041..049.
 */
public final class MediaIntegrityException extends IOException {
  private static final long serialVersionUID = 1L;

  public MediaIntegrityException() {
    super("media integrity verification failed");
  }
}
