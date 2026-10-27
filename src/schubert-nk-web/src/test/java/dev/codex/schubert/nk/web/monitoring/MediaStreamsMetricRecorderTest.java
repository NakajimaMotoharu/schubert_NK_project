package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.ToDoubleFunction;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * MEDIASTREAM001..008/1702, SS333/351 literal media-type oracle, only owned SDK; no actual
 * stream/HTTP.
 */
class MediaStreamsMetricRecorderTest {
  private static final String AUDIO_TYPE_NAME = "AUDIO";
  private static final String VIDEO_TYPE_NAME = "VIDEO";
  private static final String MUSIC_TYPE_NAME = "MUSIC";
  private static final String MEDIA_STREAMS_NAME = "nk_media_streams";
  private static final String MEDIA_TYPE_LABEL = "media_type";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<String> TYPES =
      List.of(AUDIO_TYPE_NAME, VIDEO_TYPE_NAME, MUSIC_TYPE_NAME);

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

  private static double gauge(Registry registry, String type) {
    return registry.get(MEDIA_STREAMS_NAME).tag(MEDIA_TYPE_LABEL, type).gauge().value();
  }

  private static void shape(Registry registry) {
    assertEquals(3, registry.getMeters().size());
    var types = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(MEDIA_STREAMS_NAME, id.getName());
      assertEquals(Meter.Type.GAUGE, id.getType());
      assertEquals(
          Set.of(MEDIA_TYPE_LABEL),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      types.add(id.getTag(MEDIA_TYPE_LABEL));
    }
    assertEquals(Set.of(AUDIO_TYPE_NAME, VIDEO_TYPE_NAME, MUSIC_TYPE_NAME), types);
  }

  @Test
  void mediaStream001DebugHasOnlyThreeCanonicalTypeSeriesInitiallyUnknown() {
    try (var registry = new Registry()) {
      var recorder = new MediaStreamsMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      for (String type : TYPES) {
        assertTrue(Double.isNaN(gauge(registry, type)));
        assertTrue(recorder.snapshot(MediaType.valueOf(type)).isEmpty());
      }
      assertEquals(3, registry.registrations.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mediaStream002IndependentValuesZeroThresholdsAndMaximumAreNotClampedOrSummed() {
    try (var registry = new Registry()) {
      var recorder = new MediaStreamsMetricRecorder(registry, DEBUG_MODE);
      recorder.record(MediaType.AUDIO, 1);
      recorder.record(MediaType.VIDEO, 7);
      recorder.record(MediaType.MUSIC, 19);
      assertEquals(1, gauge(registry, AUDIO_TYPE_NAME));
      assertEquals(7, gauge(registry, VIDEO_TYPE_NAME));
      assertEquals(19, gauge(registry, MUSIC_TYPE_NAME));
      for (String type : TYPES)
        for (long count : List.of(0L, 16L, 20L, 21L)) {
          var media = MediaType.valueOf(type);
          recorder.record(media, count);
          assertTrue(recorder.snapshot(media).isPresent());
          assertEquals(count, recorder.snapshot(media).orElseThrow());
          assertEquals((double) count, gauge(registry, type));
        }
      recorder.record(MediaType.MUSIC, Long.MAX_VALUE);
      assertEquals(9_223_372_036_854_775_807L, recorder.snapshot(MediaType.MUSIC).orElseThrow());
      assertEquals(9.223372036854776E18, gauge(registry, MUSIC_TYPE_NAME));
      shape(registry);
      assertEquals(3, registry.registrations.get());
    }
  }

  @Test
  void mediaStream003MissingIsNotZeroAndCannotClearOtherTypeOrOldObservation() {
    try (var registry = new Registry()) {
      var recorder = new MediaStreamsMetricRecorder(registry, DEBUG_MODE);
      recorder.record(MediaType.AUDIO, 1);
      recorder.record(MediaType.VIDEO, 2);
      recorder.record(MediaType.MUSIC, 3);
      var old = recorder.snapshot(MediaType.AUDIO);
      recorder.missing(MediaType.AUDIO);
      recorder.missing(MediaType.AUDIO);
      assertTrue(recorder.snapshot(MediaType.AUDIO).isEmpty());
      assertTrue(Double.isNaN(gauge(registry, AUDIO_TYPE_NAME)));
      assertEquals(OptionalLong.of(1), old);
      assertEquals(2, gauge(registry, VIDEO_TYPE_NAME));
      assertEquals(3, gauge(registry, MUSIC_TYPE_NAME));
      recorder.record(MediaType.AUDIO, 0);
      assertEquals(OptionalLong.of(0), recorder.snapshot(MediaType.AUDIO));
      assertEquals(0, gauge(registry, AUDIO_TYPE_NAME));
      shape(registry);
    }
  }

  @Test
  void mediaStream004StandardHasNoDetailedSeriesOrRetainedCountsAndModeIsStrict() {
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new MediaStreamsMetricRecorder(null, DEBUG_MODE));
      assertThrows(
          NullPointerException.class, () -> new MediaStreamsMetricRecorder(registry, null));
      for (String mode : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "invalid monitoring mode",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new MediaStreamsMetricRecorder(registry, mode))
                .getMessage());
      var recorder = new MediaStreamsMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      for (String type : TYPES) {
        var media = MediaType.valueOf(type);
        recorder.record(media, 21);
        assertTrue(recorder.snapshot(media).isEmpty());
        recorder.missing(media);
        assertTrue(recorder.snapshot(media).isEmpty());
      }
      assertEquals(0, registry.getMeters().size());
      assertEquals(0, registry.registrations.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mediaStream005NullAndNegativeBoundariesNeverEraseAcceptedCountInEitherMode() {
    for (String mode : List.of(DEBUG_MODE, "STANDARD"))
      try (var registry = new Registry()) {
        var recorder = new MediaStreamsMetricRecorder(registry, mode);
        recorder.record(MediaType.AUDIO, 7);
        var old = recorder.snapshot(MediaType.AUDIO);
        assertThrows(NullPointerException.class, () -> recorder.record(null, 1));
        assertThrows(NullPointerException.class, () -> recorder.missing(null));
        assertThrows(NullPointerException.class, () -> recorder.snapshot(null));
        for (long count : List.of(-1L, Long.MIN_VALUE))
          assertThrows(
              IllegalArgumentException.class, () -> recorder.record(MediaType.AUDIO, count));
        assertEquals(old, recorder.snapshot(MediaType.AUDIO));
        assertEquals(0, registry.closes.get());
        if (mode.equals(DEBUG_MODE)) {
          assertEquals(7, gauge(registry, AUDIO_TYPE_NAME));
          shape(registry);
        } else assertEquals(0, registry.getMeters().size());
      }
  }

  @Test
  void mediaStream006PartialGaugeFactoryFailureKeepsExactProblemAndBorrowedRegistry() {
    for (var problem :
        List.<Throwable>of(new UnformattableFailure(), new AssertionError("owned gauge factory"))) {
      var registry = new Registry();
      try {
        registry.failure = Optional.of(problem);
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> new MediaStreamsMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertTrue(Double.isNaN(gauge(registry, AUDIO_TYPE_NAME)));
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void mediaStream007ParallelTypePublicationAndSeparateOwnersCannotCrossStateOrGrowLabels()
      throws Exception {
    try (var registry = new Registry();
        var other = new Registry();
        var executor = Executors.newFixedThreadPool(8)) {
      var recorder = new MediaStreamsMetricRecorder(registry, DEBUG_MODE);
      var second = new MediaStreamsMetricRecorder(other, DEBUG_MODE);
      second.record(MediaType.MUSIC, 99);
      var expected =
          List.of(
              new java.util.HashSet<Long>(),
              new java.util.HashSet<Long>(),
              new java.util.HashSet<Long>());
      var tasks = new ArrayList<Callable<String>>();
      for (int i = 0; i < 64; i++) {
        int slot = i % 3;
        long count = i;
        var type = MediaType.valueOf(TYPES.get(slot));
        expected.get(slot).add(count);
        tasks.add(
            () -> {
              recorder.record(type, count);
              return "published";
            });
      }
      for (var result : executor.invokeAll(tasks)) assertEquals("published", result.get());
      for (int i = 0; i < 3; i++) {
        var type = MediaType.valueOf(TYPES.get(i));
        assertTrue(expected.get(i).contains(recorder.snapshot(type).orElseThrow()));
        var allowedGauge =
            expected.get(i).stream().map(Long::doubleValue).collect(Collectors.toSet());
        assertTrue(allowedGauge.contains(gauge(registry, TYPES.get(i))));
        long finalInput = 100L + i;
        recorder.record(type, finalInput);
        assertEquals(OptionalLong.of(finalInput), recorder.snapshot(type));
        assertEquals((double) finalInput, gauge(registry, TYPES.get(i)));
      }
      assertEquals(OptionalLong.of(99), second.snapshot(MediaType.MUSIC));
      assertEquals(99, gauge(other, MUSIC_TYPE_NAME));
      assertTrue(Double.isNaN(gauge(other, AUDIO_TYPE_NAME)));
      assertTrue(Double.isNaN(gauge(other, VIDEO_TYPE_NAME)));
      shape(registry);
      shape(other);
      assertEquals(3, registry.registrations.get());
      assertEquals(3, other.registrations.get());
    }
  }

  @Test
  void mediaStream008ForeignCounterCannotBeReplacedOrCloseCallerRegistry() {
    try (var registry = new Registry()) {
      var foreign =
          Counter.builder(MEDIA_STREAMS_NAME)
              .tag(MEDIA_TYPE_LABEL, AUDIO_TYPE_NAME)
              .register(registry);
      foreign.increment(7);
      assertThrows(
          IllegalArgumentException.class,
          () -> new MediaStreamsMetricRecorder(registry, DEBUG_MODE));
      assertEquals(1, registry.getMeters().size());
      assertSame(
          foreign,
          registry.get(MEDIA_STREAMS_NAME).tag(MEDIA_TYPE_LABEL, AUDIO_TYPE_NAME).counter());
      assertEquals(7, foreign.count());
      assertEquals(0, registry.closes.get());
    }
  }
}
