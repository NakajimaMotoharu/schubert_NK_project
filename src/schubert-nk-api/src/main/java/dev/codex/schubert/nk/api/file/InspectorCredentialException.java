package dev.codex.schubert.nk.api.file;

import java.io.IOException;

/** Fixed value-free failure. NK-DAT-001; SS343 6.4; PG-D-134; PT-DB-INBOX-129..140. */
public final class InspectorCredentialException extends IOException {
  private static final long serialVersionUID = 1L;

  public InspectorCredentialException() {
    super("inspector credential cannot be loaded");
  }
}
