package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.Objects;

/**
 * API application-service checks complement, never replace, repository owner predicates. Trace:
 * NK-AUT-001, FUN-009/011/012/013, AUT-002/003; UI226 §7; SS314 §9; PT-AUT-008.
 */
public final class AuthorizationService {
  public void requireAdmin(AuthenticatedActor actor) {
    Objects.requireNonNull(actor, "actor");
    if (actor.role() != Role.ADMIN) {
      throw new AuthorizationException(ResultCode.FORBIDDEN);
    }
  }

  /** ADMIN has no expanded scope for another user's notification. */
  public void requireNotificationOwner(AuthenticatedActor actor, long ownerUserId) {
    Objects.requireNonNull(actor, "actor");
    requireOwnerId(ownerUserId);
    if (actor.userId() != ownerUserId) {
      throw new AuthorizationException(ResultCode.NOT_FOUND);
    }
  }

  /** Only question/answer search, detail and deletion expand ADMIN scope. */
  public void requireQuestionOwner(AuthenticatedActor actor, long ownerUserId) {
    Objects.requireNonNull(actor, "actor");
    requireOwnerId(ownerUserId);
    if (actor.role() != Role.ADMIN && actor.userId() != ownerUserId) {
      throw new AuthorizationException(ResultCode.NOT_FOUND);
    }
  }

  private static void requireOwnerId(long ownerUserId) {
    if (ownerUserId < 1 || ownerUserId > 999_999_999_999L) {
      throw new IllegalArgumentException("owner ID is outside N12");
    }
  }
}
