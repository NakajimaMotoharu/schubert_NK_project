package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** MEDIACONN001..008/1704; owned function/SDK/thread fixtures, no media/HTTP/file I/O. */
class MediaStreamsMetricCollectorTest {
  private static final int BLOCKED_READ_ORDINAL = 2;
  private static final String STREAMS_NAME = "nk_media_streams";
  private static final String MEDIA_LABEL = "media_type";
  private static final String AUDIO_TYPE = "AUDIO";
  private static final String VIDEO_TYPE = "VIDEO";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<MediaType> TYPES =
      List.of(MediaType.AUDIO, MediaType.VIDEO, MediaType.MUSIC);

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> failure = Optional.empty();

    @Override
    protected <T> Gauge newGauge(Meter.Id id, T object, ToDoubleFunction<T> value) {
      if (registrations.incrementAndGet() == 2 && failure.isPresent()) fail(failure.orElseThrow());
      return super.newGauge(id, object, value);
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class Unformattable extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("provider message forbidden");
    }

    @Override
    public String toString() {
      throw new AssertionError("provider formatting forbidden");
    }
  }

  private static void fail(Throwable problem) {
    if (problem instanceof Error error) throw error;
    throw (RuntimeException) problem;
  }

  private static double gauge(Registry registry, String type) {
    return registry.get(STREAMS_NAME).tag(MEDIA_LABEL, type).gauge().value();
  }

  private static void shape(Registry registry) {
    assertEquals(3, registry.getMeters().size());
    var observed = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      assertEquals(STREAMS_NAME, meter.getId().getName());
      assertEquals(Meter.Type.GAUGE, meter.getId().getType());
      assertEquals(
          Set.of(MEDIA_LABEL),
          meter.getId().getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      observed.add(meter.getId().getTag(MEDIA_LABEL));
    }
    assertEquals(Set.of(AUDIO_TYPE, VIDEO_TYPE, "MUSIC"), observed);
  }

  @Test
  void mediaConn001NoReadDuringAssemblyThenOneSelectedObservationPerCall() {
    try (var registry = new Registry()) {
      var calls = new ArrayList<MediaType>();
      var inputs = java.util.Map.of(MediaType.AUDIO, 1L, MediaType.VIDEO, 7L, MediaType.MUSIC, 19L);
      var collector =
          new MediaStreamsMetricCollector(
              type -> {
                calls.add(type);
                return OptionalLong.of(inputs.get(type));
              },
              registry,
              DEBUG_MODE);
      assertTrue(calls.isEmpty());
      for (var type : TYPES) {
        assertTrue(Double.isNaN(gauge(registry, type.name())));
        assertTrue(collector.snapshot(type).isEmpty());
        assertEquals(OptionalLong.of(inputs.get(type)), collector.collect(type));
        assertEquals((double) inputs.get(type), gauge(registry, type.name()));
      }
      assertEquals(TYPES, calls);
      shape(registry);
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mediaConn002UnknownOnlyClearsSelectedTypeAndZeroIsNotMissing() {
    try (var registry = new Registry()) {
      var next = new AtomicReference<>(OptionalLong.of(7));
      var collector = new MediaStreamsMetricCollector(type -> next.get(), registry, DEBUG_MODE);
      for (var type : TYPES) collector.collect(type);
      var old = collector.snapshot(MediaType.AUDIO);
      next.set(OptionalLong.empty());
      assertTrue(collector.collect(MediaType.AUDIO).isEmpty());
      assertTrue(Double.isNaN(gauge(registry, AUDIO_TYPE)));
      assertEquals(7, gauge(registry, VIDEO_TYPE));
      assertEquals(7, gauge(registry, "MUSIC"));
      assertEquals(OptionalLong.of(7), old);
      next.set(OptionalLong.of(0));
      assertEquals(OptionalLong.of(0), collector.collect(MediaType.AUDIO));
      assertEquals(OptionalLong.of(0), collector.snapshot(MediaType.AUDIO));
      assertEquals(0, gauge(registry, AUDIO_TYPE));
      shape(registry);
    }
  }

  @Test
  void mediaConn003StandardNeverCallsSourceAndEveryBoundaryIsStrict() {
    try (var registry = new Registry()) {
      var calls = new AtomicInteger();
      java.util.function.Function<MediaType, OptionalLong> source =
          type -> {
            calls.incrementAndGet();
            throw new AssertionError("STANDARD must not read");
          };
      assertThrows(
          NullPointerException.class,
          () -> new MediaStreamsMetricCollector(null, registry, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new MediaStreamsMetricCollector(source, null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class,
          () -> new MediaStreamsMetricCollector(source, registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "invalid monitoring mode",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new MediaStreamsMetricCollector(source, registry, mode))
                .getMessage());
      var collector = new MediaStreamsMetricCollector(source, registry, "STANDARD");
      for (var type : TYPES) {
        assertTrue(collector.collect(type).isEmpty());
        assertTrue(collector.snapshot(type).isEmpty());
      }
      assertThrows(NullPointerException.class, () -> collector.collect(null));
      assertThrows(NullPointerException.class, () -> collector.snapshot(null));
      assertEquals(0, calls.get());
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mediaConn004ProviderFailureKeepsExactIdentityAndOnlySelectedTypeBecomesUnknown() {
    for (var problem : List.<Throwable>of(new Unformattable(), new AssertionError("owned error"))) {
      var registry = new Registry();
      var calls = new AtomicInteger();
      var failure = new AtomicReference<>(Optional.<Throwable>empty());
      try {
        var collector =
            new MediaStreamsMetricCollector(
                type -> {
                  calls.incrementAndGet();
                  if (failure.get().isPresent()) fail(failure.get().orElseThrow());
                  return OptionalLong.of(type == MediaType.AUDIO ? 7 : 2);
                },
                registry,
                DEBUG_MODE);
        collector.collect(MediaType.AUDIO);
        collector.collect(MediaType.VIDEO);
        failure.set(Optional.of(problem));
        assertSame(
            problem, assertThrows(problem.getClass(), () -> collector.collect(MediaType.AUDIO)));
        assertEquals(3, calls.get());
        assertTrue(collector.snapshot(MediaType.AUDIO).isEmpty());
        assertTrue(Double.isNaN(gauge(registry, AUDIO_TYPE)));
        assertEquals(2, gauge(registry, VIDEO_TYPE));
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void mediaConn005NullOrNegativeObservationIsNotSuccessfulZeroAndMaximumIsRetained() {
    try (var registry = new Registry()) {
      var next = new AtomicReference<>(OptionalLong.of(2));
      var collector = new MediaStreamsMetricCollector(type -> next.get(), registry, DEBUG_MODE);
      collector.collect(MediaType.VIDEO);
      for (var invalid : List.of(OptionalLong.of(-1), OptionalLong.of(Long.MIN_VALUE))) {
        next.set(OptionalLong.of(7));
        collector.collect(MediaType.AUDIO);
        next.set(invalid);
        assertThrows(IllegalArgumentException.class, () -> collector.collect(MediaType.AUDIO));
        assertTrue(collector.snapshot(MediaType.AUDIO).isEmpty());
        assertEquals(2, gauge(registry, VIDEO_TYPE));
      }
      next.set(null);
      assertThrows(NullPointerException.class, () -> collector.collect(MediaType.AUDIO));
      assertTrue(Double.isNaN(gauge(registry, AUDIO_TYPE)));
      next.set(OptionalLong.of(Long.MAX_VALUE));
      assertEquals(OptionalLong.of(9_223_372_036_854_775_807L), collector.collect(MediaType.AUDIO));
      assertEquals(9.223372036854776E18, gauge(registry, AUDIO_TYPE));
      next.set(OptionalLong.of(0));
      assertEquals(OptionalLong.of(0), collector.collect(MediaType.AUDIO));
      assertEquals(0, gauge(registry, AUDIO_TYPE));
      assertThrows(NullPointerException.class, () -> collector.collect(null));
      assertThrows(NullPointerException.class, () -> collector.snapshot(null));
      shape(registry);
    }
  }

  private static void await(CountDownLatch gate) {
    try {
      assertTrue(gate.await(5, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError("owned fixture interrupted");
    }
  }

  @Test
  void mediaConn006SecondCallerActuallyBlocksUntilFirstReadAndPublicationComplete()
      throws Exception {
    try (var registry = new Registry();
        var executor = Executors.newFixedThreadPool(2)) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var calls = new AtomicInteger();
      var collector =
          new MediaStreamsMetricCollector(
              type -> {
                int call = calls.incrementAndGet();
                if (call == BLOCKED_READ_ORDINAL) {
                  entered.countDown();
                  await(release);
                }
                return OptionalLong.of(call == 1 ? 7 : call == 2 ? 11 : 13);
              },
              registry,
              DEBUG_MODE);
      collector.collect(MediaType.AUDIO);
      var first = executor.submit(() -> collector.collect(MediaType.AUDIO));
      await(entered);
      var contender = new AtomicReference<Thread>();
      var second =
          executor.submit(
              () -> {
                contender.set(Thread.currentThread());
                return collector.collect(MediaType.VIDEO);
              });
      try {
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
        while ((contender.get() == null || contender.get().getState() != Thread.State.BLOCKED)
            && System.nanoTime() < deadline) Thread.onSpinWait();
        assertNotNull(contender.get());
        assertEquals(Thread.State.BLOCKED, contender.get().getState());
        assertEquals(2, calls.get());
        assertFalse(first.isDone());
        assertFalse(second.isDone());
        assertEquals(7, gauge(registry, AUDIO_TYPE));
        assertTrue(Double.isNaN(gauge(registry, VIDEO_TYPE)));
      } finally {
        release.countDown();
      }
      assertEquals(OptionalLong.of(11), first.get(5, TimeUnit.SECONDS));
      assertEquals(OptionalLong.of(13), second.get(5, TimeUnit.SECONDS));
      assertEquals(11, gauge(registry, AUDIO_TYPE));
      assertEquals(13, gauge(registry, VIDEO_TYPE));
      assertEquals(3, calls.get());
    }
  }

  @Test
  void mediaConn007ConcurrentResultsAreExactlyFixtureInputsAndOwnersAreSeparate() throws Exception {
    try (var registry = new Registry();
        var otherRegistry = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var expected = Collections.synchronizedMap(new IdentityHashMap<OptionalLong, Long>());
      var perType = new java.util.EnumMap<MediaType, Set<Long>>(MediaType.class);
      for (var type : TYPES) perType.put(type, java.util.concurrent.ConcurrentHashMap.newKeySet());
      var serial = new AtomicInteger();
      var collector =
          new MediaStreamsMetricCollector(
              type -> {
                long scalar = 321L + serial.incrementAndGet();
                var observation = OptionalLong.of(scalar);
                expected.put(observation, scalar);
                perType.get(type).add(scalar);
                return observation;
              },
              registry,
              DEBUG_MODE);
      var tasks = new ArrayList<Callable<OptionalLong>>();
      for (int index = 0; index < 64; index++) {
        var type = TYPES.get(index % 3);
        tasks.add(() -> collector.collect(type));
      }
      for (var result : executor.invokeAll(tasks)) {
        var observation = result.get(5, TimeUnit.SECONDS);
        assertTrue(expected.containsKey(observation));
        assertEquals(expected.get(observation).longValue(), observation.orElseThrow());
      }
      assertEquals(64, serial.get());
      assertEquals(64, expected.size());
      var observed = new AtomicInteger(99);
      var other =
          new MediaStreamsMetricCollector(
              type -> OptionalLong.of(observed.incrementAndGet()), otherRegistry, DEBUG_MODE);
      for (var type : TYPES) other.collect(type);
      assertEquals(100, gauge(otherRegistry, AUDIO_TYPE));
      assertEquals(101, gauge(otherRegistry, VIDEO_TYPE));
      assertEquals(102, gauge(otherRegistry, "MUSIC"));
      for (var type : TYPES) {
        assertTrue(perType.get(type).contains((long) gauge(registry, type.name())));
        assertTrue(gauge(registry, type.name()) >= 322);
        assertTrue(gauge(registry, type.name()) <= 385);
      }
      shape(registry);
      shape(otherRegistry);
    }
  }

  @Test
  void mediaConn008AssemblyFailureDoesNotReadRetryCloseOrReplaceForeignMeter() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned factory"))) {
      var registry = new Registry();
      var reads = new AtomicInteger();
      registry.failure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(),
                () ->
                    new MediaStreamsMetricCollector(
                        type -> {
                          reads.incrementAndGet();
                          return OptionalLong.of(7);
                        },
                        registry,
                        DEBUG_MODE)));
        assertEquals(0, reads.get());
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertTrue(Double.isNaN(gauge(registry, AUDIO_TYPE)));
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
    try (var registry = new Registry()) {
      var foreign = Counter.builder(STREAMS_NAME).tag(MEDIA_LABEL, AUDIO_TYPE).register(registry);
      foreign.increment(7);
      assertThrows(
          IllegalArgumentException.class,
          () -> new MediaStreamsMetricCollector(type -> OptionalLong.of(1), registry, DEBUG_MODE));
      assertSame(foreign, registry.get(STREAMS_NAME).tag(MEDIA_LABEL, AUDIO_TYPE).counter());
      assertEquals(7, foreign.count());
      assertEquals(0, registry.closes.get());
    }
  }
}
