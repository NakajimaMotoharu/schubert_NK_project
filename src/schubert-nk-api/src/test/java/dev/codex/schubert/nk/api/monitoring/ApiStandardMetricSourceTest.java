package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS351/1808 APIHOST001..016; independent ownership counts and official own-JVM CPU oracle. */
class ApiStandardMetricSourceTest {
  @Test
  void apihost001StandardIsEntirelyLazyIncludingAfterClose() {
    var calls = new AtomicInteger();
    var owner =
        new ApiStandardMetricSource(
            () -> {
              calls.incrementAndGet();
              throw new AssertionError("unexpected acquire");
            },
            (source, gc) -> {
              throw new AssertionError("unexpected registration");
            });
    owner.bind("STANDARD");
    assertEquals("", owner.scrape("STANDARD"));
    owner.close();
    owner.bind("STANDARD");
    assertEquals("", owner.scrape("STANDARD"));
    assertEquals(0, calls.get());
    assertThrows(IllegalStateException.class, () -> owner.bind("DEBUG"));
  }

  @Test
  void apihost002DefaultUsesOfficialStandardTextAndFixedApiTag() {
    var owner = new ApiStandardMetricSource();
    try {
      owner.bind("DEBUG");
      String text = owner.scrape("DEBUG");
      String expected =
          "system_cpu_count{service=\"API\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      assertTrue(
          text.lines().anyMatch(expected::equals),
          "standard CPU count must equal the independent own JVM observation");
      assertTrue(text.contains("# TYPE system_cpu_count gauge\n"));
      assertTrue(text.contains("jvm_memory_used_bytes{"));
      assertFalse(text.contains("nk_http_"));
      assertEquals("", owner.scrape("STANDARD"));
    } finally {
      owner.close();
    }
    assertThrows(IllegalStateException.class, () -> owner.scrape("DEBUG"));
  }

  @Test
  void apihost003UnboundScrapeNeverAcquires() {
    var count = new AtomicInteger();
    var owner =
        new ApiStandardMetricSource(
            () -> {
              count.incrementAndGet();
              return new ProbeRegistry(new ArrayList<>());
            },
            (source, gc) -> {});
    assertThrows(IllegalStateException.class, () -> owner.scrape("DEBUG"));
    assertEquals("", owner.scrape("STANDARD"));
    assertEquals(0, count.get());
    owner.close();
  }

  @Test
  void apihost004NullAndUnknownModesFailBeforeAcquisition() {
    var count = new AtomicInteger();
    var owner =
        new ApiStandardMetricSource(
            () -> {
              count.incrementAndGet();
              return new ProbeRegistry(new ArrayList<>());
            },
            (source, gc) -> {});
    assertThrows(NullPointerException.class, () -> owner.bind(null));
    assertThrows(NullPointerException.class, () -> owner.scrape(null));
    assertEquals(
        "CONFIG_INVALID",
        assertThrows(IllegalArgumentException.class, () -> owner.bind("unknown")).getMessage());
    assertEquals(
        "CONFIG_INVALID",
        assertThrows(IllegalArgumentException.class, () -> owner.scrape("")).getMessage());
    assertEquals(0, count.get());
    owner.close();
  }

  @Test
  void apihost005ConstructorEstablishesNonNullPorts() {
    assertThrows(
        NullPointerException.class, () -> new ApiStandardMetricSource(null, (source, gc) -> {}));
    assertThrows(
        NullPointerException.class,
        () -> new ApiStandardMetricSource(() -> new ProbeRegistry(new ArrayList<>()), null));
  }

  @Test
  void apihost006FactoryRuntimeIdentityAndNoAutomaticRetry() {
    var failure = new IllegalArgumentException("factory fixture");
    var calls = new AtomicInteger();
    var owner =
        new ApiStandardMetricSource(
            () -> {
              calls.incrementAndGet();
              throw failure;
            },
            (source, gc) -> {});
    assertSame(failure, assertThrows(IllegalArgumentException.class, () -> owner.bind("DEBUG")));
    assertThrows(IllegalStateException.class, () -> owner.bind("DEBUG"));
    assertThrows(IllegalStateException.class, () -> owner.scrape("DEBUG"));
    assertEquals(1, calls.get());
    owner.close();
  }

  @Test
  void apihost007FactoryErrorIdentityIsNotNormalized() {
    var failure = new AssertionError("factory fatal fixture");
    var owner =
        new ApiStandardMetricSource(
            () -> {
              throw failure;
            },
            (source, gc) -> {});
    assertSame(failure, assertThrows(AssertionError.class, () -> owner.bind("DEBUG")));
    assertThrows(IllegalStateException.class, () -> owner.bind("DEBUG"));
    owner.close();
  }

  @Test
  void apihost008NullFactoryResultIsNotSuccess() {
    var owner =
        new ApiStandardMetricSource(
            () -> null,
            (source, gc) -> {
              throw new AssertionError("unexpected registrar");
            });
    assertThrows(NullPointerException.class, () -> owner.bind("DEBUG"));
    assertThrows(IllegalStateException.class, () -> owner.scrape("DEBUG"));
    owner.close();
  }

  @Test
  void apihost009ClosedCandidateIsRejectedAndRetainedUntilCallerClose() {
    var source = new ProbeRegistry(new ArrayList<>());
    source.close();
    var owner =
        new ApiStandardMetricSource(
            () -> source,
            (value, gc) -> {
              throw new AssertionError("unexpected registrar");
            });
    assertThrows(IllegalStateException.class, () -> owner.bind("DEBUG"));
    assertEquals(1, source.closes);
    owner.close();
    assertEquals(2, source.closes);
  }

  @Test
  void apihost010PartialRegistryBeforeGcRemainsOwnedAfterFailure() {
    var source = new ProbeRegistry(new ArrayList<>());
    var failure = new IllegalArgumentException("registration fixture");
    var owner =
        new ApiStandardMetricSource(
            () -> source,
            (value, gc) -> {
              throw failure;
            });
    assertSame(failure, assertThrows(IllegalArgumentException.class, () -> owner.bind("DEBUG")));
    assertFalse(source.isClosed());
    assertThrows(IllegalStateException.class, () -> owner.scrape("DEBUG"));
    owner.close();
    assertEquals(1, source.closes);
  }

  @Test
  void apihost011GcRetainedBeforeFatalAndClosedInReverseOrder() {
    var order = new ArrayList<String>();
    var source = new ProbeRegistry(order);
    var gc = new ProbeGc(order);
    var failure = new AssertionError("post-owner fixture");
    var owner =
        new ApiStandardMetricSource(
            () -> source,
            (value, ack) -> {
              assertTrue(ack.test(gc));
              throw failure;
            });
    assertSame(failure, assertThrows(AssertionError.class, () -> owner.bind("DEBUG")));
    assertEquals(List.of(), order);
    owner.close();
    owner.close();
    assertEquals(List.of("gc", "registry"), order);
  }

  @Test
  void apihost012FailedGcCloseKeepsRegistryAndExplicitRetryOwnership() {
    var order = new ArrayList<String>();
    var source = new ProbeRegistry(order);
    var gc = new ProbeGc(order);
    var failure = new IllegalStateException("GC close fixture");
    gc.failure = Optional.of(failure);
    var owner = new ApiStandardMetricSource(() -> source, (value, ack) -> assertTrue(ack.test(gc)));
    owner.bind("DEBUG");
    assertSame(failure, assertThrows(IllegalStateException.class, owner::close));
    assertFalse(source.isClosed());
    assertEquals(List.of("gc"), order);
    gc.failure = Optional.empty();
    owner.close();
    assertEquals(List.of("gc", "gc", "registry"), order);
    assertTrue(source.isClosed());
  }

  @Test
  void apihost013FailedRegistryCloseIsNotConfirmedAndCanBeExplicitlyRetried() {
    var source = new ProbeRegistry(new ArrayList<>());
    var failure = new IllegalStateException("registry close fixture");
    source.failure = Optional.of(failure);
    var owner = new ApiStandardMetricSource(() -> source, (value, ack) -> {});
    owner.bind("DEBUG");
    assertSame(failure, assertThrows(IllegalStateException.class, owner::close));
    assertFalse(source.isClosed());
    source.failure = Optional.empty();
    owner.close();
    owner.close();
    assertTrue(source.isClosed());
    assertEquals(2, source.closes);
  }

  @Test
  void apihost014NullGcCallbackFailsWithoutImplicitRegistryClose() {
    var source = new ProbeRegistry(new ArrayList<>());
    var owner = new ApiStandardMetricSource(() -> source, (value, ack) -> ack.test(null));
    assertThrows(NullPointerException.class, () -> owner.bind("DEBUG"));
    assertFalse(source.isClosed());
    assertThrows(IllegalStateException.class, () -> owner.scrape("DEBUG"));
    owner.close();
    assertTrue(source.isClosed());
  }

  @Test
  void apihost015SingleBindAndIdempotentClose() {
    var source = new ProbeRegistry(new ArrayList<>());
    var calls = new AtomicInteger();
    var owner = new ApiStandardMetricSource(() -> source, (value, ack) -> calls.incrementAndGet());
    owner.bind("DEBUG");
    assertEquals("standard", owner.scrape("DEBUG"));
    assertThrows(IllegalStateException.class, () -> owner.bind("DEBUG"));
    owner.bind("STANDARD");
    owner.close();
    owner.close();
    assertEquals(1, calls.get());
    assertEquals(1, source.closes);
  }

  @Test
  void apihost016CloseWaitsForOwnedScrapeAndThenRejectsNewScrapes() throws Exception {
    var source = new ProbeRegistry(new ArrayList<>());
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    source.entered = Optional.of(entered);
    source.release = Optional.of(release);
    var owner = new ApiStandardMetricSource(() -> source, (value, ack) -> {});
    owner.bind("DEBUG");
    var executor = Executors.newFixedThreadPool(2);
    try {
      var scrape = executor.submit(() -> owner.scrape("DEBUG"));
      assertTrue(entered.await(10, TimeUnit.SECONDS));
      var attemptedClose = new CountDownLatch(1);
      var close =
          executor.submit(
              () -> {
                attemptedClose.countDown();
                owner.close();
              });
      assertTrue(attemptedClose.await(10, TimeUnit.SECONDS));
      assertFalse(source.isClosed());
      release.countDown();
      assertEquals("standard", scrape.get(10, TimeUnit.SECONDS));
      close.get(10, TimeUnit.SECONDS);
      assertTrue(source.isClosed());
      assertThrows(IllegalStateException.class, () -> owner.scrape("DEBUG"));
    } finally {
      release.countDown();
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      owner.close();
    }
  }

  private static final class ProbeRegistry extends PrometheusMeterRegistry {
    private final List<String> order;
    private Optional<RuntimeException> failure = Optional.empty();
    private Optional<CountDownLatch> entered = Optional.empty();
    private Optional<CountDownLatch> release = Optional.empty();
    private int closes;

    ProbeRegistry(List<String> order) {
      super(PrometheusConfig.DEFAULT);
      this.order = order;
    }

    @Override
    public String scrape() {
      entered.ifPresent(CountDownLatch::countDown);
      if (release.isPresent()) {
        try {
          assertTrue(release.orElseThrow().await(10, TimeUnit.SECONDS));
        } catch (InterruptedException interrupted) {
          Thread.currentThread().interrupt();
          throw new IllegalStateException("owned test interrupted");
        }
      }
      return "standard";
    }

    @Override
    public void close() {
      order.add("registry");
      closes++;
      if (failure.isPresent()) throw failure.orElseThrow();
      super.close();
    }
  }

  private static final class ProbeGc extends JvmGcMetrics {
    private final List<String> order;
    private Optional<RuntimeException> failure = Optional.empty();

    ProbeGc(List<String> order) {
      this.order = order;
    }

    @Override
    public void close() {
      order.add("gc");
      if (failure.isPresent()) throw failure.orElseThrow();
      super.close();
    }
  }
}
