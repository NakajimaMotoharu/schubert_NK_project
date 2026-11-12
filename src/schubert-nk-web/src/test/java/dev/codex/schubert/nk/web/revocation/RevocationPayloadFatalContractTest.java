package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.security.ProviderException;
import java.security.SecureRandom;
import java.sql.SQLException;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/**
 * WEB-REVOCATION-FATAL001..005; BUG2711/SS314328352: public synthetic provider, no deployed keys.
 */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class RevocationPayloadFatalContractTest {
  private static final RevocationPayloadIdentity IDENTITY =
      new RevocationPayloadIdentity(new UUID(0, 19), Instant.EPOCH);
  private static final AuthenticationContext AUTH = AuthenticationContext.of("0".repeat(64));

  @Test
  void fatal001ProviderCauseKeepsExactFatalAndWipesNonce() {
    var fatal = new AssertionError("PUBLIC cause fixture");
    var random = new FailingRandom(new ProviderException("PUBLIC provider", fatal));
    try (var codec = codec(random)) {
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, AUTH)));
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
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, AUTH)));
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
          assertThrows(RevocationPayloadException.class, () -> codec.encrypt(IDENTITY, AUTH));
      assertEquals(RevocationPayloadException.Reason.CRYPTO_UNAVAILABLE, failure.reason());
      assertEquals(
          "revocation encrypted payload rejected: CRYPTO_UNAVAILABLE", failure.getMessage());
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
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, AUTH)));
      assertArrayEquals(new byte[12], random.observed);
    }
  }

  @Test
  void fatal005FatalOperationStillAllowsIdempotentClose() {
    var fatal = new AssertionError("PUBLIC lifetime fixture");
    var random = new FailingRandom(new ProviderException("PUBLIC provider", fatal));
    var codec = codec(random);
    try {
      assertSame(fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, AUTH)));
    } finally {
      codec.close();
    }
    codec.close();
    assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, AUTH));
    assertArrayEquals(new byte[12], random.observed);
  }

  private static RevocationPayloadCodec codec(SecureRandom random) {
    // Public zero vector belongs only to this unit process; production credentials are never read.
    return new RevocationPayloadCodec("fixture", new byte[32], null, null, random);
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
