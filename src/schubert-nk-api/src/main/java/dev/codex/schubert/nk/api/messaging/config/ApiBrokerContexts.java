package dev.codex.schubert.nk.api.messaging.config;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import jakarta.jms.ConnectionFactory;
import jakarta.jms.JMSContext;
import java.util.Arrays;
import java.util.Objects;
import java.util.function.Supplier;
import org.jspecify.annotations.NullMarked;

/**
 * API-only borrowed credential boundary for the two admitted consumer profiles. A context is
 * caller-owned; this owner closes its factories before the outer credential set and DB scope.
 * Password copies are erased after each createContext call; Jakarta's immutable String boundary
 * cannot promise physical erasure and must never be logged. It is not Broker management readiness.
 * NK-MSG-001/NK-OPS-001; RD MQ-001/003/006/008,SYS-004; UI231/253; SS321§6/342/343§6;
 * PG361/PT-JMS-024; 471 D01/D03/D05.
 */
@NullMarked
public final class ApiBrokerContexts implements AutoCloseable {
  private static final String UNAVAILABLE = "API broker context unavailable";
  private final Object stateLock = new Object();
  private final Supplier<char[]> passwords;
  private final ConnectionFactory sync;
  private final ConnectionFactory webLog;
  private final AutoCloseable syncOwner;
  private final AutoCloseable webLogOwner;
  private boolean closed;

  public static ApiBrokerContexts create(ServiceCredentialSet credentials, String endpoint) {
    Objects.requireNonNull(credentials, "credentials");
    var provider = ArtemisConnectionFactoryProvider.INSTANCE;
    var sync = provider.create(ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC, endpoint);
    try {
      var webLog =
          provider.create(ArtemisConnectionFactoryProvider.ConsumerProfile.WEB_LOG, endpoint);
      return new ApiBrokerContexts(
          () -> credentials.copyPassword(ServiceCredentialId.MQ_API), sync, webLog, sync, webLog);
    } catch (RuntimeException | Error failure) {
      try {
        sync.close();
      } catch (RuntimeException | Error closing) {
        if (closing != failure) failure.addSuppressed(closing);
      }
      throw failure;
    }
  }

  ApiBrokerContexts(
      Supplier<char[]> passwords,
      ConnectionFactory sync,
      ConnectionFactory webLog,
      AutoCloseable syncOwner,
      AutoCloseable webLogOwner) {
    this.passwords = Objects.requireNonNull(passwords, "password source");
    this.sync = Objects.requireNonNull(sync, "sync factory");
    this.webLog = Objects.requireNonNull(webLog, "Web Log factory");
    this.syncOwner = Objects.requireNonNull(syncOwner, "sync factory owner");
    this.webLogOwner = Objects.requireNonNull(webLogOwner, "Web Log factory owner");
  }

  public Supplier<JMSContext> sync() {
    return () -> open(sync);
  }

  public Supplier<JMSContext> webLog() {
    return () -> open(webLog);
  }

  private JMSContext open(ConnectionFactory factory) {
    synchronized (stateLock) {
      if (closed) throw new IllegalStateException(UNAVAILABLE);
      char[] copy;
      try {
        copy = Objects.requireNonNull(passwords.get(), "password copy");
      } catch (RuntimeException failure) {
        throw new IllegalStateException(UNAVAILABLE);
      }
      try {
        if (copy.length < 1 || copy.length > 65_536)
          throw new IllegalArgumentException("credential length unavailable");
        return Objects.requireNonNull(
            factory.createContext("nk_api", new String(copy), JMSContext.SESSION_TRANSACTED),
            "JMS context");
      } catch (RuntimeException failure) {
        throw new IllegalStateException(UNAVAILABLE);
      } finally {
        Arrays.fill(copy, '\0');
      }
    }
  }

  @Override
  public void close() {
    synchronized (stateLock) {
      if (closed) return;
      closed = true;
      Throwable failure = null;
      try {
        webLogOwner.close();
      } catch (Exception | Error closing) {
        failure = closing;
      }
      try {
        syncOwner.close();
      } catch (Exception | Error closing) {
        if (failure == null || closing instanceof Error && !(failure instanceof Error))
          failure = closing;
      }
      if (failure instanceof Error fatal) throw fatal;
      if (failure != null) throw new IllegalStateException("API broker factory close failed");
    }
  }

  @Override
  public String toString() {
    return "ApiBrokerContexts[REDACTED]";
  }
}
