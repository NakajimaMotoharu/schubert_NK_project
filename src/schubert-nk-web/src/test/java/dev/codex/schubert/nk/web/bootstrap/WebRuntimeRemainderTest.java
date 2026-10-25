package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.WebNativeRuntimeCredentialFixture;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PG-D378/SS313314342352/PT-OPS-WEB-REM001..003. Literal controls and UI routes, no native claim.
 */
final class WebRuntimeRemainderTest {
  @TempDir Path temporary;

  @Test
  void rem001ReadyUsesOnlyTheSameCapturedManagerAndPreservesFailure() {
    var calls = new AtomicInteger();
    assertFalse(
        WebRuntimeHealth.ready(
            null,
            ignored -> {
              calls.incrementAndGet();
              return true;
            }));
    assertEquals(0, calls.get());
    Object manager = new Object();
    for (boolean answer : new boolean[] {false, true}) {
      assertEquals(
          answer,
          WebRuntimeHealth.ready(
              manager,
              actual -> {
                assertSame(manager, actual);
                calls.incrementAndGet();
                return answer;
              }));
    }
    assertEquals(2, calls.get());
    var failure = new IllegalStateException("synthetic management");
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class,
            () ->
                WebRuntimeHealth.ready(
                    manager,
                    actual -> {
                      assertSame(manager, actual);
                      throw failure;
                    })));
  }

  @Test
  void rem002BothTerminalCallbacksAreStickyAndVisibleWithoutClosingAnything() throws Exception {
    assertThrows(NullPointerException.class, () -> new WebRuntimeFailureSignal<Throwable>(null));
    for (boolean consumer : new boolean[] {false, true}) {
      var terminal = new AtomicBoolean();
      var signal = new WebRuntimeFailureSignal<Throwable>(terminal);
      assertFalse(terminal.get());
      if (consumer) signal.accept(new IOException("synthetic private failure"));
      else signal.run();
      assertTrue(terminal.get());
      try (var threads = Executors.newFixedThreadPool(4)) {
        List<Future<?>> tasks = new ArrayList<>();
        for (int n = 0; n < 16; n++)
          tasks.add(
              threads.submit(
                  () -> {
                    signal.run();
                    signal.accept(new AssertionError("synthetic"));
                  }));
        for (var task : tasks) task.get();
      }
      assertTrue(terminal.get());
    }
  }

  @Test
  void rem003ExactUiMappingsRejectEveryMissingOrForeignRoute() throws Exception {
    Set<String> routes =
        Set.of(
            "/",
            "/login",
            "/logout",
            "/error",
            "/search",
            "/logs",
            "/scenarios",
            "/scenarios/{id:[0-9]{1,12}}",
            "/scenarios/{game:NUKITASHI[12]}",
            "/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}",
            "/animation",
            "/animation/main",
            "/animation/ova",
            "/animation/opening",
            "/animation/videos/{id}",
            "/animation/media/{id}",
            "/music",
            "/music/{category}",
            "/music/{category}/{section}",
            "/music/media/{id}",
            "/music/download/{id}",
            "/audio/{id}",
            "/audio/{id}/download",
            "/admin/users",
            "/admin/users/new",
            "/admin/users/{id:[0-9]{1,12}}",
            "/questions",
            "/questions/new",
            "/questions/accepted/{receiptId}",
            "/questions/{id:[0-9]{1,12}}",
            "/notifications",
            "/notifications/{id:[0-9]{1,12}}");
    assertEquals(32, routes.size());
    WebNativeRuntime.requireMappings(routes);
    for (String missing : routes) {
      var bad = new HashSet<>(routes);
      bad.remove(missing);
      assertEquals(
          "Web business mapping unavailable",
          assertThrows(IOException.class, () -> WebNativeRuntime.requireMappings(bad))
              .getMessage());
      bad.add("/unapproved");
      assertEquals(
          "Web business mapping unavailable",
          assertThrows(IOException.class, () -> WebNativeRuntime.requireMappings(bad))
              .getMessage());
    }
    assertThrows(NullPointerException.class, () -> WebNativeRuntime.requireMappings(null));
  }

  @Test
  void rem003FailedFirstAcquisitionCannotBeRetriedOrCloseBorrowedKeys() throws Exception {
    var calls = new AtomicInteger();
    DataSource unavailable =
        (DataSource)
            Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {DataSource.class},
                (p, m, a) -> {
                  assertEquals("getConnection", m.getName());
                  calls.incrementAndGet();
                  throw new IllegalStateException("synthetic private provider");
                });
    var released = new AtomicInteger();
    var admission =
        new ServiceStartupAdmission.Ready() {
          public void release() {
            released.incrementAndGet();
          }

          public Map<String, String> information() {
            return Map.of("app", "0.1.0-SNAPSHOT", "config", "1");
          }
        };
    WebNativeRuntimeCredentialFixture.withKeys(
        temporary,
        keys -> {
          var runtime =
              new WebNativeRuntime(
                  unavailable, keys, WebNonSecretConfig.parse("", ""), admission, () -> false);
          try {
            assertEquals(
                "Web technical database is unavailable",
                assertThrows(WebStartupException.class, runtime::start).getMessage());
            assertEquals(1, calls.get());
            assertEquals(
                "Web startup unavailable",
                assertThrows(IOException.class, runtime::start).getMessage());
            assertEquals(1, calls.get());
            assertFalse(runtime.ready());
            assertFalse(runtime.healthy());
          } finally {
            runtime.close();
          }
          assertEquals(0, released.get());
          assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
        });
  }
}
