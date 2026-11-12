package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.security.ProviderException;
import java.security.SecureRandom;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** WEB-CSRF-FATAL001..005; BUG2707/SS314352: public CSPRNG boundary, no deployed token. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class WebCsrfFatalContractTest {
  @Test
  void fatal001ProviderCauseRetainsIdentityAndWipesThirtyTwoBytes() {
    var fatal = new AssertionError("PUBLIC cause fixture");
    var random = new FailingRandom(new ProviderException("PUBLIC provider", fatal));
    assertSame(fatal, assertThrows(AssertionError.class, () -> WebCsrfToken.generate(random)));
    assertArrayEquals(new byte[32], random.observed);
  }

  @Test
  void fatal002SuppressedSqlNextRetainsIdentityAndOriginalGraph() {
    var fatal = new AssertionError("PUBLIC SQL next fixture");
    var next = new SQLException("PUBLIC next", fatal);
    var sql = new SQLException("PUBLIC SQL");
    sql.setNextException(next);
    var provider = new ProviderException("PUBLIC provider");
    provider.addSuppressed(sql);
    var random = new FailingRandom(provider);
    assertSame(fatal, assertThrows(AssertionError.class, () -> WebCsrfToken.generate(random)));
    assertSame(sql, provider.getSuppressed()[0]);
    assertEquals(1, provider.getSuppressed().length);
    assertSame(next, sql.getNextException());
    assertSame(fatal, next.getCause());
    assertArrayEquals(new byte[32], random.observed);
  }

  @Test
  void fatal003NonfatalCyclesReturnOnlyFixedCatalogAndWipeBuffer() {
    var provider = new ProviderException("PUBLIC cycle");
    var alias = new IllegalStateException("PUBLIC alias", provider);
    provider.initCause(alias);
    provider.addSuppressed(alias);
    alias.addSuppressed(provider);
    var random = new FailingRandom(provider);
    var failure = assertThrows(IllegalStateException.class, () -> WebCsrfToken.generate(random));
    assertEquals("CSRF generation is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertSame(alias, provider.getCause());
    assertSame(provider, alias.getCause());
    assertArrayEquals(new byte[32], random.observed);
  }

  @Test
  void fatal004DirectErrorPropagatesAndCleanupStillRuns() {
    var fatal = new AssertionError("PUBLIC direct fixture");
    var random = new FailingRandom(fatal);
    assertSame(fatal, assertThrows(AssertionError.class, () -> WebCsrfToken.generate(random)));
    assertArrayEquals(new byte[32], random.observed);
  }

  @Test
  void fatal005NextGenerationAfterFatalHasNoRetainedFailureOrBufferState() {
    var fatal = new AssertionError("PUBLIC recovery fixture");
    var random = new FailingRandom(new ProviderException("PUBLIC provider", fatal));
    assertSame(fatal, assertThrows(AssertionError.class, () -> WebCsrfToken.generate(random)));
    assertArrayEquals(new byte[32], random.observed);
    random.fail = false;
    var result = WebCsrfToken.generate(random);
    assertEquals("29".repeat(32), result.formValue());
    assertTrue(result.matches("29".repeat(32)));
    assertEquals("WebCsrfToken[REDACTED]", result.toString());
    assertArrayEquals(new byte[32], random.observed);
  }

  private static final class FailingRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    private final Throwable failure;
    private byte[] observed = new byte[0];
    private boolean fail = true;

    private FailingRandom(Throwable failure) {
      this.failure = failure;
    }

    @Override
    public void nextBytes(byte[] output) {
      observed = output;
      java.util.Arrays.fill(output, (byte) 41);
      if (fail) {
        if (failure instanceof Error fatal) throw fatal;
        throw (ProviderException) failure;
      }
    }
  }
}
