package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

/**
 * 1874/APIOBSBOOT001..008: static seams only. Never constructs ApiProcessMain, reads startup files,
 * invokes main/run/admission, registers hooks, starts a provider pool or touches real JDBC.
 */
final class ApiProcessObservationFactoryTest {
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
          () -> ApiProcessMain.prepareObservations("STANDARD", null, lifetime));
      assertThrows(
          NullPointerException.class,
          () -> ApiProcessMain.prepareObservations("STANDARD", pool, null));
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
      var observations = ApiProcessMain.prepareObservations("STANDARD", pool(opens), lifetime);
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
      var observations = ApiProcessMain.prepareObservations("STANDARD", pool(opens), lifetime);
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
      var observations = ApiProcessMain.prepareObservations("STANDARD", pool(opens), lifetime);
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
    var observations = ApiProcessMain.prepareObservations("STANDARD", pool(opens), lifetime);
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
}
