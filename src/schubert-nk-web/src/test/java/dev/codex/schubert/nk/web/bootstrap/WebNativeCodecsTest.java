package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.web.logging.EncryptedWebLogPayload;
import dev.codex.schubert.nk.web.logging.WebLogPayloadIdentity;
import dev.codex.schubert.nk.web.session.SessionAttributes;
import dev.codex.schubert.nk.web.session.SessionPayloadIdentity;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-WEB-002; SS314/324/343/352; PG367/PT-WEB-NKEY001..004. Synthetic keys only. */
final class WebNativeCodecsTest {
  private static final SessionPayloadIdentity SESSION_ID =
      new SessionPayloadIdentity(
          UUID.fromString("00112233-4455-6677-8899-aabbccddeeff"),
          "a".repeat(64),
          Instant.parse("2026-09-08T00:00:00Z"));
  private static final SessionAttributes EMPTY =
      new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), List.of());

  @Test
  void nkey001CopiesErasedButBorrowedCodecsSurviveUntilOwnerClose() {
    byte[] sessionKey = bytes(1), logKey = bytes(65);
    var owner = WebNativeCodecs.create(new Source(sessionKey, logKey));
    assertArrayEquals(new byte[32], sessionKey);
    assertArrayEquals(new byte[32], logKey);
    var session = owner.session();
    var log = owner.log();
    var encrypted = session.encrypt(SESSION_ID, EMPTY);
    assertEquals("v1", encrypted.keyVersion());
    assertEquals(EMPTY, session.decrypt(SESSION_ID, encrypted));
    owner.close();
    owner.close();
    assertThrows(IllegalStateException.class, owner::session);
    assertThrows(IllegalStateException.class, owner::log);
    assertThrows(IllegalStateException.class, () -> session.encrypt(SESSION_ID, EMPTY));
    assertThrows(
        IllegalStateException.class,
        () ->
            log.decrypt(
                new WebLogPayloadIdentity(UUID.randomUUID(), UUID.randomUUID()),
                new EncryptedWebLogPayload("v1", new byte[29])));
  }

  @Test
  void nkey002NullMissingSecondCopyAndInvalidLengthFailClosed() {
    assertThrows(
        NullPointerException.class, () -> WebNativeCodecs.create((WebNativeCodecs.KeySource) null));
    assertThrows(
        IllegalStateException.class,
        () ->
            WebNativeCodecs.create(
                new WebNativeCodecs.KeySource() {
                  public byte[] copyKey(ServiceCredentialId id) {
                    throw new IllegalStateException("synthetic source unavailable");
                  }

                  public String version(ServiceCredentialId id) {
                    throw new AssertionError("version not reached");
                  }
                }));
    byte[] first = bytes(1);
    var failSecond =
        new Source(first, bytes(65)) {
          @Override
          public byte[] copyKey(ServiceCredentialId id) {
            if (id == ServiceCredentialId.WEB_LOG_AES_CURRENT)
              throw new IllegalStateException("synthetic second copy unavailable");
            return super.copyKey(id);
          }
        };
    assertThrows(IllegalStateException.class, () -> WebNativeCodecs.create(failSecond));
    assertArrayEquals(new byte[32], first);
    for (boolean sessionBad : new boolean[] {true, false}) {
      byte[] session = sessionBad ? new byte[31] : bytes(1);
      byte[] log = sessionBad ? bytes(65) : new byte[31];
      assertThrows(
          IllegalArgumentException.class, () -> WebNativeCodecs.create(new Source(session, log)));
      assertArrayEquals(new byte[session.length], session);
      assertArrayEquals(new byte[log.length], log);
    }
  }

  @Test
  void nkey003PurposeOrderAndVersionFailureNeverUseFallback() {
    byte[] session = bytes(1), log = bytes(65);
    var source =
        new Source(session, log) {
          @Override
          public String version(ServiceCredentialId id) {
            if (id == ServiceCredentialId.WEB_LOG_AES_CURRENT) return "invalid version";
            return super.version(id);
          }
        };
    assertThrows(IllegalArgumentException.class, () -> WebNativeCodecs.create(source));
    assertEquals(
        List.of(
            ServiceCredentialId.WEB_SESSION_AES_CURRENT, ServiceCredentialId.WEB_LOG_AES_CURRENT),
        ((Source) source).requests);
    assertArrayEquals(new byte[32], session);
    assertArrayEquals(new byte[32], log);
  }

  @Test
  void nkey004ConcurrentBorrowAndCloseHaveOnlyOwnedOrClosedOutcome() throws Exception {
    var owner = WebNativeCodecs.create(new Source(bytes(1), bytes(65)));
    try (var workers = Executors.newFixedThreadPool(2)) {
      var started = new CountDownLatch(1);
      var reader =
          workers.submit(
              () -> {
                started.countDown();
                int returned = 0;
                for (int i = 0; i < 100; i++) {
                  try {
                    assertNotNull(owner.session());
                    returned++;
                  } catch (IllegalStateException closed) {
                    break;
                  }
                }
                return returned;
              });
      assertTrue(started.await(5, TimeUnit.SECONDS));
      owner.close();
      assertTrue(reader.get(5, TimeUnit.SECONDS).intValue() <= 100);
      assertThrows(IllegalStateException.class, owner::session);
    } finally {
      owner.close();
    }
  }

  private static byte[] bytes(int first) {
    byte[] result = new byte[32];
    for (int i = 0; i < result.length; i++) result[i] = (byte) (first + i);
    return result;
  }

  private static class Source implements WebNativeCodecs.KeySource {
    private final byte[] session;
    private final byte[] log;
    private final List<ServiceCredentialId> requests = new ArrayList<>();

    private Source(byte[] session, byte[] log) {
      this.session = session;
      this.log = log;
    }

    @Override
    public byte[] copyKey(ServiceCredentialId id) {
      requests.add(id);
      if (id == ServiceCredentialId.WEB_SESSION_AES_CURRENT) return session;
      if (id == ServiceCredentialId.WEB_LOG_AES_CURRENT) return log;
      throw new AssertionError("unexpected key purpose");
    }

    @Override
    public String version(ServiceCredentialId id) {
      if (id == ServiceCredentialId.WEB_SESSION_AES_CURRENT
          || id == ServiceCredentialId.WEB_LOG_AES_CURRENT) return "v1";
      throw new AssertionError("unexpected version purpose");
    }
  }
}
