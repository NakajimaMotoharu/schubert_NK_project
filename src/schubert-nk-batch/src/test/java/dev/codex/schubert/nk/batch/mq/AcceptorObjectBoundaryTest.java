package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;

/** SS321/342; PG-D507; PT-OPS-MQ-OBJ001..002. Pure fixed JSON, no broker/session operation. */
final class AcceptorObjectBoundaryTest {
  private static final String FACTORY =
      "org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory";
  private static final String PARAMS =
      "{\"scheme\":\"tcp\",\"host\":\"127.0.0.1\",\"port\":\"61616\",\"protocols\":\"CORE\"}";
  private static final List<String> NON_OBJECTS =
      List.of("null", "[]", "\"public-fixture\"", "7", "true");

  private static String response(String params, String extra) {
    return "[{\"name\":\"core\",\"factoryClassName\":\""
        + FACTORY
        + "\",\"params\":"
        + params
        + ",\"extraProps\":"
        + extra
        + "}]";
  }

  private static ClientSession unusedSession(AtomicInteger uses) {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, arguments) -> {
              uses.incrementAndGet();
              throw new AssertionError("data-only reader must never use borrowed session");
            });
  }

  private static void rejectsBeforeStarted(String json, ClientSession session) {
    var reads = new AtomicInteger();
    var client =
        new ArtemisAcceptorReadinessClient(
            ignored -> json,
            ignored -> {
              reads.incrementAndGet();
              return true;
            });
    var failure =
        assertThrows(ArtemisManagementReadinessException.class, () -> client.inspect(session));
    assertEquals("Artemis effective broker configuration is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(0, reads.get());
  }

  @Test
  void opsMqObj001RejectsEachNonObjectExtraPropsBeforeStartedRead() {
    var uses = new AtomicInteger();
    var session = unusedSession(uses);
    var started = new AtomicInteger();
    var normal =
        new ArtemisAcceptorReadinessClient(
            ignored -> response(PARAMS, "{}"),
            ignored -> {
              started.incrementAndGet();
              return true;
            });
    assertEquals(
        Map.of(
            "name",
            "core",
            "factoryClassName",
            FACTORY,
            "scheme",
            "tcp",
            "host",
            "127.0.0.1",
            "port",
            "61616",
            "protocols",
            "CORE",
            "started",
            "1"),
        normal.inspect(session));
    assertEquals(1, started.get());
    for (String value : NON_OBJECTS) rejectsBeforeStarted(response(PARAMS, value), session);
    assertEquals(0, uses.get());
  }

  @Test
  void opsMqObj002RejectsEachNonObjectParamsBeforeStartedRead() {
    var uses = new AtomicInteger();
    var session = unusedSession(uses);
    for (String value : NON_OBJECTS) rejectsBeforeStarted(response(value, "{}"), session);
    assertEquals(0, uses.get());
  }
}
