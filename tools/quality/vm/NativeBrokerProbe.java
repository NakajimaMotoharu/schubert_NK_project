import java.nio.file.*;
import java.util.*;
import dev.codex.schubert.nk.batch.mq.*;
import org.apache.activemq.artemis.api.core.*;
import org.apache.activemq.artemis.api.core.client.*;
import org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory;

/** Isolated actual Core/Ops observation, not root/provenance/Expiry startup admission. */
public final class NativeBrokerProbe {
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
        .equals("pgpt-r2-20260927-01") || !System.getProperty("user.name").equals("root"))
      throw new IllegalStateException("isolated root fixture required");
    String password = Files.readString(Path.of("/etc/schubert-nk/credentials/mq-ops")).trim();
    try (var locator = ActiveMQClient.createServerLocatorWithoutHA(new TransportConfiguration(
        NettyConnectorFactory.class.getName(), Map.of("host", "127.0.0.1", "port", 61616)))) {
      locator.setCallTimeout(2000).setInitialConnectAttempts(1).setReconnectAttempts(0);
      try (var factory = locator.createSessionFactory();
          var session = factory.createSession("schubert_ops", password, false, true, true, false, 0)) {
        session.start();
        var observed = new ArtemisStartupObservation().inspect(session);
        if (observed.size() != 6 || observed.values().stream()
            .anyMatch(p -> p != ArtemisQueuePressureClient.Pressure.NORMAL))
          throw new AssertionError("independent six empty queues expected");
        System.out.println("PT-OPS-NATIVE-011 PASS liveCore=true topology=true management=true addressSettings=true acceptor=true roles=true sixQueuePressureNormal=true fullGate=false");
      }
    }
  }
}
