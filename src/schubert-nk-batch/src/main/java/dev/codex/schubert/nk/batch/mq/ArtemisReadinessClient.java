package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
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
  // SS321 §4 literal operational topology; Batch must not depend on Protocol (SS311 §3).
  private static final List<String> APPROVED_ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");

  public void verifyTopology(ClientSession session) {
    inspectTopology(session);
  }

  /** SSC130: complete approved Address/Queue fields from the same two actual queries. */
  public Map<String, Map<String, String>> inspectTopology(ClientSession session) {
    Objects.requireNonNull(session, "session");
    try {
      var actual = new LinkedHashMap<String, Map<String, String>>();
      for (var addressName : APPROVED_ADDRESSES) {
        var address = SimpleString.of(addressName);
        var queue = SimpleString.of(addressName + ".q");
        var observedAddress = session.addressQuery(address);
        if (observedAddress == null) throw new ArtemisReadinessException();
        if (!observedAddress.isExists()
            || !observedAddress.isSupportsAnycast()
            || observedAddress.isSupportsMulticast()
            || observedAddress.isAutoCreateQueues()
            || observedAddress.isAutoCreateAddresses()
            || !List.of(queue).equals(observedAddress.getQueueNames())) {
          throw new ArtemisReadinessException();
        }
        var observedQueue = session.queueQuery(queue);
        if (observedQueue == null) throw new ArtemisReadinessException();
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
        var fields = new LinkedHashMap<String, String>();
        fields.put("address_exists", bit(observedAddress.isExists()));
        fields.put("anycast", bit(observedAddress.isSupportsAnycast()));
        fields.put("multicast", bit(observedAddress.isSupportsMulticast()));
        fields.put("auto_create_queues", bit(observedAddress.isAutoCreateQueues()));
        fields.put("auto_create_addresses", bit(observedAddress.isAutoCreateAddresses()));
        fields.put("queue_names", observedAddress.getQueueNames().getFirst().toString());
        fields.put("queue_exists", bit(observedQueue.isExists()));
        fields.put("temporary", bit(observedQueue.isTemporary()));
        fields.put("durable", bit(observedQueue.isDurable()));
        fields.put("auto_created", bit(observedQueue.isAutoCreated()));
        fields.put("queue_auto_create", bit(observedQueue.isAutoCreateQueues()));
        fields.put("routing_type", observedQueue.getRoutingType().name());
        fields.put("queue_address", observedQueue.getAddress().toString());
        fields.put("queue_name", observedQueue.getName().toString());
        actual.put(addressName, Map.copyOf(fields));
      }
      return Map.copyOf(actual);
    } catch (ActiveMQException failure) {
      JdbcFailureGraph.preserveFatal(failure);
      throw new ArtemisReadinessException();
    }
  }

  private static String bit(boolean actual) {
    return actual ? "1" : "0";
  }
}
