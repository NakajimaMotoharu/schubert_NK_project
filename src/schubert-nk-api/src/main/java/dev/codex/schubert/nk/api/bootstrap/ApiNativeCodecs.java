package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * Three actual current credential purposes for the admitted ordinary API assembly.
 * NK-AUT-001/NK-MSG-002; DAT009/AUT001/MQ006; UI226241253; SS314324343352/SSC149;
 * PT-OPS-API-KEY-001..005. Previous profiles must be explicitly provisioned; no key fallback.
 */
public final class ApiNativeCodecs implements AutoCloseable {
  interface KeySource {
    byte[] copyKey(ServiceCredentialId id);

    String version(ServiceCredentialId id);
  }

  private final Object lock = new Object();
  private final AuthContextCodec contexts;
  private final ResponseSnapshotCodec snapshots;
  private final FingerprintKeyRing fingerprints;
  private boolean closed;

  private ApiNativeCodecs(
      AuthContextCodec contexts, ResponseSnapshotCodec snapshots, FingerprintKeyRing fingerprints) {
    this.contexts = contexts;
    this.snapshots = snapshots;
    this.fingerprints = fingerprints;
  }

  public static ApiNativeCodecs create(ServiceCredentialSet credentials) {
    Objects.requireNonNull(credentials, "API credentials");
    return create(
        new KeySource() {
          public byte[] copyKey(ServiceCredentialId id) {
            return credentials.copyKey(id);
          }

          public String version(ServiceCredentialId id) {
            return credentials.version(id);
          }
        });
  }

  static ApiNativeCodecs create(KeySource source) {
    Objects.requireNonNull(source, "API key source");
    byte @Nullable [] context = null, response = null, fingerprint = null;
    @Nullable AuthContextCodec contexts = null;
    @Nullable ResponseSnapshotCodec snapshots = null;
    try {
      context =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.API_CONTEXT_AES_CURRENT), "context key");
      response =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.API_INBOX_RESPONSE_AES_CURRENT), "response key");
      fingerprint =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.OPERATION_HMAC_CURRENT), "fingerprint key");
      if (MessageDigest.isEqual(context, response)
          || MessageDigest.isEqual(context, fingerprint)
          || MessageDigest.isEqual(response, fingerprint))
        throw new IllegalArgumentException("API key purposes must differ");
      contexts =
          new AuthContextCodec(
              source.version(ServiceCredentialId.API_CONTEXT_AES_CURRENT), context, null, null);
      snapshots =
          new ResponseSnapshotCodec(
              source.version(ServiceCredentialId.API_INBOX_RESPONSE_AES_CURRENT),
              response,
              null,
              null);
      var fingerprints =
          new FingerprintKeyRing(
              source.version(ServiceCredentialId.OPERATION_HMAC_CURRENT), fingerprint, null, null);
      return new ApiNativeCodecs(contexts, snapshots, fingerprints);
    } catch (RuntimeException | Error failure) {
      if (snapshots != null) snapshots.close();
      if (contexts != null) contexts.close();
      throw failure;
    } finally {
      if (context != null) Arrays.fill(context, (byte) 0);
      if (response != null) Arrays.fill(response, (byte) 0);
      if (fingerprint != null) Arrays.fill(fingerprint, (byte) 0);
    }
  }

  public AuthContextCodec contexts() {
    synchronized (lock) {
      requireOpen();
      return contexts;
    }
  }

  public ResponseSnapshotCodec snapshots() {
    synchronized (lock) {
      requireOpen();
      return snapshots;
    }
  }

  public FingerprintKeyRing fingerprints() {
    synchronized (lock) {
      requireOpen();
      return fingerprints;
    }
  }

  private void requireOpen() {
    if (closed) throw new IllegalStateException("API native codecs closed");
  }

  public void close() {
    synchronized (lock) {
      if (closed) return;
      closed = true;
      fingerprints.close();
      snapshots.close();
      contexts.close();
    }
  }
}
