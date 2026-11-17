package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/PG337; PT-OPS-MTERMS001-005. */
final class MorningUnitTerminalsTest {
  @Test
  void issuerGate002CapturesOrderedEightUnderSameMorningActor() throws Exception {
    var f = new RootStartupContextTest.Fixture();
    f.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    f.unit = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
    var context = f.context();
    var parent = context.capture(RootStartupContext.Service.MORNING);
    var seen = new ArrayList<MaintenanceUnit>();
    var actual =
        MorningUnitTerminals.capture(
            context,
            parent,
            unit -> {
              seen.add(unit);
              var terminal = new MaintenanceUnitTerminationTest.Fixture();
              terminal.target = unit;
              terminal.name = unit.serviceName();
              var value = terminal.adapter().quiescentObservation();
              terminal.closed();
              return value;
            });
    assertSame(parent, actual.parent());
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
    assertEquals(seen, actual.units().stream().map(row -> row.manager().unit()).toList());
    assertThrows(UnsupportedOperationException.class, () -> actual.units().clear());
    assertEquals("MorningStopSet[actual=<redacted>]", actual.toString());
    assertThrows(
        IOException.class,
        () -> MorningUnitTerminals.capture(context, parent, unit -> java.util.Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> MorningUnitTerminals.capture(context, parent, unit -> null));
    assertThrows(
        NullPointerException.class, () -> MorningUnitTerminals.capture(context, parent, null));
    var wrong = new MaintenanceUnitTerminationTest.Fixture().adapter().quiescentObservation();
    assertThrows(
        IOException.class, () -> MorningUnitTerminals.capture(context, parent, unit -> wrong));
  }

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
