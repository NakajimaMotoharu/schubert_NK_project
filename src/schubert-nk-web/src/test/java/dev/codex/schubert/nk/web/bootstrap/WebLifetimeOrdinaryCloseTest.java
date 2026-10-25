package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** 1880/WLCLOSE001..003: uninstalled lifetime only; no native hook, process, Main or provider. */
final class WebLifetimeOrdinaryCloseTest {
  @Test
  void wlClose001() {
    var lifetime = new WebProcessLifetime();
    try {
      assertFalse(lifetime.stopping());
      lifetime.close();
      assertTrue(lifetime.stopping());
      lifetime.close();
      assertTrue(lifetime.stopping());
    } finally {
      lifetime.close();
    }
  }

  @Test
  void wlClose002() throws IOException {
    try (var lifetime = new WebProcessLifetime()) {
      assertThrows(NullPointerException.class, () -> lifetime.await(null));
      lifetime.fail();
      var error =
          assertThrows(IOException.class, () -> lifetime.await(() -> fail("no provider poll")));
      assertEquals("Web runtime unavailable", error.getMessage());
      assertTrue(lifetime.stopping());
    }
  }

  @Test
  void wlClose003() throws Exception {
    var lifetime = new WebProcessLifetime();
    try (var executor = Executors.newSingleThreadExecutor()) {
      lifetime.close();
      executor
          .submit(
              () -> {
                lifetime.shutdown();
                return Boolean.TRUE;
              })
          .get(5, TimeUnit.SECONDS);
      assertTrue(lifetime.stopping());
      lifetime.await(() -> fail("already stopped owner does not poll"));
    } finally {
      lifetime.close();
    }
  }
}
