package dev.codex.schubert.nk.api.security;

/** Closed DDL/audit reasons. NK-AUT-001; AUT-004; UI226; SS314/331; PT-AUT-006-03/008-R. */
public enum SessionRevocationReason {
  LOGOUT,
  DISABLED,
  PASSWORD_RESET,
  ADMIN,
  EXPIRED,
  REPLACED
}
