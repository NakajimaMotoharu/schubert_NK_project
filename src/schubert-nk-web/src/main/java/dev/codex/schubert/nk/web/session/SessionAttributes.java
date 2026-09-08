package dev.codex.schubert.nk.web.session;

import dev.codex.schubert.nk.web.security.SavedRequestTarget;
import java.util.*;

/**
 * Immutable allowlist; absent principal is anonymous, not partially authenticated.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.1;
 * SSC-038/PG-D-094/PT-WEB-009..015. Constructor rejects null collections/elements and duplicate
 * IDs.
 */
public record SessionAttributes(
    Optional<SessionPrincipal> principal,
    Optional<String> csrfToken,
    Optional<SavedRequestTarget> savedRequest,
    List<SessionOperationToken> operationTokens) {
  public SessionAttributes {
    Objects.requireNonNull(principal, "principal");
    Objects.requireNonNull(csrfToken, "csrfToken");
    Objects.requireNonNull(savedRequest, "savedRequest");
    operationTokens = List.copyOf(operationTokens);
    if (operationTokens.size() > 10)
      throw new IllegalArgumentException("session operation count is invalid");
    var ids = new HashSet<UUID>();
    for (var token : operationTokens)
      if (!ids.add(token.token()))
        throw new IllegalArgumentException("session operation identity is duplicated");
    csrfToken.ifPresent(
        value -> {
          if (!value.matches("[A-Za-z0-9_-]{64,128}"))
            throw new IllegalArgumentException("session CSRF value is invalid");
        });
  }

  @Override
  public String toString() {
    return "SessionAttributes[REDACTED]";
  }
}
