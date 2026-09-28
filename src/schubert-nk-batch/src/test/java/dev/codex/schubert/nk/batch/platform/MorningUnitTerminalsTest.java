package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/PG337; PT-OPS-MTERMS001-005. */
final class MorningUnitTerminalsTest {
  @Test
  void mterms001AllEightOrderedAndFresh() throws Exception {
    var seen = new ArrayList<MaintenanceUnit>();
    MorningUnitTerminals.requireQuiescent(
        unit -> {
          seen.add(unit);
          return true;
        });
    assertEquals(
        List.of(
            MaintenanceUnit.CADDY,
            MaintenanceUnit.WEB,
            MaintenanceUnit.API,
            MaintenanceUnit.CLEANUP,
            MaintenanceUnit.INSPECTOR,
            MaintenanceUnit.EXPIRY,
            MaintenanceUnit.BACKUP,
            MaintenanceUnit.ARTEMIS),
        seen);
  }

  @Test
  void mterms002BusyUnitShortCircuitsWithoutSuccess() {
    for (MaintenanceUnit busy : List.of(MaintenanceUnit.CADDY, MaintenanceUnit.ARTEMIS)) {
      var seen = new ArrayList<MaintenanceUnit>();
      IOException refusal =
          assertThrows(
              IOException.class,
              () ->
                  MorningUnitTerminals.requireQuiescent(
                      unit -> {
                        seen.add(unit);
                        return unit != busy;
                      }));
      assertEquals("Morning whole-Unit termination unavailable", refusal.getMessage());
      assertNull(refusal.getCause());
      assertEquals(busy.ordinal() + 1, seen.size());
      assertEquals(busy, seen.getLast());
    }
  }

  @Test
  void mterms003KnownFailureRedactedUnknownIdentityPreserved() {
    var known = new StopGateException(StopGateFailure.NOT_STOPPED);
    IOException refusal =
        assertThrows(
            IOException.class,
            () ->
                MorningUnitTerminals.requireQuiescent(
                    unit -> {
                      throw known;
                    }));
    assertEquals("Morning whole-Unit termination unavailable", refusal.getMessage());
    assertNull(refusal.getCause());
    assertEquals(0, refusal.getSuppressed().length);
    var unknown = new IllegalStateException("unknown programming error");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningUnitTerminals.requireQuiescent(
                    unit -> {
                      throw unknown;
                    })));
    var io = new IOException("fixed observer unavailable");
    assertSame(
        io,
        assertThrows(
            IOException.class,
            () ->
                MorningUnitTerminals.requireQuiescent(
                    unit -> {
                      throw io;
                    })));
  }

  @Test
  void mterms004NullAndWrongActorRejectedBeforeNativeRead() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> MorningUnitTerminals.requireQuiescent((MorningUnitTerminals.Observation) null));
    assertThrows(
        NullPointerException.class, () -> MorningUnitTerminals.requireQuiescent(null, null));
    var fixture = new RootStartupContextTest.Fixture();
    var context = fixture.context();
    var api = context.capture(RootStartupContext.Service.API);
    int before = fixture.reads;
    IOException refusal =
        assertThrows(IOException.class, () -> MorningUnitTerminals.requireQuiescent(context, api));
    assertEquals("Morning whole-Unit termination unavailable", refusal.getMessage());
    assertNull(refusal.getCause());
    assertEquals(before, fixture.reads); // No native manager observation after capture.
  }

  @Test
  void mterms005InterruptBeforeDuringAndAfterObservationPreservesFlag() {
    try {
      Thread.currentThread().interrupt();
      assertThrows(
          IOException.class,
          () -> MorningUnitTerminals.requireQuiescent(unit -> fail("not called")));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    var seen = new ArrayList<MaintenanceUnit>();
    try {
      assertThrows(
          IOException.class,
          () ->
              MorningUnitTerminals.requireQuiescent(
                  unit -> {
                    seen.add(unit);
                    Thread.currentThread().interrupt();
                    return true;
                  }));
      assertEquals(List.of(MaintenanceUnit.CADDY), seen);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    seen.clear();
    try {
      assertThrows(
          IOException.class,
          () ->
              MorningUnitTerminals.requireQuiescent(
                  unit -> {
                    seen.add(unit);
                    if (unit == MaintenanceUnit.ARTEMIS) Thread.currentThread().interrupt();
                    return true;
                  }));
      assertEquals(Arrays.asList(MaintenanceUnit.values()), seen);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }
}
