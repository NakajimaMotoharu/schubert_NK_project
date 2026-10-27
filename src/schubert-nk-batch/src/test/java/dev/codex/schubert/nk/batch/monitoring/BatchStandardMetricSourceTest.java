package dev.codex.schubert.nk.batch.monitoring;

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

/** SS351/1810 BATCHHOST001..016; independent ownership counts and official own-JVM CPU oracle. */
class BatchStandardMetricSourceTest {
  private static final String STANDARD_MODE = "STANDARD";
  private static final String DEBUG_MODE = "DEBUG";

  @Test
  void batchhost001StandardIsEntirelyLazyIncludingAfterClose() {
    var calls = new AtomicInteger();
    var owner =
        new BatchStandardMetricSource(
            () -> {
              calls.incrementAndGet();
              throw new AssertionError("unexpected acquire");
            },
            (source, gc) -> {
              throw new AssertionError("unexpected registration");
            });
    try {

      owner.bind(STANDARD_MODE);
      assertEquals("", owner.scrape(STANDARD_MODE));
      owner.close();
      owner.bind(STANDARD_MODE);
      assertEquals("", owner.scrape(STANDARD_MODE));
      assertEquals(0, calls.get());
      assertThrows(IllegalStateException.class, () -> owner.bind(DEBUG_MODE));
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost002DefaultUsesOfficialStandardTextAndFixedBatchTag() {
    var owner = new BatchStandardMetricSource();
    try {
      owner.bind(DEBUG_MODE);
      String text = owner.scrape(DEBUG_MODE);
      String expected =
          "system_cpu_count{service=\"BATCH\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      assertTrue(
          text.lines().anyMatch(expected::equals),
          "standard CPU count must equal the independent own JVM observation");
      assertTrue(text.contains("# TYPE system_cpu_count gauge\n"));
      assertTrue(text.contains("jvm_memory_used_bytes{"));
      assertFalse(text.contains("nk_http_"));
      assertEquals("", owner.scrape(STANDARD_MODE));
    } finally {
      owner.close();
    }
    assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
  }

  @Test
  void batchhost003UnboundScrapeNeverAcquires() {
    var count = new AtomicInteger();
    var owner =
        new BatchStandardMetricSource(
            () -> {
              count.incrementAndGet();
              return new ProbeRegistry(new ArrayList<>());
            },
            (source, gc) -> {});
    try {

      assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
      assertEquals("", owner.scrape(STANDARD_MODE));
      assertEquals(0, count.get());
      owner.close();
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost004NullAndUnknownModesFailBeforeAcquisition() {
    var count = new AtomicInteger();
    var owner =
        new BatchStandardMetricSource(
            () -> {
              count.incrementAndGet();
              return new ProbeRegistry(new ArrayList<>());
            },
            (source, gc) -> {});
    try {

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
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost005ConstructorEstablishesNonNullPorts() {
    assertThrows(
        NullPointerException.class, () -> new BatchStandardMetricSource(null, (source, gc) -> {}));
    assertThrows(
        NullPointerException.class,
        () -> new BatchStandardMetricSource(() -> new ProbeRegistry(new ArrayList<>()), null));
  }

  @Test
  void batchhost006FactoryRuntimeIdentityAndNoAutomaticRetry() {
    var failure = new IllegalArgumentException("factory fixture");
    var calls = new AtomicInteger();
    var owner =
        new BatchStandardMetricSource(
            () -> {
              calls.incrementAndGet();
              throw failure;
            },
            (source, gc) -> {});
    try {

      assertSame(
          failure, assertThrows(IllegalArgumentException.class, () -> owner.bind(DEBUG_MODE)));
      assertThrows(IllegalStateException.class, () -> owner.bind(DEBUG_MODE));
      assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
      assertEquals(1, calls.get());
      owner.close();
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost007FactoryErrorIdentityIsNotNormalized() {
    var failure = new AssertionError("factory fatal fixture");
    var owner =
        new BatchStandardMetricSource(
            () -> {
              throw failure;
            },
            (source, gc) -> {});
    try {

      assertSame(failure, assertThrows(AssertionError.class, () -> owner.bind(DEBUG_MODE)));
      assertThrows(IllegalStateException.class, () -> owner.bind(DEBUG_MODE));
      owner.close();
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost008NullFactoryResultIsNotSuccess() {
    var owner =
        new BatchStandardMetricSource(
            () -> null,
            (source, gc) -> {
              throw new AssertionError("unexpected registrar");
            });
    try {

      assertThrows(NullPointerException.class, () -> owner.bind(DEBUG_MODE));
      assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
      owner.close();
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost009ClosedCandidateIsRejectedAndRetainedUntilCallerClose() {
    var source = new ProbeRegistry(new ArrayList<>());
    source.close();
    var owner =
        new BatchStandardMetricSource(
            () -> source,
            (value, gc) -> {
              throw new AssertionError("unexpected registrar");
            });
    try {

      assertThrows(IllegalStateException.class, () -> owner.bind(DEBUG_MODE));
      assertEquals(1, source.closes);
      owner.close();
      assertEquals(2, source.closes);
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost010PartialRegistryBeforeGcRemainsOwnedAfterFailure() {
    var source = new ProbeRegistry(new ArrayList<>());
    var failure = new IllegalArgumentException("registration fixture");
    var owner =
        new BatchStandardMetricSource(
            () -> source,
            (value, gc) -> {
              throw failure;
            });
    try {

      assertSame(
          failure, assertThrows(IllegalArgumentException.class, () -> owner.bind(DEBUG_MODE)));
      assertFalse(source.isClosed());
      assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
      owner.close();
      assertEquals(1, source.closes);
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost011GcRetainedBeforeFatalAndClosedInReverseOrder() {
    var order = new ArrayList<String>();
    var source = new ProbeRegistry(order);
    var gc = new ProbeGc(order);
    var failure = new AssertionError("post-owner fixture");
    var owner =
        new BatchStandardMetricSource(
            () -> source,
            (value, ack) -> {
              assertTrue(ack.test(gc));
              throw failure;
            });
    try {

      assertSame(failure, assertThrows(AssertionError.class, () -> owner.bind(DEBUG_MODE)));
      assertEquals(List.of(), order);
      owner.close();
      owner.close();
      assertEquals(List.of("gc", "registry"), order);
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost012FailedGcCloseKeepsRegistryAndExplicitRetryOwnership() {
    var order = new ArrayList<String>();
    var source = new ProbeRegistry(order);
    var gc = new ProbeGc(order);
    var failure = new IllegalStateException("GC close fixture");
    gc.failure = Optional.of(failure);
    var owner =
        new BatchStandardMetricSource(() -> source, (value, ack) -> assertTrue(ack.test(gc)));
    try {

      owner.bind(DEBUG_MODE);
      assertSame(failure, assertThrows(IllegalStateException.class, owner::close));
      assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
      assertFalse(source.isClosed());
      assertEquals(List.of("gc"), order);
      gc.failure = Optional.empty();
      owner.close();
      assertEquals(List.of("gc", "gc", "registry"), order);
      assertTrue(source.isClosed());
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost013FailedRegistryCloseIsNotConfirmedAndCanBeExplicitlyRetried() {
    var source = new ProbeRegistry(new ArrayList<>());
    var failure = new IllegalStateException("registry close fixture");
    source.failure = Optional.of(failure);
    var owner = new BatchStandardMetricSource(() -> source, (value, ack) -> {});
    try {

      owner.bind(DEBUG_MODE);
      assertSame(failure, assertThrows(IllegalStateException.class, owner::close));
      assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
      assertFalse(source.isClosed());
      source.failure = Optional.empty();
      owner.close();
      owner.close();
      assertTrue(source.isClosed());
      assertEquals(2, source.closes);
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost014NullGcCallbackFailsWithoutImplicitRegistryClose() {
    var source = new ProbeRegistry(new ArrayList<>());
    var owner = new BatchStandardMetricSource(() -> source, (value, ack) -> ack.test(null));
    try {

      assertThrows(NullPointerException.class, () -> owner.bind(DEBUG_MODE));
      assertFalse(source.isClosed());
      assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
      owner.close();
      assertTrue(source.isClosed());
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost015SingleBindAndIdempotentClose() {
    var source = new ProbeRegistry(new ArrayList<>());
    var calls = new AtomicInteger();
    var owner =
        new BatchStandardMetricSource(() -> source, (value, ack) -> calls.incrementAndGet());
    try {

      owner.bind(DEBUG_MODE);
      assertEquals("standard", owner.scrape(DEBUG_MODE));
      assertThrows(IllegalStateException.class, () -> owner.bind(DEBUG_MODE));
      owner.bind(STANDARD_MODE);
      owner.close();
      owner.close();
      assertEquals(1, calls.get());
      assertEquals(1, source.closes);
    } finally {
      owner.close();
    }
  }

  @Test
  void batchhost016CloseWaitsForOwnedScrapeAndThenRejectsNewScrapes() throws Exception {
    var source = new ProbeRegistry(new ArrayList<>());
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    source.entered = Optional.of(entered);
    source.release = Optional.of(release);
    var owner = new BatchStandardMetricSource(() -> source, (value, ack) -> {});
    try {

      owner.bind(DEBUG_MODE);
      try (var executor = Executors.newFixedThreadPool(2)) {
        try {
          var scrape = executor.submit(() -> owner.scrape(DEBUG_MODE));
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
          assertThrows(IllegalStateException.class, () -> owner.scrape(DEBUG_MODE));
        } finally {
          release.countDown();
          executor.shutdownNow();
          assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
          owner.close();
        }
      }
    } finally {
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
