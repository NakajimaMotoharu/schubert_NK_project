package dev.codex.schubert.nk.api.messaging.config;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import jakarta.jms.ConnectionFactory;
import jakarta.jms.JMSContext;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.function.BiFunction;
import java.util.function.Consumer;
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
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final Supplier<char[]> passwords;
  private final ConnectionFactory retainedSync;
  private final ConnectionFactory retainedWebLog;
  private final @Nullable ConnectionFactory retainedAsync;
  private final List<AutoCloseable> owners;
  private final boolean[] ownerClosed;
  // SSC334/FACT334002..003: prepare scratch before any factory acquisition; never publish it.
  private final @Nullable Throwable[] closeFailures = new Throwable[3];
  private final Consumer<Throwable> onUnconfirmed;
  private boolean stopping;
  private boolean closed;

  public static ApiBrokerContexts create(ServiceCredentialSet credentials, String endpoint) {
    return create(credentials, endpoint, false);
  }

  /** SSC316: ordinary native assembly retains returned and partial factory UNKNOWN scopes. */
  public static ApiBrokerContexts createRetainingUnknown(
      ServiceCredentialSet credentials, String endpoint) {
    return create(credentials, endpoint, true);
  }

  private static ApiBrokerContexts create(
      ServiceCredentialSet credentials, String endpoint, boolean retainUnknown) {
    Objects.requireNonNull(credentials, "credentials");
    return createOwned(
        () -> credentials.copyPassword(ServiceCredentialId.MQ_API),
        endpoint,
        (profile, admittedEndpoint) ->
            retainUnknown
                ? ArtemisConnectionFactoryProvider.INSTANCE.createRetainingUnknown(
                    profile, admittedEndpoint)
                : ArtemisConnectionFactoryProvider.INSTANCE.create(profile, admittedEndpoint),
        retainUnknown);
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
    return createOwned(passwords, endpoint, provider, false);
  }

  static ApiBrokerContexts createOwned(
      Supplier<char[]> passwords,
      String endpoint,
      BiFunction<
              ArtemisConnectionFactoryProvider.ConsumerProfile, String, ActiveMQConnectionFactory>
          provider,
      boolean retainUnknown) {
    Objects.requireNonNull(passwords, "password source");
    Objects.requireNonNull(provider, "factory provider");
    Objects.requireNonNull(endpoint, "Artemis endpoint");
    return new ApiBrokerContexts(passwords, endpoint, provider, retainUnknown);
  }

  /** SSC315: prepare all ownership state before the first provider resource exists. */
  private ApiBrokerContexts(
      Supplier<char[]> passwords,
      String endpoint,
      BiFunction<
              ArtemisConnectionFactoryProvider.ConsumerProfile, String, ActiveMQConnectionFactory>
          provider,
      boolean retainUnknown) {
    this.passwords = passwords;
    this.onUnconfirmed =
        retainUnknown ? ServiceProcessResources.unknownReleasePolicy() : ignored -> {};
    this.owners = new ArrayList<>(3);
    this.ownerClosed = new boolean[3];
    var sync =
        Objects.requireNonNull(
            provider.apply(ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC, endpoint),
            "sync factory");
    owners.add(sync);
    try {
      var webLog =
          Objects.requireNonNull(
              provider.apply(ArtemisConnectionFactoryProvider.ConsumerProfile.WEB_LOG, endpoint),
              "Web Log factory");
      owners.add(webLog);
      var async =
          Objects.requireNonNull(
              provider.apply(ArtemisConnectionFactoryProvider.ConsumerProfile.ASYNC, endpoint),
              "async factory");
      owners.add(async);
      this.retainedSync = sync;
      this.retainedWebLog = webLog;
      this.retainedAsync = async;
    } catch (RuntimeException | Error failure) {
      try {
        for (int index = owners.size() - 1; index >= 0; index--) {
          try {
            owners.get(index).close();
          } catch (Exception | Error closing) {
            closeFailures[index] = closing;
            onUnconfirmed.accept(closing);
            // Keep the existing raw primary and individual reverse-order secondary.
            if (closing != failure) failure.addSuppressed(closing);
          }
        }
        if (failure.getSuppressed().length == 0) {
          // Only an unretained secondary needs fallback, after all required close attempts.
          for (int index = owners.size() - 1; index >= 0; index--) {
            Throwable closing = closeFailures[index];
            if (closing != null) TemporaryInfrastructureException.attachSecondary(failure, closing);
          }
        }
        throw failure;
      } finally {
        Arrays.fill(closeFailures, null);
      }
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
    this.ownerClosed = new boolean[owners.size()];
    this.onUnconfirmed = ignored -> {};
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
    stateLock.lock();
    try {
      if (stopping) throw new IllegalStateException(UNAVAILABLE);
      char[] copy;
      try {
        copy = Objects.requireNonNull(passwords.get(), "password copy");
      } catch (RuntimeException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        throw new IllegalStateException(UNAVAILABLE);
      }
      try {
        if (copy.length < 1 || copy.length > 65_536)
          throw new IllegalArgumentException("credential length unavailable");
        return Objects.requireNonNull(
            factory.createContext("nk_api", new String(copy), JMSContext.SESSION_TRANSACTED),
            "JMS context");
      } catch (RuntimeException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        throw new IllegalStateException(UNAVAILABLE);
      } finally {
        Arrays.fill(copy, '\0');
      }
    } finally {
      stateLock.unlock();
    }
  }

  @Override
  public void close() {
    stateLock.lock();
    try {
      if (closed) return;
      stopping = true;
      Throwable failure = null;
      for (int index = owners.size() - 1; index >= 0; index--) {
        if (ownerClosed[index]) continue;
        try {
          owners.get(index).close();
          ownerClosed[index] = true;
        } catch (Exception | Error closing) {
          closeFailures[index] = closing;
          if (failure == null || closing instanceof Error && !(failure instanceof Error))
            failure = closing;
        }
      }
      if (failure != null) onUnconfirmed.accept(failure);
      if (failure instanceof Error fatal) throw fatal;
      if (failure != null) {
        TemporaryInfrastructureException.preserveFatal(failure);
        for (int index = owners.size() - 1; index >= 0; index--) {
          Throwable closing = closeFailures[index];
          if (closing != null) TemporaryInfrastructureException.preserveFatal(closing);
        }
        throw new IllegalStateException("API broker factory close failed");
      }
      closed = true;
    } finally {
      Arrays.fill(closeFailures, null);
      stateLock.unlock();
    }
  }

  @Override
  public String toString() {
    return "ApiBrokerContexts[REDACTED]";
  }
}
