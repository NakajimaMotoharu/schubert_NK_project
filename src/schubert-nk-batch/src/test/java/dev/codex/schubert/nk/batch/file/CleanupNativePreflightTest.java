package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.MaintenanceStopSnapshot;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS341/343/SSC104/PG335; NCLEAN002..004 ordered public-unit oracle, no DELETE authority. */
final class CleanupNativePreflightTest {
  @Test
  void nclean002WebThenApiMustBothBeFreshAndQuiet() throws Exception {
    var seen = new ArrayList<MaintenanceUnit>();
    CleanupNativePreflight.requireApplicationsStopped(
        unit -> {
          seen.add(unit);
          return true;
        });
    assertEquals(List.of(MaintenanceUnit.WEB, MaintenanceUnit.API), seen);
  }

  @Test
  void nclean003FirstBusyOrSecondBusyStopsImmediately() {
    var seen = new ArrayList<MaintenanceUnit>();
    assertThrows(
        IOException.class,
        () ->
            CleanupNativePreflight.requireApplicationsStopped(
                unit -> {
                  seen.add(unit);
                  return false;
                }));
    assertEquals(List.of(MaintenanceUnit.WEB), seen);
    seen.clear();
    assertThrows(
        IOException.class,
        () ->
            CleanupNativePreflight.requireApplicationsStopped(
                unit -> {
                  seen.add(unit);
                  return unit == MaintenanceUnit.WEB;
                }));
    assertEquals(List.of(MaintenanceUnit.WEB, MaintenanceUnit.API), seen);
  }

  @Test
  void nclean004NullKnownIoAndUnknownRemainNonSuccess() {
    assertThrows(
        NullPointerException.class, () -> CleanupNativePreflight.requireApplicationsStopped(null));
    var known = new IOException("PRIVATE_CANARY");
    assertSame(
        known,
        assertThrows(
            IOException.class,
            () ->
                CleanupNativePreflight.requireApplicationsStopped(
                    unit -> {
                      throw known;
                    })));
    var unknown = new IllegalStateException("PRIVATE_CANARY");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                CleanupNativePreflight.requireApplicationsStopped(
                    unit -> {
                      throw unknown;
                    })));
  }

  @Test
  void nclean005KnownNotFoundStopFailureBecomesFixedSafetyFailure() {
    String notFound =
        "Id=schubert-nk-web.service\nLoadState=not-found\nActiveState=inactive\n"
            + "SubState=dead\nJob=\nMainPID=0\nControlPID=0\nSlice=system.slice\n"
            + "Delegate=no\nControlGroup=\nInvocationID=\nStateChangeTimestampMonotonic=0\n";
    StopGateException fixed =
        assertThrows(
            StopGateException.class,
            () ->
                MaintenanceStopSnapshot.parse(
                    MaintenanceUnit.WEB, notFound.getBytes(StandardCharsets.US_ASCII)));
    var seen = new ArrayList<MaintenanceUnit>();
    IOException denied =
        assertThrows(
            IOException.class,
            () ->
                CleanupNativePreflight.requireApplicationsStopped(
                    unit -> {
                      seen.add(unit);
                      throw fixed;
                    }));
    assertEquals("root cleanup preflight unavailable", denied.getMessage());
    assertNull(denied.getCause());
    assertEquals(List.of(MaintenanceUnit.WEB), seen);
  }
}
