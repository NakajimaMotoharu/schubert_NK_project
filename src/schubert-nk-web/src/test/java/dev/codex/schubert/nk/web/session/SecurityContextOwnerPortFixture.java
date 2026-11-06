package dev.codex.schubert.nk.web.session;

import java.lang.reflect.Proxy;
import java.security.Provider;
import java.security.SecureRandom;
import java.security.SecureRandomSpi;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import javax.sql.DataSource;

/** Constructor-only owner identity for PT-WEB-SCTXPORT. Never obtains a session, nonce or DB. */
public final class SecurityContextOwnerPortFixture implements AutoCloseable {
  private final SessionPayloadCodec codec;
  private final SpringEncryptedSessionRepository retainedRepository;

  public SecurityContextOwnerPortFixture() {
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
    var lifecycle =
        new EncryptedWebSessionRepository(
            database,
            codec,
            clock,
            random,
            () -> {
              throw new AssertionError("session identifier generation forbidden");
            });
    retainedRepository = new SpringEncryptedSessionRepository(lifecycle, clock);
  }

  public SpringEncryptedSessionRepository sessions() {
    return retainedRepository;
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
