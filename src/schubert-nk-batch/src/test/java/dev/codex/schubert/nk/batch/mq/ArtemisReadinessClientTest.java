package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.InputStream;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.apache.activemq.artemis.api.core.RoutingType;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG223/PT-OPS-MQ-001..004; real broker and independent Core query fault matrix. */
final class ArtemisReadinessClientTest {
  private static final String FIXTURE_ISEXISTS_4121EC78 = "isExists";
  private static final String FIXTURE_ISAUTOCREATEQUEUES_DBD40EFD = "isAutoCreateQueues";
  private static final List<String> ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");

  @TempDir Path root;

  @Test
  void opsMq001ActualBrokerHasSixDurableAnycastPairs() throws Exception {
    var broker = start(Files.createDirectory(root.resolve("broker")));
    try (var locator = ActiveMQClient.createServerLocator("vm://0");
        var factory = locator.createSessionFactory();
        var session = factory.createSession()) {
      for (String address : ADDRESSES) {
        var queried = session.addressQuery(SimpleString.of(address));
        assertTrue(queried.isExists());
        assertEquals(List.of(SimpleString.of(address + ".q")), queried.getQueueNames());
      }
      assertDoesNotThrow(() -> new ArtemisReadinessClient().verifyTopology(session));
      assertFalse(session.isClosed());
      assertTrue(session.queueQuery(SimpleString.of("nk.expiry.q")).isExists());
    } finally {
      broker.stop();
    }
  }

  @Test
  void opsMq002MissingLiveQueueFailsWithoutRecreation() throws Exception {
    var broker = start(Files.createDirectory(root.resolve("missing")));
    try (var locator = ActiveMQClient.createServerLocator("vm://0");
        var factory = locator.createSessionFactory();
        var session = factory.createSession()) {
      session.deleteQueue(SimpleString.of("nk.sync.request.q"));
      assertEquals(
          "Artemis effective Queue topology is unavailable",
          assertThrows(
                  ArtemisReadinessException.class,
                  () -> new ArtemisReadinessClient().verifyTopology(session))
              .getMessage());
      assertFalse(session.queueQuery(SimpleString.of("nk.sync.request.q")).isExists());
    } finally {
      broker.stop();
    }
  }

  @Test
  void opsMq003EveryAddressAndQueueMismatchFailsClosed() {
    var reader = new ArtemisReadinessClient();
    for (var fault :
        Map.<String, Object>ofEntries(
                Map.entry(FIXTURE_ISEXISTS_4121EC78, false),
                Map.entry("isSupportsAnycast", false),
                Map.entry("isSupportsMulticast", true),
                Map.entry(FIXTURE_ISAUTOCREATEQUEUES_DBD40EFD, true),
                Map.entry("isAutoCreateAddresses", true),
                Map.entry("getQueueNames", List.of(SimpleString.of("foreign.q"))))
            .entrySet()) {
      assertRejected(reader, synthetic(fault.getKey(), fault.getValue(), true));
    }
    for (var fault :
        Map.<String, Object>ofEntries(
                Map.entry(FIXTURE_ISEXISTS_4121EC78, false),
                Map.entry("isTemporary", true),
                Map.entry("isDurable", false),
                Map.entry("isAutoCreated", true),
                Map.entry(FIXTURE_ISAUTOCREATEQUEUES_DBD40EFD, true),
                Map.entry("getRoutingType", RoutingType.MULTICAST),
                Map.entry("getAddress", SimpleString.of("foreign")),
                Map.entry("getName", SimpleString.of("foreign.q")))
            .entrySet()) {
      assertRejected(reader, synthetic(fault.getKey(), fault.getValue(), false));
    }
    assertRejected(reader, synthetic("addressQuery", null, true));
    assertRejected(reader, synthetic("queueQuery", null, false));
    assertRejected(reader, synthetic("getQueueNames", null, true));
    assertRejected(reader, synthetic("getAddress", null, false));
  }

  @Test
  void opsMq004NullProviderFaultAndBorrowedConcurrentSession() throws Exception {
    var reader = new ArtemisReadinessClient();
    assertThrows(NullPointerException.class, () -> reader.verifyTopology(null));
    for (Object fault :
        List.of(
            new ActiveMQException("private-broker-password"),
            new IllegalArgumentException("private-broker-password"))) {
      var closes = new AtomicInteger();
      ClientSession session =
          proxy(
              ClientSession.class,
              (instance, method, args) -> {
                if (method.getName().equals("addressQuery")) throw (Exception) fault;
                if (method.getName().equals("close")) {
                  closes.incrementAndGet();
                  return null;
                }
                throw new AssertionError("unexpected method " + method.getName());
              });
      if (fault instanceof RuntimeException unknown) {
        assertSame(unknown, assertThrows(unknown.getClass(), () -> reader.verifyTopology(session)));
      } else {
        var failure =
            assertThrows(ArtemisReadinessException.class, () -> reader.verifyTopology(session));
        assertEquals("Artemis effective Queue topology is unavailable", failure.getMessage());
        assertNull(failure.getCause());
      }
      assertEquals(0, closes.get());
    }
    var session = synthetic(null, null, true);
    try (var pool = Executors.newFixedThreadPool(8)) {
      var tasks =
          java.util.stream.IntStream.range(0, 32)
              .<java.util.concurrent.Callable<Boolean>>mapToObj(
                  i ->
                      () -> {
                        reader.verifyTopology(session);
                        return Boolean.TRUE;
                      })
              .toList();
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get(5, TimeUnit.SECONDS));
    }
  }

  private static void assertRejected(ArtemisReadinessClient reader, ClientSession session) {
    var failure =
        assertThrows(ArtemisReadinessException.class, () -> reader.verifyTopology(session));
    assertEquals("Artemis effective Queue topology is unavailable", failure.getMessage());
    assertNull(failure.getCause());
  }

  private static ClientSession synthetic(
      String faultMethod, Object faultValue, boolean addressFault) {
    return proxy(
        ClientSession.class,
        (instance, method, args) -> {
          String called = method.getName();
          if (called.equals("addressQuery")) {
            var address = (SimpleString) args[0];
            if (addressFault && called.equals(faultMethod)) return faultValue;
            return proxy(
                ClientSession.AddressQuery.class,
                (query, property, ignored) -> {
                  if (addressFault && property.getName().equals(faultMethod)) return faultValue;
                  return switch (property.getName()) {
                    case FIXTURE_ISEXISTS_4121EC78, "isSupportsAnycast" -> true;
                    case "isSupportsMulticast",
                        FIXTURE_ISAUTOCREATEQUEUES_DBD40EFD,
                        "isAutoCreateAddresses" ->
                        false;
                    case "getQueueNames" -> List.of(SimpleString.of(address + ".q"));
                    default ->
                        throw new AssertionError(
                            "unexpected address property " + property.getName());
                  };
                });
          }
          if (called.equals("queueQuery")) {
            var queue = (SimpleString) args[0];
            if (!addressFault && called.equals(faultMethod)) return faultValue;
            return proxy(
                ClientSession.QueueQuery.class,
                (query, property, ignored) -> {
                  if (!addressFault && property.getName().equals(faultMethod)) return faultValue;
                  return switch (property.getName()) {
                    case FIXTURE_ISEXISTS_4121EC78, "isDurable" -> true;
                    case "isTemporary", "isAutoCreated", FIXTURE_ISAUTOCREATEQUEUES_DBD40EFD ->
                        false;
                    case "getRoutingType" -> RoutingType.ANYCAST;
                    case "getAddress" ->
                        SimpleString.of(queue.toString().replaceFirst("\\.q$", ""));
                    case "getName" -> queue;
                    default ->
                        throw new AssertionError("unexpected queue property " + property.getName());
                  };
                });
          }
          if (called.equals("close")) throw new AssertionError("borrowed session closed");
          throw new AssertionError("unexpected session method " + called);
        });
  }

  @SuppressWarnings("unchecked")
  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return (T) Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler);
  }

  private static EmbeddedActiveMQ start(Path root) throws Exception {
    Configuration config;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      config = new FileConfigurationParser().parseMainConfig(input);
    }
    config
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large-messages").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(config).start();
  }
}
