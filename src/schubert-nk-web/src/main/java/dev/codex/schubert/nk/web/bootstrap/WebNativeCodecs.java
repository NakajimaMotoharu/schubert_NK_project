package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.web.logging.WebLogPayloadCodec;
import dev.codex.schubert.nk.web.revocation.RevocationPayloadCodec;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Owns three purpose-separated Web current-key codecs for a native process scope. Copies borrowed
 * from the fixed Web credential set are erased even when the second acquisition or constructor
 * fails. Previous-key rotation, HTTP readiness and broker ownership are separate mandatory gates;
 * this owner cannot declare the process ready. NK-WEB-002; AUT001, MON003,SYS004; UI226/242/253;
 * SS314/324/343/352; PG367/PT-WEB-NKEY001..004; 471 D01/05/06.
 */
@NullMarked
public final class WebNativeCodecs implements AutoCloseable {
  interface KeySource {
    byte[] copyKey(ServiceCredentialId id);

    String version(ServiceCredentialId id);
  }

  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final SessionPayloadCodec retainedSession;
  private final WebLogPayloadCodec retainedLog;
  private final RevocationPayloadCodec retainedRevoke;
  private boolean closed;

  private WebNativeCodecs(
      SessionPayloadCodec session, WebLogPayloadCodec log, RevocationPayloadCodec revoke) {
    this.retainedSession = session;
    this.retainedLog = log;
    this.retainedRevoke = revoke;
  }

  public static WebNativeCodecs create(ServiceCredentialSet credentials) {
    Objects.requireNonNull(credentials, "Web credentials");
    return create(
        new KeySource() {
          @Override
          public byte[] copyKey(ServiceCredentialId id) {
            return credentials.copyKey(id);
          }

          @Override
          public String version(ServiceCredentialId id) {
            return credentials.version(id);
          }
        });
  }

  static WebNativeCodecs create(KeySource source) {
    Objects.requireNonNull(source, "Web key source");
    byte @Nullable [] sessionKey = null;
    byte @Nullable [] logKey = null;
    byte @Nullable [] revokeKey = null;
    @Nullable SessionPayloadCodec sessionCodec = null;
    @Nullable WebLogPayloadCodec logCodec = null;
    try {
      sessionKey =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.WEB_SESSION_AES_CURRENT), "Web session key");
      logKey =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.WEB_LOG_AES_CURRENT), "Web Log key");
      revokeKey =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.WEB_REVOKE_AES_CURRENT), "Web revoke key");
      sessionCodec =
          new SessionPayloadCodec(
              source.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT), sessionKey, null, null);
      logCodec =
          new WebLogPayloadCodec(
              source.version(ServiceCredentialId.WEB_LOG_AES_CURRENT), logKey, null, null);
      var revokeCodec =
          new RevocationPayloadCodec(
              source.version(ServiceCredentialId.WEB_REVOKE_AES_CURRENT), revokeKey, null, null);
      return new WebNativeCodecs(sessionCodec, logCodec, revokeCodec);
    } catch (RuntimeException | Error failure) {
      if (logCodec != null) logCodec.close();
      if (sessionCodec != null) sessionCodec.close();
      throw failure;
    } finally {
      if (sessionKey != null) Arrays.fill(sessionKey, (byte) 0);
      if (logKey != null) Arrays.fill(logKey, (byte) 0);
      if (revokeKey != null) Arrays.fill(revokeKey, (byte) 0);
    }
  }

  /** Borrowed until this owner closes; callers must not close a child before the process ends. */
  public SessionPayloadCodec session() {
    stateLock.lock();
    try {
      requireOpen();
      return retainedSession;
    } finally {
      stateLock.unlock();
    }
  }

  /** Borrowed until this owner closes; callers must not close a child before the process ends. */
  public WebLogPayloadCodec log() {
    stateLock.lock();
    try {
      requireOpen();
      return retainedLog;
    } finally {
      stateLock.unlock();
    }
  }

  /** Third purpose, retained until the worker and every borrower has been joined. */
  public RevocationPayloadCodec revoke() {
    stateLock.lock();
    try {
      requireOpen();
      return retainedRevoke;
    } finally {
      stateLock.unlock();
    }
  }

  private void requireOpen() {
    if (closed) throw new IllegalStateException("Web native codecs are closed");
  }

  @Override
  public void close() {
    stateLock.lock();
    try {
      if (closed) return;
      closed = true;
      try {
        retainedRevoke.close();
      } finally {
        try {
          retainedLog.close();
        } finally {
          retainedSession.close();
        }
      }
    } finally {
      stateLock.unlock();
    }
  }
}
