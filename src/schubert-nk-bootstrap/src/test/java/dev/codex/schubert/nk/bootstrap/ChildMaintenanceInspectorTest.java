package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SSC119/018-289 CINSPECT001..004: independent manager and two actual actor vectors. */
final class ChildMaintenanceInspectorTest {
  private static final UUID BOOT = UUID.fromString("11111111-1111-4111-8111-111111111111");
  private static final String INV = "7".repeat(32);
  private static final FixedServiceIdentity.Value FIXED =
      new FixedServiceIdentity.Value(200, 201, List.of(200L, 201L, 202L));

  @Test
  void wrapperAndJavaAreDifferentButSameRestrictedUnitGeneration() throws Exception {
    var f = new Fixture();
    var result = new ChildStartupContext(f).verifyInspector(BOOT, INV, FIXED);
    assertEquals(44, result.child().pid());
    assertEquals(43, result.wrapper().pid());
    assertEquals(12346, result.child().startTicks());
    assertEquals(12345, result.wrapper().startTicks());
    assertEquals(INV, result.invocation());
    assertEquals("InspectorIdentity[REDACTED]", result.toString());
    for (byte[] bytes : f.owned) assertArrayEquals(new byte[bytes.length], bytes);
  }

  @Test
  void unprivilegedCallerStillRequiresExactOwnAndWrapperIdentity() {
    for (String fault :
        List.of(
            "uid",
            "gid",
            "groups",
            "caps",
            "nnp",
            "group",
            "boot",
            "wrapperUid",
            "wrapperGroup",
            "wrapperDead",
            "wrapperDrift",
            "childDrift",
            "managerDrift",
            "samePid",
            "badPid",
            "invocation",
            "unit",
            "loaded",
            "inactive",
            "sub",
            "managerGroup",
            "unknownField",
            "duplicate",
            "badLine",
            "io",
            "null",
            "unknown")) {
      var f = new Fixture();
      f.fault = fault;
      if (fault.equals("null"))
        assertThrows(
            NullPointerException.class,
            () -> new ChildStartupContext(f).verifyInspector(BOOT, INV, FIXED));
      else if (fault.equals("unknown"))
        assertSame(
            f.unknown,
            assertThrows(
                IllegalStateException.class,
                () -> new ChildStartupContext(f).verifyInspector(BOOT, INV, FIXED)));
      else {
        var error =
            assertThrows(
                IOException.class,
                () -> new ChildStartupContext(f).verifyInspector(BOOT, INV, FIXED),
                fault);
        assertEquals("child startup context unavailable", error.getMessage());
        assertNull(error.getCause());
        assertEquals(0, error.getSuppressed().length);
      }
      for (byte[] bytes : f.owned) assertArrayEquals(new byte[bytes.length], bytes);
    }
    var context = new ChildStartupContext(new Fixture());
    assertThrows(IOException.class, () -> context.verifyInspector(BOOT, "0".repeat(32), FIXED));
    assertThrows(NullPointerException.class, () -> context.verifyInspector(null, INV, FIXED));
    assertThrows(NullPointerException.class, () -> context.verifyInspector(BOOT, null, FIXED));
    assertThrows(NullPointerException.class, () -> context.verifyInspector(BOOT, INV, null));
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, () -> context.verifyInspector(BOOT, INV, FIXED));
    } finally {
      Thread.interrupted();
    }
  }

  private static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  @Test
  void cinspect005TerminalInterruptPidOneAndCapturedUidDifferentFromNssDeny() {
    for (String fault : List.of("pidOne", "ownUid", "terminalInterrupt")) {
      var fixture = new Fixture();
      fixture.fault = fault;
      try {
        var error =
            assertThrows(
                IOException.class,
                () -> new ChildStartupContext(fixture).verifyInspector(BOOT, INV, FIXED),
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

  private static final class Fixture implements ChildStartupContext.Io {
    String fault = "";
    int managerReads;
    int childReads;
    int wrapperReads;
    final List<byte[]> owned = new ArrayList<>();
    final IllegalStateException unknown = new IllegalStateException("private unknown");

    public long pid() {
      return 44;
    }

    public long uid() {
      return fault.equals("uid") || fault.equals("ownUid") ? 201 : 200;
    }

    public String filesystem() {
      return "proc";
    }

    public byte[] boot() {
      return bytes(
          (fault.equals("boot") ? UUID.fromString("22222222-2222-4222-8222-222222222222") : BOOT)
              + "\n");
    }

    public byte[] stat(long pid) {
      assertTrue(pid == 43 || pid == 44);
      int read = pid == 43 ? ++wrapperReads : ++childReads;
      boolean drift = read > 1 && fault.equals(pid == 43 ? "wrapperDrift" : "childDrift");
      return bytes(
          pid
              + " (owned actor) "
              + (pid == 43 && fault.equals("wrapperDead") ? "Z " : "S ")
              + "0 ".repeat(18)
              + (pid == 43 ? (drift ? 12347 : 12345) : (drift ? 12347 : 12346))
              + "\n");
    }

    public byte[] status(long pid) {
      String result =
          "Uid:\t200 200 200 200\nGid:\t201 201 201 201\nGroups:\t200 201 202\n"
              + "CapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\n"
              + "CapBnd:\t0000000000000000\nCapAmb:\t0000000000000000\nNoNewPrivs:\t1\n";
      if (fault.equals("gid")) result = result.replace("201 201 201 201", "202 202 202 202");
      if (fault.equals("wrapperUid") && pid == 43)
        result = result.replace("200 200 200 200", "201 201 201 201");
      if (fault.equals("ownUid")) result = result.replace("200 200 200 200", "201 201 201 201");
      if (fault.equals("groups")) result = result.replace("200 201 202", "200 201 203");
      if (fault.equals("caps"))
        result = result.replace("CapEff:\t0000000000000000", "CapEff:\t0000000000000001");
      if (fault.equals("nnp")) result = result.replace("NoNewPrivs:\t1", "NoNewPrivs:\t0");
      return bytes(result);
    }

    public byte[] cgroup(long pid) {
      return bytes(
          fault.equals("group") || (fault.equals("wrapperGroup") && pid == 43)
              ? "0::/system.slice/schubert-nk-api.service\n"
              : "0::/system.slice/schubert-nk-inbox-inspector.service\n");
    }

    public byte[] inspectorUnit() throws IOException {
      managerReads++;
      if (fault.equals("io")) throw new IOException("private manager diagnostics");
      if (fault.equals("null")) return null;
      if (fault.equals("unknown")) throw unknown;
      String text =
          "Id=schubert-nk-inbox-inspector.service\nLoadState=loaded\nActiveState=activating\n"
              + "SubState=start\nMainPID=43\nInvocationID="
              + INV
              + "\nControlGroup=/system.slice/schubert-nk-inbox-inspector.service\n";
      text =
          switch (fault) {
            case "samePid" -> text.replace("MainPID=43", "MainPID=44");
            case "pidOne" -> text.replace("MainPID=43", "MainPID=1");
            case "badPid" -> text.replace("MainPID=43", "MainPID=01");
            case "invocation" -> text.replace(INV, "8".repeat(32));
            case "unit" ->
                text.replace(
                    "Id=schubert-nk-inbox-inspector.service", "Id=schubert-nk-api.service");
            case "loaded" -> text.replace("LoadState=loaded", "LoadState=not-found");
            case "inactive" -> text.replace("ActiveState=activating", "ActiveState=inactive");
            case "sub" -> text.replace("SubState=start", "SubState=exited");
            case "managerGroup" ->
                text.replace(
                    "ControlGroup=/system.slice/schubert-nk-inbox-inspector.service",
                    "ControlGroup=/wrong");
            case "unknownField" -> text + "Unknown=1\n";
            case "duplicate" -> text + "MainPID=43\n";
            case "badLine" -> text + "BadLine\n";
            case "managerDrift" -> managerReads > 1 ? text.replace(INV, "8".repeat(32)) : text;
            default -> text;
          };
      byte[] received = bytes(text);
      owned.add(received);
      if (fault.equals("terminalInterrupt") && managerReads == 2)
        Thread.currentThread().interrupt();
      return received;
    }
  }
}
