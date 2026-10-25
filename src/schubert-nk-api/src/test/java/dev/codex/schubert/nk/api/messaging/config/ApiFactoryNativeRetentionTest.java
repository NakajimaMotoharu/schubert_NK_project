package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.file.OwnedRetentionProcess;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import java.util.Collections;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** PT-NHOLD316003: original exception/policy and self-owned unconnected factory lifetime. */
final class ApiFactoryNativeRetentionTest {
  @Test
  void hold316006FinitePolicyStillFailsAndNullPolicyPrecedesAcquisition() {
    var probe = new ApiFactoryOwnershipTest.ProbeFactory();
    try {
      probe.failAt = 1;
      probe.primary = new IllegalStateException("fixture setup");
      probe.closeFailure = new IllegalStateException("fixture close");
      var seen = new AtomicReference<Throwable>();
      assertSame(
          probe.primary,
          assertThrows(
              IllegalStateException.class,
              () ->
                  ArtemisConnectionFactoryProvider.configureOwned(
                      ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC,
                      () -> probe,
                      seen::set)));
      assertSame(probe.closeFailure, seen.get());
      assertEquals(1, probe.closes);
      var opens = new AtomicInteger();
      assertThrows(
          NullPointerException.class,
          () ->
              ArtemisConnectionFactoryProvider.configureOwned(
                  ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC,
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
        () -> ApiBrokerContexts.createRetainingUnknown(null, "tcp://127.0.0.1:61616"));
  }

  @Test
  void hold316007ProviderPartialAndReturnedBrokerKeepOuterFrameWithoutRetry() throws Exception {
    for (int kind = 0; kind < 3; kind++)
      OwnedRetentionProcess.assertFactoryHeld(
          Driver.class, Collections.nCopies(kind == 2 ? 3 : 1, "CLOSE"), Integer.toString(kind));
  }

  /** No connection/session is opened. The own child ends before its finite watchdog deadline. */
  public static final class FaultFactory extends ApiFactoryOwnershipTest.ProbeFactory {
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
        if (kind == 0) {
          var probe = new FaultFactory();
          probe.failAt = 1;
          probe.primary = new IllegalStateException("fixture setup");
          ArtemisConnectionFactoryProvider.configureOwned(
              ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC,
              () -> probe,
              ServiceProcessResources::retainUnknownRelease);
        } else {
          var owner =
              ApiBrokerContexts.createOwned(
                  () -> new char[] {'P', 'T'},
                  "tcp://127.0.0.1:61616",
                  (profile, endpoint) -> {
                    if (kind == 1
                        && profile == ArtemisConnectionFactoryProvider.ConsumerProfile.ASYNC)
                      throw new IllegalStateException("fixture third factory");
                    return new FaultFactory();
                  },
                  true);
          owner.close();
        }
      } finally {
        System.out.println("OUTER_RELEASED");
      }
    }
  }
}
