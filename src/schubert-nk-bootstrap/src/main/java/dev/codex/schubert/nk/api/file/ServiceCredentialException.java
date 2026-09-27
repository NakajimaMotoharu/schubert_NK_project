package dev.codex.schubert.nk.api.file;

import java.io.IOException;

/** Fixed, value-free Web/API private-credential failure. SS343 §6/SSC-081; PG281. */
public final class ServiceCredentialException extends IOException {
  private static final long serialVersionUID = 1L;

  public ServiceCredentialException() {
    super("service credential cannot be loaded");
  }
}
