package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import org.junit.jupiter.api.Test;

/** PT-AUT-008 policy matrix only; JDBC predicates and HTTP mapping remain separately required. */
final class AuthorizationServiceTest {
  private final AuthorizationService service = new AuthorizationService();

  @Test
  void literalOwnerAndAdminMatrixNeverExposesOtherNotifications() {
    for (Role role : Role.values()) {
      AuthenticatedActor actor = new AuthenticatedActor(7, "synthetic-user", role);
      assertEquals(7, actor.userId());
      assertEquals("synthetic-user", actor.username());
      assertEquals(role, actor.role());
      assertDoesNotThrow(() -> service.requireNotificationOwner(actor, 7));
      assertDoesNotThrow(() -> service.requireQuestionOwner(actor, 7));
      AuthorizationException notification =
          assertThrows(
              AuthorizationException.class, () -> service.requireNotificationOwner(actor, 8));
      assertEquals(ResultCode.NOT_FOUND, notification.resultCode());
      assertEquals("operation is not available", notification.getMessage());
      assertNull(notification.getCause());
      if (role == Role.ADMIN) {
        assertDoesNotThrow(() -> service.requireAdmin(actor));
        assertDoesNotThrow(() -> service.requireQuestionOwner(actor, 8));
      } else {
        assertEquals(
            ResultCode.FORBIDDEN,
            assertThrows(AuthorizationException.class, () -> service.requireAdmin(actor))
                .resultCode());
        assertEquals(
            ResultCode.NOT_FOUND,
            assertThrows(AuthorizationException.class, () -> service.requireQuestionOwner(actor, 8))
                .resultCode());
      }
      assertEquals("AuthenticatedActor[identity=<redacted>, role=" + role + "]", actor.toString());
    }
  }

  @Test
  void actorOwnerAndErrorNullInvariantsFailAtBoundaries() {
    AuthenticatedActor actor = new AuthenticatedActor(999_999_999_999L, "é".repeat(32), Role.ADMIN);
    assertDoesNotThrow(() -> service.requireNotificationOwner(actor, 999_999_999_999L));
    assertThrows(IllegalArgumentException.class, () -> new AuthenticatedActor(0, "u", Role.USER));
    assertThrows(
        IllegalArgumentException.class,
        () -> new AuthenticatedActor(1_000_000_000_000L, "u", Role.USER));
    assertThrows(IllegalArgumentException.class, () -> new AuthenticatedActor(1, "", Role.USER));
    assertThrows(
        IllegalArgumentException.class,
        () -> new AuthenticatedActor(1, "é".repeat(32) + "x", Role.USER));
    assertThrows(NullPointerException.class, () -> new AuthenticatedActor(1, null, Role.USER));
    assertThrows(NullPointerException.class, () -> new AuthenticatedActor(1, "u", null));
    assertThrows(NullPointerException.class, () -> service.requireAdmin(null));
    assertThrows(NullPointerException.class, () -> service.requireNotificationOwner(null, 1));
    assertThrows(NullPointerException.class, () -> service.requireQuestionOwner(null, 1));
    for (long invalid : new long[] {0, 1_000_000_000_000L}) {
      assertThrows(
          IllegalArgumentException.class, () -> service.requireNotificationOwner(actor, invalid));
      assertThrows(
          IllegalArgumentException.class, () -> service.requireQuestionOwner(actor, invalid));
    }
    assertThrows(NullPointerException.class, () -> new AuthorizationException(null));
    assertThrows(
        IllegalArgumentException.class, () -> new AuthorizationException(ResultCode.SUCCESS));
  }
}
