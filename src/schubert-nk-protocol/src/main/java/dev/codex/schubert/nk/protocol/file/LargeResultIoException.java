package dev.codex.schubert.nk.protocol.file;

/** I/O failure while reading or writing a large-result stream. */
public final class LargeResultIoException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public LargeResultIoException(String message, Throwable cause) {
    super(message, cause);
  }
}
