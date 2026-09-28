package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.web.logging.WebLogPayloadCodec;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Owns two purpose-separated Web current-key codecs for a native process scope. Copies borrowed
 * from the fixed Web credential set are erased even when the second acquisition or constructor
 * fails. Previous-key rotation, revoke encryption, HTTP readiness and broker ownership are separate
 * mandatory gates; this owner cannot declare the process ready. NK-WEB-002; AUT001, MON003,SYS004;
 * UI226/242/253; SS314/324/343/352; PG367/PT-WEB-NKEY001..004; 471 D01/05/06.
 */
@NullMarked
public final class WebNativeCodecs implements AutoCloseable {
  interface KeySource {
    byte[] copyKey(ServiceCredentialId id);

    String version(ServiceCredentialId id);
  }

  private final Object stateLock = new Object();
  private final SessionPayloadCodec session;
  private final WebLogPayloadCodec log;
  private boolean closed;

  private WebNativeCodecs(SessionPayloadCodec session, WebLogPayloadCodec log) {
    this.session = session;
    this.log = log;
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
    @Nullable SessionPayloadCodec sessionCodec = null;
    try {
      sessionKey =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.WEB_SESSION_AES_CURRENT), "Web session key");
      logKey =
          Objects.requireNonNull(
              source.copyKey(ServiceCredentialId.WEB_LOG_AES_CURRENT), "Web Log key");
      sessionCodec =
          new SessionPayloadCodec(
              source.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT), sessionKey, null, null);
      var logCodec =
          new WebLogPayloadCodec(
              source.version(ServiceCredentialId.WEB_LOG_AES_CURRENT), logKey, null, null);
      return new WebNativeCodecs(sessionCodec, logCodec);
    } catch (RuntimeException | Error failure) {
      if (sessionCodec != null) sessionCodec.close();
      throw failure;
    } finally {
      if (sessionKey != null) Arrays.fill(sessionKey, (byte) 0);
      if (logKey != null) Arrays.fill(logKey, (byte) 0);
    }
  }

  /** Borrowed until this owner closes; callers must not close a child before the process ends. */
  public SessionPayloadCodec session() {
    synchronized (stateLock) {
      requireOpen();
      return session;
    }
  }

  /** Borrowed until this owner closes; callers must not close a child before the process ends. */
  public WebLogPayloadCodec log() {
    synchronized (stateLock) {
      requireOpen();
      return log;
    }
  }

  private void requireOpen() {
    if (closed) throw new IllegalStateException("Web native codecs are closed");
  }

  @Override
  public void close() {
    synchronized (stateLock) {
      if (closed) return;
      closed = true;
      try {
        log.close();
      } finally {
        session.close();
      }
    }
  }
}
