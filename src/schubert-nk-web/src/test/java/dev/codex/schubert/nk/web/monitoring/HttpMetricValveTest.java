package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.logging.WebRequestTrace;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.distribution.pause.PauseDetector;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import jakarta.servlet.ServletException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.catalina.connector.Connector;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.valves.ValveBase;
import org.junit.jupiter.api.Test;

/** Unstarted owned Tomcat objects, actual Micrometer; no HTTP/socket/DB/Root. Spec1577. */
class HttpMetricValveTest {
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_LOGIN_F843C044 = "/login";
  private static final String FIXTURE_ROUTE_E050EFD0 = "route";
  private static final String FIXTURE_SUPPRESSION_DISABLED_BC2139ED = "suppression-disabled";
  private static final String ATTRIBUTE = HttpMetricValve.class.getName();
  private static final String REQUESTS = "nk_http_requests_total";
  private static final String DURATION = "nk_http_request_duration_seconds";

  private static class OwnedRegistry extends SimpleMeterRegistry
      implements AutoCloseable, OverflowSafeDurationSupport {
    final AtomicInteger closes = new AtomicInteger();

    OwnedRegistry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    @Override
    protected Timer newTimer(Meter.Id id, DistributionStatisticConfig config, PauseDetector pause) {
      return OverflowSafeHttpMeterRegistry.durationTimer(
          this, config, pause, () -> super.newTimer(id, config, pause));
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static final class FaultRegistry extends OwnedRegistry {
    Optional<Throwable> fault = Optional.empty();
    final AtomicInteger attempts = new AtomicInteger();
    boolean timerFailure;

    private void inject() {
      attempts.incrementAndGet();
      if (fault.isEmpty()) return;
      Throwable failure = fault.orElseThrow();
      if (failure instanceof Error fatal) throw fatal;
      throw (RuntimeException) failure;
    }

    @Override
    protected Counter newCounter(Meter.Id id) {
      var delegate = super.newCounter(id);
      return new Counter() {
        @Override
        public void increment(double amount) {
          if (!timerFailure) inject();
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
      return (Timer)
          Proxy.newProxyInstance(
              Timer.class.getClassLoader(),
              new Class<?>[] {Timer.class},
              (instance, method, args) -> {
                if (timerFailure && method.getName().equals("record")) inject();
                try {
                  return method.invoke(delegate, args);
                } catch (InvocationTargetException wrapped) {
                  throw wrapped.getCause();
                }
              });
    }
  }

  private static final class UnformattableFailure extends IllegalStateException {
    private static final long serialVersionUID = 1L;

    @Override
    public String getMessage() {
      throw new AssertionError("must not read provider text");
    }

    @Override
    public String toString() {
      throw new AssertionError("must not format provider");
    }
  }

  private static final class SuppressionDisabledFailure extends RuntimeException {
    private static final long serialVersionUID = 1L;

    SuppressionDisabledFailure() {
      super(null, null, false, false);
    }
  }

  private static Request request(String method, String route) {
    var coyote = new org.apache.coyote.Request();
    coyote.setMethod(method);
    coyote.requestURI().setString("/synthetic-unknown?private-canary");
    var request = new Request(new Connector(), coyote);
    WebRequestTrace.ensure(request, () -> new UUID(1, 2)).captureRoute(route);
    return request;
  }

  private static Response response(int status) {
    var coyote = new org.apache.coyote.Response();
    coyote.setStatus(status);
    return new Response(coyote);
  }

  private static HttpMetricValve valve(OwnedRegistry registry, Runnable signal) {
    var valve = new HttpMetricValve(new HttpMetricRecorder(registry, "DEBUG"), signal);
    valve.setNext(
        new ValveBase(true) {
          @Override
          public void invoke(Request request, Response response) {}
        });
    return valve;
  }

  private static long total(OwnedRegistry registry) {
    return (long) registry.find(REQUESTS).counters().stream().mapToDouble(Counter::count).sum();
  }

  @Test
  void httpTerm001RealTerminalRecordsOnceWithoutHttpMutation() throws Exception {
    var signal = new AtomicInteger();
    var registry = new OwnedRegistry();
    try (registry) {
      var valve = valve(registry, signal::incrementAndGet);
      var request = request(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044);
      var response = response(200);
      valve.invoke(request, response);
      assertEquals(0, total(registry));
      valve.log(request, response, 250_000_000);
      valve.log(request, response, 900_000_000);
      assertEquals(1, total(registry));
      assertEquals(
          1,
          registry
              .get(REQUESTS)
              .tags(
                  FIXTURE_ROUTE_E050EFD0,
                  FIXTURE_LOGIN_F843C044,
                  "method",
                  FIXTURE_GET_04F32A7E,
                  "status_class",
                  "2xx")
              .counter()
              .count());
      var timer =
          registry.get(DURATION).tag(FIXTURE_ROUTE_E050EFD0, FIXTURE_LOGIN_F843C044).timer();
      assertEquals(1, timer.count());
      assertEquals(250_000_000, timer.totalTime(TimeUnit.NANOSECONDS));
      assertEquals(200, response.getStatus());
      assertEquals(0, response.getCoyoteResponse().getContentWritten());
      assertEquals(0, signal.get());
      assertEquals(0, registry.closes.get());
    }
    assertEquals(1, registry.closes.get());
  }

  @Test
  void httpTerm002RedispatchAndConcurrentTerminalAreRequestOwned() throws Exception {
    try (var registry = new OwnedRegistry();
        var pool = Executors.newFixedThreadPool(8)) {
      var signal = new AtomicInteger();
      var valve = valve(registry, signal::incrementAndGet);
      var request = request("POST", FIXTURE_LOGIN_F843C044);
      var response = response(202);
      valve.invoke(request, response);
      valve.invoke(request, response);
      var jobs =
          java.util.stream.IntStream.range(0, 64)
              .<Callable<Void>>mapToObj(
                  i ->
                      () -> {
                        valve.log(request, response, 1);
                        return null;
                      })
              .toList();
      for (var result : pool.invokeAll(jobs)) result.get();
      assertEquals(1, total(registry));
      var other = request("POST", FIXTURE_LOGIN_F843C044);
      valve.invoke(other, response);
      valve.log(other, response, 0);
      assertEquals(2, total(registry));
      assertEquals(0, signal.get());
    }
  }

  @Test
  void httpTerm003UnknownAndFinalStatusNeverUseRawUriOrDispatchResult() throws Exception {
    try (var registry = new OwnedRegistry()) {
      var signal = new AtomicInteger();
      var valve = valve(registry, signal::incrementAndGet);
      int[] statuses = {100, 302, 403, 599};
      long[] times = {0, 1, 1_000_000_000, Long.MAX_VALUE};
      for (int i = 0; i < statuses.length; i++) {
        var request = request("private-canary", "/not-registered?private-canary");
        var response = response(statuses[i]);
        valve.invoke(request, response);
        valve.log(request, response, times[i]);
        assertEquals(
            1,
            registry
                .get(REQUESTS)
                .tags(
                    FIXTURE_ROUTE_E050EFD0,
                    "/**",
                    "method",
                    "OTHER",
                    "status_class",
                    (statuses[i] / 100) + "xx")
                .counter()
                .count());
      }
      assertEquals(4, total(registry));
      assertEquals(4, registry.get(DURATION).tag(FIXTURE_ROUTE_E050EFD0, "/**").timer().count());
      assertEquals(0, signal.get());
      for (var meter : registry.getMeters())
        assertFalse(meter.getId().toString().contains("canary"));
    }
  }

  @Test
  void httpTerm004InvalidMissingAndNullObservationsAreNotSuccessful() throws Exception {
    try (var registry = new OwnedRegistry()) {
      var signal = new AtomicInteger();
      var valve = valve(registry, signal::incrementAndGet);
      valve.log(null, null, 0);
      valve.log(request(FIXTURE_GET_04F32A7E, "/"), null, 0);
      valve.log(request(FIXTURE_GET_04F32A7E, "/"), response(200), 0);
      var wrong = request(FIXTURE_GET_04F32A7E, "/");
      wrong.setAttribute(ATTRIBUTE, "not-owned");
      valve.log(wrong, response(200), 0);
      for (int invalid = 0; invalid < 5; invalid++) {
        var request =
            invalid == 1
                ? new Request(new Connector(), new org.apache.coyote.Request())
                : request(FIXTURE_GET_04F32A7E, "/");
        if (invalid == 1) WebRequestTrace.ensure(request, () -> new UUID(1, 2));
        var response = response(invalid == 2 ? 99 : invalid == 3 ? 600 : 200);
        valve.invoke(request, response);
        if (invalid == 0) request.removeAttribute(WebRequestTrace.class.getName());
        valve.log(request, response, invalid == 4 ? -1 : 0);
        valve.log(request, response, 0);
      }
      assertEquals(9, signal.get());
      assertEquals(0, total(registry));
    }
  }

  @Test
  void httpTerm005MetadataFailuresAndSignalAreSeparated() throws Exception {
    try (var registry = new OwnedRegistry()) {
      var signal = new AtomicInteger();
      var valve = valve(registry, signal::incrementAndGet);
      for (RuntimeException failure :
          List.of(new IllegalArgumentException(), new IllegalStateException())) {
        var request =
            new Request(new Connector(), new org.apache.coyote.Request()) {
              @Override
              public Object getAttribute(String name) {
                throw failure;
              }
            };
        valve.log(request, response(200), 0);
      }
      var request = request(FIXTURE_GET_04F32A7E, "/");
      valve.invoke(request, response(200));
      request.setAttribute(WebRequestTrace.class.getName(), "not-a-trace");
      valve.log(request, response(200), 0);
      assertEquals(3, signal.get());
      assertEquals(0, total(registry));
      for (RuntimeException signalFailure :
          List.of(new IllegalArgumentException(), new IllegalStateException())) {
        var called = new AtomicInteger();
        var failing =
            valve(
                registry,
                () -> {
                  called.incrementAndGet();
                  throw signalFailure;
                });
        var denied =
            assertThrows(
                IllegalStateException.class,
                () -> failing.log(request(FIXTURE_GET_04F32A7E, "/"), response(200), 0));
        assertEquals("HTTP metric terminal signal failed", denied.getMessage());
        assertEquals(1, called.get());
      }
    }
  }

  @Test
  void httpTerm006ProviderFailureIsNotRetriedOrFormatted() throws Exception {
    for (boolean timerFailure : List.of(false, true))
      for (Throwable failure :
          List.of(new IllegalStateException(), new AssertionError(), new UnformattableFailure())) {
        try (var registry = new FaultRegistry()) {
          registry.timerFailure = timerFailure;
          var called = new AtomicInteger();
          var valve = valve(registry, called::incrementAndGet);
          var request = request(FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044);
          var response = response(200);
          valve.invoke(request, response);
          registry.fault = Optional.of(failure);
          assertSame(
              failure, assertThrows(failure.getClass(), () -> valve.log(request, response, 1)));
          valve.log(request, response, 1);
          assertEquals(1, called.get());
          assertEquals(1, registry.attempts.get());
          assertEquals(timerFailure ? 1 : 0, total(registry));
          assertEquals(
              0,
              registry
                  .get(DURATION)
                  .tag(FIXTURE_ROUTE_E050EFD0, FIXTURE_LOGIN_F843C044)
                  .timer()
                  .count());
          assertEquals(0, registry.closes.get());
          assertEquals(200, response.getStatus());
        }
      }
  }

  @Test
  void httpTerm007SignalAndCyclicFatalGraphsKeepFatalIdentity() throws Exception {
    for (String mode :
        List.of("ordinary", "fatal", "same", "cycle", FIXTURE_SUPPRESSION_DISABLED_BC2139ED)) {
      try (var registry = new FaultRegistry()) {
        var called = new AtomicInteger();
        RuntimeException primary =
            mode.equals(FIXTURE_SUPPRESSION_DISABLED_BC2139ED)
                ? new SuppressionDisabledFailure()
                : new IllegalArgumentException();
        var fatal = new AssertionError();
        Throwable secondary =
            mode.equals("fatal") || mode.equals(FIXTURE_SUPPRESSION_DISABLED_BC2139ED)
                ? fatal
                : mode.equals("same") ? primary : new IllegalStateException();
        if (mode.equals("cycle")) {
          var linked = new IllegalStateException();
          primary.initCause(linked);
          linked.initCause(primary);
          linked.addSuppressed(fatal);
        }
        registry.fault = Optional.of(primary);
        var valve =
            valve(
                registry,
                () -> {
                  called.incrementAndGet();
                  if (secondary instanceof Error error) throw error;
                  throw (RuntimeException) secondary;
                });
        var request = request(FIXTURE_GET_04F32A7E, "/");
        var response = response(200);
        valve.invoke(request, response);
        Throwable expected =
            mode.equals("fatal")
                    || mode.equals("cycle")
                    || mode.equals(FIXTURE_SUPPRESSION_DISABLED_BC2139ED)
                ? fatal
                : primary;
        assertSame(
            expected, assertThrows(expected.getClass(), () -> valve.log(request, response, 0)));
        valve.log(request, response, 0);
        assertEquals(1, called.get());
        assertEquals(1, registry.attempts.get());
        assertEquals(
            mode.equals("same") || mode.equals(FIXTURE_SUPPRESSION_DISABLED_BC2139ED) ? 0 : 1,
            primary.getSuppressed().length);
      }
    }
  }

  @Test
  void httpTerm008BoundaryAndDownstreamOwnershipStayUnchanged() throws Exception {
    try (var registry = new OwnedRegistry()) {
      var recorder = new HttpMetricRecorder(registry, "STANDARD");
      assertThrows(NullPointerException.class, () -> new HttpMetricValve(null, () -> {}));
      assertThrows(NullPointerException.class, () -> new HttpMetricValve(recorder, null));
      var valve = new HttpMetricValve(recorder, () -> {});
      var request = request(FIXTURE_GET_04F32A7E, "/");
      var response = response(200);
      assertThrows(NullPointerException.class, () -> valve.invoke(null, response));
      assertThrows(NullPointerException.class, () -> valve.invoke(request, null));
      assertThrows(NullPointerException.class, () -> valve.invoke(request, response));
      request.setAttribute(ATTRIBUTE, "foreign");
      assertThrows(IllegalStateException.class, () -> valve.invoke(request, response));
      request.removeAttribute(ATTRIBUTE);
      var downstream = new IOException();
      valve.setNext(
          new ValveBase(true) {
            @Override
            public void invoke(Request req, Response res) throws IOException, ServletException {
              throw downstream;
            }
          });
      assertSame(
          downstream, assertThrows(IOException.class, () -> valve.invoke(request, response)));
      assertEquals(0, registry.getMeters().size());
      assertFalse(valve.getRequestAttributesEnabled());
      valve.setRequestAttributesEnabled(false);
      assertThrows(IllegalArgumentException.class, () -> valve.setRequestAttributesEnabled(true));
      assertTrue(valve.isAsyncSupported());
    }
  }
}
