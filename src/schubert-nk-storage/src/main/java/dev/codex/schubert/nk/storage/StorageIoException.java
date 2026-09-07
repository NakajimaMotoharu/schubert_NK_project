package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.util.Objects;

/** Bounded storage failure without physical paths/native messages. SS333; PT-SCN-008-F01/F02. */
public final class StorageIoException extends IOException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    COLLISION,
    MISSING,
    UNAVAILABLE
  }

  private final Reason reason;

  public StorageIoException(Reason reason) {
    super("transfer storage operation failed");
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return reason;
  }
}
