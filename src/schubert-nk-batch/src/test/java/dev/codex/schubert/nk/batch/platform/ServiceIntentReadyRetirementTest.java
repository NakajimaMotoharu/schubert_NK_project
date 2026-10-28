package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SSC178 live-ready intent capability is separate from Backup/worker terminus. */
final class ServiceIntentReadyRetirementTest {
  private static final String FIXTURE_RETIRE_A2A9D4FF = "retire";

  static BackupUnitStartClient.Attempt attempt(MaintenanceUnit unit, List<String> events)
      throws IOException {
    var child = new InspectorUnitProbeFixture.Child(new byte[0]);
    child.waitSeconds = 120;
    return new BackupUnitStartClient(
            () -> events.add("root"),
            () -> {},
            command -> child,
            () ->
                new BackupUnitStartClient.MarkerLease() {
                  public void requireRetained() {
                    events.add("retained");
                  }

                  public void retire() {
                    events.add(FIXTURE_RETIRE_A2A9D4FF);
                  }
                },
            unit,
            Optional.empty())
        .start();
  }

  @Test
  void parent455005ReadinessBeforeAndAfterSingleRetirement() throws Exception {
    for (var unit : List.of(MaintenanceUnit.API, MaintenanceUnit.WEB, MaintenanceUnit.CADDY)) {
      var events = new ArrayList<String>();
      var owner = attempt(unit, events);
      events.clear();
      if (unit != MaintenanceUnit.CADDY) {
        owner.requireRetained(() -> events.add("generation"));
        assertEquals(List.of("root", "generation", "retained", "generation", "root"), events);
      }
      events.clear();
      owner.retireReadyAfter(() -> events.add("before"), () -> events.add("after"));
      assertEquals(1, events.stream().filter(FIXTURE_RETIRE_A2A9D4FF::equals).count());
      assertTrue(events.indexOf("before") < events.indexOf(FIXTURE_RETIRE_A2A9D4FF));
      assertTrue(events.indexOf(FIXTURE_RETIRE_A2A9D4FF) < events.indexOf("after"));
      assertThrows(IOException.class, () -> owner.retireReadyAfter(() -> fail(), () -> fail()));
      assertThrows(IOException.class, () -> owner.requireRetained(() -> fail()));
    }
  }

  @Test
  void parent455006PreFailurePreservesIntentPostFailureNeverRepeats() throws Exception {
    var events = new ArrayList<String>();
    var owner = attempt(MaintenanceUnit.WEB, events);
    var fault = new IOException("fixed readiness drift");
    assertSame(
        fault,
        assertThrows(
            IOException.class,
            () ->
                owner.retireReadyAfter(
                    () -> {
                      throw fault;
                    },
                    () -> fail())));
    assertFalse(events.contains(FIXTURE_RETIRE_A2A9D4FF));
    assertSame(
        fault,
        assertThrows(
            IOException.class,
            () ->
                owner.retireReadyAfter(
                    () -> {},
                    () -> {
                      throw fault;
                    })));
    assertEquals(1, events.stream().filter(FIXTURE_RETIRE_A2A9D4FF::equals).count());
    assertThrows(IOException.class, () -> owner.retireReadyAfter(() -> fail(), () -> fail()));
    assertThrows(NullPointerException.class, () -> owner.retireReadyAfter(null, () -> {}));
    assertThrows(NullPointerException.class, () -> owner.retireReadyAfter(() -> {}, null));
    assertThrows(NullPointerException.class, () -> owner.requireRetained(null));
  }

  @Test
  void parent455007WorkerIntentCannotUseLiveReadyContract() throws Exception {
    for (var unit :
        List.of(
            MaintenanceUnit.BACKUP,
            MaintenanceUnit.CLEANUP,
            MaintenanceUnit.EXPIRY,
            MaintenanceUnit.INSPECTOR,
            MaintenanceUnit.ARTEMIS)) {
      var events = new ArrayList<String>();
      var owner = attempt(unit, events);
      assertThrows(IOException.class, () -> owner.requireRetained(() -> fail()));
      assertThrows(IOException.class, () -> owner.retireReadyAfter(() -> fail(), () -> fail()));
      assertFalse(events.contains(FIXTURE_RETIRE_A2A9D4FF));
    }
  }
}
