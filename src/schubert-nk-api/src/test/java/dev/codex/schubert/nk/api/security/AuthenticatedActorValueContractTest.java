package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import java.util.HashMap;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-ACTORVALUE001/002; SS314/331/451; synthetic verified-row value contracts only. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AuthenticatedActorValueContractTest {
  private static final String OWNER_NAME = "synthetic-owner";

  @Test
  void actorValue001ValidScalarByteBoundariesPreserveExactRowText() {
    // Independent byte arithmetic: 64*1, 32*2, 21*3+1, 16*4; no production length helper.
    for (String username :
        List.of("a", "a".repeat(64), "é".repeat(32), "漢".repeat(21) + "a", "😀".repeat(16))) {
      var actor = new AuthenticatedActor(999_999_999_999L, username, Role.ADMIN);
      assertEquals(999_999_999_999L, actor.userId());
      assertEquals(username, actor.username());
      assertEquals(Role.ADMIN, actor.role());
      assertEquals("AuthenticatedActor[identity=<redacted>, role=ADMIN]", actor.toString());
    }
    for (String username :
        List.of(
            "a".repeat(65), "é".repeat(32) + "a", "漢".repeat(21) + "aa", "😀".repeat(16) + "a")) {
      assertThrows(
          IllegalArgumentException.class, () -> new AuthenticatedActor(1, username, Role.USER));
    }
  }

  @Test
  void actorValue002EqualDistinctRowsLookUpLiteralOwnerAndKeepDifferencesSeparate() {
    var first = new AuthenticatedActor(7, OWNER_NAME, Role.USER);
    var equal = new AuthenticatedActor(7, new String(OWNER_NAME), Role.USER);
    var otherUser = new AuthenticatedActor(8, OWNER_NAME, Role.USER);
    var otherName = new AuthenticatedActor(7, "synthetic-other", Role.USER);
    var otherRole = new AuthenticatedActor(7, OWNER_NAME, Role.ADMIN);
    assertNotSame(first, equal);
    assertNotSame(first.username(), equal.username());
    assertTrue(first.equals(first));
    assertTrue(first.equals(equal));
    assertTrue(equal.equals(first));
    assertFalse(first.equals(otherUser));
    assertFalse(first.equals(otherName));
    assertFalse(first.equals(otherRole));
    assertFalse(first.equals(null));
    assertFalse(first.equals(OWNER_NAME));
    var owners = new HashMap<AuthenticatedActor, String>();
    owners.put(first, "owner");
    assertEquals("owner", owners.get(equal));
    assertNull(owners.get(otherUser));
    assertNull(owners.get(otherName));
    assertNull(owners.get(otherRole));
    owners.put(otherRole, "admin-owner");
    assertEquals(2, owners.size());
    assertEquals("admin-owner", owners.get(otherRole));
    assertEquals("owner", owners.get(equal));
    assertEquals("AuthenticatedActor[identity=<redacted>, role=USER]", first.toString());
  }
}
