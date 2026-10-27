package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;

/** SSC130/ISSBROKER001: actual values and query cardinality, not expected policy substitution. */
final class ArtemisDetailedValuesTest {
  private static final String PUBLIC_FIELD = "public";
  private static final String FIELD_VALUE = "value";
  private static final String ADDRESS_KEY = "address";

  @Test
  void detailedNestedDataHasNoMutableInputOrOutputAliases() {
    var fields = new HashMap<>(Map.of(PUBLIC_FIELD, FIELD_VALUE));
    var pairs = new HashMap<String, Map<String, String>>(Map.of(ADDRESS_KEY, fields));
    var permissions = new HashMap<>(Map.of("send", true));
    var roles =
        new HashMap<String, Map<String, Map<String, Boolean>>>(
            Map.of("match", new HashMap<>(Map.of("role", permissions))));
    var pressure =
        new HashMap<>(
            Map.of(
                ADDRESS_KEY,
                new ArtemisQueuePressureClient.Value(
                    1, 2, ArtemisQueuePressureClient.Pressure.NORMAL)));
    var result =
        new ArtemisStartupObservation.Evidence(pairs, fields, pairs, fields, roles, pressure);
    fields.clear();
    pairs.clear();
    permissions.clear();
    roles.clear();
    pressure.clear();
    assertEquals(Map.of(ADDRESS_KEY, Map.of(PUBLIC_FIELD, FIELD_VALUE)), result.topology());
    assertEquals(Map.of(ADDRESS_KEY, Map.of(PUBLIC_FIELD, FIELD_VALUE)), result.settings());
    assertEquals(Map.of(PUBLIC_FIELD, FIELD_VALUE), result.broker());
    assertEquals(Map.of(PUBLIC_FIELD, FIELD_VALUE), result.acceptor());
    assertEquals(Map.of("match", Map.of("role", Map.of("send", true))), result.roles());
    assertEquals(
        new ArtemisQueuePressureClient.Value(1, 2, ArtemisQueuePressureClient.Pressure.NORMAL),
        result.pressure().get(ADDRESS_KEY));
    assertThrows(UnsupportedOperationException.class, () -> result.topology().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> result.topology().get(ADDRESS_KEY).clear());
    assertThrows(UnsupportedOperationException.class, () -> result.settings().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> result.settings().get(ADDRESS_KEY).clear());
    assertThrows(
        UnsupportedOperationException.class, () -> result.roles().get("match").get("role").clear());
    assertThrows(UnsupportedOperationException.class, () -> result.pressure().clear());
  }

  private static ClientSession unused() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, args) -> {
              throw new AssertionError("borrowed session not needed by fixed reader fixture");
            });
  }

  @Test
  void brokerFieldsComeFromElevenReadsAndMutableDiskNumberIsCapturedOnce() {
    var diskCalls = new AtomicInteger();
    Number disk =
        new Number() {
          private static final long serialVersionUID = 1L;

          public int intValue() {
            throw new AssertionError();
          }

          public long longValue() {
            throw new AssertionError();
          }

          public float floatValue() {
            throw new AssertionError();
          }

          public double doubleValue() {
            diskCalls.incrementAndGet();
            return 0.125;
          }
        };
    var observed =
        new HashMap<String, Object>(
            Map.ofEntries(
                Map.entry("name", "schubert-nk-broker"),
                Map.entry("persistenceEnabled", true),
                Map.entry("journalType", "NIO"),
                Map.entry("journalFileSize", 10485760),
                Map.entry("journalMinFiles", 4),
                Map.entry("journalPoolFiles", 20),
                Map.entry("globalMaxSize", 536870912L),
                Map.entry("IDCacheSize", 20000),
                Map.entry("persistIDCache", true),
                Map.entry("maxDiskUsage", 90),
                Map.entry("diskStoreUsage", disk)));
    var reads = new ArrayList<String>();
    var result =
        new ArtemisManagementReadinessClient(
                (session, key) -> {
                  reads.add(key);
                  return observed.get(key);
                })
            .inspectBroker(unused());
    assertEquals(11, reads.size());
    assertEquals(11, new HashSet<>(reads).size());
    assertEquals(1, diskCalls.get());
    assertEquals(
        Map.ofEntries(
            Map.entry("name", "schubert-nk-broker"),
            Map.entry("persistenceEnabled", "1"),
            Map.entry("journalType", "NIO"),
            Map.entry("journalFileSize", "10485760"),
            Map.entry("journalMinFiles", "4"),
            Map.entry("journalPoolFiles", "20"),
            Map.entry("globalMaxSize", "536870912"),
            Map.entry("IDCacheSize", "20000"),
            Map.entry("persistIDCache", "1"),
            Map.entry("maxDiskUsage", "90"),
            Map.entry("diskStoreUsage", "3fc0000000000000")),
        result);
    observed.clear();
    assertEquals(11, result.size());
    assertThrows(UnsupportedOperationException.class, result::clear);
  }

  @Test
  void queueCountAndBytesAreNotLostAndRemainIndependentOfLaterFixtureChanges() {
    var queries = new ArrayList<String>();
    var counts = new HashMap<>(Map.of("nk.async.work.q", 5200L));
    var actual =
        new ArtemisQueuePressureClient(
                (session, queue, field) -> {
                  queries.add(queue + "/" + field);
                  return field.equals("messageCount") ? counts.getOrDefault(queue, 0L) : 10L;
                })
            .inspectValues(unused());
    assertEquals(12, queries.size());
    assertEquals(12, new HashSet<>(queries).size());
    assertEquals(
        new ArtemisQueuePressureClient.Value(5200, 10, ArtemisQueuePressureClient.Pressure.WARNING),
        actual.get("nk.async.work"));
    counts.clear();
    assertEquals(5200, actual.get("nk.async.work").count());
    assertThrows(UnsupportedOperationException.class, actual::clear);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ArtemisQueuePressureClient.Value(
                -1, 0, ArtemisQueuePressureClient.Pressure.NORMAL));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ArtemisQueuePressureClient.Value(
                0, -1, ArtemisQueuePressureClient.Pressure.NORMAL));
    assertThrows(
        NullPointerException.class, () -> new ArtemisQueuePressureClient.Value(0, 0, null));
  }
}
