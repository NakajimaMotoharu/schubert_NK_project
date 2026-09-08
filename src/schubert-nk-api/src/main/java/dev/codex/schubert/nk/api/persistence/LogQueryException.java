package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.protocol.header.ResultCode;

/** Fixed Log query failure. NK-ADM-001/FUN-008; UI225/235; SS332; PT-ADM-058/059. */
public final class LogQueryException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final boolean capacity;

  LogQueryException(boolean capacity) {
    super("log query is unavailable");
    this.capacity = capacity;
  }

  public ResultCode resultCode() {
    return capacity ? ResultCode.RESOURCE_LIMIT : ResultCode.TEMPORARY_FAILURE;
  }
}
