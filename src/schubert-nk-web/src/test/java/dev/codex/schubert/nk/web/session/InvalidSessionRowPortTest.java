package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

/** PT-WEB-INVALIDROW001..002; UI226 SS3147.2.4/331/352. No stored row or provider. */
final class InvalidSessionRowPortTest {
  @Test
  void invalidRowHasFixedPublicDiagnosticAndNoProviderCauseOrSuppressedData() {
    var failure = new InvalidSessionRowException();
    assertEquals("session storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(InvalidSessionRowException.class, failure.getClass());
    assertEquals(
        "dev.codex.schubert.nk.web.session.InvalidSessionRowException: session storage is"
            + " unavailable",
        failure.toString());
    assertSame(
        failure,
        assertThrows(
            SessionStoreException.class,
            () -> {
              throw failure;
            }));
  }

  @Test
  void eachFailureOwnsItsDiagnosticStateWithoutChangingAnotherFailure() {
    var first = new InvalidSessionRowException();
    var second = new InvalidSessionRowException();
    assertNotSame(first, second);
    StackTraceElement[] retained = second.getStackTrace();
    assertTrue(retained.length > 0);
    first.setStackTrace(new StackTraceElement[0]);
    assertEquals(0, first.getStackTrace().length);
    assertEquals(java.util.List.of(retained), java.util.List.of(second.getStackTrace()));
    assertNull(second.getCause());
    assertEquals(0, second.getSuppressed().length);
  }
}
