package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SS342 SSC186; PT-OPS-CADDYFENCE001..003. Independent literal ownership order. */
final class CaddyAdmissionFenceTest {
  private static final List<String> ORDER =
      List.of(
          "full",
          "API-context",
          "owner",
          "API-marker",
          "owner",
          "API-context",
          "WEB-context",
          "owner",
          "WEB-marker",
          "owner",
          "WEB-context",
          "full");

  @FunctionalInterface
  interface Check {
    void run(String event) throws IOException;
  }

  static BackupUnitStartClient.Attempt attempt(MaintenanceUnit unit, Check check, int[] starts)
      throws IOException {
    var child = new InspectorUnitProbeFixture.Child(new byte[0]);
    child.waitSeconds = 120;
    return new BackupUnitStartClient(
            () -> check.run(unit.name() + "-context"),
            () -> {},
            command -> {
              starts[0]++;
              assertEquals(unit.serviceName(), command.getLast());
              return child;
            },
            () ->
                new BackupUnitStartClient.MarkerLease() {
                  public void retire() {
                    fail("admission cannot retire");
                  }

                  public void requireRetained() throws IOException {
                    check.run(unit.name() + "-marker");
                  }

                  public void closeObservation() {}
                },
            unit,
            Optional.empty())
        .start();
  }

  @Test
  void caddyfence001FullPeerDbChecksBracketBothPureOwnersWithoutReentry() throws Exception {
    var events = new ArrayList<String>();
    var starts = new int[1];
    boolean[] armed = {false};
    Check check =
        e -> {
          if (armed[0]) events.add(e);
        };
    var api = attempt(MaintenanceUnit.API, check, starts);
    var web = attempt(MaintenanceUnit.WEB, check, starts);
    var fence =
        BackupUnitStartClient.caddyAdmissionFence(
            () -> check.run("full"), () -> check.run("owner"), api, web);
    armed[0] = true;
    fence.verify();
    assertEquals(ORDER, events);
    assertEquals(2, Collections.frequency(events, "full"));
    assertEquals(4, Collections.frequency(events, "owner"));
    assertEquals(2, starts[0]);
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, api.status());
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, web.status());
  }

  @Test
  void caddyfence002EveryBeforeMarkerAndAfterFaultPreservesIdentityAndStopsLaterChecks()
      throws Exception {
    for (int point = 0; point < ORDER.size(); point++)
      for (Throwable fault :
          List.of(
              new IOException("independent-io"),
              new IllegalStateException("independent-runtime"),
              new AssertionError("independent-error"))) {
        int failAt = point;
        var events = new ArrayList<String>();
        var starts = new int[1];
        boolean[] armed = {false};
        Check check =
            e -> {
              if (!armed[0]) return;
              events.add(e);
              if (events.size() == failAt + 1) {
                if (fault instanceof IOException io) throw io;
                if (fault instanceof RuntimeException runtime) throw runtime;
                throw (Error) fault;
              }
            };
        var api = attempt(MaintenanceUnit.API, check, starts);
        var web = attempt(MaintenanceUnit.WEB, check, starts);
        var fence =
            BackupUnitStartClient.caddyAdmissionFence(
                () -> check.run("full"), () -> check.run("owner"), api, web);
        armed[0] = true;
        assertSame(fault, assertThrows(fault.getClass(), fence::verify));
        assertEquals(ORDER.subList(0, failAt + 1), events);
        assertEquals(2, starts[0]);
      }
  }

  @Test
  void caddyfence003NullWrongRoleAndCloseOnlyIntentCannotPassAdmission() throws Exception {
    var starts = new int[1];
    Check check = e -> {};
    var api = attempt(MaintenanceUnit.API, check, starts);
    var web = attempt(MaintenanceUnit.WEB, check, starts);
    BackupUnitStartClient.RetirementGate gate = () -> {};
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitStartClient.caddyAdmissionFence(null, gate, api, web));
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitStartClient.caddyAdmissionFence(gate, null, api, web));
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitStartClient.caddyAdmissionFence(gate, gate, null, web));
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitStartClient.caddyAdmissionFence(gate, gate, api, null));
    assertThrows(
        IOException.class, () -> BackupUnitStartClient.caddyAdmissionFence(gate, gate, web, web));
    assertThrows(
        IOException.class, () -> BackupUnitStartClient.caddyAdmissionFence(gate, gate, api, api));
    var fence = BackupUnitStartClient.caddyAdmissionFence(gate, gate, api, web);
    api.preserveObservation();
    assertThrows(IOException.class, fence::verify);
    assertEquals(2, starts[0]);
  }
}
