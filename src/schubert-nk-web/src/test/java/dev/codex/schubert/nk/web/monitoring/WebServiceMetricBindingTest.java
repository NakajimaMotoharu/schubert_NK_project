package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.web.logging.WebRequestTrace;
import dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricObservationTest.Fixture;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.catalina.connector.Connector;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.valves.ValveBase;
import org.junit.jupiter.api.Test;

/** 1835 WEBSERVICE001..014: own unstarted requests/SDK only, never a server/DB/native startup. */
final class WebServiceMetricBindingTest {
  static final String REQUEST_ONE =
      "nk_http_requests_total{method=\"GET\",route=\"/login\",service=\"WEB\",status_class=\"2xx\"} 1.0\n";
  static final String REQUEST_ZERO =
      "nk_http_requests_total{method=\"GET\",route=\"/login\",service=\"WEB\",status_class=\"2xx\"} 0.0\n";

  static Fixture fixture() {
    var value = new Fixture();
    value.active = 1;
    value.idle = 1;
    value.pending = 0;
    value.maximum = 2;
    return value;
  }

  static Request request() {
    var coyote = new org.apache.coyote.Request();
    coyote.setMethod("GET");
    coyote.requestURI().setString("/fixture");
    var request = new Request(new Connector(), coyote);
    WebRequestTrace.ensure(request, () -> new UUID(1, 2)).captureRoute("/login");
    return request;
  }

  static Response response() {
    var coyote = new org.apache.coyote.Response();
    coyote.setStatus(200);
    return new Response(coyote);
  }

  static HttpMetricValve observer(WebServiceMetricBinding binding) {
    var valve = binding.httpValve();
    valve.setNext(
        new ValveBase(true) {
          @Override
          public void invoke(Request request, Response response) {}
        });
    return valve;
  }

  static void recordOne(WebServiceMetricBinding binding) throws Exception {
    var request = request();
    var response = response();
    var valve = observer(binding);
    valve.invoke(request, response);
    valve.log(request, response, 250_000_000);
    valve.log(request, response, 900_000_000);
    assertEquals(200, response.getStatus());
    assertEquals(0, response.getCoyoteResponse().getContentWritten());
  }

  private static WebMetricContext<WebServiceMetricBinding> prepared(Fixture f, Runnable terminal) {
    return WebServiceMetricBinding.prepareContext("DEBUG", f::pool, f::config, terminal);
  }

  @Test
  void webservice001ConstructorBoundariesRejectWithoutGetterOrInvalidModeSeries() {
    var f = fixture();
    try (var registry = new OverflowSafeHttpMeterRegistry()) {
      assertThrows(
          NullPointerException.class,
          () -> new WebServiceMetricBinding(null, f.config(), registry, "DEBUG", () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new WebServiceMetricBinding(f.pool(), null, registry, "DEBUG", () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new WebServiceMetricBinding(f.pool(), f.config(), null, "DEBUG", () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new WebServiceMetricBinding(f.pool(), f.config(), registry, null, () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new WebServiceMetricBinding(f.pool(), f.config(), registry, "DEBUG", null));
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebServiceMetricBinding(f.pool(), f.config(), registry, "debug", () -> {}));
      assertTrue(f.calls.isEmpty());
      assertTrue(registry.getMeters().isEmpty());
    }
  }

  @Test
  void webservice002FactoryRejectsNullReferencesAndModeBeforeAcquisition() {
    var f = fixture();
    var reads = new AtomicInteger();
    java.util.function.Supplier<com.zaxxer.hikari.HikariPoolMXBean> pool =
        () -> {
          reads.incrementAndGet();
          return f.pool();
        };
    assertThrows(
        NullPointerException.class,
        () -> WebServiceMetricBinding.prepareContext("DEBUG", null, f::config, () -> {}));
    assertThrows(
        NullPointerException.class,
        () -> WebServiceMetricBinding.prepareContext("DEBUG", pool, null, () -> {}));
    assertThrows(
        NullPointerException.class,
        () -> WebServiceMetricBinding.prepareContext("DEBUG", pool, f::config, null));
    assertThrows(
        NullPointerException.class,
        () -> WebServiceMetricBinding.prepareContext(null, pool, f::config, () -> {}));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebServiceMetricBinding.prepareContext("unknown", pool, f::config, () -> {}));
    assertEquals(0, reads.get());
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void webservice003StandardFactoryDoesNotReadAnyDetailedSupplierOrCreateObserver() {
    try (var context =
        WebServiceMetricBinding.prepareContext(
            "STANDARD",
            () -> {
              throw new AssertionError("pool unreached");
            },
            () -> {
              throw new AssertionError("config unreached");
            },
            () -> {
              throw new AssertionError("terminal unreached");
            })) {
      context.initialize();
      assertTrue(context.bindings().isEmpty());
      assertEquals(
          "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready 1\n", context.render(true));
    }
  }

  @Test
  void webservice004DebugCapturesOwnerBeforeSetupThenDefersStatisticsUntilRender() {
    var f = fixture();
    var order = new ArrayList<String>();
    var owner = new AtomicReference<WebMetricContext<WebServiceMetricBinding>>();
    try (var context =
        WebServiceMetricBinding.prepareContext(
            "DEBUG",
            () -> {
              assertNotNull(owner.get());
              order.add("pool");
              return f.pool();
            },
            () -> {
              assertNotNull(owner.get());
              order.add("config");
              return f.config();
            },
            () -> {})) {
      owner.set(context);
      assertTrue(order.isEmpty());
      context.initialize();
      assertEquals(List.of("pool", "config"), order);
      assertTrue(f.calls.isEmpty());
      var binding = context.bindings().orElseThrow();
      assertSame(binding, context.bindings().orElseThrow());
      String body = context.render(true);
      assertTrue(body.contains("nk_db_pool_connections{service=\"WEB\",state=\"active\"} 1.0\n"));
      assertTrue(body.contains("nk_db_pool_connections{service=\"WEB\",state=\"max\"} 2.0\n"));
      assertTrue(body.contains(REQUEST_ZERO));
      f.complete();
      assertEquals(List.of("pool", "config"), order);
    }
  }

  @Test
  void webservice005BorrowedValveIsRetainedAndRefreshReadsOnlyFourStatistics() {
    var f = fixture();
    try (var registry = new OverflowSafeHttpMeterRegistry()) {
      var binding = new WebServiceMetricBinding(f.pool(), f.config(), registry, "DEBUG", () -> {});
      assertSame(binding.httpValve(), binding.httpValve());
      assertTrue(f.calls.isEmpty());
      binding.refresh();
      f.complete();
      assertFalse(registry.isClosed());
      assertEquals(
          1.0,
          registry
              .get("nk_db_pool_connections")
              .tags("service", "WEB", "state", "active")
              .gauge()
              .value());
    }
  }

  @Test
  void webservice006StandaloneStandardObserverNeverCreatesDetailedSeries() throws Exception {
    var f = fixture();
    var signal = new AtomicInteger();
    try (var registry = new OverflowSafeHttpMeterRegistry()) {
      var binding =
          new WebServiceMetricBinding(
              f.pool(), f.config(), registry, "STANDARD", signal::incrementAndGet);
      binding.refresh();
      recordOne(binding);
      assertTrue(registry.getMeters().isEmpty());
      assertTrue(f.calls.isEmpty());
      assertEquals(0, signal.get());
    }
  }

  @Test
  void webservice007TerminalIsRecordedOnceInSameCustomPayloadAsDatabase() throws Exception {
    var f = fixture();
    var signal = new AtomicInteger();
    try (var context = prepared(f, signal::incrementAndGet)) {
      context.initialize();
      recordOne(context.bindings().orElseThrow());
      String body = context.render(true);
      assertTrue(body.contains(REQUEST_ONE));
      assertTrue(
          body.contains(
              "nk_http_request_duration_seconds_count{route=\"/login\",service=\"WEB\"} 1\n"));
      assertTrue(
          body.contains(
              "nk_http_request_duration_seconds_sum{route=\"/login\",service=\"WEB\"} 0.25\n"));
      assertTrue(body.contains("nk_db_pool_connections{service=\"WEB\",state=\"max\"} 2.0\n"));
      assertEquals(0, signal.get());
      f.complete();
    }
  }

  @Test
  void webservice008RedispatchAndConcurrentTerminalRetainRequestOwnedClaim() throws Exception {
    var f = fixture();
    try (var context = prepared(f, () -> {});
        var workers = Executors.newFixedThreadPool(4)) {
      context.initialize();
      var valve = observer(context.bindings().orElseThrow());
      var request = request();
      var response = response();
      valve.invoke(request, response);
      valve.invoke(request, response);
      var jobs = new ArrayList<java.util.concurrent.Future<?>>();
      for (int i = 0; i < 16; i++)
        jobs.add(workers.submit(() -> valve.log(request, response, 250_000_000)));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertTrue(context.render(true).contains(REQUEST_ONE));
      var other = request();
      valve.invoke(other, response);
      valve.log(other, response, 0);
      assertTrue(context.render(true).contains(REQUEST_ONE.replace("1.0\n", "2.0\n")));
    }
  }

  @Test
  void webservice009MissingTerminalMetadataSignalsOwnerWithoutSuccessSample() {
    var f = fixture();
    var signal = new AtomicInteger();
    try (var context = prepared(f, signal::incrementAndGet)) {
      context.initialize();
      var valve = context.bindings().orElseThrow().httpValve();
      valve.log(null, response(), 1);
      valve.log(request(), null, 1);
      valve.log(request(), response(), -1);
      assertEquals(3, signal.get());
      assertTrue(context.render(false).contains(REQUEST_ZERO));
    }
  }

  @Test
  void webservice010PoolSupplierFailureOrNullNeverAcquiresConfigurationOrRetries() {
    for (int kind = 0; kind < 3; kind++) {
      final int selected = kind;
      var runtime = new IllegalStateException("pool fixture");
      var fatal = new AssertionError("pool fatal fixture");
      var reads = new AtomicInteger();
      try (var context =
          WebServiceMetricBinding.prepareContext(
              "DEBUG",
              () -> {
                reads.incrementAndGet();
                if (selected == 0) throw runtime;
                if (selected == 1) throw fatal;
                return null;
              },
              () -> {
                throw new AssertionError("config unreached");
              },
              () -> {})) {
        if (selected == 0)
          assertSame(runtime, assertThrows(IllegalStateException.class, context::initialize));
        else if (selected == 1)
          assertSame(fatal, assertThrows(AssertionError.class, context::initialize));
        else assertThrows(NullPointerException.class, context::initialize);
        assertThrows(IllegalStateException.class, context::initialize);
        assertThrows(IllegalStateException.class, context::bindings);
        assertEquals(1, reads.get());
      }
    }
  }

  @Test
  void webservice011ConfigurationSupplierFailureOrNullRetainsOriginalPrimaryAndPartialOwner() {
    for (int kind = 0; kind < 3; kind++) {
      final int selected = kind;
      var f = fixture();
      var order = new ArrayList<String>();
      var runtime = new IllegalArgumentException("config fixture");
      var fatal = new AssertionError("config fatal fixture");
      try (var context =
          WebServiceMetricBinding.prepareContext(
              "DEBUG",
              () -> {
                order.add("pool");
                return f.pool();
              },
              () -> {
                order.add("config");
                if (selected == 0) throw runtime;
                if (selected == 1) throw fatal;
                return null;
              },
              () -> {})) {
        if (selected == 0)
          assertSame(runtime, assertThrows(IllegalArgumentException.class, context::initialize));
        else if (selected == 1)
          assertSame(fatal, assertThrows(AssertionError.class, context::initialize));
        else assertThrows(NullPointerException.class, context::initialize);
        assertEquals(List.of("pool", "config"), order);
        assertTrue(f.calls.isEmpty());
        assertThrows(IllegalStateException.class, context::initialize);
      }
    }
  }

  @Test
  void webservice012DatabaseFailureNeverReturnsPartialTextOrReplaysHttpSuccess() throws Exception {
    var f = fixture();
    var primary = new IllegalStateException("getter fixture");
    try (var context = prepared(f, () -> {})) {
      context.initialize();
      recordOne(context.bindings().orElseThrow());
      f.faults.put("active", primary);
      assertSame(primary, assertThrows(IllegalStateException.class, () -> context.render(true)));
      assertEquals(List.of("active"), f.calls);
      f.faults.clear();
      f.calls.clear();
      assertTrue(context.render(true).contains(REQUEST_ONE));
      f.complete();
    }
  }

  @Test
  void webservice013TerminalSignalFailureIsOriginalAndDoesNotTransferOwnership() {
    var f = fixture();
    var primary = new AssertionError("owner terminal fixture");
    try (var context =
        prepared(
            f,
            () -> {
              throw primary;
            })) {
      context.initialize();
      var valve = context.bindings().orElseThrow().httpValve();
      assertSame(primary, assertThrows(AssertionError.class, () -> valve.log(null, null, 1)));
      assertTrue(context.render(false).contains(REQUEST_ZERO));
    }
  }

  @Test
  void webservice014QuiescentContextCloseReleasesOnlyOwnedSdkAndRejectsNewAccess() {
    var f = fixture();
    var registry = new AtomicReference<MeterRegistry>();
    var context =
        new WebMetricContext<WebServiceMetricBinding>(
            "DEBUG",
            source -> {
              registry.set(source);
              return new WebServiceMetricBinding(f.pool(), f.config(), source, "DEBUG", () -> {});
            },
            WebServiceMetricBinding::refresh);
    try {
      context.initialize();
      context.render(true);
      f.complete();
      f.calls.clear();
      assertFalse(registry.get().isClosed());
      context.close();
      assertTrue(registry.get().isClosed());
      assertTrue(f.calls.isEmpty());
      assertThrows(IllegalStateException.class, context::bindings);
      assertThrows(IllegalStateException.class, () -> context.render(true));
    } finally {
      context.close();
    }
  }
}
