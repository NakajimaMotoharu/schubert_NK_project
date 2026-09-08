package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.protocol.header.ResultCode;

/** Redacted query boundary. NK-MED-001; SS332/333; PT-MED-012/013. */
public final class MediaQueryException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final boolean capacity;

  MediaQueryException(boolean capacity) {
    super("media query is unavailable");
    this.capacity = capacity;
  }

  public ResultCode resultCode() {
    return capacity ? ResultCode.RESOURCE_LIMIT : ResultCode.TEMPORARY_FAILURE;
  }
}
