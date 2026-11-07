package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;

/** NK-OPS-001; MQ001/002/009/010; UI231/251/253; SS321§5/10/13; OPS-ASET-001..005. */
final class AddressSettingsProjectionPortTest {
  private static final int FAILURE_READ = 3;
  private static final String FALSE = "false";
  private static final String THOUSAND = "1000";
  private static final String NINE_THOUSAND = "9000";
  private static final String REQUEST = "nk.sync.request";
  private static final String EXTRA = "unapprovedField";
  private static final String SYNTHETIC = "synthetic port failure";
  private static final Map<String, String> COMMON =
      Map.ofEntries(
          Map.entry("deadLetterAddress", "\"nk.dead.letter\""),
          Map.entry("expiryAddress", "\"nk.expiry\""),
          Map.entry("autoCreateDeadLetterResources", FALSE),
          Map.entry("autoCreateExpiryResources", FALSE),
          Map.entry("autoCreateAddresses", FALSE),
          Map.entry("autoCreateQueues", FALSE),
          Map.entry("autoDeleteAddresses", FALSE),
          Map.entry("autoDeleteQueues", FALSE),
          Map.entry("autoDeleteCreatedQueues", FALSE),
          Map.entry("addressFullMessagePolicy", "\"PAGE\""),
          Map.entry("pageFullMessagePolicy", "\"FAIL\""),
          Map.entry("diskFullMessagePolicy", "\"BLOCK\""),
          Map.entry("pageSizeBytes", "8388608"),
          Map.entry("maxReadPageBytes", "16777216"),
          Map.entry("maxReadPageMessages", "100"),
          Map.entry("redeliveryCollisionAvoidanceFactor", "0.0"),
          Map.entry("redeliveryDelay", "1000"),
          Map.entry("redeliveryMultiplier", "5.0"),
          Map.entry("maxRedeliveryDelay", "30000"),
          Map.entry("maxDeliveryAttempts", "4"),
          Map.entry("enableMetrics", "true"),
          Map.entry("enableIngressTimestamp", "true"));
  // Independent SS321§5.3 integers, not read from broker settings or Production capacities.
  private static final Map<String, List<String>> CAPACITIES =
      Map.of(
          REQUEST,
          List.of("33554432", "50", "234881024", "450"),
          "nk.sync.reply.web",
          List.of("33554432", "50", "234881024", "450"),
          "nk.async.work",
          List.of("134217728", THOUSAND, "939524096", NINE_THOUSAND),
          "nk.web.log",
          List.of("67108864", THOUSAND, "201326592", NINE_THOUSAND),
          "nk.dead.letter",
          List.of("134217728", THOUSAND, "2013265920", NINE_THOUSAND),
          "nk.expiry",
          List.of("67108864", THOUSAND, "1006632960", NINE_THOUSAND));

  @Test
  void aset001ReturnsExactApprovedFieldsForAllSixAddressesWithoutUsingSession() {
    var reads = new ArrayList<String>();
    var client =
        new ArtemisAddressSettingsReadinessClient(
            (session, address) -> {
              reads.add(address);
              var fields = new LinkedHashMap<>(expected(address));
              fields.put(EXTRA, "\"ignored\"");
              return json(fields);
            });
    var actual = client.inspect(unusedSession());
    assertEquals(CAPACITIES.keySet(), actual.keySet());
    assertEquals(6, reads.size());
    assertEquals(CAPACITIES.keySet(), java.util.Set.copyOf(reads));
    actual.forEach(
        (address, fields) -> {
          assertEquals(26, fields.size());
          assertEquals(expected(address), fields);
          assertEquals(false, fields.containsKey(EXTRA));
        });
  }

  @Test
  void aset002ImmutableSnapshotsRemainIndependentAcrossLaterFailureAndSuccess() {
    var attempts = new AtomicInteger();
    var client =
        new ArtemisAddressSettingsReadinessClient(
            (session, address) -> attempts.get() == 1 ? "{}" : json(expected(address)));
    var before = client.inspect(unusedSession());
    assertThrows(UnsupportedOperationException.class, () -> before.put(EXTRA, Map.of()));
    assertThrows(UnsupportedOperationException.class, () -> before.get(REQUEST).clear());
    attempts.incrementAndGet();
    assertThrows(ArtemisManagementReadinessException.class, () -> client.inspect(unusedSession()));
    attempts.incrementAndGet();
    var after = client.inspect(unusedSession());
    assertEquals(before, after);
    assertNotSame(before, after);
    assertNotSame(before.get(REQUEST), after.get(REQUEST));
    assertEquals(expected(REQUEST), before.get(REQUEST));
  }

  @Test
  void aset003RejectsQuotedNumbersAndBooleansAtThirdReadWithoutReturningPartialResult() {
    for (String field : List.of("pageSizeBytes", "enableMetrics", "maxDeliveryAttempts")) {
      var reads = new AtomicInteger();
      var client =
          new ArtemisAddressSettingsReadinessClient(
              (session, address) -> {
                var fields = new LinkedHashMap<>(expected(address));
                if (reads.incrementAndGet() == FAILURE_READ) {
                  fields.put(field, "\"" + fields.get(field) + "\"");
                }
                return json(fields);
              });
      var failure =
          assertThrows(
              ArtemisManagementReadinessException.class, () -> client.inspect(unusedSession()));
      assertEquals("Artemis effective broker configuration is unavailable", failure.getMessage());
      assertEquals(3, reads.get());
    }
  }

  @Test
  void aset004RejectsMalformedOrMissingProjectionAndPreservesProviderFailureIdentity() {
    assertThrows(NullPointerException.class, () -> new ArtemisAddressSettingsReadinessClient(null));
    var client =
        new ArtemisAddressSettingsReadinessClient((session, address) -> json(expected(address)));
    assertThrows(NullPointerException.class, () -> client.inspect(null));
    var invalid = new ArrayList<Object>(List.of(7, "", "not-json", "[]", "{}"));
    invalid.add(null);
    for (Object response : invalid) {
      var reads = new AtomicInteger();
      var failing =
          new ArtemisAddressSettingsReadinessClient(
              (session, address) -> {
                reads.incrementAndGet();
                return response;
              });
      assertThrows(
          ArtemisManagementReadinessException.class, () -> failing.inspect(unusedSession()));
      assertEquals(1, reads.get());
    }
    for (Throwable failure :
        List.of(new IllegalStateException(SYNTHETIC), new AssertionError(SYNTHETIC))) {
      var reads = new AtomicInteger();
      var failing =
          new ArtemisAddressSettingsReadinessClient(
              (session, address) -> {
                reads.incrementAndGet();
                if (failure instanceof Error fatal) throw fatal;
                throw (RuntimeException) failure;
              });
      assertSame(failure, assertThrows(failure.getClass(), () -> failing.inspect(unusedSession())));
      assertEquals(1, reads.get());
    }
  }

  @Test
  void aset005VerifyUsesSameSixReadContractAndDefaultAssemblyDoesNotOpenSession() {
    var unconnected = new ArtemisAddressSettingsReadinessClient();
    assertThrows(NullPointerException.class, () -> unconnected.verify(null));
    var reads = new AtomicInteger();
    var client =
        new ArtemisAddressSettingsReadinessClient(
            (session, address) -> {
              reads.incrementAndGet();
              return json(expected(address));
            });
    client.verify(unusedSession());
    assertEquals(6, reads.get());
  }

  private static Map<String, String> expected(String address) {
    var values = new LinkedHashMap<>(COMMON);
    var capacity = CAPACITIES.get(address);
    values.put("maxSizeBytes", capacity.get(0));
    values.put("maxSizeMessages", capacity.get(1));
    values.put("pageLimitBytes", capacity.get(2));
    values.put("pageLimitMessages", capacity.get(3));
    return values;
  }

  private static String json(Map<String, String> values) {
    return values.entrySet().stream()
        .map(entry -> "\"" + entry.getKey() + "\":" + entry.getValue())
        .collect(Collectors.joining(",", "{", "}"));
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, arguments) -> {
              throw new AssertionError("borrowed session must remain untouched");
            });
  }
}
