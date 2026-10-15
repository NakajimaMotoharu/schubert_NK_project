package dev.codex.schubert.nk.api.messaging.config;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import jakarta.jms.ConnectionFactory;
import jakarta.jms.JMSContext;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.function.BiFunction;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * API-only borrowed credential boundary for the three admitted consumer profiles. A context is
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
  private final ConnectionFactory retainedSync;
  private final ConnectionFactory retainedWebLog;
  private final @Nullable ConnectionFactory retainedAsync;
  private final List<AutoCloseable> owners;
  private boolean closed;

  public static ApiBrokerContexts create(ServiceCredentialSet credentials, String endpoint) {
    Objects.requireNonNull(credentials, "credentials");
    return createOwned(
        () -> credentials.copyPassword(ServiceCredentialId.MQ_API),
        endpoint,
        ArtemisConnectionFactoryProvider.INSTANCE::create);
  }

  /**
   * PG-D379: same partial factory ownership; package-only deterministic provider fault boundary.
   */
  static ApiBrokerContexts createOwned(
      Supplier<char[]> passwords,
      String endpoint,
      BiFunction<
              ArtemisConnectionFactoryProvider.ConsumerProfile, String, ActiveMQConnectionFactory>
          provider) {
    Objects.requireNonNull(passwords, "password source");
    Objects.requireNonNull(provider, "factory provider");
    var sync = provider.apply(ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC, endpoint);
    try {
      var webLog =
          provider.apply(ArtemisConnectionFactoryProvider.ConsumerProfile.WEB_LOG, endpoint);
      try {
        var async =
            provider.apply(ArtemisConnectionFactoryProvider.ConsumerProfile.ASYNC, endpoint);
        return new ApiBrokerContexts(passwords, sync, webLog, async, sync, webLog, async);
      } catch (RuntimeException | Error failure) {
        try {
          webLog.close();
        } catch (RuntimeException | Error closing) {
          if (closing != failure) failure.addSuppressed(closing);
        }
        throw failure;
      }
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
    this(passwords, sync, webLog, null, List.of(syncOwner, webLogOwner));
  }

  ApiBrokerContexts(
      Supplier<char[]> passwords,
      ConnectionFactory sync,
      ConnectionFactory webLog,
      ConnectionFactory async,
      AutoCloseable syncOwner,
      AutoCloseable webLogOwner,
      AutoCloseable asyncOwner) {
    this(
        passwords,
        sync,
        webLog,
        Objects.requireNonNull(async, "async factory"),
        List.of(syncOwner, webLogOwner, asyncOwner));
  }

  private ApiBrokerContexts(
      Supplier<char[]> passwords,
      ConnectionFactory sync,
      ConnectionFactory webLog,
      @Nullable ConnectionFactory async,
      List<AutoCloseable> owners) {
    this.passwords = Objects.requireNonNull(passwords, "password source");
    this.retainedSync = Objects.requireNonNull(sync, "sync factory");
    this.retainedWebLog = Objects.requireNonNull(webLog, "Web Log factory");
    this.retainedAsync = async;
    this.owners = owners;
  }

  public Supplier<JMSContext> sync() {
    return () -> open(retainedSync);
  }

  public Supplier<JMSContext> webLog() {
    return () -> open(retainedWebLog);
  }

  /** Ordinary runtime must use the complete create() profile, never legacy package-local PT. */
  public Supplier<JMSContext> async() {
    var factory = Objects.requireNonNull(retainedAsync, "async profile unavailable");
    return () -> open(factory);
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
      for (int index = owners.size() - 1; index >= 0; index--) {
        try {
          owners.get(index).close();
        } catch (Exception | Error closing) {
          if (failure == null || closing instanceof Error && !(failure instanceof Error))
            failure = closing;
        }
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
