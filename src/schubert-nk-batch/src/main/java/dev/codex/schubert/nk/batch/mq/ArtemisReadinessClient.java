package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import java.util.List;
import java.util.Objects;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.apache.activemq.artemis.api.core.RoutingType;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.api.core.client.ClientSession;

/**
 * Read-only live Core query of the six approved Address/Queue pairs. The caller owns and closes the
 * Ops-credential session; this class never creates a Queue or consumes a message. Journal, disk,
 * ACL and address-settings checks remain separate mandatory SS321 readiness gates. NK-OPS-001;
 * MQ-001/002/009/010,SYS-004; UI231/251; SS311/321/341/342; PG223/PT-OPS-MQ-001..004.
 */
public final class ArtemisReadinessClient {
  public void verifyTopology(ClientSession session) {
    Objects.requireNonNull(session, "session");
    try {
      for (var expected : BrokerTopology.values()) {
        var address = SimpleString.of(expected.address());
        var queue = SimpleString.of(expected.queue());
        var observedAddress = Objects.requireNonNull(session.addressQuery(address));
        if (!observedAddress.isExists()
            || !observedAddress.isSupportsAnycast()
            || observedAddress.isSupportsMulticast()
            || observedAddress.isAutoCreateQueues()
            || observedAddress.isAutoCreateAddresses()
            || !List.of(queue).equals(observedAddress.getQueueNames())) {
          throw new ArtemisReadinessException();
        }
        var observedQueue = Objects.requireNonNull(session.queueQuery(queue));
        if (!observedQueue.isExists()
            || observedQueue.isTemporary()
            || !observedQueue.isDurable()
            || observedQueue.isAutoCreated()
            || observedQueue.isAutoCreateQueues()
            || observedQueue.getRoutingType() != RoutingType.ANYCAST
            || !address.equals(observedQueue.getAddress())
            || !queue.equals(observedQueue.getName())) {
          throw new ArtemisReadinessException();
        }
      }
    } catch (ActiveMQException | RuntimeException failure) {
      throw new ArtemisReadinessException();
    }
  }
}
