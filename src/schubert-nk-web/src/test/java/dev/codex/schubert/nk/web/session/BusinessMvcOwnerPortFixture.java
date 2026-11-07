package dev.codex.schubert.nk.web.session;

import dev.codex.schubert.nk.web.receipt.ReceiptReferenceRepository;
import java.lang.reflect.Proxy;
import java.security.Provider;
import java.security.SecureRandom;
import java.security.SecureRandomSpi;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import javax.sql.DataSource;

/**
 * Same lexical core for Spring Session and token lifecycle. PT-SCR-BIZBEAN001..006; no operations.
 */
public final class BusinessMvcOwnerPortFixture implements AutoCloseable {
  private final SessionPayloadCodec codec;
  private final SessionOperationTokenLifecycle retainedTokens;
  private final ReceiptReferenceRepository retainedReceipts;
  private final SpringEncryptedSessionRepository retainedRepository;
  private final EncryptedWebSessionRepository retainedLifecycle;

  public BusinessMvcOwnerPortFixture() {
    DataSource database =
        (DataSource)
            Proxy.newProxyInstance(
                DataSource.class.getClassLoader(),
                new Class<?>[] {DataSource.class},
                (proxy, method, args) -> {
                  throw new AssertionError("database callback forbidden in adapter fixture");
                });
    var random = new NeverRandom();
    var clock = Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);
    // Public zero bytes are a constructor-format canary only; no encrypt/decrypt is called.
    codec = new SessionPayloadCodec("public-fixture", new byte[32], null, null, random);
    retainedLifecycle =
        new EncryptedWebSessionRepository(
            database,
            codec,
            clock,
            random,
            () -> {
              throw new AssertionError("session identifier generation forbidden");
            });
    retainedRepository = new SpringEncryptedSessionRepository(retainedLifecycle, clock);
    retainedTokens =
        new SessionOperationTokenLifecycle(
            retainedLifecycle,
            clock,
            () -> {
              throw new AssertionError("operation identifier generation forbidden");
            });
    retainedReceipts = new ReceiptReferenceRepository(database);
  }

  public SpringEncryptedSessionRepository sessions() {
    return retainedRepository;
  }

  /** Same borrowed owner for Logout composition; no session operation or new capability. */
  public EncryptedWebSessionRepository localSessions() {
    return retainedLifecycle;
  }

  public SessionOperationTokenLifecycle tokens() {
    return retainedTokens;
  }

  public ReceiptReferenceRepository receipts() {
    return retainedReceipts;
  }

  @Override
  public void close() {
    codec.close();
  }

  private static final class NeverRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;

    NeverRandom() {
      super(new NeverSpi(), new OwnProvider());
    }
  }

  private static final class OwnProvider extends Provider {
    private static final long serialVersionUID = 1L;

    OwnProvider() {
      super("PGPT_NO_RANDOM", "1.0", "Own fixture, no services or global registration");
    }
  }

  private static final class NeverSpi extends SecureRandomSpi {
    private static final long serialVersionUID = 1L;

    @Override
    protected void engineSetSeed(byte[] seed) {
      throw new AssertionError("random seeding forbidden");
    }

    @Override
    protected void engineNextBytes(byte[] bytes) {
      throw new AssertionError("random generation forbidden");
    }

    @Override
    protected byte[] engineGenerateSeed(int count) {
      throw new AssertionError("random seed generation forbidden");
    }
  }
}
