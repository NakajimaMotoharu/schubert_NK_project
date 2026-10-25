package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import java.io.IOException;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS343/SSC178: default resume port cannot confer an original-owner capability. */
final class UnsupportedOriginalProofTest {
  @Test
  void originalPort001DefaultResumeVerificationNeverProvesOriginalOrRetainedOwnership()
      throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("00000000-0000-0000-0000-000000000345"),
            Instant.parse("2026-09-27T15:00:00.123456Z"));
    var state =
        new MaintenanceRunState(
            new MaintenanceActivation(run, UUID.fromString("00000000-0000-0000-0000-000000000346")),
            Optional.empty());
    var gates = new AtomicInteger();
    var resumes = new AtomicInteger();
    MorningResumeAdmission.Files files =
        (id, activation) -> {
          resumes.incrementAndGet();
          return state;
        };
    var alive = new AtomicBoolean(true);
    var proof =
        MorningNewRunAdmission.scopedOriginalProof(
            gates::incrementAndGet, files, state, alive, () -> new IOException("owner inactive"));
    assertEquals(
        "Morning same-run resume unavailable",
        assertThrows(IOException.class, proof::verify).getMessage());
    assertEquals(1, gates.get(), "no post-verification owner gate after absent capability");
    assertEquals(
        "Morning same-run resume unavailable",
        assertThrows(IOException.class, proof::verifyRetained).getMessage());
    assertEquals(2, gates.get());
    assertEquals(0, resumes.get(), "verification may not issue another resume");
    alive.set(false);
    assertEquals("owner inactive", assertThrows(IOException.class, proof::verify).getMessage());
    assertEquals(2, gates.get(), "closed owner must be rejected before any verification IO");
  }
}
