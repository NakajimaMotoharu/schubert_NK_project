package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.protocol.header.ResultCode;

/** Redacted query error. NK-ADM-001; FUN-009/AUT-003; UI225/236; SS332; PT-ADM-005/006. */
public final class UserQueryException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final boolean capacity;

  UserQueryException(boolean capacity) {
    super("user query is unavailable");
    this.capacity = capacity;
  }

  public ResultCode resultCode() {
    return capacity ? ResultCode.RESOURCE_LIMIT : ResultCode.TEMPORARY_FAILURE;
  }
}
