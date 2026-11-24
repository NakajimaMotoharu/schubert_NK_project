package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles.StartupOriginal;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

final class MaintenanceStartupOriginalValueTest {
  private static final UUID RUN_ID = new UUID(3, 11);
  private static final UUID ACTIVATION_ID = new UUID(4, 19);
  private static final Instant CUTOFF = Instant.parse("2026-11-01T20:00:00Z");
  private static final Instant END = Instant.parse("2026-11-01T20:04:00Z");
  private static final MaintenanceActivation ACTIVATION =
      new MaintenanceActivation(new BatchRun(RUN_ID, CUTOFF), ACTIVATION_ID);

  @Test
  @DisplayName("PT-BAT-STARTUP-VAL-001 uncompleted value retains the activation alone")
  void pendingValueContainsNoCompletion() {
    var pending = new StartupOriginal(ACTIVATION, Optional.empty());
    assertEquals(ACTIVATION, pending.activation());
    assertEquals(Optional.empty(), pending.completed());
    assertEquals(pending, new StartupOriginal(ACTIVATION, Optional.empty()));
  }

  @Test
  @DisplayName("PT-BAT-STARTUP-VAL-002 completed value retains the exact terminal metadata")
  void equalActivationMayCarryCompletionAndUsesFixedDiagnostic() {
    var equivalent = new MaintenanceActivation(new BatchRun(RUN_ID, CUTOFF), ACTIVATION_ID);
    var done = new MaintenanceCompletion(equivalent, END, MaintenanceCompletion.Outcome.WARNING);
    var completed = new StartupOriginal(ACTIVATION, Optional.of(done));

    assertEquals(ACTIVATION, completed.activation());
    assertEquals(Optional.of(done), completed.completed());
    assertEquals("StartupOriginal[identity=<redacted>]", completed.toString());
    assertNotEquals(new StartupOriginal(ACTIVATION, Optional.empty()), completed);
    assertEquals(
        new StartupOriginal(equivalent, Optional.of(done)).hashCode(), completed.hashCode());
  }

  @Test
  @DisplayName("PT-BAT-STARTUP-VAL-003 terminal metadata must match each activation field")
  void rejectsMismatchesInRunCutoffAndActivationId() {
    var differentRun =
        new MaintenanceActivation(new BatchRun(new UUID(3, 12), CUTOFF), ACTIVATION_ID);
    var differentCutoff =
        new MaintenanceActivation(new BatchRun(RUN_ID, CUTOFF.plusSeconds(1)), ACTIVATION_ID);
    var differentId = new MaintenanceActivation(new BatchRun(RUN_ID, CUTOFF), new UUID(4, 20));

    for (var other : new MaintenanceActivation[] {differentRun, differentCutoff, differentId}) {
      var completion = new MaintenanceCompletion(other, END, MaintenanceCompletion.Outcome.SUCCESS);
      assertThrows(
          IllegalArgumentException.class,
          () -> new StartupOriginal(ACTIVATION, Optional.of(completion)));
    }
  }

  @Test
  @DisplayName("PT-BAT-STARTUP-VAL-004 rejects absent required values at construction")
  void rejectsNullActivationAndNullOptionalIndependently() {
    assertThrows(NullPointerException.class, () -> new StartupOriginal(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> new StartupOriginal(ACTIVATION, null));
  }
}
