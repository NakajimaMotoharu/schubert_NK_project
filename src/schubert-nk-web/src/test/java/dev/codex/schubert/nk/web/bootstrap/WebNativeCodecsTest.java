package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
  void nkey005ThirdPurposeCopyNullFaultAndIndependentCipher() throws Exception {
    for (String fault : List.of("copy", "null", "short", "version", "version-null", "fatal")) {
      var source =
          new Source(bytes(1), bytes(65)) {
            @Override
            public byte[] copyKey(ServiceCredentialId id) {
              if (id == ServiceCredentialId.WEB_REVOKE_AES_CURRENT) {
                if (fault.equals("copy"))
                  throw new IllegalStateException("private key unavailable");
                if (fault.equals("null")) return null;
                if (fault.equals("short")) return new byte[31];
              }
              return super.copyKey(id);
            }

            @Override
            public String version(ServiceCredentialId id) {
              if (id == ServiceCredentialId.WEB_REVOKE_AES_CURRENT) {
                if (fault.equals("version")) return "invalid version";
                if (fault.equals("version-null")) return null;
                if (fault.equals("fatal")) throw new AssertionError("private fatal");
              }
              return super.version(id);
            }
          };
      if (fault.equals("fatal"))
        assertThrows(AssertionError.class, () -> WebNativeCodecs.create(source));
      else assertThrows(RuntimeException.class, () -> WebNativeCodecs.create(source));
      assertArrayEquals(new byte[32], ((Source) source).session);
      assertArrayEquals(new byte[32], ((Source) source).log);
    }
    var source = new Source(bytes(1), bytes(65));
    try (var owner = WebNativeCodecs.create(source)) {
      assertArrayEquals(new byte[32], source.revoke);
      UUID id = UUID.fromString("00112233-4455-6677-8899-aabbccddeeff");
      Instant requested = Instant.parse("2026-09-08T00:00:00Z");
      var identity =
          new dev.codex.schubert.nk.web.revocation.RevocationPayloadIdentity(id, requested);
      var actual =
          owner
              .revoke()
              .encrypt(
                  identity,
                  dev.codex.schubert.nk.protocol.header.AuthenticationContext.of("b".repeat(64)))
              .ciphertext();
      var bytes = new java.io.ByteArrayOutputStream();
      try (var out = new java.io.DataOutputStream(bytes)) {
        for (byte[] field :
            List.of(
                "web-revoke".getBytes(java.nio.charset.StandardCharsets.US_ASCII),
                "schubert_web_session.pending_context_revocations"
                    .getBytes(java.nio.charset.StandardCharsets.US_ASCII),
                java.nio.ByteBuffer.allocate(16)
                    .putLong(id.getMostSignificantBits())
                    .putLong(id.getLeastSignificantBits())
                    .array(),
                java.nio.ByteBuffer.allocate(12)
                    .putLong(requested.getEpochSecond())
                    .putInt(0)
                    .array(),
                new byte[] {1},
                "v1".getBytes(java.nio.charset.StandardCharsets.US_ASCII))) {
          out.writeInt(field.length);
          out.write(field);
        }
      }
      assertArrayEquals(
          "NKENC1".getBytes(java.nio.charset.StandardCharsets.US_ASCII),
          java.util.Arrays.copyOf(actual, 6));
      assertEquals(102, actual.length);
      var cipher = javax.crypto.Cipher.getInstance("AES/GCM/NoPadding");
      cipher.init(
          javax.crypto.Cipher.DECRYPT_MODE,
          new javax.crypto.spec.SecretKeySpec(bytes(129), "AES"),
          new javax.crypto.spec.GCMParameterSpec(128, actual, 10, 12));
      cipher.updateAAD(bytes.toByteArray());
      assertArrayEquals(
          "b".repeat(64).getBytes(java.nio.charset.StandardCharsets.US_ASCII),
          cipher.doFinal(actual, 22, 80));
    }
  }

  @Test
  void nkey001CopiesErasedButBorrowedCodecsSurviveUntilOwnerClose() {
    byte[] sessionKey = bytes(1);
    byte[] logKey = bytes(65);
    var owner = WebNativeCodecs.create(new Source(sessionKey, logKey));
    assertArrayEquals(new byte[32], sessionKey);
    assertArrayEquals(new byte[32], logKey);
    var session = owner.session();
    var log = owner.log();
    var revoke = owner.revoke();
    var encrypted = session.encrypt(SESSION_ID, EMPTY);
    assertEquals("v1", encrypted.keyVersion());
    assertEquals(EMPTY, session.decrypt(SESSION_ID, encrypted));
    owner.close();
    owner.close();
    assertThrows(IllegalStateException.class, owner::session);
    assertThrows(IllegalStateException.class, owner::log);
    assertThrows(IllegalStateException.class, owner::revoke);
    assertThrows(
        IllegalStateException.class,
        () ->
            revoke.encrypt(
                new dev.codex.schubert.nk.web.revocation.RevocationPayloadIdentity(
                    UUID.randomUUID(), Instant.parse("2026-09-08T00:00:00Z")),
                dev.codex.schubert.nk.protocol.header.AuthenticationContext.of("b".repeat(64))));
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
    byte[] session = bytes(1);
    byte[] log = bytes(65);
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
            ServiceCredentialId.WEB_SESSION_AES_CURRENT,
            ServiceCredentialId.WEB_LOG_AES_CURRENT,
            ServiceCredentialId.WEB_REVOKE_AES_CURRENT),
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
    private final byte[] revoke = bytes(129);
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
      if (id == ServiceCredentialId.WEB_REVOKE_AES_CURRENT) return revoke;
      throw new AssertionError("unexpected key purpose");
    }

    @Override
    public String version(ServiceCredentialId id) {
      if (id == ServiceCredentialId.WEB_SESSION_AES_CURRENT
          || id == ServiceCredentialId.WEB_LOG_AES_CURRENT
          || id == ServiceCredentialId.WEB_REVOKE_AES_CURRENT) return "v1";
      throw new AssertionError("unexpected version purpose");
    }
  }
}
