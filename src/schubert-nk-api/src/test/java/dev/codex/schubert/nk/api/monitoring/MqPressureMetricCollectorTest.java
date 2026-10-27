package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.MqPressureMetricRecorder.Snapshot;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.Test;

/** MQCONN001..008/1697. Own Function/SDK/thread fixtures only, no broker/JMS/management/Root. */
class MqPressureMetricCollectorTest {
  private static final int FIRST_READ_ORDINAL = 1;
  private static final String ASYNC_ADDRESS = "nk.async.work";
  private static final String LOG_ADDRESS = "nk.web.log";
  private static final String QUEUE_MESSAGES = "nk_mq_queue_messages";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<String> ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          ASYNC_ADDRESS,
          LOG_ADDRESS,
          "nk.dead.letter",
          "nk.expiry");

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (registrations.incrementAndGet() == 2 && failure.isPresent()) {
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
      throw new AssertionError("no provider text access");
    }

    @Override
    public String toString() {
      throw new AssertionError("no provider formatting");
    }
  }

  private static double gauge(Registry registry, String metric, String address) {
    boolean queue = metric.equals(QUEUE_MESSAGES) || metric.equals("nk_mq_queue_bytes");
    return registry
        .get(metric)
        .tag(queue ? "queue" : "address", queue ? address + ".q" : address)
        .gauge()
        .value();
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
    assertEquals(messages, gauge(registry, QUEUE_MESSAGES, address));
    assertEquals(bytes, gauge(registry, "nk_mq_queue_bytes", address));
    assertEquals(memory, gauge(registry, "nk_mq_address_memory_bytes", address));
    assertEquals(paged, gauge(registry, "nk_mq_address_paged_bytes", address));
    assertEquals(paging, gauge(registry, "nk_mq_paging_active", address));
    assertEquals(files, gauge(registry, "nk_mq_page_files", address));
  }

  private static void unknown(Registry registry, String address) {
    for (String metric :
        List.of(
            QUEUE_MESSAGES,
            "nk_mq_queue_bytes",
            "nk_mq_address_memory_bytes",
            "nk_mq_address_paged_bytes",
            "nk_mq_paging_active",
            "nk_mq_page_files")) assertTrue(Double.isNaN(gauge(registry, metric, address)));
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(5, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError("owned fixture interrupted", interrupted);
    }
  }

  @Test
  void mqConn001EachSuppliedResultPublishesAllSixValuesOnlyAfterReadCompletes() {
    try (var registry = new Registry()) {
      var calls = new AtomicInteger();
      var owner = new AtomicReference<MqPressureMetricCollector>();
      var sample = new Snapshot(1, 2, 3, 4, true, 5);
      var collector =
          new MqPressureMetricCollector(
              destination -> {
                calls.incrementAndGet();
                assertTrue(owner.get().snapshot(destination).isEmpty());
                unknown(registry, destination.address());
                return Optional.of(sample);
              },
              registry,
              DEBUG_MODE);
      owner.set(collector);
      assertEquals(0, calls.get());
      for (String address : ADDRESSES) {
        var destination = BrokerTopology.requireAddress(address);
        assertSame(sample, collector.collect(destination).orElseThrow());
        assertSame(sample, collector.snapshot(destination).orElseThrow());
        values(registry, address, 1, 2, 3, 4, 1, 5);
      }
      assertEquals(6, calls.get());
      assertEquals(36, registry.registrations.get());
      assertEquals(36, registry.getMeters().size());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqConn002UnknownClearsOnlySelectedDestinationAndTrueZeroRecovers() {
    try (var registry = new Registry()) {
      var sample = new Snapshot(1, 2, 3, 4, true, 5);
      var supplied = new AtomicReference<>(Optional.of(sample));
      var calls = new AtomicInteger();
      var collector =
          new MqPressureMetricCollector(
              destination -> {
                calls.incrementAndGet();
                return supplied.get();
              },
              registry,
              DEBUG_MODE);
      collector.collect(BrokerTopology.ASYNC_WORK);
      collector.collect(BrokerTopology.WEB_LOG);
      var old = collector.snapshot(BrokerTopology.ASYNC_WORK);
      supplied.set(Optional.empty());
      assertTrue(collector.collect(BrokerTopology.ASYNC_WORK).isEmpty());
      unknown(registry, ASYNC_ADDRESS);
      assertTrue(collector.snapshot(BrokerTopology.ASYNC_WORK).isEmpty());
      assertSame(sample, old.orElseThrow());
      values(registry, LOG_ADDRESS, 1, 2, 3, 4, 1, 5);
      var zero = new Snapshot(0, 0, 0, 0, false, 0);
      supplied.set(Optional.of(zero));
      assertSame(zero, collector.collect(BrokerTopology.ASYNC_WORK).orElseThrow());
      values(registry, ASYNC_ADDRESS, 0, 0, 0, 0, 0, 0);
      assertEquals(4, calls.get());
      assertEquals(36, registry.getMeters().size());
    }
  }

  @Test
  void mqConn003RuntimeAndFatalReadFailuresClearSelectedValuesAndRethrowSameObjectOnce() {
    for (var problem :
        List.<Throwable>of(
            new IllegalArgumentException("owned invalid observation"),
            new UnformattableFailure(),
            new AssertionError("owned fatal observation"))) {
      try (var registry = new Registry()) {
        var failed = new AtomicReference<Optional<Throwable>>(Optional.empty());
        var calls = new AtomicInteger();
        var sample = new Snapshot(1, 2, 3, 4, true, 5);
        var collector =
            new MqPressureMetricCollector(
                destination -> {
                  calls.incrementAndGet();
                  if (failed.get().isPresent()) {
                    var error = failed.get().orElseThrow();
                    if (error instanceof Error fatal) throw fatal;
                    throw (RuntimeException) error;
                  }
                  return Optional.of(sample);
                },
                registry,
                DEBUG_MODE);
        collector.collect(BrokerTopology.ASYNC_WORK);
        collector.collect(BrokerTopology.WEB_LOG);
        var old = collector.snapshot(BrokerTopology.ASYNC_WORK);
        failed.set(Optional.of(problem));
        calls.set(0);
        assertSame(
            problem,
            assertThrows(problem.getClass(), () -> collector.collect(BrokerTopology.ASYNC_WORK)));
        assertEquals(1, calls.get());
        assertTrue(collector.snapshot(BrokerTopology.ASYNC_WORK).isEmpty());
        unknown(registry, ASYNC_ADDRESS);
        assertSame(sample, old.orElseThrow());
        values(registry, LOG_ADDRESS, 1, 2, 3, 4, 1, 5);
        assertEquals(0, registry.closes.get());
        failed.set(Optional.empty());
        assertSame(sample, collector.collect(BrokerTopology.ASYNC_WORK).orElseThrow());
        values(registry, ASYNC_ADDRESS, 1, 2, 3, 4, 1, 5);
        assertEquals(2, calls.get());
      }
    }
  }

  @Test
  void mqConn004StandardNeverReadsEvenFailingSourceAndAssemblyChecksAllNullModes() {
    try (var registry = new Registry()) {
      var calls = new AtomicInteger();
      var source =
          (java.util.function.Function<BrokerTopology, Optional<Snapshot>>)
              destination -> {
                calls.incrementAndGet();
                throw new AssertionError("STANDARD source must not run");
              };
      assertThrows(
          NullPointerException.class,
          () -> new MqPressureMetricCollector(null, registry, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new MqPressureMetricCollector(source, null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class, () -> new MqPressureMetricCollector(source, registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new MqPressureMetricCollector(source, registry, mode))
                .getMessage());
      var collector = new MqPressureMetricCollector(source, registry, "STANDARD");
      for (String address : ADDRESSES) {
        var destination = BrokerTopology.requireAddress(address);
        assertTrue(collector.collect(destination).isEmpty());
        assertTrue(collector.snapshot(destination).isEmpty());
      }
      assertThrows(NullPointerException.class, () -> collector.collect(null));
      assertThrows(NullPointerException.class, () -> collector.snapshot(null));
      assertEquals(0, calls.get());
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mqConn005NullDestinationCannotEraseStateAndIllegalNullResultIsNotNormalUnknown() {
    try (var registry = new Registry()) {
      var illegal = new AtomicReference<>(false);
      var calls = new AtomicInteger();
      var sample = new Snapshot(1, 2, 3, 4, true, 5);
      var collector =
          new MqPressureMetricCollector(
              destination -> {
                calls.incrementAndGet();
                return illegal.get() ? null : Optional.of(sample);
              },
              registry,
              DEBUG_MODE);
      collector.collect(BrokerTopology.ASYNC_WORK);
      collector.collect(BrokerTopology.WEB_LOG);
      var old = collector.snapshot(BrokerTopology.ASYNC_WORK);
      assertThrows(NullPointerException.class, () -> collector.collect(null));
      assertThrows(NullPointerException.class, () -> collector.snapshot(null));
      assertEquals(2, calls.get());
      assertEquals(old, collector.snapshot(BrokerTopology.ASYNC_WORK));
      illegal.set(true);
      assertEquals(
          "MQ pressure observation",
          assertThrows(
                  NullPointerException.class, () -> collector.collect(BrokerTopology.ASYNC_WORK))
              .getMessage());
      assertEquals(3, calls.get());
      assertTrue(collector.snapshot(BrokerTopology.ASYNC_WORK).isEmpty());
      unknown(registry, ASYNC_ADDRESS);
      values(registry, LOG_ADDRESS, 1, 2, 3, 4, 1, 5);
      illegal.set(false);
      assertSame(sample, collector.collect(BrokerTopology.ASYNC_WORK).orElseThrow());
      assertEquals(4, calls.get());
    }
  }

  @Test
  void mqConn006OwnedContenderIsBlockedUntilReadAndPublicationComplete() throws Exception {
    try (var registry = new Registry();
        var executor = Executors.newFixedThreadPool(2)) {
      var calls = new AtomicInteger();
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var attempted = new CountDownLatch(1);
      var contender = new AtomicReference<Thread>();
      var owner = new AtomicReference<MqPressureMetricCollector>();
      var firstSample = new Snapshot(1, 2, 3, 4, true, 5);
      var secondSample = new Snapshot(7, 8, 9, 10, false, 11);
      var collector =
          new MqPressureMetricCollector(
              destination -> {
                int call = calls.incrementAndGet();
                if (call == FIRST_READ_ORDINAL) {
                  entered.countDown();
                  await(release);
                  return Optional.of(firstSample);
                }
                assertSame(firstSample, owner.get().snapshot(destination).orElseThrow());
                return Optional.of(secondSample);
              },
              registry,
              DEBUG_MODE);
      owner.set(collector);
      var first = executor.submit(() -> collector.collect(BrokerTopology.ASYNC_WORK));
      try {
        await(entered);
        var second =
            executor.submit(
                () -> {
                  contender.set(Thread.currentThread());
                  attempted.countDown();
                  return collector.collect(BrokerTopology.ASYNC_WORK);
                });
        await(attempted);
        long until = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
        while (contender.get().getState() != Thread.State.BLOCKED
            && !second.isDone()
            && System.nanoTime() < until) Thread.onSpinWait();
        assertEquals(Thread.State.BLOCKED, contender.get().getState());
        assertEquals(1, calls.get());
        assertTrue(collector.snapshot(BrokerTopology.ASYNC_WORK).isEmpty());
        unknown(registry, ASYNC_ADDRESS);
        release.countDown();
        assertSame(firstSample, first.get(5, TimeUnit.SECONDS).orElseThrow());
        assertSame(secondSample, second.get(5, TimeUnit.SECONDS).orElseThrow());
        assertSame(secondSample, collector.snapshot(BrokerTopology.ASYNC_WORK).orElseThrow());
        values(registry, ASYNC_ADDRESS, 7, 8, 9, 10, 0, 11);
        assertEquals(2, calls.get());
      } finally {
        release.countDown();
      }
    }
  }

  @Test
  void mqConn007ParallelCallsAndSeparateOwnersKeepExactReturnedObservations() throws Exception {
    try (var registry = new Registry();
        var other = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var calls = new AtomicInteger();
      var expectedByIdentity =
          java.util.Collections.synchronizedMap(new java.util.IdentityHashMap<Snapshot, long[]>());
      var collector =
          new MqPressureMetricCollector(
              destination -> {
                int n = calls.incrementAndGet();
                long[] fixture = {n, n * 10L, n * 100L, n * 1000L, n * 10000L};
                var sample =
                    new Snapshot(fixture[0], fixture[1], fixture[2], fixture[3], true, fixture[4]);
                expectedByIdentity.put(sample, fixture);
                return Optional.of(sample);
              },
              registry,
              DEBUG_MODE);
      var separate = new Snapshot(7, 8, 9, 10, false, 11);
      var second =
          new MqPressureMetricCollector(destination -> Optional.of(separate), other, DEBUG_MODE);
      second.collect(BrokerTopology.ASYNC_WORK);
      var tasks = new ArrayList<Callable<Long>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            () -> {
              var actual = collector.collect(BrokerTopology.ASYNC_WORK).orElseThrow();
              var fixture = java.util.Objects.requireNonNull(expectedByIdentity.get(actual));
              assertEquals(fixture[0], actual.messages());
              assertEquals(fixture[1], actual.queueBytes());
              assertEquals(fixture[2], actual.addressMemoryBytes());
              assertEquals(fixture[3], actual.addressPagedBytes());
              assertTrue(actual.pagingActive());
              assertEquals(fixture[4], actual.pageFiles());
              return actual.messages();
            });
      var observed = new java.util.HashSet<Long>();
      for (var result : executor.invokeAll(tasks)) observed.add(result.get(5, TimeUnit.SECONDS));
      assertEquals(
          IntStream.rangeClosed(1, 64).mapToObj(i -> (long) i).collect(Collectors.toSet()),
          observed);
      assertEquals(64, calls.get());
      assertEquals(64, collector.snapshot(BrokerTopology.ASYNC_WORK).orElseThrow().messages());
      assertSame(separate, second.snapshot(BrokerTopology.ASYNC_WORK).orElseThrow());
      values(other, ASYNC_ADDRESS, 7, 8, 9, 10, 0, 11);
      assertEquals(36, registry.getMeters().size());
      assertEquals(36, other.getMeters().size());
      assertTrue(collector.snapshot(BrokerTopology.WEB_LOG).isEmpty());
    }
  }

  @Test
  void mqConn008PartialAssemblyFailureNeverReadsSourceClosesRegistryOrRetries() {
    for (var problem :
        List.<Throwable>of(new UnformattableFailure(), new AssertionError("owned gauge factory"))) {
      var registry = new Registry();
      var calls = new AtomicInteger();
      try {
        registry.failure = Optional.of(problem);
        assertSame(
            problem,
            assertThrows(
                problem.getClass(),
                () ->
                    new MqPressureMetricCollector(
                        destination -> {
                          calls.incrementAndGet();
                          return Optional.empty();
                        },
                        registry,
                        DEBUG_MODE)));
        assertEquals(0, calls.get());
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, registry.closes.get());
        assertTrue(Double.isNaN(gauge(registry, QUEUE_MESSAGES, "nk.sync.request")));
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }
}
