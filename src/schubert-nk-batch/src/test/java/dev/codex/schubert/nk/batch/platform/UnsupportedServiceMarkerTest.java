package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS343/SSC178/186: incomplete marker capabilities cannot prove readiness or release ownership. */
final class UnsupportedServiceMarkerTest {
  @Test
  void serviceMarkerPort001MissingRetainedProofNeverGrantsDaemonReadiness() throws Exception {
    var gates = new AtomicInteger();
    var retires = new AtomicInteger();
    var child = new InspectorUnitProbeFixture.Child(new byte[0]);
    child.waitSeconds = 120;
    var attempt =
        new BackupUnitStartClient(
                () -> {},
                () -> {},
                command -> child,
                () -> retires::incrementAndGet,
                MaintenanceUnit.API,
                Optional.empty())
            .start();
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.status());
    var failure =
        assertThrows(IOException.class, () -> attempt.requireRetained(gates::incrementAndGet));
    assertEquals("service intent proof unavailable", failure.getMessage());
    assertEquals(1, gates.get(), "post-proof gate must not run after missing marker proof");
    assertEquals(0, retires.get());
    child.allClosed();
  }

  @Test
  void serviceMarkerPort002MissingObservationClosePreservesUnknownAndCannotRetire()
      throws Exception {
    var retires = new AtomicInteger();
    var child = new InspectorUnitProbeFixture.Child(new byte[0]);
    child.waitSeconds = 120;
    var attempt =
        new BackupUnitStartClient(
                () -> {},
                () -> {},
                command -> child,
                () -> retires::incrementAndGet,
                MaintenanceUnit.WEB,
                Optional.empty())
            .start();
    var failure = assertThrows(IOException.class, attempt::preserveObservation);
    assertEquals("service observation close unavailable", failure.getMessage());
    assertThrows(IOException.class, attempt::preserveObservation);
    assertThrows(IOException.class, () -> attempt.retireAfter(() -> fail("unknown cannot retire")));
    assertEquals(0, retires.get());
    child.allClosed();
  }
}
