package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-DATA-511002 / SSC137: argument validation only, every IO method must stay uncalled. */
final class ServiceDeadlineArgumentTest {
  @Test
  void data511002UnsupportedActorAndNonpositiveBudgetRefuseBeforeAllIo() {
    var calls = new AtomicInteger();
    var io =
        (RootStartupContext.Io)
            Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {RootStartupContext.Io.class},
                (proxy, method, args) -> {
                  calls.incrementAndGet();
                  throw new AssertionError("argument rejection must precede every IO port");
                });
    var subject = new RootStartupContext(io);
    for (var service : RootStartupContext.Service.values()) {
      var data =
          new RootStartupContext.Snapshot(
              service,
              "11111111-1111-4111-8111-111111111111",
              "2".repeat(32),
              42,
              43,
              44,
              "/public-synthetic-cgroup");
      long[] invalid =
          service == RootStartupContext.Service.API || service == RootStartupContext.Service.WEB
              ? new long[] {0, -1}
              : new long[] {1, Long.MAX_VALUE};
      for (long budget : invalid) {
        var failure =
            assertThrows(IOException.class, () -> subject.serviceRootDeadline(data, budget));
        assertEquals("startup context unavailable", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
      }
    }
    assertThrows(NullPointerException.class, () -> subject.serviceRootDeadline(null, 1));
    assertEquals(0, calls.get());
  }
}
