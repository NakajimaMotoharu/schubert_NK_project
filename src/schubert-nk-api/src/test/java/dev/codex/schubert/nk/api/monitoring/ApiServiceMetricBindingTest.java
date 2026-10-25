package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.DbPoolMetricObservationTest.Fixture;
import dev.codex.schubert.nk.api.monitoring.OutboxAgeMetricRecorder.Ages;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Counts;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository.Snapshot;
import java.time.Duration;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** 1852 APISERVICE001..016: immutable supplied data/typed fake bean only, no DB or clock. */
final class ApiServiceMetricBindingTest {
  private static Snapshot sample() {
    return new Snapshot(
        new Counts(3, 5, 7),
        new Ages(Duration.ofSeconds(2), Duration.ofSeconds(4), Duration.ofSeconds(6)));
  }

  private static Set<String> outboxLines(String body) {
    return Set.copyOf(
        body.lines()
            .filter(
                line ->
                    line.startsWith("nk_outbox_rows{")
                        || line.startsWith("nk_outbox_oldest_seconds{"))
            .toList());
  }

  private static void missing(String body) {
    assertEquals(
        Set.of(
            "nk_outbox_rows{status=\"PENDING\",store=\"API\"} NaN",
            "nk_outbox_rows{status=\"SENT\",store=\"API\"} NaN",
            "nk_outbox_rows{status=\"ERROR\",store=\"API\"} NaN",
            "nk_outbox_oldest_seconds{status=\"PENDING\",store=\"API\"} NaN",
            "nk_outbox_oldest_seconds{status=\"SENT\",store=\"API\"} NaN",
            "nk_outbox_oldest_seconds{status=\"ERROR\",store=\"API\"} NaN"),
        outboxLines(body));
  }

  @Test
  void apiservice001() {
    var f = new Fixture();
    var pools = new AtomicInteger();
    var configs = new AtomicInteger();
    var reads = new AtomicInteger();
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            () -> {
              pools.incrementAndGet();
              return f.pool();
            },
            () -> {
              configs.incrementAndGet();
              return f.config();
            },
            () -> {
              reads.incrementAndGet();
              return Optional.of(sample());
            })) {
      assertEquals(0, pools.get());
      assertEquals(0, configs.get());
      assertEquals(0, reads.get());
      context.initialize();
      assertEquals(1, pools.get());
      assertEquals(1, configs.get());
      assertEquals(0, reads.get());
      assertTrue(f.calls.isEmpty());
      context.render(true);
      context.render(false);
      assertEquals(1, pools.get());
      assertEquals(1, configs.get());
      assertEquals(2, reads.get());
      assertEquals(
          List.of("active", "idle", "pending", "max", "active", "idle", "pending", "max"), f.calls);
    }
    assertEquals(2, reads.get());
  }

  @Test
  void apiservice002() {
    var f = new Fixture();
    var first = sample();
    var value = new AtomicReference<>(Optional.of(first));
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", f::pool, f::config, value::get)) {
      context.initialize();
      String body = context.render(true);
      assertEquals(
          Set.of(
              "nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0",
              "nk_outbox_rows{status=\"SENT\",store=\"API\"} 5.0",
              "nk_outbox_rows{status=\"ERROR\",store=\"API\"} 7.0",
              "nk_outbox_oldest_seconds{status=\"PENDING\",store=\"API\"} 2.0",
              "nk_outbox_oldest_seconds{status=\"SENT\",store=\"API\"} 4.0",
              "nk_outbox_oldest_seconds{status=\"ERROR\",store=\"API\"} 6.0"),
          outboxLines(body));
      assertSame(first, context.bindings().orElseThrow().snapshot().orElseThrow());
      var second =
          new Snapshot(
              new Counts(11, 13, 17),
              new Ages(Duration.ofSeconds(8), Duration.ofSeconds(10), Duration.ofSeconds(12)));
      value.set(Optional.of(second));
      body = context.render(false);
      assertTrue(body.contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} 11.0\n"));
      assertTrue(body.contains("nk_outbox_oldest_seconds{status=\"PENDING\",store=\"API\"} 8.0\n"));
      assertSame(second, context.bindings().orElseThrow().snapshot().orElseThrow());
    }
  }

  @Test
  void apiservice003() {
    var f = new Fixture();
    try (var context = ApiServiceMetricBinding.prepareContext("DEBUG", f::pool, f::config)) {
      context.initialize();
      missing(context.render(true));
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
      f.complete();
    }
  }

  @Test
  void apiservice004() {
    var f = new Fixture();
    var value = new AtomicReference<>(Optional.of(sample()));
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", f::pool, f::config, value::get)) {
      context.initialize();
      context.render(true);
      value.set(Optional.empty());
      missing(context.render(true));
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
    }
  }

  @Test
  void apiservice005() {
    var f = new Fixture();
    var fail = new AtomicBoolean();
    var primary = new IllegalStateException("synthetic metadata failure");
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            f::pool,
            f::config,
            () -> {
              if (fail.get()) throw primary;
              return Optional.of(sample());
            })) {
      context.initialize();
      context.render(true);
      fail.set(true);
      assertSame(primary, assertThrows(IllegalStateException.class, () -> context.render(true)));
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
    }
  }

  @Test
  void apiservice006() {
    var f = new Fixture();
    var fail = new AtomicBoolean();
    var primary = new AssertionError("synthetic metadata error");
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            f::pool,
            f::config,
            () -> {
              if (fail.get()) throw primary;
              return Optional.of(sample());
            })) {
      context.initialize();
      context.render(true);
      fail.set(true);
      assertSame(primary, assertThrows(AssertionError.class, () -> context.render(true)));
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
    }
  }

  @Test
  void apiservice007() {
    var f = new Fixture();
    var value = new AtomicReference<>(Optional.of(sample()));
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", f::pool, f::config, value::get)) {
      context.initialize();
      context.render(true);
      value.set(null);
      assertThrows(NullPointerException.class, () -> context.render(true));
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
      value.set(Optional.empty());
      missing(context.render(true));
    }
  }

  @Test
  void apiservice008() {
    var f = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> ApiServiceMetricBinding.prepareContext("DEBUG", null, f::config));
    assertThrows(
        NullPointerException.class,
        () -> ApiServiceMetricBinding.prepareContext("DEBUG", f::pool, null));
    assertThrows(
        NullPointerException.class,
        () -> ApiServiceMetricBinding.prepareContext("DEBUG", f::pool, f::config, null));
    assertThrows(
        NullPointerException.class,
        () -> ApiServiceMetricBinding.prepareContext(null, f::pool, f::config));
    assertThrows(
        IllegalArgumentException.class,
        () -> ApiServiceMetricBinding.prepareContext("debug", f::pool, f::config));
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void apiservice009() {
    var f = new Fixture();
    var reads = new AtomicInteger();
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            () -> null,
            f::config,
            () -> {
              reads.incrementAndGet();
              return Optional.empty();
            })) {
      assertThrows(NullPointerException.class, context::initialize);
      assertEquals(0, reads.get());
      assertTrue(f.calls.isEmpty());
    }
  }

  @Test
  void apiservice010() {
    var f = new Fixture();
    var reads = new AtomicInteger();
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            f::pool,
            () -> null,
            () -> {
              reads.incrementAndGet();
              return Optional.empty();
            })) {
      assertThrows(NullPointerException.class, context::initialize);
      assertEquals(0, reads.get());
      assertTrue(f.calls.isEmpty());
    }
  }

  @Test
  void apiservice011() {
    var f = new Fixture();
    var primary = new IllegalStateException("synthetic bean supplier");
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            () -> {
              throw primary;
            },
            f::config)) {
      assertSame(primary, assertThrows(IllegalStateException.class, context::initialize));
      assertTrue(f.calls.isEmpty());
    }
  }

  @Test
  void apiservice012() {
    var f = new Fixture();
    var primary = new AssertionError("synthetic configuration supplier");
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            f::pool,
            () -> {
              throw primary;
            })) {
      assertSame(primary, assertThrows(AssertionError.class, context::initialize));
      assertTrue(f.calls.isEmpty());
    }
  }

  @Test
  void apiservice013() {
    var reads = new AtomicInteger();
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "STANDARD",
            () -> {
              reads.incrementAndGet();
              throw new AssertionError("STD pool read");
            },
            () -> {
              reads.incrementAndGet();
              throw new AssertionError("STD config read");
            },
            () -> {
              reads.incrementAndGet();
              throw new AssertionError("STD source read");
            })) {
      context.initialize();
      assertEquals(
          "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready 1\n", context.render(true));
      assertTrue(context.bindings().isEmpty());
      assertEquals(0, reads.get());
    }
    assertEquals(0, reads.get());
  }

  @Test
  void apiservice014() {
    var f = new Fixture();
    var zero =
        new Snapshot(new Counts(0, 0, 0), new Ages(Duration.ZERO, Duration.ZERO, Duration.ZERO));
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG", f::pool, f::config, () -> Optional.of(zero))) {
      context.initialize();
      String body = context.render(true);
      for (String status : List.of("PENDING", "SENT", "ERROR")) {
        assertTrue(body.contains("nk_outbox_rows{status=\"" + status + "\",store=\"API\"} 0.0\n"));
        assertTrue(
            body.contains(
                "nk_outbox_oldest_seconds{status=\"" + status + "\",store=\"API\"} 0.0\n"));
      }
      assertSame(zero, context.bindings().orElseThrow().snapshot().orElseThrow());
    }
  }

  @Test
  void apiservice015() {
    var f = new Fixture();
    var reads = new AtomicInteger();
    var primary = new IllegalStateException("synthetic pool getter");
    try (var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            f::pool,
            f::config,
            () -> {
              reads.incrementAndGet();
              return Optional.of(sample());
            })) {
      context.initialize();
      context.render(true);
      assertEquals(1, reads.get());
      f.faults.put("active", primary);
      assertSame(primary, assertThrows(IllegalStateException.class, () -> context.render(true)));
      assertEquals(1, reads.get());
      assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
    }
  }

  @Test
  void apiservice016() {
    var f = new Fixture();
    var reads = new AtomicInteger();
    var context =
        ApiServiceMetricBinding.prepareContext(
            "DEBUG",
            f::pool,
            f::config,
            () -> {
              reads.incrementAndGet();
              return Optional.of(sample());
            });
    try {
      context.initialize();
      context.render(true);
      context.close();
      int getterCalls = f.calls.size();
      assertThrows(IllegalStateException.class, () -> context.render(true));
      assertEquals(1, reads.get());
      assertEquals(getterCalls, f.calls.size());
    } finally {
      context.close();
    }
  }
}
