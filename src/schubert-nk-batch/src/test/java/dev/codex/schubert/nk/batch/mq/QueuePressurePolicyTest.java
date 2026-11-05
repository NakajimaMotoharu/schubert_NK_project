package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** OPS-QPP-PORT-001..006: synthetic metric callbacks only; no Core session operation or broker. */
final class QueuePressurePolicyTest {

  private static final String SYNC = "nk.sync.request";
  private static final String DEAD = "nk.dead.letter";
  private static final String COUNT = "messageCount";
  private static final String BYTES = "persistentSize";
  private static final Set<String> ADDRESSES =
      Set.of(SYNC, "nk.sync.reply.web", "nk.async.work", "nk.web.log", DEAD, "nk.expiry");
  // SS321 literal ceilings and count boundaries, independent of production fraction/limits.
  private static final Map<String, long[]> BOUNDARIES =
      Map.of(
          SYNC,
          new long[] {250, 450, 187904820, 241591911},
          "nk.sync.reply.web",
          new long[] {250, 450, 187904820, 241591911},
          "nk.async.work",
          new long[] {5000, 9000, 751619277, 966367642},
          "nk.web.log",
          new long[] {5000, 9000, 187904820, 241591911},
          "nk.expiry",
          new long[] {1000, 5000, 751619277, 966367642});

  @Test
  void sixImmutableSnapshotsUseExactlyTwoAttributesAndNeverOperateTheBorrowedSession() {
    Fixture fixture = new Fixture();
    var values = fixture.client().inspectValues(fixture.borrowed);
    assertEquals(ADDRESSES, values.keySet());
    for (String address : ADDRESSES) {
      var actual = values.get(address);
      assertEquals(0, actual.count());
      assertEquals(0, actual.bytes());
      assertEquals(ArtemisQueuePressureClient.Pressure.NORMAL, actual.state());
      assertEquals(List.of(COUNT, BYTES), fixture.reads.get(address + ".q"));
    }
    assertEquals(6, fixture.reads.size());
    assertThrows(UnsupportedOperationException.class, () -> values.clear());
    fixture.reads.clear();
    var policy = fixture.client().inspect(fixture.borrowed);
    assertEquals(ADDRESSES, policy.keySet());
    for (var state : policy.values())
      assertEquals(ArtemisQueuePressureClient.Pressure.NORMAL, state);
    assertThrows(
        UnsupportedOperationException.class,
        () -> policy.put(SYNC, ArtemisQueuePressureClient.Pressure.ALERT));
    for (String address : ADDRESSES)
      assertEquals(List.of(COUNT, BYTES), fixture.reads.get(address + ".q"));
    assertEquals(0, fixture.sessionOperations);
  }

  @Test
  void everyNonDlqCountAndByteThresholdHasLiteralBeforeEqualAndAfterVectors() {
    for (var entry : BOUNDARIES.entrySet()) {
      String address = entry.getKey();
      long[] b = entry.getValue();
      assertState(address, b[0] - 1, 0, ArtemisQueuePressureClient.Pressure.NORMAL);
      assertState(address, b[0], 0, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, b[0] + 1, 0, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, b[1] - 1, 0, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, b[1], 0, ArtemisQueuePressureClient.Pressure.CRITICAL);
      assertState(address, b[1] + 1, 0, ArtemisQueuePressureClient.Pressure.CRITICAL);
      assertState(address, 0, b[2] - 1, ArtemisQueuePressureClient.Pressure.NORMAL);
      assertState(address, 0, b[2], ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, 0, b[2] + 1, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, 0, b[3] - 1, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, 0, b[3], ArtemisQueuePressureClient.Pressure.CRITICAL);
      assertState(address, 0, b[3] + 1, ArtemisQueuePressureClient.Pressure.CRITICAL);
    }
  }

  @Test
  void dlqAlertPrecedesSeventyPercentWarningButNinetyPercentBytesPrecedesEveryCount() {
    assertState(DEAD, 0, 0, ArtemisQueuePressureClient.Pressure.NORMAL);
    assertState(DEAD, 1, 0, ArtemisQueuePressureClient.Pressure.ALERT);
    assertState(DEAD, Long.MAX_VALUE, 0, ArtemisQueuePressureClient.Pressure.ALERT);
    assertState(DEAD, 0, 1503238553, ArtemisQueuePressureClient.Pressure.NORMAL);
    assertState(DEAD, 0, 1503238554, ArtemisQueuePressureClient.Pressure.WARNING);
    assertState(DEAD, 1, 1503238554, ArtemisQueuePressureClient.Pressure.ALERT);
    assertState(DEAD, 0, 1932735283, ArtemisQueuePressureClient.Pressure.WARNING);
    assertState(DEAD, 1, 1932735283, ArtemisQueuePressureClient.Pressure.ALERT);
    assertState(DEAD, 0, 1932735284, ArtemisQueuePressureClient.Pressure.CRITICAL);
    assertState(DEAD, 1, 1932735284, ArtemisQueuePressureClient.Pressure.CRITICAL);
    assertState(DEAD, 0, Long.MAX_VALUE, ArtemisQueuePressureClient.Pressure.CRITICAL);
    assertState(SYNC, 250, 241591911, ArtemisQueuePressureClient.Pressure.CRITICAL);
  }

  @Test
  void missingUnknownNegativeMetricsAreCataloguedButProviderRuntimeAndErrorKeepIdentity() {
    for (Object invalid :
        new Object[] {
          null, -1, -1L, Long.MIN_VALUE, 0.0d, 0.0f, "0", true, (short) 0, BigInteger.ZERO
        })
      for (int column = 0; column < 2; column++) {
        Fixture fixture = new Fixture();
        Object[] pair = {0L, 0L};
        pair[column] = invalid;
        fixture.samples.put(SYNC + ".q", pair);
        catalog(() -> fixture.client().inspectValues(fixture.borrowed));
        assertEquals(0, fixture.sessionOperations);
      }
    Fixture fixture = new Fixture();
    for (Throwable expected :
        List.of(
            new IllegalStateException("private provider"), new AssertionError("private fatal"))) {
      var client =
          new ArtemisQueuePressureClient(
              (session, queue, attribute) -> {
                if (expected instanceof RuntimeException failure) throw failure;
                throw (Error) expected;
              });
      assertSame(
          expected,
          assertThrows(expected.getClass(), () -> client.inspectValues(fixture.borrowed)));
      assertEquals(0, fixture.sessionOperations);
    }
  }

  @Test
  void publicNullEntryAndValueInvariantsRejectBeforeAnyReaderOrManagementQuery() {
    assertThrows(NullPointerException.class, () -> new ArtemisQueuePressureClient(null));
    var defaults = new ArtemisQueuePressureClient();
    assertEquals(
        "ops session",
        assertThrows(NullPointerException.class, () -> defaults.inspect(null)).getMessage());
    assertEquals(
        "ops session",
        assertThrows(NullPointerException.class, () -> defaults.inspectValues(null)).getMessage());
    var calls = new AtomicInteger();
    var injected =
        new ArtemisQueuePressureClient(
            (s, q, a) -> {
              calls.incrementAndGet();
              return 0L;
            });
    assertThrows(NullPointerException.class, () -> injected.inspect(null));
    assertThrows(NullPointerException.class, () -> injected.inspectValues(null));
    assertEquals(0, calls.get());
    assertThrows(
        NullPointerException.class, () -> new ArtemisQueuePressureClient.Value(0, 0, null));
    for (long[] bad : new long[][] {{-1, 0}, {0, -1}, {Long.MIN_VALUE, 0}, {0, Long.MIN_VALUE}})
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new ArtemisQueuePressureClient.Value(
                  bad[0], bad[1], ArtemisQueuePressureClient.Pressure.NORMAL));
    var largest =
        new ArtemisQueuePressureClient.Value(
            Long.MAX_VALUE, Long.MAX_VALUE, ArtemisQueuePressureClient.Pressure.CRITICAL);
    assertEquals(Long.MAX_VALUE, largest.count());
    assertEquals(Long.MAX_VALUE, largest.bytes());
    assertEquals(ArtemisQueuePressureClient.Pressure.CRITICAL, largest.state());
  }

  @Test
  void integerAndLongMetricsAreBothExactAndSnapshotsCannotRetainMutableProviderCells() {
    for (Object zero : List.of(Integer.valueOf(0), Long.valueOf(0))) {
      Fixture fixture = new Fixture();
      for (String address : ADDRESSES)
        fixture.samples.put(address + ".q", new Object[] {zero, zero});
      var actual = fixture.client().inspectValues(fixture.borrowed);
      for (var value : actual.values())
        assertEquals(ArtemisQueuePressureClient.Pressure.NORMAL, value.state());
      assertEquals(0, fixture.sessionOperations);
    }
    Fixture fixture = new Fixture();
    var snapshot = fixture.client().inspectValues(fixture.borrowed);
    fixture.samples.get(SYNC + ".q")[0] = 450L;
    fixture.samples.get(SYNC + ".q")[1] = 241591911L;
    assertEquals(0, snapshot.get(SYNC).count());
    assertEquals(0, snapshot.get(SYNC).bytes());
    assertEquals(ArtemisQueuePressureClient.Pressure.NORMAL, snapshot.get(SYNC).state());
    var changed = fixture.client().inspectValues(fixture.borrowed).get(SYNC);
    assertEquals(450, changed.count());
    assertEquals(241591911, changed.bytes());
    assertEquals(ArtemisQueuePressureClient.Pressure.CRITICAL, changed.state());
    for (String address : BOUNDARIES.keySet())
      assertState(address, Long.MAX_VALUE, 0, ArtemisQueuePressureClient.Pressure.CRITICAL);
    assertEquals(0, fixture.sessionOperations);
  }

  private static void assertState(
      String address, long count, long bytes, ArtemisQueuePressureClient.Pressure expected) {
    Fixture fixture = new Fixture();
    fixture.samples.put(address + ".q", new Object[] {count, bytes});
    var actual = fixture.client().inspectValues(fixture.borrowed).get(address);
    assertEquals(count, actual.count());
    assertEquals(bytes, actual.bytes());
    assertEquals(expected, actual.state(), address);
    assertEquals(0, fixture.sessionOperations);
  }

  private static void catalog(Executable action) {
    var error = assertThrows(ArtemisManagementReadinessException.class, action);
    assertEquals("Artemis effective broker configuration is unavailable", error.getMessage());
    assertEquals(null, error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static final class Fixture {
    private final Map<String, Object[]> samples = new HashMap<>();
    private final Map<String, List<String>> reads = new HashMap<>();
    private int sessionOperations;
    private final ClientSession borrowed =
        (ClientSession)
            Proxy.newProxyInstance(
                Fixture.class.getClassLoader(),
                new Class<?>[] {ClientSession.class},
                (proxy, method, args) -> {
                  sessionOperations++;
                  throw new AssertionError(
                      "borrowed Core session operation forbidden: " + method.getName());
                });

    private Fixture() {
      for (String address : ADDRESSES) samples.put(address + ".q", new Object[] {0L, 0L});
    }

    private ArtemisQueuePressureClient client() {
      return new ArtemisQueuePressureClient(
          (session, queue, attribute) -> {
            assertSame(borrowed, session);
            assertTrue(samples.containsKey(queue), queue);
            assertTrue(attribute.equals(COUNT) || attribute.equals(BYTES), attribute);
            reads.computeIfAbsent(queue, key -> new ArrayList<>()).add(attribute);
            return samples.get(queue)[attribute.equals(COUNT) ? 0 : 1];
          });
    }
  }
}
