package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.security.ProviderException;
import java.security.SecureRandom;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** WEB-SESSION-FATAL001..005; BUG2704/SS314328352: public synthetic provider, no deployed keys. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class SessionPayloadFatalContractTest {
  private static final SessionPayloadIdentity IDENTITY =
      new SessionPayloadIdentity(new UUID(0, 19), "a".repeat(64), Instant.EPOCH);
  private static final SessionAttributes EMPTY =
      new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), List.of());

  @Test
  void fatal001ProviderCauseKeepsExactFatalAndWipesNonce() {
    var fatal = new AssertionError("PUBLIC cause fixture");
    var random = new FailingRandom(new ProviderException("PUBLIC provider", fatal));
    try (var codec = codec(random)) {
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, EMPTY)));
      assertArrayEquals(new byte[12], random.observed);
    }
  }

  @Test
  void fatal002SuppressedSqlNextReachesSameFatalWithoutChangingGraph() {
    var fatal = new AssertionError("PUBLIC SQL next fixture");
    var next = new SQLException("PUBLIC next", fatal);
    var sql = new SQLException("PUBLIC SQL");
    sql.setNextException(next);
    var provider = new ProviderException("PUBLIC provider");
    provider.addSuppressed(sql);
    var random = new FailingRandom(provider);
    try (var codec = codec(random)) {
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, EMPTY)));
      assertSame(sql, provider.getSuppressed()[0]);
      assertEquals(1, provider.getSuppressed().length);
      assertSame(next, sql.getNextException());
      assertSame(fatal, next.getCause());
      assertArrayEquals(new byte[12], random.observed);
    }
  }

  @Test
  void fatal003NonfatalCyclesReturnOnlyFixedCatalogAndWipeNonce() {
    var provider = new ProviderException("PUBLIC cycle");
    var alias = new IllegalStateException("PUBLIC alias", provider);
    provider.initCause(alias);
    provider.addSuppressed(alias);
    alias.addSuppressed(provider);
    var random = new FailingRandom(provider);
    try (var codec = codec(random)) {
      var failure =
          assertThrows(SessionPayloadException.class, () -> codec.encrypt(IDENTITY, EMPTY));
      assertEquals(SessionPayloadException.Reason.CRYPTO_UNAVAILABLE, failure.reason());
      assertEquals("session encrypted payload rejected: CRYPTO_UNAVAILABLE", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertSame(alias, provider.getCause());
      assertSame(provider, alias.getCause());
      assertArrayEquals(new byte[12], random.observed);
    }
  }

  @Test
  void fatal004DirectErrorIsNotNormalizedAndCleanupStillRuns() {
    var fatal = new AssertionError("PUBLIC direct fixture");
    var random = new FailingRandom(fatal);
    try (var codec = codec(random)) {
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, EMPTY)));
      assertArrayEquals(new byte[12], random.observed);
    }
  }

  @Test
  void fatal005FatalOperationStillAllowsIdempotentClose() {
    var fatal = new AssertionError("PUBLIC lifetime fixture");
    var random = new FailingRandom(new ProviderException("PUBLIC provider", fatal));
    var codec = codec(random);
    try {
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, EMPTY)));
    } finally {
      codec.close();
    }
    codec.close();
    assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, EMPTY));
    assertArrayEquals(new byte[12], random.observed);
  }

  private static SessionPayloadCodec codec(SecureRandom random) {
    // Public zero vector belongs only to this unit process; production credentials are never read.
    return new SessionPayloadCodec("fixture", new byte[32], null, null, random);
  }

  private static final class FailingRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    private final Throwable failure;
    private byte[] observed = new byte[0];

    private FailingRandom(Throwable failure) {
      this.failure = failure;
    }

    @Override
    public void nextBytes(byte[] output) {
      observed = output;
      java.util.Arrays.fill(output, (byte) 41);
      if (failure instanceof Error fatal) throw fatal;
      throw (ProviderException) failure;
    }
  }
}
