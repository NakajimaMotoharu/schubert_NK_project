package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.web.monitoring.MediaBytesMetricRecorder.Mode;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** MEDIABYTE001..008/1706; literal labels and independent supplied-byte oracle, no delivery. */
class MediaBytesMetricRecorderTest {
  private static final int FAILURE_FACTORY_CALL = 2;
  private static final String MEDIA_BYTES_NAME = "nk_media_bytes_total";
  private static final String MEDIA_TYPE_LABEL = "media_type";
  private static final String MODE_LABEL = "mode";
  private static final String STATUS_LABEL = "status";
  private static final String AUDIO_TYPE_NAME = "AUDIO";
  private static final String VIDEO_TYPE_NAME = "VIDEO";
  private static final String MUSIC_TYPE_NAME = "MUSIC";
  private static final String INLINE_MODE_NAME = "INLINE";
  private static final String DOWNLOAD_MODE_NAME = "DOWNLOAD";
  private static final String RANGE_MODE_NAME = "RANGE";
  private static final String DEBUG_MODE = "DEBUG";
  private static final List<MediaType> TYPES =
      List.of(MediaType.AUDIO, MediaType.VIDEO, MediaType.MUSIC);
  private static final List<Mode> MODES = List.of(Mode.INLINE, Mode.DOWNLOAD, Mode.RANGE);
  private static final List<Integer> STATUSES = List.of(200, 206, 416, 503);

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger registrations = new AtomicInteger();
    final AtomicInteger increments = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    Optional<Throwable> registrationFailure = Optional.empty();
    Optional<Throwable> incrementFailure = Optional.empty();
    boolean failAfter;

    @Override
    protected Counter newCounter(Meter.Id id) {
      if (registrations.incrementAndGet() == FAILURE_FACTORY_CALL) fail(registrationFailure);
      var delegate = super.newCounter(id);
      return new Counter() {
        @Override
        public Meter.Id getId() {
          return delegate.getId();
        }

        @Override
        public double count() {
          return delegate.count();
        }

        @Override
        public void increment(double amount) {
          increments.incrementAndGet();
          if (!failAfter) fail(incrementFailure);
          delegate.increment(amount);
          if (failAfter) fail(incrementFailure);
        }
      };
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

  private static void fail(Optional<Throwable> failure) {
    if (failure.isPresent()) {
      var problem = failure.orElseThrow();
      if (problem instanceof Error error) throw error;
      throw (RuntimeException) problem;
    }
  }

  private static double count(Registry registry, String type, String mode, int status) {
    return registry
        .get(MEDIA_BYTES_NAME)
        .tags(MEDIA_TYPE_LABEL, type, MODE_LABEL, mode, STATUS_LABEL, Integer.toString(status))
        .counter()
        .count();
  }

  private static void shape(Registry registry) {
    assertEquals(36, registry.getMeters().size());
    var observed = new java.util.HashSet<String>();
    for (var meter : registry.getMeters()) {
      var id = meter.getId();
      assertEquals(MEDIA_BYTES_NAME, id.getName());
      assertEquals(Meter.Type.COUNTER, id.getType());
      assertEquals(
          Set.of(MEDIA_TYPE_LABEL, MODE_LABEL, STATUS_LABEL),
          id.getTags().stream().map(t -> t.getKey()).collect(Collectors.toSet()));
      observed.add(
          id.getTag(MEDIA_TYPE_LABEL)
              + "/"
              + id.getTag(MODE_LABEL)
              + "/"
              + id.getTag(STATUS_LABEL));
    }
    var expected = new java.util.HashSet<String>();
    for (String type : List.of(AUDIO_TYPE_NAME, VIDEO_TYPE_NAME, MUSIC_TYPE_NAME))
      for (String mode : List.of(INLINE_MODE_NAME, DOWNLOAD_MODE_NAME, RANGE_MODE_NAME))
        for (int status : List.of(200, 206, 416, 503))
          expected.add(type + "/" + mode + "/" + status);
    assertEquals(expected, observed);
  }

  @Test
  void mediaByte001ExactlyThirtySixCanonicalSeriesStartAtZero() {
    try (var registry = new Registry()) {
      var recorder = new MediaBytesMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      shape(registry);
      for (String type : List.of(AUDIO_TYPE_NAME, VIDEO_TYPE_NAME, MUSIC_TYPE_NAME))
        for (String mode : List.of(INLINE_MODE_NAME, DOWNLOAD_MODE_NAME, RANGE_MODE_NAME))
          for (int status : STATUSES) assertEquals(0, count(registry, type, mode, status));
      assertEquals(36, registry.registrations.get());
      assertEquals(0, registry.increments.get());
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void mediaByte002BytesNotEventsAndZeroMaximumOrOtherSeriesDoNotChangeCardinality() {
    try (var registry = new Registry()) {
      var recorder = new MediaBytesMetricRecorder(registry, DEBUG_MODE);
      for (var type : TYPES)
        for (var mode : MODES)
          for (int status : STATUSES) {
            recorder.record(type, mode, status, 1);
            recorder.record(type, mode, status, 2);
            recorder.record(type, mode, status, 0);
            assertEquals(3, count(registry, type.name(), mode.name(), status));
          }
      recorder.record(MediaType.MUSIC, Mode.DOWNLOAD, 200, Long.MAX_VALUE);
      assertEquals(9.223372036854776E18, count(registry, MUSIC_TYPE_NAME, DOWNLOAD_MODE_NAME, 200));
      assertEquals(3, count(registry, MUSIC_TYPE_NAME, INLINE_MODE_NAME, 200));
      assertEquals(3, count(registry, VIDEO_TYPE_NAME, RANGE_MODE_NAME, 206));
      assertEquals(109, registry.increments.get());
      assertEquals(36, registry.registrations.get());
      shape(registry);
    }
  }

  @Test
  void mediaByte003ModesAreClosedAndGeneratedFactoriesHaveIndependentTypedContracts() {
    assertEquals(Mode.INLINE, Mode.parse(INLINE_MODE_NAME));
    assertEquals(Mode.DOWNLOAD, Mode.parse(DOWNLOAD_MODE_NAME));
    assertEquals(Mode.RANGE, Mode.parse(RANGE_MODE_NAME));
    for (String unknown : List.of("", "inline", "ATTACHMENT", "unknown-mode"))
      assertEquals(
          "invalid media byte mode",
          assertThrows(IllegalArgumentException.class, () -> Mode.parse(unknown)).getMessage());
    assertThrows(NullPointerException.class, () -> Mode.parse(null));
    assertArrayEquals(new Mode[] {Mode.INLINE, Mode.DOWNLOAD, Mode.RANGE}, Mode.values());
    var mutable = Mode.values();
    mutable[0] = Mode.RANGE;
    assertArrayEquals(new Mode[] {Mode.INLINE, Mode.DOWNLOAD, Mode.RANGE}, Mode.values());
    assertSame(Mode.INLINE, Mode.valueOf(INLINE_MODE_NAME));
    assertSame(Mode.DOWNLOAD, Mode.valueOf(DOWNLOAD_MODE_NAME));
    assertSame(Mode.RANGE, Mode.valueOf(RANGE_MODE_NAME));
    assertThrows(IllegalArgumentException.class, () -> Mode.valueOf("inline"));
    assertThrows(NullPointerException.class, () -> Mode.valueOf(null));
    assertEquals(List.of(200, 206, 416, 503), MediaBytesMetricRecorder.statuses());
    assertThrows(
        UnsupportedOperationException.class, () -> MediaBytesMetricRecorder.statuses().add(999));
    assertEquals(List.of(200, 206, 416, 503), MediaBytesMetricRecorder.statuses());
  }

  @Test
  void mediaByte004NullUnknownAndNegativeAreRejectedBeforeAnyIncrementInEitherMode() {
    for (String monitoring : List.of(DEBUG_MODE, "STANDARD"))
      try (var registry = new Registry()) {
        var recorder = new MediaBytesMetricRecorder(registry, monitoring);
        recorder.record(MediaType.AUDIO, Mode.INLINE, 200, 7);
        int before = registry.increments.get();
        assertThrows(NullPointerException.class, () -> recorder.record(null, Mode.INLINE, 200, 1));
        assertThrows(
            NullPointerException.class, () -> recorder.record(MediaType.AUDIO, null, 200, 1));
        for (int status :
            List.of(
                Integer.MIN_VALUE,
                -1,
                0,
                199,
                201,
                205,
                207,
                415,
                417,
                502,
                504,
                599,
                Integer.MAX_VALUE))
          assertThrows(
              IllegalArgumentException.class,
              () -> recorder.record(MediaType.AUDIO, Mode.INLINE, status, 1));
        for (long bytes : List.of(-1L, Long.MIN_VALUE))
          assertThrows(
              IllegalArgumentException.class,
              () -> recorder.record(MediaType.AUDIO, Mode.INLINE, 200, bytes));
        assertEquals(before, registry.increments.get());
        if (monitoring.equals(DEBUG_MODE)) {
          assertTrue(recorder.detailedMetricsRequested());
          assertEquals(7, count(registry, AUDIO_TYPE_NAME, INLINE_MODE_NAME, 200));
          shape(registry);
        } else {
          assertFalse(recorder.detailedMetricsRequested());
          for (var type : TYPES)
            for (var mode : MODES)
              for (int status : STATUSES) recorder.record(type, mode, status, 0);
          assertEquals(0, registry.getMeters().size());
          assertEquals(0, registry.increments.get());
        }
        assertEquals(0, registry.closes.get());
      }
    try (var registry = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> new MediaBytesMetricRecorder(null, DEBUG_MODE));
      assertThrows(NullPointerException.class, () -> new MediaBytesMetricRecorder(registry, null));
      for (String monitoring : List.of("", "debug", "unknown-mode"))
        assertEquals(
            "invalid monitoring mode",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new MediaBytesMetricRecorder(registry, monitoring))
                .getMessage());
      assertEquals(0, registry.getMeters().size());
    }
  }

  @Test
  void mediaByte005PartialFactoryFailureKeepsIdentityPrefixAndBorrowedRegistry() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned factory"))) {
      var registry = new Registry();
      registry.registrationFailure = Optional.of(problem);
      try {
        assertSame(
            problem,
            assertThrows(
                problem.getClass(), () -> new MediaBytesMetricRecorder(registry, DEBUG_MODE)));
        assertEquals(2, registry.registrations.get());
        assertEquals(1, registry.getMeters().size());
        assertEquals(0, count(registry, AUDIO_TYPE_NAME, INLINE_MODE_NAME, 200));
        assertEquals(0, registry.increments.get());
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }

  @Test
  void mediaByte006FailureBeforeOrAfterIncrementNeverRetriesCompensatesOrReturnsSuccess() {
    for (var problem :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned increment")))
      for (boolean after : List.of(false, true)) {
        var registry = new Registry();
        try {
          var recorder = new MediaBytesMetricRecorder(registry, DEBUG_MODE);
          registry.incrementFailure = Optional.of(problem);
          registry.failAfter = after;
          assertSame(
              problem,
              assertThrows(
                  problem.getClass(), () -> recorder.record(MediaType.AUDIO, Mode.INLINE, 200, 3)));
          assertEquals(1, registry.increments.get());
          assertEquals(after ? 3 : 0, count(registry, AUDIO_TYPE_NAME, INLINE_MODE_NAME, 200));
          assertEquals(0, count(registry, VIDEO_TYPE_NAME, RANGE_MODE_NAME, 206));
          assertEquals(0, registry.closes.get());
          shape(registry);
        } finally {
          registry.close();
        }
        assertEquals(1, registry.closes.get());
      }
  }

  @Test
  void mediaByte007ConcurrentByteTotalsComeFromPrecomputedInputsAndOwnersAreIndependent()
      throws Exception {
    try (var registry = new Registry();
        var otherRegistry = new Registry()) {
      var executor = Executors.newFixedThreadPool(8);
      try {
        var recorder = new MediaBytesMetricRecorder(registry, DEBUG_MODE);
        Map<String, Long> expected = new HashMap<>();
        var tasks = new ArrayList<Callable<Void>>();
        for (int index = 0; index < 64; index++) {
          var type = TYPES.get(index % 3);
          var mode = MODES.get((index / 3) % 3);
          int status = STATUSES.get((index / 9) % 4);
          long bytes = 1L + index;
          expected.merge(type.name() + "/" + mode.name() + "/" + status, bytes, Long::sum);
          tasks.add(
              () -> {
                recorder.record(type, mode, status, bytes);
                return null;
              });
        }
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          result.get(5, TimeUnit.SECONDS);
        for (var type : TYPES)
          for (var mode : MODES)
            for (int status : STATUSES)
              assertEquals(
                  expected
                      .getOrDefault(type.name() + "/" + mode.name() + "/" + status, 0L)
                      .doubleValue(),
                  count(registry, type.name(), mode.name(), status));
        assertEquals(64, registry.increments.get());
        var other = new MediaBytesMetricRecorder(otherRegistry, DEBUG_MODE);
        other.record(MediaType.AUDIO, Mode.INLINE, 200, 7);
        assertEquals(7, count(otherRegistry, AUDIO_TYPE_NAME, INLINE_MODE_NAME, 200));
        assertEquals(
            expected.get("AUDIO/INLINE/200").doubleValue(),
            count(registry, AUDIO_TYPE_NAME, INLINE_MODE_NAME, 200));
        shape(registry);
        shape(otherRegistry);
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void mediaByte008ForeignGaugeIsNeverReplacedOrClosed() {
    try (var registry = new Registry()) {
      var foreign =
          Gauge.builder(MEDIA_BYTES_NAME, new AtomicInteger(7), AtomicInteger::get)
              .tags(
                  MEDIA_TYPE_LABEL,
                  AUDIO_TYPE_NAME,
                  MODE_LABEL,
                  INLINE_MODE_NAME,
                  STATUS_LABEL,
                  "200")
              .register(registry);
      assertThrows(
          IllegalArgumentException.class, () -> new MediaBytesMetricRecorder(registry, DEBUG_MODE));
      assertSame(
          foreign,
          registry
              .get(MEDIA_BYTES_NAME)
              .tags(
                  MEDIA_TYPE_LABEL,
                  AUDIO_TYPE_NAME,
                  MODE_LABEL,
                  INLINE_MODE_NAME,
                  STATUS_LABEL,
                  "200")
              .gauge());
      assertEquals(7, foreign.value());
      assertEquals(0, registry.closes.get());
    }
  }
}
