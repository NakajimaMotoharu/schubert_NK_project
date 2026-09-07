package dev.codex.schubert.nk.api.messaging.outbound;

/** Typed, bounded failure at the JMS provider boundary; wire bodies are never included. */
public final class OutboxSendException extends Exception {
  private static final long serialVersionUID = 1L;

  public OutboxSendException(String message) {
    super(message);
  }

  public OutboxSendException(String message, Throwable cause) {
    super(message, cause);
  }
}
