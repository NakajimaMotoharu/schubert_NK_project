package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.distribution.pause.PauseDetector;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** Actual owned Micrometer registry, fixed metadata/vectors and no HTTP/DB/target. Spec1573. */
class HttpMetricRecorderTest {
  private static final String SERVICE_LABEL = "service";
  private static final String WEB_SERVICE_NAME = "WEB";
  private static final String ROUTE_LABEL = "route";
  private static final String LOGIN_PATH = "/login";
  private static final String GET_METHOD = "GET";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String SUCCESS_STATUS_LABEL = "2xx";
  private static final String SEARCH_PATH = "/search";
  private static final String REQUESTS = "nk_http_requests_total";
  private static final String DURATION_METRIC = "nk_http_request_duration_seconds";
  private static final double[] BOUNDS = {
    50_000_000,
    100_000_000,
    250_000_000,
    500_000_000,
    1_000_000_000,
    1_500_000_000,
    2_000_000_000,
    2_500_000_000L,
    5_000_000_000L
  };

  private static class InspectingRegistry extends SimpleMeterRegistry
      implements AutoCloseable, OverflowSafeDurationSupport {
    final List<double[]> boundaries = new ArrayList<>();
    final AtomicInteger closes = new AtomicInteger();

    InspectingRegistry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    @Override
    protected Timer newTimer(Meter.Id id, DistributionStatisticConfig config, PauseDetector pause) {
      boundaries.add(Objects.requireNonNull(config.getServiceLevelObjectiveBoundaries()).clone());
      return OverflowSafeHttpMeterRegistry.durationTimer(
          this, config, pause, () -> super.newTimer(id, config, pause));
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class FaultRegistry extends InspectingRegistry {
    private final boolean counterFault;
    private Optional<Throwable> fault = Optional.empty();
    final AtomicInteger attempts = new AtomicInteger();

    FaultRegistry(boolean counterFault) {
      this.counterFault = counterFault;
    }

    void arm(Throwable value) {
      fault = Optional.of(value);
    }

    private void inject() {
      attempts.incrementAndGet();
      Throwable value = fault.orElseThrow();
      if (value instanceof Error error) throw error;
      throw (RuntimeException) value;
    }

    @Override
    protected Counter newCounter(Meter.Id id) {
      Counter delegate = super.newCounter(id);
      if (!counterFault) return delegate;
      return new Counter() {
        @Override
        public void increment(double amount) {
          if (fault.isPresent()) inject();
          delegate.increment(amount);
        }

        @Override
        public double count() {
          return delegate.count();
        }

        @Override
        public Meter.Id getId() {
          return delegate.getId();
        }
      };
    }

    @Override
    protected Timer newTimer(Meter.Id id, DistributionStatisticConfig config, PauseDetector pause) {
      Timer delegate = super.newTimer(id, config, pause);
      if (counterFault) return delegate;
      return (Timer)
          Proxy.newProxyInstance(
              Timer.class.getClassLoader(),
              new Class<?>[] {Timer.class},
              (proxy, method, args) -> {
                if (method.getName().equals("record")
                    && args != null
                    && args.length == 2
                    && args[0] instanceof Long
                    && args[1] instanceof TimeUnit
                    && fault.isPresent()) inject();
                return method.invoke(delegate, args);
              });
    }
  }

  private static Counter request(
      SimpleMeterRegistry registry, String route, String method, String status) {
    return registry
        .get(REQUESTS)
        .tags(
            SERVICE_LABEL,
            WEB_SERVICE_NAME,
            ROUTE_LABEL,
            route,
            "method",
            method,
            "status_class",
            status)
        .counter();
  }

  private static Timer duration(SimpleMeterRegistry registry, String route) {
    return registry
        .get(DURATION_METRIC)
        .tags(SERVICE_LABEL, WEB_SERVICE_NAME, ROUTE_LABEL, route)
        .timer();
  }

  private static List<String> routes() throws Exception {
    try (var reader =
        new BufferedReader(
            new InputStreamReader(
                Objects.requireNonNull(
                    HttpMetricRecorderTest.class.getResourceAsStream(
                        "/monitoring/http-route-labels.txt")),
                StandardCharsets.UTF_8))) {
      return reader.lines().toList();
    }
  }

  /**
   * SS nine boundaries plus pinned Simple provider's distinct auxiliary histogram representation.
   */
  private static void assertRegistryShape(InspectingRegistry registry) throws Exception {
    assertEquals(2100, registry.getMeters().size());
    assertEquals(
        1750,
        registry.getMeters().stream()
            .filter(m -> m.getId().getType() == Meter.Type.COUNTER)
            .count());
    assertEquals(
        35,
        registry.getMeters().stream().filter(m -> m.getId().getType() == Meter.Type.TIMER).count());
    var gauges =
        registry.getMeters().stream().filter(m -> m.getId().getType() == Meter.Type.GAUGE).toList();
    assertEquals(315, gauges.size());
    var byRoute = new HashMap<String, Set<Double>>();
    var counts = new HashMap<String, Integer>();
    for (var meter : gauges) {
      var id = meter.getId();
      assertEquals(DURATION_METRIC + ".histogram", id.getName());
      assertEquals(
          Set.of(SERVICE_LABEL, ROUTE_LABEL, "le"),
          id.getTags().stream().map(t -> t.getKey()).collect(java.util.stream.Collectors.toSet()));
      assertEquals(WEB_SERVICE_NAME, id.getTag(SERVICE_LABEL));
      String route = Objects.requireNonNull(id.getTag(ROUTE_LABEL));
      double boundary = Double.parseDouble(Objects.requireNonNull(id.getTag("le")));
      assertTrue(Double.isFinite(boundary));
      byRoute.computeIfAbsent(route, ignored -> new HashSet<>()).add(boundary);
      counts.merge(route, 1, Integer::sum);
    }
    assertEquals(new HashSet<>(routes()), byRoute.keySet());
    for (Map.Entry<String, Set<Double>> entry : byRoute.entrySet()) {
      assertEquals(Set.of(.05, .1, .25, .5, 1.0, 1.5, 2.0, 2.5, 5.0), entry.getValue());
      assertEquals(9, counts.get(entry.getKey()));
    }
  }

  @Test
  void httpRec001StandardDoesNotRegisterOrClose() {
    try (var registry = new InspectingRegistry()) {
      var recorder = new HttpMetricRecorder(registry, "STANDARD");
      assertFalse(recorder.detailedMetricsRequested());
      recorder.record(LOGIN_PATH, GET_METHOD, 200, 1_000_000_000);
      assertTrue(registry.getMeters().isEmpty());
      assertEquals(0, registry.closes.get());
      assertFalse(registry.isClosed());
    }
  }

  @Test
  void httpRec002ActualMeterNamesTagsAndNineSlos() throws Exception {
    try (var registry = new InspectingRegistry()) {
      var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
      assertTrue(recorder.detailedMetricsRequested());
      assertRegistryShape(registry);
      assertEquals(
          1750,
          registry.getMeters().stream()
              .filter(m -> m.getId().getType() == Meter.Type.COUNTER)
              .count());
      assertEquals(35, registry.boundaries.size());
      for (var actual : registry.boundaries) assertArrayEquals(BOUNDS, actual, 0.0);
      recorder.record(LOGIN_PATH, GET_METHOD, 200, 1_000_000_000);
      var counter = request(registry, LOGIN_PATH, GET_METHOD, SUCCESS_STATUS_LABEL);
      var timer = duration(registry, LOGIN_PATH);
      assertEquals(1.0, counter.count());
      assertEquals(1, timer.count());
      assertEquals(1.0, timer.totalTime(TimeUnit.SECONDS), 0.0);
      assertEquals(4, counter.getId().getTags().size());
      assertEquals(2, timer.getId().getTags().size());
      var actual =
          java.util.Arrays.stream(timer.takeSnapshot().histogramCounts())
              .mapToDouble(v -> v.bucket())
              .toArray();
      assertArrayEquals(BOUNDS, actual, 0.0);
    }
  }

  @Test
  void httpRec003WholeIndependentMatrixHasExactCounts() throws Exception {
    try (var registry = new InspectingRegistry()) {
      var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
      String[] methods = {
        GET_METHOD, "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT", "OTHER"
      };
      int[] statuses = {100, 200, 300, 400, 500};
      String[] groups = {"1xx", SUCCESS_STATUS_LABEL, "3xx", "4xx", "5xx"};
      var routes = routes();
      assertEquals(35, routes.size());
      for (String route : routes)
        for (String method : methods)
          for (int status : statuses) recorder.record(route, method, status, 1_000_000_000);
      for (String route : routes) {
        for (String method : methods)
          for (String group : groups)
            assertEquals(1.0, request(registry, route, method, group).count());
        assertEquals(50, duration(registry, route).count());
        assertEquals(50.0, duration(registry, route).totalTime(TimeUnit.SECONDS), 0.0);
      }
      assertRegistryShape(registry);
    }
  }

  @Test
  void httpRec004UnknownInputsCannotCreateSeries() throws Exception {
    try (var registry = new InspectingRegistry()) {
      var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
      for (int index = 0; index < 10_000; index++)
        recorder.record(
            "/questions/" + index + "?actor=PT_FIXTURE_ONLY",
            "RAW_FIXTURE_" + index,
            200,
            1_000_000);
      assertEquals(10_000.0, request(registry, "/**", "OTHER", SUCCESS_STATUS_LABEL).count());
      assertEquals(10_000, duration(registry, "/**").count());
      assertRegistryShape(registry);
      for (var meter : registry.getMeters())
        for (var tag : meter.getId().getTags()) {
          assertFalse(tag.getValue().contains("PT_FIXTURE_ONLY"));
          assertFalse(tag.getValue().contains("RAW_FIXTURE_"));
        }
    }
  }

  @Test
  void httpRec005InvalidAndSingleMaximumBoundaries() {
    assertThrows(NullPointerException.class, () -> new HttpMetricRecorder(null, "STANDARD"));
    try (var registry = new InspectingRegistry()) {
      assertThrows(NullPointerException.class, () -> new HttpMetricRecorder(registry, null));
      assertThrows(IllegalArgumentException.class, () -> new HttpMetricRecorder(registry, "debug"));
      assertTrue(registry.getMeters().isEmpty());
      var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
      assertThrows(NullPointerException.class, () -> recorder.record(null, GET_METHOD, 200, 1));
      assertThrows(NullPointerException.class, () -> recorder.record("/", null, 200, 1));
      assertThrows(IllegalArgumentException.class, () -> recorder.record("/", GET_METHOD, 99, 1));
      assertThrows(IllegalArgumentException.class, () -> recorder.record("/", GET_METHOD, 600, 1));
      assertEquals(
          "invalid HTTP elapsed time",
          assertThrows(
                  IllegalArgumentException.class, () -> recorder.record("/", GET_METHOD, 200, -1))
              .getMessage());
      assertEquals(0, duration(registry, "/").count());
      recorder.record("/", GET_METHOD, 100, 0);
      assertEquals(1.0, request(registry, "/", GET_METHOD, "1xx").count());
      assertEquals(0.0, duration(registry, "/").totalTime(TimeUnit.NANOSECONDS));
      recorder.record(LOGIN_PATH, GET_METHOD, 599, Long.MAX_VALUE);
      assertEquals(1.0, request(registry, LOGIN_PATH, GET_METHOD, "5xx").count());
      assertEquals(1, duration(registry, LOGIN_PATH).count());
      assertEquals(
          9_223_372_036_854_776_000.0,
          duration(registry, LOGIN_PATH).totalTime(TimeUnit.NANOSECONDS),
          1024.0);
    }
    try (var registry = new InspectingRegistry()) {
      var disabled = new HttpMetricRecorder(registry, "STANDARD");
      assertThrows(IllegalArgumentException.class, () -> disabled.record("/", GET_METHOD, 200, -1));
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void httpRec006ProviderFailuresAreNotNormalizedOrRetried() {
    var nested =
        new IllegalStateException(
            "owned fixture runtime", new AssertionError("owned fixture nested fatal"));
    for (Throwable failure : List.of(nested, new AssertionError("owned fixture fatal")))
      for (boolean counter : new boolean[] {false, true})
        try (var registry = new FaultRegistry(counter)) {
          var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
          registry.arm(failure);
          Throwable actual =
              assertThrows(
                  Throwable.class,
                  () -> recorder.record(LOGIN_PATH, GET_METHOD, 200, 1_000_000_000));
          assertSame(failure, actual);
          assertEquals(1, registry.attempts.get());
          assertEquals(
              counter ? 0.0 : 1.0,
              request(registry, LOGIN_PATH, GET_METHOD, SUCCESS_STATUS_LABEL).count());
          assertEquals(0, duration(registry, LOGIN_PATH).count());
          assertEquals(0, registry.closes.get());
          assertFalse(registry.isClosed());
        }
  }

  @Test
  void httpRec007ConcurrentActualProviderCounts() throws Exception {
    try (var registry = new InspectingRegistry()) {
      var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
      try (var executor = Executors.newFixedThreadPool(4)) {
        try {
          var tasks = new ArrayList<Callable<Boolean>>();
          for (int index = 0; index < 64; index++)
            tasks.add(
                () -> {
                  recorder.record(SEARCH_PATH, GET_METHOD, 200, 1_000_000_000);
                  return true;
                });
          for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
            assertTrue(future.get());
        } finally {
          executor.shutdownNow();
          assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
        }
      }
      assertEquals(64.0, request(registry, SEARCH_PATH, GET_METHOD, SUCCESS_STATUS_LABEL).count());
      assertEquals(64, duration(registry, SEARCH_PATH).count());
      assertEquals(64.0, duration(registry, SEARCH_PATH).totalTime(TimeUnit.SECONDS), 0.0);
    }
  }

  @Test
  void httpRec008BorrowedOwnerAndExternalMeterRemainUntouched() {
    var registry = new InspectingRegistry();
    try {
      var external = registry.counter("fixture.external");
      external.increment(7);
      var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
      recorder.record(LOGIN_PATH, "POST", 302, 1_000_000_000);
      assertEquals(7.0, external.count());
      assertSame(external, registry.get("fixture.external").counter());
      assertEquals(0, registry.closes.get());
      assertFalse(registry.isClosed());
    } finally {
      registry.close();
    }
    assertEquals(1, registry.closes.get());
    assertTrue(registry.isClosed());
  }

  @Test
  void httpRec009WrongTypeIsRejectedWithoutAlternativeIdentity() {
    for (boolean timer : new boolean[] {false, true})
      try (var registry = new InspectingRegistry()) {
        if (timer)
          Gauge.builder(DURATION_METRIC, () -> 1.0)
              .tags(SERVICE_LABEL, WEB_SERVICE_NAME, ROUTE_LABEL, "/")
              .register(registry);
        else
          Gauge.builder(REQUESTS, () -> 1.0)
              .tags(
                  SERVICE_LABEL,
                  WEB_SERVICE_NAME,
                  ROUTE_LABEL,
                  "/",
                  "method",
                  GET_METHOD,
                  "status_class",
                  "1xx")
              .register(registry);
        assertThrows(
            IllegalArgumentException.class, () -> new HttpMetricRecorder(registry, DEBUG_MODE));
        assertEquals(timer ? 1 : 11, registry.getMeters().size());
        assertFalse(registry.isClosed());
        assertEquals(0, registry.closes.get());
      }
  }

  @Test
  void httpRec010ExtremeRangeOrdersNeverWrapCumulativeTimerOrLoseSmallBuckets() {
    for (long[] values :
        List.of(
            new long[] {0, 1, Long.MAX_VALUE, Long.MAX_VALUE, 1},
            new long[] {Long.MAX_VALUE, Long.MAX_VALUE, 1, 0, 1})) {
      try (var registry = new InspectingRegistry()) {
        var recorder = new HttpMetricRecorder(registry, DEBUG_MODE);
        for (long value : values) recorder.record(SEARCH_PATH, GET_METHOD, 200, value);
        var metric = duration(registry, SEARCH_PATH);
        // Only self-owned literal-fixture numbers; never HTTP values, exception text or
        // identifiers.
        System.out.println(
            "HTTP_EXTREME_FIXTURE count="
                + metric.count()
                + ";sumSeconds="
                + metric.totalTime(TimeUnit.SECONDS)
                + ";maxSeconds="
                + metric.max(TimeUnit.SECONDS));
        assertEquals(5, metric.count());
        assertEquals(5, request(registry, SEARCH_PATH, GET_METHOD, SUCCESS_STATUS_LABEL).count());
        assertEquals(1.8446744073709553E10, metric.totalTime(TimeUnit.SECONDS));
        assertEquals(9.223372036854776E9, metric.max(TimeUnit.SECONDS));
        Map<Double, Double> counts = new HashMap<>();
        for (var bucket : metric.takeSnapshot().histogramCounts())
          counts.put(bucket.bucket(), bucket.count());
        assertEquals(
            Set.of(
                50000000.0,
                100000000.0,
                250000000.0,
                500000000.0,
                1000000000.0,
                1500000000.0,
                2000000000.0,
                2500000000.0,
                5000000000.0),
            counts.keySet());
        for (double boundary : BOUNDS) assertEquals(3.0, counts.get(boundary).doubleValue());
      }
    }
  }
}
