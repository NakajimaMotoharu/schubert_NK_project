package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** MQREDEL001..008/1695. Literal SS321/351 oracle, own SDK only; no JMS/broker/retry/wait. */
class MqRedeliveryMetricRecorderTest {
  private static final int FAILURE_REGISTRATION_ORDINAL = 2;
  private static final String ASYNC_WORK_ADDRESS = "nk.async.work";
  private static final String REDELIVERY_METRIC = "nk_mq_redeliveries_total";
  private static final String QUEUE_LABEL = "queue";
  private static final String DELIVERY_COUNT_LABEL = "delivery_count";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<String> ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          ASYNC_WORK_ADDRESS,
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger increments = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> registrationFailure = Optional.empty();
    Optional<Throwable> beforeIncrement = Optional.empty();
    Optional<Throwable> afterIncrement = Optional.empty();

    private static void fail(Optional<Throwable> supplied) {
      if (supplied.isPresent()) {
        var problem = supplied.orElseThrow();
        if (problem instanceof Error fatal) throw fatal;
        throw (RuntimeException) problem;
      }
    }

    @Override
    protected Counter newCounter(Meter.Id id) {
      if (registrations.incrementAndGet() == FAILURE_REGISTRATION_ORDINAL)
        fail(registrationFailure);
      var actual = super.newCounter(id);
      return new Counter() {
        @Override
        public Meter.Id getId() {
          return actual.getId();
        }

        @Override
        public double count() {
          return actual.count();
        }

        @Override
        public void increment(double amount) {
          increments.incrementAndGet();
          fail(beforeIncrement);
          actual.increment(amount);
          fail(afterIncrement);
        }
      };
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
      throw new AssertionError("no provider text access");
    }

    @Override
    public String toString() {
      throw new AssertionError("no provider formatting");
    }
  }

  private static double count(Registry registry, String address, String delivery) {
    return registry
        .get(REDELIVERY_METRIC)
        .tag(QUEUE_LABEL, address + ".q")
        .tag(DELIVERY_COUNT_LABEL, delivery)
        .counter()
        .count();
  }

  private static void shape(Registry registry) {
    assertEquals(18, registry.getMeters().size());
    var pairs = new java.util.HashSet<String>();
    var expected = new java.util.HashSet<String>();
    for (String address : ADDRESSES)
      for (String delivery : List.of("2", "3", "4")) expected.add(address + ".q:" + delivery);
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(REDELIVERY_METRIC, id.getName());
      assertEquals(Meter.Type.COUNTER, id.getType());
      assertEquals(
          Set.of(QUEUE_LABEL, DELIVERY_COUNT_LABEL),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      pairs.add(id.getTag(QUEUE_LABEL) + ":" + id.getTag(DELIVERY_COUNT_LABEL));
    }
    assertEquals(expected, pairs);
  }

  @Test
  void mqRedel001OnlySixApprovedQueuesAndThreeRedeliveryLabelsExistAtZero() {
    try (var registry = new Registry()) {
      var recorder = new MqRedeliveryMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      for (String address : ADDRESSES)
        for (String delivery : List.of("2", "3", "4"))
          assertEquals(0, count(registry, address, delivery));
      assertEquals(18, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqRedel002InitialDeliveryNeverCountsAndEachRedeliveryCountsExactlyOnce() {
    try (var registry = new Registry()) {
      var recorder = new MqRedeliveryMetricRecorder(registry, DEBUG_MODE);
      for (String address : ADDRESSES)
        recorder.recordDelivery(BrokerTopology.requireAddress(address), 1);
      assertEquals(0, registry.increments.get());
      for (String address : ADDRESSES)
        for (int delivery : List.of(2, 3, 4))
          recorder.recordDelivery(BrokerTopology.requireAddress(address), delivery);
      for (String address : ADDRESSES)
        for (String delivery : List.of("2", "3", "4"))
          assertEquals(1, count(registry, address, delivery));
      recorder.recordDelivery(BrokerTopology.ASYNC_WORK, 2);
      assertEquals(2, count(registry, ASYNC_WORK_ADDRESS, "2"));
      assertEquals(19, registry.increments.get());
      shape(registry);
      assertEquals(18, registry.registrations.get());
    }
  }

  @Test
  void mqRedel003StandardDoesNotRegisterRetainOrIncrementAnyDetailedCounter() {
    try (var registry = new Registry()) {
      var recorder = new MqRedeliveryMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      for (String address : ADDRESSES)
        for (int delivery : List.of(1, 2, 3, 4))
          recorder.recordDelivery(BrokerTopology.requireAddress(address), delivery);
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqRedel004NullModeDestinationAndOutOfRangeCountsNeverMutateExistingCounters() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new MqRedeliveryMetricRecorder(null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class, () -> new MqRedeliveryMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new MqRedeliveryMetricRecorder(registry, mode))
                .getMessage());
      assertEquals(0, registry.registrations.get());
    }
    for (String mode : List.of(DEBUG_MODE, "STANDARD"))
      try (var registry = new Registry()) {
        var recorder = new MqRedeliveryMetricRecorder(registry, mode);
        recorder.recordDelivery(BrokerTopology.ASYNC_WORK, 2);
        assertThrows(NullPointerException.class, () -> recorder.recordDelivery(null, 2));
        for (int invalid : List.of(Integer.MIN_VALUE, -1, 0, 5, Integer.MAX_VALUE))
          assertThrows(
              IllegalArgumentException.class,
              () -> recorder.recordDelivery(BrokerTopology.ASYNC_WORK, invalid));
        if (mode.equals(DEBUG_MODE)) {
          assertEquals(1, registry.increments.get());
          assertEquals(1, count(registry, ASYNC_WORK_ADDRESS, "2"));
          shape(registry);
        } else {
          assertEquals(0, registry.increments.get());
          assertEquals(0, registry.getMeters().size());
        }
      }
  }

  @Test
  void mqRedel005PartialFactoryFailureKeepsSameProblemAndCallerOwnedRegistry() {
    for (var problem :
        List.<Throwable>of(
            new UnformattableFailure(), new AssertionError("owned factory fixture"))) {
      var registry = new Registry();
      try {
        registry.registrationFailure = Optional.of(problem);
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> new MqRedeliveryMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertEquals(0, count(registry, "nk.sync.request", "2"));
        assertEquals(0, registry.increments.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void mqRedel006IncrementBeforeAfterFailuresAreNotFormattedRetriedOrCompensated() {
    for (boolean after : List.of(false, true))
      for (var problem :
          List.<Throwable>of(
              new UnformattableFailure(), new AssertionError("owned increment fixture"))) {
        try (var registry = new Registry()) {
          var recorder = new MqRedeliveryMetricRecorder(registry, DEBUG_MODE);
          if (after) registry.afterIncrement = Optional.of(problem);
          else registry.beforeIncrement = Optional.of(problem);
          assertSame(
              problem,
              assertThrows(
                  problem.getClass(),
                  () -> recorder.recordDelivery(BrokerTopology.SYNC_REQUEST, 2)));
          assertEquals(1, registry.increments.get());
          assertEquals(after ? 1 : 0, count(registry, "nk.sync.request", "2"));
          assertEquals(0, registry.closes.get());
          shape(registry);
        }
      }
  }

  @Test
  void mqRedel007ConcurrentSamePairAndSeparateOwnerHaveExactIndependentCounts() throws Exception {
    try (var registry = new Registry();
        var other = new Registry()) {
      var recorder = new MqRedeliveryMetricRecorder(registry, DEBUG_MODE);
      var second = new MqRedeliveryMetricRecorder(other, DEBUG_MODE);
      second.recordDelivery(BrokerTopology.WEB_LOG, 4);
      var tasks = new ArrayList<Callable<String>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            () -> {
              recorder.recordDelivery(BrokerTopology.ASYNC_WORK, 3);
              return "counted";
            });
      try (var pool = Executors.newFixedThreadPool(8)) {
        for (var result : pool.invokeAll(tasks)) assertEquals("counted", result.get());
      }
      assertEquals(64, count(registry, ASYNC_WORK_ADDRESS, "3"));
      assertEquals(0, count(other, ASYNC_WORK_ADDRESS, "3"));
      assertEquals(1, count(other, "nk.web.log", "4"));
      assertEquals(0, count(registry, "nk.web.log", "4"));
      assertEquals(64, registry.increments.get());
      assertEquals(1, other.increments.get());
      shape(registry);
      shape(other);
    }
  }

  @Test
  void mqRedel008ForeignGaugeCannotBeReplacedOrCloseBorrowedRegistry() {
    try (var registry = new Registry()) {
      var foreign =
          Gauge.builder(REDELIVERY_METRIC, () -> 7d)
              .tag(QUEUE_LABEL, "nk.sync.request.q")
              .tag(DELIVERY_COUNT_LABEL, "2")
              .register(registry);
      assertThrows(
          IllegalArgumentException.class,
          () -> new MqRedeliveryMetricRecorder(registry, DEBUG_MODE));
      assertEquals(1, registry.getMeters().size());
      assertSame(
          foreign,
          registry
              .get(REDELIVERY_METRIC)
              .tag(QUEUE_LABEL, "nk.sync.request.q")
              .tag(DELIVERY_COUNT_LABEL, "2")
              .gauge());
      assertEquals(7, foreign.value());
      assertEquals(0, registry.closes.get());
      assertEquals(0, registry.increments.get());
    }
  }
}
