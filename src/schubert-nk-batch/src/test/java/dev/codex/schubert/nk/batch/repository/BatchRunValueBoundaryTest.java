package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BAT-RUNVALUE001/002; SS341/343; pure immutable values, never runtime admission. */
final class BatchRunValueBoundaryTest {
  private static final UUID ID = new UUID(0, 16);

  @Test
  void cutoffBoundsNullsAndFixedRunDiagnostic() {
    for (String value :
        List.of("0001-01-01T00:00:00Z", "1582-10-10T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      Instant cutoff = Instant.parse(value);
      var run = new BatchRun(ID, cutoff);
      assertEquals(ID, run.id());
      assertEquals(cutoff, run.cutoff());
      assertEquals("BatchRun[identity/cutoff=<redacted>]", run.toString());
    }
    for (String value :
        List.of(
            "0000-12-31T23:59:59.999999Z",
            "+10000-01-01T00:00:00Z",
            "2026-09-13T00:00:00.000000001Z")) {
      Instant invalid = Instant.parse(value);
      assertThrows(IllegalArgumentException.class, () -> new BatchRun(ID, invalid));
    }
    assertThrows(NullPointerException.class, () -> new BatchRun(null, Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> new BatchRun(ID, null));
  }

  @Test
  void activationNullsValueAccessorsAndFixedDiagnostic() {
    var run = new BatchRun(ID, Instant.parse("2026-09-12T15:00:00Z"));
    var activation = new MaintenanceActivation(run, ID);
    assertEquals(run, activation.run());
    assertEquals(ID, activation.id());
    assertEquals(LocalDate.of(2026, 9, 13), activation.businessDate());
    assertEquals("MaintenanceActivation[identity/cutoff=<redacted>]", activation.toString());
    assertThrows(NullPointerException.class, () -> new MaintenanceActivation(null, ID));
    assertThrows(NullPointerException.class, () -> new MaintenanceActivation(run, null));
  }
}
