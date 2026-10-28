package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.ApiFactoryObservationFixture;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

/**
 * 1874/APIOBSBOOT001..008: static seams only. Never constructs ApiProcessMain, reads startup files,
 * invokes main/run/admission, registers hooks, starts a provider pool or touches real JDBC.
 */
final class ApiProcessObservationFactoryTest {
  private static final String FIXTURE_STANDARD_E303A9CB = "STANDARD";

  private static DataSource pool(AtomicInteger opens) {
    return DataSource.class.cast(
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (proxy, method, arguments) -> {
              opens.incrementAndGet();
              throw new AssertionError("no provider method is authorized in this fixture");
            }));
  }

  @Test
  void apiObsBoot001() {
    var opens = new AtomicInteger();
    var pool = pool(opens);
    try (var lifetime = new ApiProcessLifetime(() -> 0)) {
      assertThrows(
          NullPointerException.class,
          () -> ApiProcessMain.prepareObservations(null, pool, lifetime));
      assertThrows(
          NullPointerException.class,
          () -> ApiProcessMain.prepareObservations(FIXTURE_STANDARD_E303A9CB, null, lifetime));
      assertThrows(
          NullPointerException.class,
          () -> ApiProcessMain.prepareObservations(FIXTURE_STANDARD_E303A9CB, pool, null));
      assertFalse(lifetime.stopping());
    }
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot002() {
    var opens = new AtomicInteger();
    try (var lifetime = new ApiProcessLifetime(() -> 0)) {
      for (String mode : List.of("", "debug", "UNKNOWN"))
        assertThrows(
            IllegalArgumentException.class,
            () -> ApiProcessMain.prepareObservations(mode, pool(opens), lifetime));
      assertFalse(lifetime.stopping());
    }
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot003() throws IOException {
    var opens = new AtomicInteger();
    try (var lifetime = new ApiProcessLifetime(() -> 0)) {
      var observations =
          ApiProcessMain.prepareObservations(FIXTURE_STANDARD_E303A9CB, pool(opens), lifetime);
      try {
        observations.initialize();
        assertTrue(observations.metrics().bindings().isEmpty());
        assertFalse(observations.metrics().render(true).contains("nk_outbox_"));
        ApiProcessMain.closeObservations(observations, lifetime);
        assertTrue(lifetime.stopping());
        assertEquals(60_000_000_000L, lifetime.remainingStopNanos());
        assertThrows(IllegalStateException.class, () -> observations.metrics().render(true));
      } finally {
        observations.close();
      }
    }
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot004() throws IOException {
    var opens = new AtomicInteger();
    var reads = new AtomicInteger();
    try (var lifetime =
        new ApiProcessLifetime(
            () -> {
              reads.incrementAndGet();
              return 0;
            })) {
      var observations = ApiProcessMain.prepareObservations("DEBUG", pool(opens), lifetime);
      try {
        assertEquals(0, reads.get());
        assertThrows(IllegalStateException.class, lifetime::remainingStopNanos);
        assertThrows(IllegalStateException.class, () -> observations.metrics().render(true));
        ApiProcessMain.closeObservations(observations, lifetime);
        assertEquals(1, reads.get());
      } finally {
        observations.close();
      }
    }
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot005() throws IOException {
    var opens = new AtomicInteger();
    var reads = new AtomicInteger();
    try (var lifetime =
        new ApiProcessLifetime(
            () -> {
              reads.incrementAndGet();
              return 0;
            })) {
      assertThrows(
          NullPointerException.class, () -> ApiProcessMain.closeObservations(null, lifetime));
      var observations =
          ApiProcessMain.prepareObservations(FIXTURE_STANDARD_E303A9CB, pool(opens), lifetime);
      try {
        assertThrows(
            NullPointerException.class, () -> ApiProcessMain.closeObservations(observations, null));
        assertFalse(lifetime.stopping());
        assertEquals(0, reads.get());
        observations.initialize();
        assertTrue(observations.metrics().bindings().isEmpty());
      } finally {
        observations.close();
      }
    }
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot006() throws IOException {
    var opens = new AtomicInteger();
    var now = new AtomicLong(100);
    var reads = new AtomicInteger();
    try (var lifetime =
        new ApiProcessLifetime(
            () -> {
              reads.incrementAndGet();
              return now.get();
            })) {
      var observations =
          ApiProcessMain.prepareObservations(FIXTURE_STANDARD_E303A9CB, pool(opens), lifetime);
      try {
        observations.initialize();
        ApiProcessMain.closeObservations(observations, lifetime);
        now.set(109);
        ApiProcessMain.closeObservations(observations, lifetime);
        assertEquals(1, reads.get());
        assertEquals(59_999_999_991L, lifetime.remainingStopNanos());
      } finally {
        observations.close();
      }
    }
    assertEquals(2, reads.get());
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot007() throws IOException {
    var opens = new AtomicInteger();
    var fatal = new AssertionError("own clock fault");
    var lifetime =
        new ApiProcessLifetime(
            () -> {
              throw fatal;
            });
    var observations =
        ApiProcessMain.prepareObservations(FIXTURE_STANDARD_E303A9CB, pool(opens), lifetime);
    try {
      observations.initialize();
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> ApiProcessMain.closeObservations(observations, lifetime)));
      assertTrue(lifetime.stopping());
      assertEquals(0, lifetime.remainingStopNanos());
      // Existing ResourceScope must release this known-no-worker owner before propagating fatal.
      assertThrows(IllegalStateException.class, () -> observations.metrics().render(true));
    } finally {
      observations.close();
      lifetime.close();
    }
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot008() throws IOException {
    var opens = new AtomicInteger();
    try (var lifetime = new ApiProcessLifetime(() -> 0)) {
      var observations = ApiProcessMain.prepareObservations("DEBUG", pool(opens), lifetime);
      try {
        // Production gets the admitted Hikari pool. This wrong typed fake is rejected by SDK
        // setup before observation worker start; no connection or provider-pool operation occurs.
        assertThrows(ClassCastException.class, observations::initialize);
        assertFalse(lifetime.stopping());
        assertThrows(IllegalStateException.class, () -> observations.metrics().render(true));
        ApiProcessMain.closeObservations(observations, lifetime);
        assertTrue(lifetime.stopping());
      } finally {
        observations.close();
      }
    }
    assertEquals(0, opens.get());
  }

  @Test
  void apiObsBoot009() throws Exception {
    var fixture = ApiFactoryObservationFixture.create();
    var lifetime = new ApiProcessLifetime(() -> 0);
    var observations = ApiProcessMain.prepareObservations("DEBUG", fixture.pool(), lifetime);
    try {
      observations.initialize();
      long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(10);
      String body;
      do {
        body = observations.metrics().render(true);
        if (body.contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0")) break;
        assertTrue(deadline - System.nanoTime() > 0, "own fake producer publication bound");
        Thread.sleep(1);
      } while (true);
      for (String line :
          List.of(
              "nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0",
              "nk_outbox_rows{status=\"SENT\",store=\"API\"} 5.0",
              "nk_outbox_rows{status=\"ERROR\",store=\"API\"} 7.0"))
        assertTrue(body.lines().anyMatch(line::equals));
      double elapsed = Duration.between(fixture.created(), Instant.now()).toNanos() / 1e9;
      for (var entry : java.util.Map.of("PENDING", 2, "SENT", 4, "ERROR", 6).entrySet()) {
        String prefix =
            "nk_outbox_oldest_seconds{status=\"" + entry.getKey() + "\",store=\"API\"} ";
        double actual =
            Double.parseDouble(
                body.lines()
                    .filter(line -> line.startsWith(prefix))
                    .findFirst()
                    .orElseThrow()
                    .substring(prefix.length()));
        assertTrue(Double.isFinite(actual));
        assertTrue(actual >= entry.getValue() && actual <= entry.getValue() + elapsed + 0.001);
      }
      assertFalse(lifetime.stopping());
      ApiProcessMain.closeObservations(observations, lifetime);
      assertTrue(lifetime.stopping());
      assertEquals(60_000_000_000L, lifetime.remainingStopNanos());
      assertThrows(IllegalStateException.class, () -> observations.metrics().render(true));
      fixture.assertReleased();
    } finally {
      observations.close();
      lifetime.close();
      fixture.dispose();
    }
  }
}
