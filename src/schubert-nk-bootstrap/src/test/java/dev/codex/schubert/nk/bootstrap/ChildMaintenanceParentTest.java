package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SSC119/BUG356: independent manager/kernel parent vectors, no root authority from claims. */
class ChildMaintenanceParentTest {
  private static final String FIXTURE_UNKNOWN_EB8BF0D8 = "unknown";
  private static final UUID BOOT = UUID.fromString("11111111-1111-4111-8111-111111111111");

  /** PT-OPS-MANAGER4404-003: internal key order is not an external wire oracle. */
  @Test
  void eitherStablePropertyOrderKeepsAllParentValuesAndBothFreshReads() throws Exception {
    for (var kind : ChildStartupContext.MaintenanceParent.values()) {
      for (boolean swapped : List.of(false, true)) {
        var fixture = new Fixture();
        fixture.swappedOrder = swapped;
        new ChildStartupContext(fixture).verifyMaintenanceParent(kind, owner());
        assertEquals(2, fixture.units);
        assertEquals(2, fixture.owned.size());
        for (byte[] value : fixture.owned) assertArrayEquals(new byte[value.length], value);
      }
    }
  }

  /** PT-OPS-MANAGER4404-004: canonical cross-implementation comparison never hides live drift. */
  @Test
  void orderingDriftBetweenTheTwoLiveReadsStillFailsClosed() {
    for (var kind : ChildStartupContext.MaintenanceParent.values()) {
      var fixture = new Fixture();
      fixture.orderDrift = true;
      assertThrows(
          IOException.class,
          () -> new ChildStartupContext(fixture).verifyMaintenanceParent(kind, owner()));
      assertEquals(2, fixture.units);
      for (byte[] value : fixture.owned) assertArrayEquals(new byte[value.length], value);
    }
  }

  @Test
  void existingEmptySupplementaryRootGroupsAreNotMissingOrInventedPrimaryGroup() throws Exception {
    for (var kind : ChildStartupContext.MaintenanceParent.values()) {
      for (String groups : List.of("", "0", "7", "0 7")) {
        var fixture = new Fixture();
        fixture.groups = groups;
        new ChildStartupContext(fixture).verifyMaintenanceParent(kind, owner());
        assertEquals(2, fixture.owned.size()); // Two manager reads for one parent, not two parents.
        for (byte[] bytes : fixture.owned) assertArrayEquals(new byte[bytes.length], bytes);
      }
      for (String groups :
          List.of(
              "0 0", "-1", FIXTURE_UNKNOWN_EB8BF0D8, "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16")) {
        var fixture = new Fixture();
        fixture.groups = groups;
        assertThrows(
            IOException.class,
            () -> new ChildStartupContext(fixture).verifyMaintenanceParent(kind, owner()));
      }
      var missing = new Fixture();
      missing.missingGroups = true;
      assertThrows(
          IOException.class,
          () -> new ChildStartupContext(missing).verifyMaintenanceParent(kind, owner()));
    }
  }

  @Test
  void bothFixedLiveRootParentsWithSameKernelGeneration() throws Exception {
    var fixture = new Fixture();
    var context = new ChildStartupContext(fixture);
    context.verifyMaintenanceParent(ChildStartupContext.MaintenanceParent.MORNING, owner());
    context.verifyMaintenanceParent(ChildStartupContext.MaintenanceParent.CLEANUP, owner());
    for (byte[] owned : fixture.owned) assertArrayEquals(new byte[owned.length], owned);
    assertEquals(4, fixture.owned.size());
  }

  @Test
  void stoppedOldWrongOwnerAndUnknownManagerNeverBecomeLive() {
    for (String fault :
        new String[] {
          "uid",
          "gid",
          "boot",
          "pid",
          "ticks",
          "zombie",
          "group",
          "nnp",
          "unit",
          "invocation",
          "inactive",
          "managerPid",
          "managerGroup",
          "loaded",
          "extra",
          "duplicate",
          "malformed",
          "managerDrift",
          "io",
          "kernelDrift",
          "null",
          FIXTURE_UNKNOWN_EB8BF0D8
        }) {
      var f = new Fixture();
      f.fault = fault;
      var context = new ChildStartupContext(f);
      if (fault.equals("null")) {
        assertThrows(
            NullPointerException.class,
            () ->
                context.verifyMaintenanceParent(
                    ChildStartupContext.MaintenanceParent.MORNING, owner()));
      } else if (fault.equals(FIXTURE_UNKNOWN_EB8BF0D8)) {
        assertSame(
            f.unknown,
            assertThrows(
                IllegalStateException.class,
                () ->
                    context.verifyMaintenanceParent(
                        ChildStartupContext.MaintenanceParent.MORNING, owner())));
      } else {
        var error =
            assertThrows(
                IOException.class,
                () ->
                    context.verifyMaintenanceParent(
                        ChildStartupContext.MaintenanceParent.MORNING, owner()));
        assertEquals("child startup context unavailable", error.getMessage());
        assertNull(error.getCause());
      }
      for (byte[] owned : f.owned) assertArrayEquals(new byte[owned.length], owned);
    }
    var context = new ChildStartupContext(new Fixture());
    assertThrows(NullPointerException.class, () -> context.verifyMaintenanceParent(null, owner()));
    assertThrows(
        NullPointerException.class,
        () -> context.verifyMaintenanceParent(ChildStartupContext.MaintenanceParent.MORNING, null));
    var noCleanup =
        new MaintenanceOwnerFrame(
            owner().boot(),
            owner().run(),
            owner().activation(),
            owner().cutoff(),
            owner().epoch(),
            owner().morning(),
            Optional.empty(),
            owner().deadlineNanos());
    assertThrows(
        IOException.class,
        () ->
            context.verifyMaintenanceParent(
                ChildStartupContext.MaintenanceParent.CLEANUP, noCleanup));
    Thread.currentThread().interrupt();
    try {
      assertThrows(
          IOException.class,
          () ->
              context.verifyMaintenanceParent(
                  ChildStartupContext.MaintenanceParent.MORNING, owner()));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }

  private static MaintenanceOwnerFrame owner() {
    return new MaintenanceOwnerFrame(
        BOOT,
        UUID.fromString("22222222-2222-4222-8222-222222222222"),
        UUID.fromString("33333333-3333-4333-8333-333333333333"),
        Instant.parse("2026-09-27T15:00:00Z"),
        UUID.fromString("44444444-4444-4444-8444-444444444444"),
        new MaintenanceOwnerFrame.Parent("5".repeat(32), 42, 12345),
        Optional.of(new MaintenanceOwnerFrame.Parent("6".repeat(32), 43, 23456)),
        1_800_000_000_007L);
  }

  @Test
  void cparent005TerminalInterruptAndWrongSubstateCannotBecomeLiveRoot() {
    for (var kind : ChildStartupContext.MaintenanceParent.values()) {
      for (String fault : List.of("substate", "terminalInterrupt")) {
        var fixture = new Fixture();
        fixture.fault = fault;
        try {
          var error =
              assertThrows(
                  IOException.class,
                  () -> new ChildStartupContext(fixture).verifyMaintenanceParent(kind, owner()),
                  fault);
          assertEquals("child startup context unavailable", error.getMessage());
          assertNull(error.getCause());
          assertEquals(fault.equals("terminalInterrupt"), Thread.currentThread().isInterrupted());
          for (byte[] buffer : fixture.owned) assertArrayEquals(new byte[buffer.length], buffer);
        } finally {
          Thread.interrupted();
        }
      }
    }
  }

  static final class Fixture implements ChildStartupContext.Io {
    String fault = "";
    String groups = "0";
    boolean missingGroups;
    boolean swappedOrder;
    boolean orderDrift;
    final IllegalStateException unknown = new IllegalStateException("PRIVATE unknown");
    final List<byte[]> owned = new ArrayList<>();
    int units;
    int stats;

    public long pid() {
      return 200;
    }

    public long uid() {
      return 300;
    }

    public String filesystem() {
      return "proc";
    }

    public byte[] boot() {
      return bytes(
          (fault.equals("boot") ? "77777777-7777-4777-8777-777777777777" : BOOT.toString()) + "\n");
    }

    public byte[] stat(long pid) {
      stats++;
      return bytes(
          (fault.equals("pid") ? 99 : pid)
              + " (root owner) "
              + (fault.equals("zombie") ? "Z" : "S")
              + " "
              + "0 ".repeat(18)
              + (fault.equals("ticks") || (fault.equals("kernelDrift") && stats > 1)
                  ? 999
                  : pid == 42 ? 12345 : 23456)
              + " 0\n");
    }

    public byte[] status(long pid) {
      return bytes(
          "Uid:"
              + (fault.equals("uid") ? "1 1 1 1" : "0 0 0 0")
              + "\nGid:"
              + (fault.equals("gid") ? "1 1 1 1" : "0 0 0 0")
              + (missingGroups ? "\n" : "\nGroups:" + groups + "\n")
              + "CapInh:0000000000000000\nCapPrm:0000000000000001\nCapEff:0000000000000001\nCapBnd:0000000000000001\nCapAmb:0000000000000000\nNoNewPrivs:"
              + (fault.equals("nnp") ? "0" : "1")
              + "\n");
    }

    public byte[] cgroup(long pid) {
      return bytes(
          "0::/system.slice/"
              + (fault.equals("group")
                  ? "other.service"
                  : pid == 42
                      ? "schubert-nk-morning-controller.service"
                      : "schubert-nk-cleanup.service")
              + "\n");
    }

    public byte[] maintenanceUnit(ChildStartupContext.MaintenanceParent kind) throws IOException {
      if (fault.equals("io")) throw new IOException("PRIVATE provider cause");
      if (fault.equals("null")) return null;
      if (fault.equals(FIXTURE_UNKNOWN_EB8BF0D8)) throw unknown;
      units++;
      boolean morning = kind == ChildStartupContext.MaintenanceParent.MORNING;
      String unit =
          morning ? "schubert-nk-morning-controller.service" : "schubert-nk-cleanup.service";
      String text =
          "Id="
              + unit
              + "\nLoadState=loaded\nActiveState=activating\nSubState=start\nMainPID="
              + (morning ? 42 : 43)
              + "\nInvocationID="
              + (morning ? "5" : "6").repeat(32)
              + "\nControlGroup=/system.slice/"
              + unit
              + "\n";
      text =
          switch (fault) {
            case "unit" -> text.replace("Id=" + unit, "Id=other.service");
            case "invocation" -> text.replace("5".repeat(32), "7".repeat(32));
            case "inactive" -> text.replace("ActiveState=activating", "ActiveState=inactive");
            case "substate" -> text.replace("SubState=start", "SubState=exited");
            case "managerPid" -> text.replace("MainPID=42", "MainPID=99");
            case "managerGroup" ->
                text.replace("ControlGroup=/system.slice/" + unit, "ControlGroup=/other");
            case "loaded" -> text.replace("LoadState=loaded", "LoadState=not-found");
            case "extra" -> text + "Unknown=1\n";
            case "duplicate" -> text + "MainPID=42\n";
            case "malformed" -> text + "broken\n";
            case "managerDrift" -> units > 1 ? text.replace("5".repeat(32), "7".repeat(32)) : text;
            default -> text;
          };
      if (swappedOrder || (orderDrift && units > 1)) {
        var lines = new ArrayList<>(List.of(text.split("\n", -1)));
        Collections.swap(lines, 4, 5);
        text = String.join("\n", lines);
      }
      byte[] result = bytes(text);
      owned.add(result);
      if (fault.equals("terminalInterrupt") && units == 2) Thread.currentThread().interrupt();
      return result;
    }

    private static byte[] bytes(String value) {
      return value.getBytes(StandardCharsets.US_ASCII);
    }
  }
}
