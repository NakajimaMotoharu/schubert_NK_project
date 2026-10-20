package dev.codex.schubert.nk.api.messaging.config;

import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.regex.Pattern;
import org.apache.activemq.artemis.api.core.TransportConfiguration;
import org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory;
import org.apache.activemq.artemis.core.remoting.impl.netty.TransportConstants;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;

/**
 * Credential-free factory template for the loopback Artemis Core endpoint.
 *
 * <p>Credentials are supplied only to {@code createConnection/createContext} by the process
 * credential boundary and are never stored in this provider. Trace: NK-MSG-001; SS 321 §6.
 */
public enum ArtemisConnectionFactoryProvider {
  INSTANCE;
  private static final int MAXIMUM_TCP_PORT = 65_535;

  private static final int MIB = 1024 * 1024;
  private static final Pattern LOOPBACK_CORE =
      Pattern.compile("tcp://127\\.0\\.0\\.1:([1-9][0-9]{0,4})");

  /** Creates a caller-owned factory with the approved reconnect and flow-control policy. */
  public ActiveMQConnectionFactory create(ConsumerProfile profile) {
    return create(profile, "tcp://127.0.0.1:61616");
  }

  /** Uses the admitted loopback Core URL verbatim; no provider-selected host or fallback port. */
  public ActiveMQConnectionFactory create(ConsumerProfile profile, String endpoint) {
    return create(profile, endpoint, false);
  }

  ActiveMQConnectionFactory createRetainingUnknown(ConsumerProfile profile, String endpoint) {
    return create(profile, endpoint, true);
  }

  private ActiveMQConnectionFactory create(
      ConsumerProfile profile, String endpoint, boolean retainUnknown) {
    Objects.requireNonNull(profile, "profile");
    Objects.requireNonNull(endpoint, "endpoint");
    var match = LOOPBACK_CORE.matcher(endpoint);
    if (!match.matches()) throw new IllegalArgumentException("Artemis endpoint unavailable");
    int port = Integer.parseInt(Objects.requireNonNull(match.group(1), "matched port"));
    if (port > MAXIMUM_TCP_PORT) throw new IllegalArgumentException("Artemis endpoint unavailable");
    TransportConfiguration connector =
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
    Consumer<Throwable> onUnconfirmed =
        retainUnknown ? ServiceProcessResources.unknownReleasePolicy() : ignored -> {};
    return configureOwned(
        profile, () -> new ActiveMQConnectionFactory(false, connector), onUnconfirmed);
  }

  /** SSC315/PG-D464: all input ports precede acquisition; failed setup owns one close. */
  static ActiveMQConnectionFactory configureOwned(
      ConsumerProfile profile, Supplier<ActiveMQConnectionFactory> acquire) {
    return configureOwned(profile, acquire, ignored -> {});
  }

  static ActiveMQConnectionFactory configureOwned(
      ConsumerProfile profile,
      Supplier<ActiveMQConnectionFactory> acquire,
      Consumer<Throwable> onUnconfirmed) {
    Objects.requireNonNull(profile, "profile");
    Objects.requireNonNull(acquire, "factory acquisition");
    Objects.requireNonNull(onUnconfirmed, "unconfirmed close policy");
    int windowBytes = profile.windowBytes();
    var factory = Objects.requireNonNull(acquire.get(), "JMS factory");
    try {
      factory.setCallTimeout(2_000);
      factory.setClientFailureCheckPeriod(10_000);
      factory.setConnectionTTL(30_000);
      factory.setInitialConnectAttempts(3);
      factory.setReconnectAttempts(-1);
      factory.setRetryInterval(1_000);
      factory.setRetryIntervalMultiplier(2.0);
      factory.setMaxRetryInterval(30_000);
      factory.setConsumerWindowSize(windowBytes);
      factory.setBlockOnDurableSend(true);
      factory.setPreAcknowledge(false);
      factory.setUseTopologyForLoadBalancing(false);
      return factory;
    } catch (RuntimeException | Error primary) {
      try {
        factory.close();
      } catch (RuntimeException | Error secondary) {
        onUnconfirmed.accept(secondary);
        if (secondary instanceof Error && !(primary instanceof Error)) {
          secondary.addSuppressed(primary);
          throw secondary;
        }
        if (secondary != primary) primary.addSuppressed(secondary);
      }
      throw primary;
    }
  }

  /** Consumer profiles are separate factories because Artemis window size is locator-wide. */
  public enum ConsumerProfile {
    SYNC(MIB),
    ASYNC(0),
    WEB_LOG(64 * 1024);

    private final int configuredWindowBytes;

    ConsumerProfile(int windowBytes) {
      this.configuredWindowBytes = windowBytes;
    }

    public int windowBytes() {
      return configuredWindowBytes;
    }
  }
}
