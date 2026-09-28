package dev.codex.schubert.nk.api.messaging.config;

import java.util.Map;
import java.util.Objects;
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

  private static final int MIB = 1024 * 1024;
  private static final Pattern LOOPBACK_CORE =
      Pattern.compile("tcp://127\\.0\\.0\\.1:([1-9][0-9]{0,4})");

  /** Creates a caller-owned factory with the approved reconnect and flow-control policy. */
  public ActiveMQConnectionFactory create(ConsumerProfile profile) {
    return create(profile, "tcp://127.0.0.1:61616");
  }

  /** Uses the admitted loopback Core URL verbatim; no provider-selected host or fallback port. */
  public ActiveMQConnectionFactory create(ConsumerProfile profile, String endpoint) {
    Objects.requireNonNull(profile, "profile");
    Objects.requireNonNull(endpoint, "endpoint");
    var match = LOOPBACK_CORE.matcher(endpoint);
    if (!match.matches()) throw new IllegalArgumentException("Artemis endpoint unavailable");
    int port = Integer.parseInt(Objects.requireNonNull(match.group(1), "matched port"));
    if (port > 65_535) throw new IllegalArgumentException("Artemis endpoint unavailable");
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
    ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(false, connector);
    factory.setCallTimeout(2_000);
    factory.setClientFailureCheckPeriod(10_000);
    factory.setConnectionTTL(30_000);
    factory.setInitialConnectAttempts(3);
    factory.setReconnectAttempts(-1);
    factory.setRetryInterval(1_000);
    factory.setRetryIntervalMultiplier(2.0);
    factory.setMaxRetryInterval(30_000);
    factory.setConsumerWindowSize(profile.windowBytes());
    factory.setBlockOnDurableSend(true);
    factory.setPreAcknowledge(false);
    factory.setUseTopologyForLoadBalancing(false);
    return factory;
  }

  /** Consumer profiles are separate factories because Artemis window size is locator-wide. */
  public enum ConsumerProfile {
    SYNC(MIB),
    ASYNC(0),
    WEB_LOG(64 * 1024);

    private final int windowBytes;

    ConsumerProfile(int windowBytes) {
      this.windowBytes = windowBytes;
    }

    public int windowBytes() {
      return windowBytes;
    }
  }
}
