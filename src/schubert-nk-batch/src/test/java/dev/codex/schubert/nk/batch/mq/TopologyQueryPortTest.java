package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.apache.activemq.artemis.api.core.RoutingType;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** OPS-TOPO-PORT-001..006: stable query DTOs and memory Core session, never actual broker. */
final class TopologyQueryPortTest {
  private static final String TEXT_A_NK_SYNC_REQUEST = "A:nk.sync.request";
  private static final String TEXT_ADDRESSQUERY = "addressQuery";
  private static final String TEXT_DURABLE = "durable";
  private static final String TEXT_ISAUTOCREATEQUEUES = "isAutoCreateQueues";
  private static final String TEXT_ISEXISTS = "isExists";
  private static final List<String> ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");
  private static final String FIXED = "Artemis effective Queue topology is unavailable";

  @Test
  void sixLiteralPairsReturnEveryVerifiedFieldAndBothMapsStayImmutable() {
    Fixture fixture = new Fixture();
    var result = new ArtemisReadinessClient().inspectTopology(fixture.session());
    assertEquals(6, result.size());
    for (String address : ADDRESSES) {
      assertEquals(expected(address), result.get(address));
      assertThrows(
          UnsupportedOperationException.class, () -> result.get(address).put(TEXT_DURABLE, "0"));
    }
    assertThrows(UnsupportedOperationException.class, () -> result.clear());
    assertEquals(expectedQueries(), fixture.queries);
  }

  @Test
  void everyAddressFlagAndNullEmptyWrongDuplicateOrNullElementQueueListRejectsBeforeQueueQuery() {
    for (var entry :
        Map.<String, Object>of(
                TEXT_ISEXISTS,
                false,
                "isSupportsAnycast",
                false,
                "isSupportsMulticast",
                true,
                TEXT_ISAUTOCREATEQUEUES,
                true,
                "isAutoCreateAddresses",
                true)
            .entrySet()) rejectAddress(entry.getKey(), entry.getValue());
    for (Object list :
        new Object[] {
          null,
          List.of(),
          List.of(SimpleString.of("wrong.q")),
          List.of(SimpleString.of("nk.sync.request.q"), SimpleString.of("extra.q")),
          Arrays.asList((SimpleString) null)
        }) rejectAddress("getQueueNames", list);
    Fixture missing = new Fixture();
    missing.nullAddress = true;
    catalog(() -> new ArtemisReadinessClient().verifyTopology(missing.session()));
    assertEquals(List.of(TEXT_A_NK_SYNC_REQUEST), missing.queries);
  }

  @Test
  void everyQueueFlagRoutingAndNullableNameOrAddressDifferenceIsAClosedFailure() {
    for (var entry :
        Map.<String, Object>of(
                TEXT_ISEXISTS,
                false,
                "isTemporary",
                true,
                "isDurable",
                false,
                "isAutoCreated",
                true,
                TEXT_ISAUTOCREATEQUEUES,
                true,
                "getRoutingType",
                RoutingType.MULTICAST)
            .entrySet()) rejectQueue(entry.getKey(), entry.getValue());
    rejectQueue("getRoutingType", null);
    rejectQueue("getAddress", null);
    rejectQueue("getName", null);
    rejectQueue("getAddress", SimpleString.of("wrong"));
    rejectQueue("getName", SimpleString.of("wrong.q"));
    Fixture missing = new Fixture();
    missing.nullQueue = true;
    catalog(() -> new ArtemisReadinessClient().verifyTopology(missing.session()));
    assertEquals(List.of(TEXT_A_NK_SYNC_REQUEST, "Q:nk.sync.request.q"), missing.queries);
  }

  @Test
  void checkedSessionFailureHasFixedDiagnosticsWhileUnknownSessionOrGetterFailuresKeepIdentity() {
    for (String point : List.of(TEXT_ADDRESSQUERY, "queueQuery")) {
      Fixture checked = new Fixture();
      checked.sessionFault = point;
      checked.failure = new ActiveMQException("private synthetic provider");
      catalog(() -> new ArtemisReadinessClient().inspectTopology(checked.session()));
      assertEquals(point.equals(TEXT_ADDRESSQUERY) ? 1 : 2, checked.queries.size());
      for (Throwable unknown :
          List.of(
              new IllegalStateException("private runtime"), new AssertionError("private fatal"))) {
        Fixture fixture = new Fixture();
        fixture.sessionFault = point;
        fixture.failure = unknown;
        assertSame(
            unknown,
            assertThrows(
                unknown.getClass(),
                () -> new ArtemisReadinessClient().inspectTopology(fixture.session())));
      }
    }
    for (boolean address : List.of(false, true))
      for (Throwable unknown :
          List.of(
              new IllegalStateException("private getter"),
              new AssertionError("private getter fatal"))) {
        Fixture fixture = new Fixture();
        (address ? fixture.addressChanges : fixture.queueChanges).put(TEXT_ISEXISTS, unknown);
        assertSame(
            unknown,
            assertThrows(
                unknown.getClass(),
                () -> new ArtemisReadinessClient().inspectTopology(fixture.session())));
      }
  }

  @Test
  void bothPublicNullEntriesRejectBeforeAnyQueryOrCreationOrConsumption() {
    var reader = new ArtemisReadinessClient();
    assertEquals(
        "session",
        assertThrows(NullPointerException.class, () -> reader.inspectTopology(null)).getMessage());
    assertEquals(
        "session",
        assertThrows(NullPointerException.class, () -> reader.verifyTopology(null)).getMessage());
    Fixture fixture = new Fixture();
    reader.verifyTopology(fixture.session());
    assertEquals(expectedQueries(), fixture.queries);
    assertEquals(0, fixture.forbiddenSessionOperations);
  }

  @Test
  void reusedStatelessReaderKeepsIndependentSessionSnapshotsAndDoesNotRetainTheirMutableFixture() {
    var reader = new ArtemisReadinessClient();
    Fixture first = new Fixture();
    Fixture second = new Fixture();
    var snapshot = reader.inspectTopology(first.session());
    var other = reader.inspectTopology(second.session());
    assertEquals(snapshot, other);
    assertEquals(expectedQueries(), first.queries);
    assertEquals(expectedQueries(), second.queries);
    first.queueChanges.put("isDurable", false);
    catalog(() -> reader.inspectTopology(first.session()));
    assertEquals("1", snapshot.get("nk.sync.request").get(TEXT_DURABLE));
    assertEquals("1", other.get("nk.sync.request").get(TEXT_DURABLE));
    assertEquals(0, first.forbiddenSessionOperations);
    assertEquals(0, second.forbiddenSessionOperations);
  }

  private static Map<String, String> expected(String address) {
    return Map.ofEntries(
        Map.entry("address_exists", "1"),
        Map.entry("anycast", "1"),
        Map.entry("multicast", "0"),
        Map.entry("auto_create_queues", "0"),
        Map.entry("auto_create_addresses", "0"),
        Map.entry("queue_names", address + ".q"),
        Map.entry("queue_exists", "1"),
        Map.entry("temporary", "0"),
        Map.entry(TEXT_DURABLE, "1"),
        Map.entry("auto_created", "0"),
        Map.entry("queue_auto_create", "0"),
        Map.entry("routing_type", "ANYCAST"),
        Map.entry("queue_address", address),
        Map.entry("queue_name", address + ".q"));
  }

  private static List<String> expectedQueries() {
    var result = new ArrayList<String>();
    for (String a : ADDRESSES) {
      result.add("A:" + a);
      result.add("Q:" + a + ".q");
    }
    return result;
  }

  private static void rejectAddress(String name, Object value) {
    Fixture fixture = new Fixture();
    fixture.addressChanges.put(name, value);
    catalog(() -> new ArtemisReadinessClient().inspectTopology(fixture.session()));
    assertEquals(List.of(TEXT_A_NK_SYNC_REQUEST), fixture.queries);
    assertEquals(0, fixture.forbiddenSessionOperations);
  }

  private static void rejectQueue(String name, Object value) {
    Fixture fixture = new Fixture();
    fixture.queueChanges.put(name, value);
    catalog(() -> new ArtemisReadinessClient().inspectTopology(fixture.session()));
    assertEquals(List.of(TEXT_A_NK_SYNC_REQUEST, "Q:nk.sync.request.q"), fixture.queries);
    assertEquals(0, fixture.forbiddenSessionOperations);
  }

  private static void catalog(Executable action) {
    var failure = assertThrows(ArtemisReadinessException.class, action);
    assertEquals(FIXED, failure.getMessage());
    assertEquals(null, failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    private final Map<String, Object> addressChanges = new HashMap<>();
    private final Map<String, Object> queueChanges = new HashMap<>();
    private final List<String> queries = new ArrayList<>();
    private String sessionFault = "";
    private Throwable failure;
    private boolean nullAddress;
    private boolean nullQueue;
    private int forbiddenSessionOperations;

    private ClientSession session() {
      return (ClientSession)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {ClientSession.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals(TEXT_ADDRESSQUERY) || name.equals("queueQuery")) {
                  String actual = ((SimpleString) args[0]).toString();
                  boolean address = name.equals(TEXT_ADDRESSQUERY);
                  queries.add((address ? "A:" : "Q:") + actual);
                  assertTrue(
                      address
                          ? ADDRESSES.contains(actual)
                          : ADDRESSES.stream().anyMatch(a -> (a + ".q").equals(actual)),
                      actual);
                  if (name.equals(sessionFault)) throw failure;
                  if (address) return nullAddress ? null : addressResponse(actual);
                  return nullQueue ? null : queueResponse(actual.substring(0, actual.length() - 2));
                }
                forbiddenSessionOperations++;
                throw new AssertionError("Core session method forbidden: " + name);
              });
    }

    private ClientSession.AddressQuery addressResponse(String address) {
      var values =
          new HashMap<String, Object>(
              Map.of(
                  TEXT_ISEXISTS,
                  true,
                  "isSupportsAnycast",
                  true,
                  "isSupportsMulticast",
                  false,
                  TEXT_ISAUTOCREATEQUEUES,
                  false,
                  "isAutoCreateAddresses",
                  false,
                  "getQueueNames",
                  List.of(SimpleString.of(address + ".q"))));
      values.putAll(addressChanges);
      return (ClientSession.AddressQuery)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {ClientSession.AddressQuery.class},
              (proxy, method, args) -> value(values, method.getName()));
    }

    private ClientSession.QueueQuery queueResponse(String address) {
      var values =
          new HashMap<String, Object>(
              Map.of(
                  TEXT_ISEXISTS,
                  true,
                  "isTemporary",
                  false,
                  "isDurable",
                  true,
                  "isAutoCreated",
                  false,
                  TEXT_ISAUTOCREATEQUEUES,
                  false,
                  "getRoutingType",
                  RoutingType.ANYCAST,
                  "getAddress",
                  SimpleString.of(address),
                  "getName",
                  SimpleString.of(address + ".q")));
      values.putAll(queueChanges);
      return (ClientSession.QueueQuery)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {ClientSession.QueueQuery.class},
              (proxy, method, args) -> value(values, method.getName()));
    }

    private static Object value(Map<String, Object> values, String method) throws Throwable {
      assertTrue(values.containsKey(method), method);
      Object actual = values.get(method);
      if (actual instanceof Throwable failure) throw failure;
      return actual;
    }
  }
}
