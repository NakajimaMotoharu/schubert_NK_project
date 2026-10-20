package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import jakarta.jms.ConnectionFactory;
import jakarta.jms.JMSContext;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.function.Supplier;
import java.util.regex.Pattern;
import org.apache.activemq.artemis.api.core.TransportConfiguration;
import org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory;
import org.apache.activemq.artemis.core.remoting.impl.netty.TransportConstants;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.jspecify.annotations.NullMarked;

/**
 * Web-only fixed-role Artemis owner. Each borrower gets an independent transacted session, while
 * the provider's reply-consumer policy stays at SS321§6's 1MiB. Password copies are erased after
 * Jakarta's String boundary; immutable provider copies are never logged. The caller closes this
 * owner before its outer credential scope. It is not Broker Ops management readiness. NK-MSG-002;
 * RD MQ-001/002/003/006/008,SYS-004; UI231/243/253; SS311/321/342/343; PG362/PT-JMS-WEB-001..003.
 */
@NullMarked
public final class WebBrokerContexts implements AutoCloseable {
  private static final int MAXIMUM_TCP_PORT = 65_535;

  private static final String UNAVAILABLE = "Web broker context unavailable";
  private static final Pattern LOOPBACK_CORE =
      Pattern.compile("tcp://127\\.0\\.0\\.1:([1-9][0-9]{0,4})");

  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final Supplier<char[]> passwords;
  private final ConnectionFactory factory;
  private final AutoCloseable owner;
  private boolean closed;
  private boolean stopping;

  public static WebBrokerContexts create(ServiceCredentialSet credentials, String endpoint) {
    Objects.requireNonNull(credentials, "Web credentials");
    var factory = newFactory(endpoint);
    return new WebBrokerContexts(
        () -> credentials.copyPassword(ServiceCredentialId.MQ_WEB), factory, factory);
  }

  static ActiveMQConnectionFactory newFactory(String endpoint) {
    Objects.requireNonNull(endpoint, "Artemis endpoint");
    var match = LOOPBACK_CORE.matcher(endpoint);
    if (!match.matches()) throw new IllegalArgumentException("Web Artemis endpoint unavailable");
    int port = Integer.parseInt(Objects.requireNonNull(match.group(1), "matched port"));
    if (port > MAXIMUM_TCP_PORT)
      throw new IllegalArgumentException("Web Artemis endpoint unavailable");
    var connector =
        new TransportConfiguration(
            NettyConnectorFactory.class.getName(),
            Map.of(
                TransportConstants.HOST_PROP_NAME,
                "127.0.0.1",
                TransportConstants.PORT_PROP_NAME,
                port,
                TransportConstants.NETTY_CONNECT_TIMEOUT,
                3_000),
            "schubert-nk-core");
    var factory = new ActiveMQConnectionFactory(false, connector);
    factory.setCallTimeout(2_000);
    factory.setClientFailureCheckPeriod(10_000);
    factory.setConnectionTTL(30_000);
    factory.setInitialConnectAttempts(3);
    factory.setReconnectAttempts(-1);
    factory.setRetryInterval(1_000);
    factory.setRetryIntervalMultiplier(2.0);
    factory.setMaxRetryInterval(30_000);
    factory.setConsumerWindowSize(1_048_576);
    factory.setBlockOnDurableSend(true);
    factory.setPreAcknowledge(false);
    factory.setUseTopologyForLoadBalancing(false);
    return factory;
  }

  WebBrokerContexts(Supplier<char[]> passwords, ConnectionFactory factory, AutoCloseable owner) {
    this.passwords = Objects.requireNonNull(passwords, "password source");
    this.factory = Objects.requireNonNull(factory, "JMS factory");
    this.owner = Objects.requireNonNull(owner, "JMS owner");
  }

  public JmsContextFactory contexts() {
    return this::open;
  }

  private JMSContext open() {
    stateLock.lock();
    try {
      if (stopping) throw new IllegalStateException(UNAVAILABLE);
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
            factory.createContext("nk_web", new String(copy), JMSContext.SESSION_TRANSACTED),
            "JMS context");
      } catch (RuntimeException failure) {
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
      try {
        owner.close();
      } catch (Exception failure) {
        dev.codex.schubert.nk.web.session.SessionStoreException.preserveFatal(failure);
        throw new IllegalStateException("Web broker factory close failed");
      }
      closed = true;
    } finally {
      stateLock.unlock();
    }
  }

  @Override
  public String toString() {
    return "WebBrokerContexts[REDACTED]";
  }
}
