package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.MqPressureMetricRecorder.Snapshot;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** MQPRESS001..008/1693, literal SS321/351 oracle; only own SDK, no broker/JMS/management. */
class MqPressureMetricRecorderTest {
  private static final int FAILURE_REGISTRATION_ORDINAL = 2;
  private static final String SYNC_REQUEST_ADDRESS = "nk.sync.request";
  private static final String QUEUE_MESSAGES_METRIC = "nk_mq_queue_messages";
  private static final String QUEUE_LABEL = "queue";
  private static final String ADDRESS_LABEL = "address";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<String> ADDRESSES =
      List.of(
          SYNC_REQUEST_ADDRESS,
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");
  private static final Map<String, String> METRICS =
      Map.of(
          QUEUE_MESSAGES_METRIC,
          QUEUE_LABEL,
          "nk_mq_queue_bytes",
          QUEUE_LABEL,
          "nk_mq_address_memory_bytes",
          ADDRESS_LABEL,
          "nk_mq_address_paged_bytes",
          ADDRESS_LABEL,
          "nk_mq_paging_active",
          ADDRESS_LABEL,
          "nk_mq_page_files",
          ADDRESS_LABEL);

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (registrations.incrementAndGet() == FAILURE_REGISTRATION_ORDINAL && failure.isPresent()) {
        var problem = failure.orElseThrow();
        if (problem instanceof Error fatal) throw fatal;
        throw (RuntimeException) problem;
      }
      return super.newGauge(id, object, value);
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("no failure text access");
    }

    @Override
    public String toString() {
      throw new AssertionError("no failure formatting");
    }
  }

  private static double gauge(Registry registry, String metric, String address) {
    String label = METRICS.get(metric);
    return registry
        .get(metric)
        .tag(label, label.equals(QUEUE_LABEL) ? address + ".q" : address)
        .gauge()
        .value();
  }

  private static void shape(Registry registry) {
    assertEquals(36, registry.getMeters().size());
    var actual = new java.util.HashSet<String>();
    var expected = new java.util.HashSet<String>();
    for (var metric : METRICS.entrySet())
      for (String address : ADDRESSES)
        expected.add(
            metric.getKey()
                + ":"
                + (metric.getValue().equals(QUEUE_LABEL) ? address + ".q" : address));
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(Meter.Type.GAUGE, id.getType());
      assertTrue(METRICS.containsKey(id.getName()));
      String key = METRICS.get(id.getName());
      assertEquals(
          Set.of(key), id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      actual.add(id.getName() + ":" + id.getTag(key));
    }
    assertEquals(expected, actual);
  }

  private static void values(
      Registry registry,
      String address,
      double messages,
      double bytes,
      double memory,
      double paged,
      double paging,
      double files) {
    assertEquals(messages, gauge(registry, QUEUE_MESSAGES_METRIC, address));
    assertEquals(bytes, gauge(registry, "nk_mq_queue_bytes", address));
    assertEquals(memory, gauge(registry, "nk_mq_address_memory_bytes", address));
    assertEquals(paged, gauge(registry, "nk_mq_address_paged_bytes", address));
    assertEquals(paging, gauge(registry, "nk_mq_paging_active", address));
    assertEquals(files, gauge(registry, "nk_mq_page_files", address));
  }

  @Test
  void mqPress001ExactlySixFamiliesAndSixApprovedDestinationPairsStartUnknown() {
    try (var registry = new Registry()) {
      var recorder = new MqPressureMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      assertEquals(36, registry.registrations.get());
      assertEquals(0, registry.closes.get());
      for (String address : ADDRESSES) {
        assertTrue(recorder.snapshot(BrokerTopology.requireAddress(address)).isEmpty());
        for (String metric : METRICS.keySet())
          assertTrue(Double.isNaN(gauge(registry, metric, address)));
      }
    }
  }

  @Test
  void mqPress002LiteralIndependentFieldsZeroAndMaximumHaveNoInventedSumOrCapacity() {
    try (var registry = new Registry()) {
      var recorder = new MqPressureMetricRecorder(registry, DEBUG_MODE);
      for (String address : ADDRESSES) {
        var destination = BrokerTopology.requireAddress(address);
        var sample = new Snapshot(1, 2, 3, 4, true, 5);
        recorder.record(destination, sample);
        assertSame(sample, recorder.snapshot(destination).orElseThrow());
        values(registry, address, 1, 2, 3, 4, 1, 5);
        recorder.record(destination, new Snapshot(0, 0, 0, 0, false, 0));
        values(registry, address, 0, 0, 0, 0, 0, 0);
        var maximum =
            new Snapshot(
                Long.MAX_VALUE,
                Long.MAX_VALUE,
                Long.MAX_VALUE,
                Long.MAX_VALUE,
                true,
                Long.MAX_VALUE);
        recorder.record(destination, maximum);
        assertEquals(Long.MAX_VALUE, recorder.snapshot(destination).orElseThrow().queueBytes());
        values(
            registry,
            address,
            9.223372036854776E18,
            9.223372036854776E18,
            9.223372036854776E18,
            9.223372036854776E18,
            1,
            9.223372036854776E18);
      }
      shape(registry);
      assertEquals(36, registry.registrations.get());
    }
  }

  @Test
  void mqPress003MissingIsNaNNotZeroAndCannotEraseOtherDestinationOrOldSnapshot() {
    try (var registry = new Registry()) {
      var recorder = new MqPressureMetricRecorder(registry, DEBUG_MODE);
      var sample = new Snapshot(1, 2, 3, 4, true, 5);
      for (var destination : BrokerTopology.values()) recorder.record(destination, sample);
      var previous = recorder.snapshot(BrokerTopology.SYNC_REQUEST);
      recorder.missing(BrokerTopology.SYNC_REQUEST);
      assertTrue(recorder.snapshot(BrokerTopology.SYNC_REQUEST).isEmpty());
      assertSame(sample, previous.orElseThrow());
      for (String metric : METRICS.keySet())
        assertTrue(Double.isNaN(gauge(registry, metric, SYNC_REQUEST_ADDRESS)));
      for (String address : ADDRESSES.subList(1, 6)) values(registry, address, 1, 2, 3, 4, 1, 5);
      recorder.missing(BrokerTopology.SYNC_REQUEST);
      recorder.record(BrokerTopology.SYNC_REQUEST, new Snapshot(0, 0, 0, 0, false, 0));
      values(registry, SYNC_REQUEST_ADDRESS, 0, 0, 0, 0, 0, 0);
    }
  }

  @Test
  void mqPress004StandardRetainsNothingAndConfigurationOrNegativeSamplesAreNotNormalized() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new MqPressureMetricRecorder(null, DEBUG_MODE));
      assertThrows(NullPointerException.class, () -> new MqPressureMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new MqPressureMetricRecorder(registry, mode))
                .getMessage());
      var recorder = new MqPressureMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      for (var destination : BrokerTopology.values()) {
        recorder.record(destination, new Snapshot(1, 2, 3, 4, true, 5));
        assertTrue(recorder.snapshot(destination).isEmpty());
        recorder.missing(destination);
        assertTrue(recorder.snapshot(destination).isEmpty());
      }
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.closes.get());
    }
    for (long invalid : List.of(-1L, Long.MIN_VALUE)) {
      assertThrows(IllegalArgumentException.class, () -> new Snapshot(invalid, 0, 0, 0, false, 0));
      assertThrows(IllegalArgumentException.class, () -> new Snapshot(0, invalid, 0, 0, false, 0));
      assertThrows(IllegalArgumentException.class, () -> new Snapshot(0, 0, invalid, 0, false, 0));
      assertThrows(IllegalArgumentException.class, () -> new Snapshot(0, 0, 0, invalid, false, 0));
      assertThrows(IllegalArgumentException.class, () -> new Snapshot(0, 0, 0, 0, false, invalid));
    }
  }

  @Test
  void mqPress005PartialFactoryAndForeignTypeFailuresKeepExactCallerRegistry() {
    for (var problem :
        List.<Throwable>of(
            new UnformattableFailure(), new AssertionError("owned provider fixture"))) {
      var registry = new Registry();
      try {
        registry.failure = Optional.of(problem);
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> new MqPressureMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertTrue(Double.isNaN(gauge(registry, QUEUE_MESSAGES_METRIC, SYNC_REQUEST_ADDRESS)));
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
    try (var registry = new Registry()) {
      var foreign =
          Counter.builder(QUEUE_MESSAGES_METRIC)
              .tag(QUEUE_LABEL, "nk.sync.request.q")
              .register(registry);
      foreign.increment(7);
      assertThrows(
          IllegalArgumentException.class, () -> new MqPressureMetricRecorder(registry, DEBUG_MODE));
      assertEquals(1, registry.getMeters().size());
      assertSame(
          foreign,
          registry.get(QUEUE_MESSAGES_METRIC).tag(QUEUE_LABEL, "nk.sync.request.q").counter());
      assertEquals(7, foreign.count());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqPress006ConcurrentPublicationAndDifferentOwnersDoNotGrowOrShareState() throws Exception {
    try (var registry = new Registry();
        var other = new Registry()) {
      var recorder = new MqPressureMetricRecorder(registry, DEBUG_MODE);
      var second = new MqPressureMetricRecorder(other, DEBUG_MODE);
      var separate = new Snapshot(7, 8, 9, 10, false, 11);
      second.record(BrokerTopology.ASYNC_WORK, separate);
      var supplied = new ArrayList<Snapshot>();
      var tasks = new ArrayList<Callable<String>>();
      for (int i = 0; i < 64; i++) {
        var sample = new Snapshot(i, 100 + i, 200 + i, 300 + i, true, 400 + i);
        supplied.add(sample);
        tasks.add(
            () -> {
              recorder.record(BrokerTopology.ASYNC_WORK, sample);
              return "published";
            });
      }
      var pool = Executors.newFixedThreadPool(8);
      try {
        for (var result : pool.invokeAll(tasks, 10, TimeUnit.SECONDS))
          assertEquals("published", result.get());
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
      }
      assertTrue(supplied.contains(recorder.snapshot(BrokerTopology.ASYNC_WORK).orElseThrow()));
      assertSame(separate, second.snapshot(BrokerTopology.ASYNC_WORK).orElseThrow());
      values(other, "nk.async.work", 7, 8, 9, 10, 0, 11);
      assertTrue(recorder.snapshot(BrokerTopology.SYNC_REQUEST).isEmpty());
      shape(registry);
      shape(other);
      assertEquals(36, registry.registrations.get());
      assertEquals(36, other.registrations.get());
    }
  }

  @Test
  void mqPress007NullBoundariesCannotClearPreviouslyAcceptedObservationInEitherMode() {
    for (String mode : List.of(DEBUG_MODE, "STANDARD"))
      try (var registry = new Registry()) {
        var recorder = new MqPressureMetricRecorder(registry, mode);
        var sample = new Snapshot(1, 2, 3, 4, true, 5);
        recorder.record(BrokerTopology.WEB_LOG, sample);
        var previous = recorder.snapshot(BrokerTopology.WEB_LOG);
        assertThrows(NullPointerException.class, () -> recorder.record(null, sample));
        assertThrows(
            NullPointerException.class, () -> recorder.record(BrokerTopology.WEB_LOG, null));
        assertThrows(NullPointerException.class, () -> recorder.missing(null));
        assertThrows(NullPointerException.class, () -> recorder.snapshot(null));
        assertEquals(previous, recorder.snapshot(BrokerTopology.WEB_LOG));
        assertEquals(0, registry.closes.get());
      }
  }

  @Test
  void mqPress008GeneratedSnapshotContractsUseIndependentLongBooleanFoldAndFixedText() {
    var value = new Snapshot(1, 2, 3, 4, true, 5);
    var equal = new Snapshot(1, 2, 3, 4, true, 5);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertFalse(value.equals(null));
    assertFalse(value.equals("other type"));
    for (var changed :
        List.of(
            new Snapshot(2, 2, 3, 4, true, 5),
            new Snapshot(1, 3, 3, 4, true, 5),
            new Snapshot(1, 2, 4, 4, true, 5),
            new Snapshot(1, 2, 3, 5, true, 5),
            new Snapshot(1, 2, 3, 4, false, 5),
            new Snapshot(1, 2, 3, 4, true, 6))) assertNotEquals(value, changed);
    assertEquals(30607576, value.hashCode());
    assertEquals(30607762, new Snapshot(1, 2, 3, 4, false, 5).hashCode());
    var collided = new Snapshot(1L << 32, 2, 3, 4, true, 5);
    assertEquals(30607576, collided.hashCode());
    assertNotEquals(value, collided);
    assertEquals(
        "Snapshot[messages=1, queueBytes=2, addressMemoryBytes=3, addressPagedBytes=4,"
            + " pagingActive=true, pageFiles=5]",
        value.toString());
    assertEquals(1, value.messages());
    assertEquals(2, value.queueBytes());
    assertEquals(3, value.addressMemoryBytes());
    assertEquals(4, value.addressPagedBytes());
    assertTrue(value.pagingActive());
    assertEquals(5, value.pageFiles());
    assertFalse(new Snapshot(0, 0, 0, 0, false, 0).pagingActive());
  }
}
