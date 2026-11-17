package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-WEB-CURRENTVALUE001002; SS313314331352/SSC328; pure public unissued fixtures only. */
final class PrincipalCurrentClosureContractTest {
  @Test
  void currentvalue001IndependentComponentHashAndRedactedMapIdentity() {
    // Golden String/Instant components: UTF-16 233, a*64 1926890496, Instant -549611547.
    for (var role : List.of(UserRole.USER, UserRole.ADMIN)) {
      var value =
          new SessionPrincipal(
              "e\u0301",
              role,
              AuthenticationContext.of("a".repeat(64)),
              Instant.parse("2026-01-02T03:04:05.123Z"));
      int expected = 233;
      expected = 31 * expected + System.identityHashCode(role);
      expected = 31 * expected + 1926890496;
      expected = 31 * expected - 549611547;
      assertEquals(expected, value.hashCode());
      var equal =
          new SessionPrincipal(
              "é",
              role,
              AuthenticationContext.of("a".repeat(64)),
              Instant.ofEpochSecond(1767323045, 123000000));
      assertEquals("public-value", Map.of(value, "public-value").get(equal));
      assertEquals("SessionPrincipal[REDACTED]", value.toString());
    }
  }

  @Test
  void currentvalue002NullContractAndIndependentGraphOrderRemainClosed() {
    assertThrows(NullPointerException.class, () -> SessionStoreException.preserveFatal(null));
    var causeFatal = new AssertionError("public-cause");
    var suppressedFatal = new AssertionError("public-suppressed");
    var nextFatal = new AssertionError("public-next");
    var root = new SQLException("public-root", causeFatal);
    var next = new SQLException("public-next-row", nextFatal);
    root.addSuppressed(suppressedFatal);
    root.setNextException(next);
    next.setNextException(root);
    Throwable[] before = root.getSuppressed();
    assertSame(
        causeFatal,
        assertThrows(AssertionError.class, () -> SessionStoreException.preserveFatal(root)));
    assertSame(causeFatal, root.getCause());
    assertSame(next, root.getNextException());
    assertSame(root, next.getNextException());
    assertEquals(1, root.getSuppressed().length);
    assertSame(before[0], root.getSuppressed()[0]);
    assertSame(suppressedFatal, root.getSuppressed()[0]);
  }
}
