package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.protocol.header.ResultCode;

/** Bounded query failure, never SQL/metadata. NK-SCN-001; SS332 §14; PT-SCN-002/006/007. */
public final class ScenarioQueryException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final boolean capacity;

  ScenarioQueryException(boolean capacity) {
    super("scenario query is unavailable");
    this.capacity = capacity;
  }

  public ResultCode resultCode() {
    return capacity ? ResultCode.RESOURCE_LIMIT : ResultCode.TEMPORARY_FAILURE;
  }
}
