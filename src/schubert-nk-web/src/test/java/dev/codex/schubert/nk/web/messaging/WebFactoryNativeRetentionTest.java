package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.file.OwnedRetentionProcess;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** PT-NHOLD316003 Web counterpart; own unconnected locator/child, no native admission. */
final class WebFactoryNativeRetentionTest {
  @Test
  void hold316008FiniteObserverKeepsFailureAndNullPolicyDoesNotAcquire() {
    var probe = new WebBrokerFactoryOwnershipTest.ProbeFactory();
    try {
      probe.failAt = 1;
      probe.primary = new IllegalStateException("fixture setup");
      probe.closeFailure = new IllegalStateException("fixture close");
      var seen = new AtomicReference<Throwable>();
      assertSame(
          probe.primary,
          assertThrows(
              IllegalStateException.class,
              () -> WebBrokerContexts.configureOwned(() -> probe, seen::set)));
      assertSame(probe.closeFailure, seen.get());
      assertEquals(1, probe.closes);
      var opens = new AtomicInteger();
      assertThrows(
          NullPointerException.class,
          () ->
              WebBrokerContexts.configureOwned(
                  () -> {
                    opens.incrementAndGet();
                    return probe;
                  },
                  null));
      assertEquals(0, opens.get());
    } finally {
      probe.dispose();
    }
    assertThrows(
        NullPointerException.class,
        () -> WebBrokerContexts.createRetainingUnknown(null, "tcp://127.0.0.1:61616"));
  }

  @Test
  void hold316009ProviderAndReturnedOwnerKeepOuterFrame() throws Exception {
    for (int kind = 0; kind < 2; kind++)
      OwnedRetentionProcess.assertFactoryHeld(
          Driver.class, List.of("CLOSE"), Integer.toString(kind));
  }

  public static final class FaultFactory extends WebBrokerFactoryOwnershipTest.ProbeFactory {
    @java.io.Serial private static final long serialVersionUID = 1L;

    public FaultFactory() {
      super();
    }

    @Override
    public void close() {
      System.out.println("CLOSE");
      throw new IllegalStateException("fixture close before locator release");
    }
  }

  public static final class Driver {
    public static void main(String[] arguments) {
      OwnedRetentionProcess.deadline();
      int kind = Integer.parseInt(arguments[0]);
      try {
        var factory = new FaultFactory();
        if (kind == 0) {
          factory.failAt = 1;
          factory.primary = new IllegalStateException("fixture setup");
          WebBrokerContexts.configureOwned(
              () -> factory, ServiceProcessResources::retainUnknownRelease);
        } else {
          new WebBrokerContexts(() -> new char[] {'P', 'T'}, factory, factory, true).close();
        }
      } finally {
        System.out.println("OUTER_RELEASED");
      }
    }
  }
}
