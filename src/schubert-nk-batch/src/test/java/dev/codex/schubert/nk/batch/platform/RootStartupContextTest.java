package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-ROOTCTX-001..009; literal kernel/system manager vector, never production expected. */
final class RootStartupContextTest {
  private static final int FIRST_FIXTURE_SLOT = 1;
  private static final int SECOND_FIXTURE_SLOT = 2;
  private static final int THIRD_FIXTURE_SLOT = 3;
  private static final int NOT_DONE_FIXTURE = 1;
  private static final int NONZERO_EXIT_FIXTURE = 2;
  private static final int INTERRUPTED_WAIT_FIXTURE = 3;
  private static final String FIXTURE_MAINPID_42_0075A51F = "MainPID=42";
  private static final String FIXTURE_MAINPID_200_B6F3F218 = "MainPID=200";
  private static final String FIXTURE_IO_A0EA7E0E = "<IO>";
  private static final String FIXTURE_R_76BC7761 = ") R ";
  private static final String FIXTURE_Z_D3E05587 = ") Z ";
  private static final String FIXTURE_SYNTHETIC_85DA8434 = "synthetic";
  private static final String FIXTURE_PROCESS_B140B547 = "process";
  private static final String FIXTURE_999_A90868B2 = "999";
  private static final String FIXTURE_12345_AFC21EDA = "12345";
  private static final String FIXTURE_STAT_F3E718BA = "stat";
  private static final String FIXTURE_STARTUP_CONTEXT_UNAVAILABLE_1B156CA0 =
      "startup context unavailable";

  /** PT-OPS-ROOTQUERYOWN001: partial getter ownership closes in the old strict order. */
  @Test
  void rootqueryown001GetterNullRuntimeAndFatalKeepExactPartialCleanupOrder() {
    for (int at : List.of(1, 2, 3))
      for (Throwable failure :
          new Throwable[] {
            null,
            new IllegalStateException(FIXTURE_SYNTHETIC_85DA8434),
            new LinkageError(FIXTURE_SYNTHETIC_85DA8434)
          }) {
        var events = new ArrayList<String>();
        var process =
            new FakeProcess() {
              public InputStream getInputStream() {
                if (at == FIRST_FIXTURE_SLOT) {
                  if (failure != null) throwGetter(failure);
                  return null;
                }
                return super.getInputStream();
              }

              public OutputStream getOutputStream() {
                if (at == SECOND_FIXTURE_SLOT) {
                  if (failure != null) throwGetter(failure);
                  return null;
                }
                return super.getOutputStream();
              }

              public InputStream getErrorStream() {
                if (at == THIRD_FIXTURE_SLOT) {
                  if (failure != null) throwGetter(failure);
                  return null;
                }
                return super.getErrorStream();
              }

              public void destroy() {
                events.add(FIXTURE_PROCESS_B140B547);
                super.destroy();
              }
            };
        process.alive = true;
        process.output =
            new ByteArrayInputStream(bytes("PUBLIC\n")) {
              public void close() {
                events.add("stdout");
              }
            };
        process.input =
            new ByteArrayOutputStream() {
              public void close() {
                events.add("stdin");
              }
            };
        process.error =
            new ByteArrayInputStream(new byte[0]) {
              public void close() {
                events.add("stderr");
              }
            };
        Class<? extends Throwable> expected =
            failure == null ? NullPointerException.class : failure.getClass();
        Throwable actual =
            assertThrows(
                expected,
                () ->
                    new RootStartupContext.NativeIo(command -> process)
                        .unit(RootStartupContext.Service.API));
        if (failure != null) assertSame(failure, actual);
        assertEquals(
            switch (at) {
              case 1 -> List.of(FIXTURE_PROCESS_B140B547);
              case 2 -> List.of("stdout", FIXTURE_PROCESS_B140B547);
              default -> List.of("stdin", "stdout", FIXTURE_PROCESS_B140B547);
            },
            events);
        assertEquals(1, process.destroyed);
      }
  }

  private static void throwGetter(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  /** PT-OPS-ROOTQUERYOWN002: factory failures are not body IO, and never yield a held process. */
  @Test
  void rootqueryown002FactoryIoRuntimeFatalAndNullNeverBecomeAProcessOwner() {
    for (Throwable failure :
        new Throwable[] {
          new IOException(FIXTURE_SYNTHETIC_85DA8434),
          new IllegalStateException(FIXTURE_SYNTHETIC_85DA8434),
          new LinkageError(FIXTURE_SYNTHETIC_85DA8434),
          null
        }) {
      int[] opens = {0};
      var io =
          new RootStartupContext.NativeIo(
              command -> {
                opens[0]++;
                if (failure instanceof IOException known) throw known;
                if (failure != null) throwGetter(failure);
                return null;
              });
      Class<? extends Throwable> expected =
          failure == null ? NullPointerException.class : failure.getClass();
      Throwable actual =
          assertThrows(expected, () -> io.unitDeadline(RootStartupContext.Service.API));
      if (failure != null) assertSame(failure, actual);
      assertEquals(1, opens[0]);
    }
  }

  // ROOTLAUNCH001..006: the fixed other-Root query is authenticated by the same Morning self.
  static class LaunchFixture extends Fixture {
    RootStartupContext.Service target = RootStartupContext.Service.API;
    String targetUnit;
    String targetGroup;
    String targetStat = RootStartupContextTest.stat(200, FIXTURE_999_A90868B2);
    long rootUid;
    int targetReads;
    boolean targetDrift;

    LaunchFixture() {
      group = "0::/system.slice/schubert-nk-morning-controller.service\n";
      unitValues = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
      targetUnit =
          RootStartupContextTest.unit(target)
              .replace(FIXTURE_MAINPID_42_0075A51F, FIXTURE_MAINPID_200_B6F3F218)
              .replace(INV, "2".repeat(32));
      targetGroup = "0::/system.slice/" + target.unit() + "\n";
    }

    @Override
    public byte[] unit(RootStartupContext.Service service) throws IOException {
      if (service == RootStartupContext.Service.MORNING) return super.unit(service);
      assertEquals(target, service);
      targetReads++;
      return bytes(
          targetDrift && targetReads > 1
              ? targetUnit.replace(FIXTURE_MAINPID_200_B6F3F218, "MainPID=201")
              : targetUnit);
    }

    @Override
    public byte[] stat(long value) throws IOException {
      if (value == 200 && targetStat.equals("<MISSING>"))
        throw new java.nio.file.NoSuchFileException("PUBLIC_FIXED_PROC");
      if (value == 200 && targetStat.equals(FIXTURE_IO_A0EA7E0E))
        throw new IOException("PUBLIC_FIXED_IO");
      return value == 200 ? bytes(targetStat) : super.stat(value);
    }

    @Override
    public byte[] cgroup(long value) throws IOException {
      return value == 200 ? bytes(targetGroup) : super.cgroup(value);
    }

    @Override
    public long serviceRootUid(long value) {
      assertEquals(200, value);
      return rootUid;
    }
  }

  @Test
  void rootServiceDeadlineUsesActualUnitStartNotNewBudget() throws Exception {
    String literal =
        "Id=schubert-nk-api.service\nInvocationID="
            + INV
            + "\nMainPID=42\nExecMainStartTimestampMonotonic=1000000\n";
    var f =
        new Fixture() {
          public byte[] unitDeadline(RootStartupContext.Service service) {
            assertEquals(RootStartupContext.Service.API, service);
            return bytes(literal);
          }
        };
    var root = f.context();
    var self = root.capture(RootStartupContext.Service.API);
    assertEquals(121_000_000_000L, root.serviceRootDeadline(self, 200_000_000_000L));
    assertEquals(120_000_000_000L, root.serviceRootDeadline(self, 120_000_000_000L));
    assertThrows(IOException.class, () -> root.serviceRootDeadline(self, 1_000_000_000L));
    assertThrows(IOException.class, () -> root.serviceRootDeadline(self, 0));
    assertThrows(NullPointerException.class, () -> root.serviceRootDeadline(null, Long.MAX_VALUE));
  }

  @Test
  void ordinaryGenerationKeepsRootUidCaptureStrictAndBorrowsOriginalDeadline() throws Exception {
    var f =
        new LaunchFixture() {
          public byte[] unitDeadline(RootStartupContext.Service service) {
            assertEquals(RootStartupContext.Service.API, service);
            return bytes(
                "Id=schubert-nk-api.service\nInvocationID="
                    + "2".repeat(32)
                    + "\nMainPID=200\nExecMainStartTimestampMonotonic=1000000\n");
          }
        };
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    var child = root.captureServiceRoot(morning, RootStartupContext.Service.API);
    f.rootUid = 999;
    assertThrows(
        IOException.class, () -> root.captureServiceRoot(morning, RootStartupContext.Service.API));
    root.recheckServiceGeneration(morning, child);
    assertEquals(
        121_000_000_000L, root.serviceGenerationDeadline(morning, child, 200_000_000_000L));
    assertEquals(
        120_000_000_000L, root.serviceGenerationDeadline(morning, child, 120_000_000_000L));
    assertThrows(
        IOException.class, () -> root.serviceGenerationDeadline(morning, child, 1_000_000_000L));
    assertThrows(IOException.class, () -> root.serviceGenerationDeadline(morning, child, 0));
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, morning));
    assertThrows(NullPointerException.class, () -> root.recheckServiceGeneration(null, child));
    assertThrows(NullPointerException.class, () -> root.recheckServiceGeneration(morning, null));
    f.targetStat = stat(200, "1000");
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
    f.targetStat = stat(200, FIXTURE_999_A90868B2);
    f.targetDrift = true;
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
  }

  /** PT-OPS-EXECGEN309001: Linux nonleader exec can expose Z without losing the generation. */
  @Test
  void execgen309001TransientZombieIsPendingGenerationNeverAnExit() throws Exception {
    for (var service : List.of(RootStartupContext.Service.API, RootStartupContext.Service.WEB)) {
      var f = new LaunchFixture();
      f.target = service;
      f.targetUnit =
          unit(service)
              .replace(FIXTURE_MAINPID_42_0075A51F, FIXTURE_MAINPID_200_B6F3F218)
              .replace(INV, "2".repeat(32));
      f.targetGroup = "0::/system.slice/" + service.unit() + "\n";
      var root = f.context();
      var morning = root.capture(RootStartupContext.Service.MORNING);
      var child = root.captureServiceRoot(morning, service);
      f.targetStat =
          stat(200, FIXTURE_999_A90868B2).replace(FIXTURE_R_76BC7761, FIXTURE_Z_D3E05587);
      assertDoesNotThrow(() -> root.recheckServiceGeneration(morning, child));
      assertFalse(root.serviceGenerationExited(morning, child));
      f.targetStat = stat(200, FIXTURE_999_A90868B2);
      f.rootUid = 999;
      root.recheckServiceGeneration(morning, child);
      assertFalse(root.serviceGenerationExited(morning, child));
      f.targetStat = "<MISSING>";
      assertTrue(root.serviceGenerationExited(morning, child));
    }
  }

  /** PT-OPS-EXECGEN309002: a pending state grants neither Root admission nor foreign ownership. */
  @Test
  void execgen309002StrictCaptureAndForeignGenerationRemainRejected() throws Exception {
    var f = new LaunchFixture();
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    var child = root.captureServiceRoot(morning, RootStartupContext.Service.API);
    for (String state : List.of("Z", "X", "x", "?", "ZZ")) {
      f.targetStat =
          stat(200, FIXTURE_999_A90868B2).replace(FIXTURE_R_76BC7761, ") " + state + " ");
      assertThrows(IOException.class, () -> root.captureServiceRoot(morning, f.target));
      if (!state.equals("Z")) {
        assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
        assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, child));
      }
    }
    f.targetStat = stat(200, "1000").replace(FIXTURE_R_76BC7761, FIXTURE_Z_D3E05587);
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
    assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, child));
    f.targetStat = stat(200, FIXTURE_999_A90868B2).replace(FIXTURE_R_76BC7761, FIXTURE_Z_D3E05587);
    f.targetGroup = "0::/system.slice/foreign.service\n";
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
    f.targetGroup = "0::/system.slice/schubert-nk-api.service\n";
    f.targetDrift = true;
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
    f.targetDrift = false;
    f.own = stat(42, FIXTURE_12345_AFC21EDA).replace(FIXTURE_R_76BC7761, FIXTURE_Z_D3E05587);
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
    f.own = stat(42, FIXTURE_12345_AFC21EDA);
    f.init = stat(1, "5").replace(FIXTURE_R_76BC7761, FIXTURE_Z_D3E05587);
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, child));
  }

  @Test
  void capturedServicePidMustReallyDisappearAndIoOrReuseNeverBecomesTerminal() throws Exception {
    var f = new LaunchFixture();
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    var child = root.captureServiceRoot(morning, RootStartupContext.Service.API);
    assertFalse(root.serviceGenerationExited(morning, child));
    f.targetStat = "<MISSING>";
    assertTrue(root.serviceGenerationExited(morning, child));
    f.targetStat = FIXTURE_IO_A0EA7E0E;
    assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, child));
    f.targetStat = stat(200, "1000");
    assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, child));
    assertThrows(NullPointerException.class, () -> root.serviceGenerationExited(null, child));
    assertThrows(NullPointerException.class, () -> root.serviceGenerationExited(morning, null));
    assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, morning));
  }

  @Test
  void morningCapturesOnlyActualFixedServiceRootGeneration() throws Exception {
    for (var target : List.of(RootStartupContext.Service.API, RootStartupContext.Service.WEB)) {
      var f = new LaunchFixture();
      f.target = target;
      f.targetUnit =
          unit(target)
              .replace(FIXTURE_MAINPID_42_0075A51F, FIXTURE_MAINPID_200_B6F3F218)
              .replace(INV, "2".repeat(32));
      f.targetGroup = "0::/system.slice/" + target.unit() + "\n";
      var context = f.context();
      var morning = context.capture(RootStartupContext.Service.MORNING);
      var actual = context.captureServiceRoot(morning, target);
      assertEquals(target, actual.service());
      assertEquals(BOOT.trim(), actual.boot());
      assertEquals("2".repeat(32), actual.invocation());
      assertEquals(200, actual.pid());
      assertEquals(999, actual.startTicks());
      assertEquals(5, actual.initStartTicks());
      assertEquals("/system.slice/" + target.unit(), actual.controlGroup());
      assertEquals(4, f.targetReads);
      assertThrows(
          IOException.class,
          () -> context.captureServiceRoot(morning, RootStartupContext.Service.CLEANUP));
      assertThrows(NullPointerException.class, () -> context.captureServiceRoot(null, target));
      assertThrows(NullPointerException.class, () -> context.captureServiceRoot(morning, null));
    }
    var wrong = new Fixture();
    var context = wrong.context();
    var api = context.capture(RootStartupContext.Service.API);
    assertThrows(
        IOException.class, () -> context.captureServiceRoot(api, RootStartupContext.Service.WEB));
  }

  @Test
  void rootGenerationNeverNormalizesUidCgroupBootManagerAndPidDrift() throws Exception {
    for (String fault :
        List.of(
            "uid",
            "cgroup",
            FIXTURE_STAT_F3E718BA,
            "manager",
            "zeroPid",
            "largePid",
            "parentPid",
            "parentInvocation",
            "missing",
            "duplicate",
            "load",
            "active",
            "sub",
            "id",
            "group")) {
      var f = new LaunchFixture();
      var context = f.context();
      var morning = context.capture(RootStartupContext.Service.MORNING);
      switch (fault) {
        case "uid" -> f.rootUid = 1;
        case "cgroup" -> f.targetGroup = "0::/system.slice/other.service\n";
        case FIXTURE_STAT_F3E718BA -> f.targetStat = stat(200, "0");
        case "manager" -> f.targetDrift = true;
        case "zeroPid" ->
            f.targetUnit = f.targetUnit.replace(FIXTURE_MAINPID_200_B6F3F218, "MainPID=0");
        case "largePid" ->
            f.targetUnit = f.targetUnit.replace(FIXTURE_MAINPID_200_B6F3F218, "MainPID=2147483648");
        case "parentPid" ->
            f.targetUnit =
                f.targetUnit.replace(FIXTURE_MAINPID_200_B6F3F218, FIXTURE_MAINPID_42_0075A51F);
        case "parentInvocation" -> f.targetUnit = f.targetUnit.replace("2".repeat(32), INV);
        case "missing" -> f.targetUnit = f.targetUnit.replace("LoadState=loaded\n", "");
        case "duplicate" -> f.targetUnit += "LoadState=loaded\n";
        case "load" ->
            f.targetUnit = f.targetUnit.replace("LoadState=loaded", "LoadState=not-found");
        case "active" ->
            f.targetUnit = f.targetUnit.replace("ActiveState=active", "ActiveState=failed");
        case "sub" -> f.targetUnit = f.targetUnit.replace("SubState=running", "SubState=exited");
        case "id" -> f.targetUnit = f.targetUnit.replace("Id=schubert-nk-api", "Id=wrong");
        default ->
            f.targetUnit =
                f.targetUnit.replace("ControlGroup=/system.slice", "ControlGroup=/wrong");
      }
      assertThrows(IOException.class, () -> context.captureServiceRoot(morning, f.target), fault);
    }
  }

  @Test
  void kernelStatusRequiresAllFourRootUidValuesAndWholeBytes() throws Exception {
    assertEquals(
        0, RootStartupContext.rootUid(bytes("Name:\tjava\nUid:\t0\t0\t0\t0\nGid:\t0\t0\t0\t0\n")));
    assertEquals(0, RootStartupContext.rootUid(bytes("Uid: 0 0 0 0\n")));
    for (String text :
        List.of(
            "",
            "Uid: 0 0 0 0",
            "Gid: 0 0 0 0\n",
            "Uid: 0 0 0\n",
            "Uid: 0 1 0 0\n",
            "Uid: 00 0 0 0\n",
            "Uid: 0 0 0 0\nUid: 0 0 0 0\n",
            "Uid: 0 0 0 0\r\n"))
      assertThrows(IOException.class, () -> RootStartupContext.rootUid(bytes(text)));
    assertThrows(IOException.class, () -> RootStartupContext.rootUid(new byte[16385]));
    assertThrows(IOException.class, () -> RootStartupContext.rootUid(new byte[] {(byte) 255}));
    assertThrows(NullPointerException.class, () -> RootStartupContext.rootUid(null));
  }

  static final String BOOT = "11111111-1111-1111-1111-111111111111\n";
  static final String INV = "1".repeat(32);

  static byte[] bytes(String s) {
    return s.getBytes(StandardCharsets.US_ASCII);
  }

  static String stat(long pid, String ticks) {
    // field3..21: state followed by eighteen numeric fields. field22 independent literal ticks.
    return pid + " (java with ) parentheses) R " + "0 ".repeat(18) + ticks + " 0 0\n";
  }

  static String unit(RootStartupContext.Service s) {
    return "Id="
        + s.unit()
        + "\nLoadState=loaded\nActiveState=active\nSubState=running\nMainPID=42\nInvocationID="
        + INV
        + "\nControlGroup=/system.slice/"
        + s.unit()
        + "\n";
  }

  static class Fixture implements RootStartupContext.Io {
    long uid = 0;
    long processId = 42;
    String fs = "proc";
    String exe = "/usr/lib/systemd/systemd";
    String bootValue = BOOT;
    String inv = INV;
    String own = RootStartupContextTest.stat(42, FIXTURE_12345_AFC21EDA);
    String init = RootStartupContextTest.stat(1, "5");
    String group = "0::/system.slice/schubert-nk-api.service\n";
    String unitValues = RootStartupContextTest.unit(RootStartupContext.Service.API);
    int reads;
    boolean drift;
    String fail = "";

    void check(String name) throws IOException {
      if (fail.equals(name)) throw new IOException("PRIVATE cause");
    }

    public long effectiveUid() {
      return uid;
    }

    public long pid() {
      return processId;
    }

    public String procFilesystem() throws IOException {
      check("fs");
      return fs;
    }

    public String initExecutable() throws IOException {
      check("exe");
      return exe;
    }

    public byte[] boot() throws IOException {
      check("boot");
      return bytes(bootValue);
    }

    public byte[] stat(long p) throws IOException {
      check(FIXTURE_STAT_F3E718BA);
      return bytes(p == 1 ? init : own);
    }

    public byte[] cgroup(long p) throws IOException {
      check("group");
      assertEquals(processId, p);
      return bytes(group);
    }

    public String invocation() {
      return inv;
    }

    public byte[] unit(RootStartupContext.Service s) throws IOException {
      check("unit");
      reads++;
      return bytes(drift && reads > 1 ? unitValues.replace(INV, "2".repeat(32)) : unitValues);
    }

    RootStartupContext context() {
      return new RootStartupContext(this);
    }
  }

  @Test
  void rootctx010SameInvocationOuterDeadlineIsAnIndependentUpperBound() throws Exception {
    String literal =
        "Id=schubert-nk-morning-controller.service\nInvocationID="
            + INV
            + "\nMainPID=42\nExecMainStartTimestampMonotonic=12345678\n";
    String[] selected = {literal};
    byte[][] owned = {new byte[0]};
    var f =
        new Fixture() {
          @Override
          public byte[] unitDeadline(RootStartupContext.Service service) throws IOException {
            assertEquals(RootStartupContext.Service.MORNING, service);
            if (selected[0].equals(FIXTURE_IO_A0EA7E0E))
              throw new IOException("private manager detail");
            if (selected[0].equals("<NULL>")) return null;
            owned[0] = bytes(selected[0]);
            return owned[0];
          }
        };
    f.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    f.unitValues = unit(RootStartupContext.Service.MORNING);
    var context = f.context();
    var morning = context.capture(RootStartupContext.Service.MORNING);
    assertEquals(1_812_345_678_000L, context.maintenanceDeadline(morning, 1_900_000_000_000L));
    assertArrayEquals(new byte[owned[0].length], owned[0]);
    assertEquals(1_800_000_000_000L, context.maintenanceDeadline(morning, 1_800_000_000_000L));
    for (String wrong :
        new String[] {
          "0",
          "-1",
          "012345678",
          "x",
          "9223372036854775808",
          "9223372036854775807",
          "9223372036854775"
        }) {
      selected[0] = literal.replace("12345678", wrong);
      assertThrows(IOException.class, () -> context.maintenanceDeadline(morning, Long.MAX_VALUE));
      assertArrayEquals(new byte[owned[0].length], owned[0]);
    }
    for (String wrong :
        new String[] {
          literal.replace(
              "Id=schubert-nk-morning-controller.service", "Id=schubert-nk-cleanup.service"),
          literal.replace(INV, "2".repeat(32)),
          literal.replace(FIXTURE_MAINPID_42_0075A51F, "MainPID=43"),
          literal + "Unknown=1\n"
        }) {
      selected[0] = wrong;
      assertThrows(IOException.class, () -> context.maintenanceDeadline(morning, Long.MAX_VALUE));
    }
    selected[0] = literal;
    selected[0] = FIXTURE_IO_A0EA7E0E;
    var sanitized =
        assertThrows(IOException.class, () -> context.maintenanceDeadline(morning, Long.MAX_VALUE));
    assertEquals(FIXTURE_STARTUP_CONTEXT_UNAVAILABLE_1B156CA0, sanitized.getMessage());
    assertNull(sanitized.getCause());
    assertEquals(0, sanitized.getSuppressed().length);
    selected[0] = "<NULL>";
    assertThrows(
        NullPointerException.class, () -> context.maintenanceDeadline(morning, Long.MAX_VALUE));
    selected[0] = literal;
    assertThrows(IOException.class, () -> context.maintenanceDeadline(morning, 0));
    assertThrows(IOException.class, () -> context.maintenanceDeadline(morning, 12_345_678_000L));
    assertThrows(
        NullPointerException.class, () -> context.maintenanceDeadline(null, Long.MAX_VALUE));
    var unavailable = new Fixture();
    unavailable.group = f.group;
    unavailable.unitValues = f.unitValues;
    var noPort = unavailable.context();
    var observed = noPort.capture(RootStartupContext.Service.MORNING);
    assertThrows(IOException.class, () -> noPort.maintenanceDeadline(observed, Long.MAX_VALUE));
  }

  static void rejected(Fixture f) {
    IOException e =
        assertThrows(IOException.class, () -> f.context().capture(RootStartupContext.Service.API));
    assertEquals(FIXTURE_STARTUP_CONTEXT_UNAVAILABLE_1B156CA0, e.getMessage());
    assertNull(e.getCause());
  }

  @Test
  void rootctx009CleanupOwnUnitNotMorningOrApi() throws Exception {
    var f = new Fixture();
    f.group = "0::/system.slice/schubert-nk-cleanup.service\n";
    f.unitValues =
        "Id=schubert-nk-cleanup.service\nLoadState=loaded\nActiveState=active\n"
            + "SubState=running\nMainPID=42\nInvocationID="
            + INV
            + "\nControlGroup=/system.slice/schubert-nk-cleanup.service\n";
    var context = f.context();
    var snapshot = context.capture(RootStartupContext.Service.CLEANUP);
    assertEquals(RootStartupContext.Service.CLEANUP, snapshot.service());
    assertEquals("/system.slice/schubert-nk-cleanup.service", snapshot.controlGroup());
    context.recheck(snapshot);
    assertThrows(IOException.class, () -> context.capture(RootStartupContext.Service.MORNING));
    assertThrows(IOException.class, () -> context.capture(RootStartupContext.Service.API));
    f.unitValues = f.unitValues.replace(FIXTURE_MAINPID_42_0075A51F, "MainPID=43");
    assertThrows(IOException.class, () -> context.recheck(snapshot));
    assertEquals(
        FIXTURE_STARTUP_CONTEXT_UNAVAILABLE_1B156CA0,
        assertThrows(IOException.class, () -> context.recheck(snapshot)).getMessage());
  }

  @Test
  void rootctx001LiteralContextAndTwoObservations() {
    var f = new Fixture();
    var s = assertDoesNotThrow(() -> f.context().capture(RootStartupContext.Service.API));
    assertEquals(
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.API,
            BOOT.trim(),
            INV,
            42,
            12345,
            5,
            "/system.slice/schubert-nk-api.service"),
        s);
    assertEquals(2, f.reads);
    assertEquals("RootStartupContext.Snapshot[REDACTED]", s.toString());
    assertDoesNotThrow(() -> f.context().recheck(s));
    assertEquals(4, f.reads);
    f.unitValues =
        f.unitValues
            .replace("ActiveState=active", "ActiveState=activating")
            .replace("SubState=running", "SubState=start");
    assertEquals(s, assertDoesNotThrow(() -> f.context().capture(RootStartupContext.Service.API)));
    f.group = "0::/system.slice/schubert-nk-web.service\n";
    f.unitValues = unit(RootStartupContext.Service.WEB);
    assertEquals(
        RootStartupContext.Service.WEB,
        assertDoesNotThrow(() -> f.context().capture(RootStartupContext.Service.WEB)).service());
  }

  @Test
  void rootctx002RootProcInitBootAndInvocationDomains() {
    for (long uid : List.of(-1L, 1L, 1000L, 4294967295L)) {
      var f = new Fixture();
      f.uid = uid;
      rejected(f);
      assertEquals(0, f.reads);
    }
    for (String fs : List.of("", "tmpfs", "PROC")) {
      var f = new Fixture();
      f.fs = fs;
      rejected(f);
    }
    for (String exe : List.of("", "/sbin/init", "/fake/systemd")) {
      var f = new Fixture();
      f.exe = exe;
      rejected(f);
    }
    for (String boot :
        List.of(
            "",
            BOOT.trim(),
            "00000000-0000-0000-0000-000000000000\n",
            BOOT.replace('1', 'A'),
            BOOT + "\n",
            BOOT.replace("\n", "\r\n"))) {
      var f = new Fixture();
      f.bootValue = boot;
      rejected(f);
    }
    for (String inv : List.of("", "0".repeat(32), "A".repeat(32), INV + "\n", INV.substring(1))) {
      var f = new Fixture();
      f.inv = inv;
      rejected(f);
    }
  }

  @Test
  void rootctx003StatStartBoundaryAndPidNamespaceBinding() {
    for (long p : List.of(-1L, 0L, 1L, 2147483648L)) {
      var f = new Fixture();
      f.processId = p;
      rejected(f);
    }
    var max = new Fixture();
    max.processId = 2147483647;
    max.own = stat(max.processId, "9223372036854775807");
    max.unitValues =
        max.unitValues.replace(FIXTURE_MAINPID_42_0075A51F, "MainPID=" + max.processId);
    assertEquals(
        Long.MAX_VALUE,
        assertDoesNotThrow(() -> max.context().capture(RootStartupContext.Service.API))
            .startTicks());
    for (String s :
        List.of(
            "",
            stat(43, FIXTURE_12345_AFC21EDA),
            "42 foo\n",
            "42 (unclosed\n",
            "42 (x) R 1\n",
            stat(42, "0"),
            stat(42, "01"),
            stat(42, "9223372036854775808"),
            stat(42, FIXTURE_12345_AFC21EDA).trim(),
            stat(42, FIXTURE_12345_AFC21EDA).replace(" R ", " Z "),
            stat(42, FIXTURE_12345_AFC21EDA).replace(" R ", " R  "))) {
      var f = new Fixture();
      f.own = s;
      rejected(f);
    }
    var f = new Fixture();
    f.init = stat(2, "5");
    rejected(f);
  }

  @Test
  void rootctx004EveryManagerPropertyAndCgroupRefused() {
    for (String key :
        List.of(
            "Id",
            "LoadState",
            "ActiveState",
            "SubState",
            "MainPID",
            "InvocationID",
            "ControlGroup")) {
      var f = new Fixture();
      String line =
          Arrays.stream(f.unitValues.split("\n"))
                  .filter(x -> x.startsWith(key + "="))
                  .findFirst()
                  .orElseThrow()
              + "\n";
      f.unitValues = f.unitValues.replace(line, "");
      rejected(f);
      f = new Fixture();
      f.unitValues = f.unitValues + line;
      rejected(f);
      f = new Fixture();
      f.unitValues = f.unitValues.replace(line, key + "=invalid\n");
      rejected(f);
    }
    for (String extra : List.of("Extra=x\n", "\n", "badrow\n", "=value\n")) {
      var f = new Fixture();
      f.unitValues += extra;
      rejected(f);
    }
    var f = new Fixture();
    f.unitValues = f.unitValues.trim();
    rejected(f);
    for (String g :
        List.of(
            "",
            "0::/system.slice/schubert-nk-web.service\n",
            "1:systemd:/system.slice/schubert-nk-api.service\n",
            "0::/system.slice/schubert-nk-api.service\n0::/other\n")) {
      f = new Fixture();
      f.group = g;
      rejected(f);
    }
  }

  @Test
  void rootctx005AsciiBoundsNullAndObservationDrift() {
    for (String g : List.of("x".repeat(4097), "a\t", "a\0", "a\u007f", "a\u0080")) {
      var f = new Fixture();
      f.group = g;
      rejected(f);
    }
    var f = new Fixture();
    f.drift = true;
    rejected(f);
    f = new Fixture();
    var c = f.context();
    var s = assertDoesNotThrow(() -> c.capture(RootStartupContext.Service.API));
    f.bootValue = BOOT.replace('1', '2');
    assertThrows(IOException.class, () -> c.recheck(s));
    assertThrows(NullPointerException.class, () -> new RootStartupContext(null));
    assertThrows(NullPointerException.class, () -> c.capture(null));
    assertThrows(NullPointerException.class, () -> c.recheck(null));
    for (int i = 0; i < 4; i++) {
      final int n = i;
      assertThrows(
          NullPointerException.class,
          () ->
              new RootStartupContext.Snapshot(
                  n == 0 ? null : RootStartupContext.Service.API,
                  n == 1 ? null : BOOT,
                  n == 2 ? null : INV,
                  42,
                  1,
                  1,
                  n == 3 ? null : "/group"));
    }
    for (String fail : List.of("fs", "exe", "boot", FIXTURE_STAT_F3E718BA, "group", "unit")) {
      var broken = new Fixture();
      broken.fail = fail;
      IOException e =
          assertThrows(
              IOException.class, () -> broken.context().capture(RootStartupContext.Service.API));
      assertEquals(FIXTURE_STARTUP_CONTEXT_UNAVAILABLE_1B156CA0, e.getMessage());
      assertNull(e.getCause());
    }
  }

  static class FakeProcess extends Process {
    boolean alive;
    boolean done = true;
    int exit;
    boolean interrupt;
    int destroyed;
    InputStream output = new ByteArrayInputStream(bytes("PUBLIC\n"));
    InputStream error = new ByteArrayInputStream(new byte[0]);
    OutputStream input = new ByteArrayOutputStream();

    public OutputStream getOutputStream() {
      return input;
    }

    public InputStream getInputStream() {
      return output;
    }

    public InputStream getErrorStream() {
      return error;
    }

    public int waitFor() {
      return exit;
    }

    public boolean waitFor(long t, TimeUnit u) throws InterruptedException {
      assertEquals(5, t);
      assertEquals(TimeUnit.SECONDS, u);
      if (interrupt) throw new InterruptedException();
      return done;
    }

    public int exitValue() {
      return exit;
    }

    public boolean isAlive() {
      return alive;
    }

    public void destroy() {
      destroyed++;
      alive = false;
    }
  }

  @Test
  void rootctx006FixedSystemBusQueryAndAllProcessResults() {
    var p = new FakeProcess();
    var io =
        new RootStartupContext.NativeIo(
            cmd -> {
              assertEquals(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup",
                      "schubert-nk-api.service"),
                  cmd);
              return p;
            });
    assertArrayEquals(
        bytes("PUBLIC\n"), assertDoesNotThrow(() -> io.unit(RootStartupContext.Service.API)));
    assertEquals(0, p.destroyed);
    for (int bad : List.of(1, 2, 3)) {
      var q = new FakeProcess();
      q.alive = true;
      if (bad == NOT_DONE_FIXTURE) q.done = false;
      if (bad == NONZERO_EXIT_FIXTURE) q.exit = 1;
      if (bad == INTERRUPTED_WAIT_FIXTURE) q.interrupt = true;
      assertThrows(
          IOException.class,
          () -> new RootStartupContext.NativeIo(cmd -> q).unit(RootStartupContext.Service.WEB));
      assertEquals(1, q.destroyed);
      if (bad == INTERRUPTED_WAIT_FIXTURE) assertTrue(Thread.interrupted());
    }
    assertThrows(
        IOException.class,
        () ->
            new RootStartupContext.NativeIo(
                    cmd -> {
                      throw new IOException();
                    })
                .unit(RootStartupContext.Service.API));
    assertThrows(NullPointerException.class, () -> new RootStartupContext.NativeIo(null));
    assertThrows(
        NullPointerException.class,
        () -> new RootStartupContext.NativeIo(cmd -> null).unit(RootStartupContext.Service.API));
  }

  @Test
  void rootctx007NativeStreamsFaultsAndUnknownPriority() {
    for (int position : List.of(1, 2, 3)) {
      var p = new FakeProcess();
      p.alive = true;
      IOException failure = new IOException("PRIVATE");
      if (position == FIRST_FIXTURE_SLOT)
        p.output =
            new ByteArrayInputStream(bytes("PUBLIC")) {
              @Override
              public void close() throws IOException {
                throw failure;
              }
            };
      if (position == SECOND_FIXTURE_SLOT)
        p.input =
            new ByteArrayOutputStream() {
              @Override
              public void close() throws IOException {
                throw failure;
              }
            };
      if (position == THIRD_FIXTURE_SLOT)
        p.error =
            new ByteArrayInputStream(new byte[0]) {
              @Override
              public void close() throws IOException {
                throw failure;
              }
            };
      assertEquals(
          "transfer storage operation failed",
          assertThrows(
                  IOException.class,
                  () ->
                      new RootStartupContext.NativeIo(cmd -> p)
                          .unit(RootStartupContext.Service.API))
              .getMessage());
      assertEquals(1, p.destroyed);
    }
    var p = new FakeProcess();
    p.done = false;
    p.alive = true;
    var unknown = new AssertionError("PRIVATE");
    p.output =
        new ByteArrayInputStream(new byte[0]) {
          @Override
          public void close() {
            throw unknown;
          }
        };
    assertSame(
        unknown,
        assertThrows(
            AssertionError.class,
            () -> new RootStartupContext.NativeIo(cmd -> p).unit(RootStartupContext.Service.API)));
    assertEquals(1, p.destroyed);
  }

  @Test
  void rootctx008NativeKernelReadsAndOrdinaryUidRefusal() {
    var io = new RootStartupContext.NativeIo();
    assertEquals(ProcessHandle.current().pid(), io.pid());
    assertEquals("proc", assertDoesNotThrow(io::procFilesystem));
    assertThrows(IOException.class, io::initExecutable);
    var linkIo =
        new RootStartupContext.NativeIo(
            cmd -> new FakeProcess(),
            path -> {
              assertEquals(java.nio.file.Path.of("/proc/1/exe"), path);
              return java.nio.file.Path.of("/usr/lib/systemd/systemd");
            });
    assertEquals("/usr/lib/systemd/systemd", assertDoesNotThrow(linkIo::initExecutable));
    assertThrows(
        NullPointerException.class,
        () -> new RootStartupContext.NativeIo(cmd -> new FakeProcess(), null));
    assertEquals(37, assertDoesNotThrow(io::boot).length);
    assertTrue(assertDoesNotThrow(() -> io.stat(io.pid())).length > 0);
    assertTrue(assertDoesNotThrow(() -> io.cgroup(io.pid())).length > 0);
    assertNotNull(io.invocation());
    assertThrows(IOException.class, () -> io.stat(Long.MAX_VALUE));
    assertNotEquals(0, io.effectiveUid());
    assertThrows(
        IOException.class,
        () -> RootStartupContext.create().capture(RootStartupContext.Service.API));
    // systemctl show itself may exit0 for an absent Unit; context admission must reject its state.
    assertTrue(
        new String(
                assertDoesNotThrow(() -> io.unit(RootStartupContext.Service.API)),
                StandardCharsets.US_ASCII)
            .contains("LoadState=not-found\n"));
  }

  /** PT-OPS-ROOTCTX-010: genuine proc status boundary; no reflection or other PID action. */
  @Test
  void rootctx010NativeServiceUidRejectsInvalidPidAndOrdinaryCaller() {
    var io = new RootStartupContext.NativeIo();
    for (long pid :
        new long[] {Long.MIN_VALUE, 0, 1, (long) Integer.MAX_VALUE + 1, Long.MAX_VALUE}) {
      assertEquals(
          FIXTURE_STARTUP_CONTEXT_UNAVAILABLE_1B156CA0,
          assertThrows(IOException.class, () -> io.serviceRootUid(pid)).getMessage());
    }
    // The qualified host PT runs as its ordinary account. Reading our own proc status
    // is allowed, but that identity must never qualify as a service Root identity.
    assertNotEquals(0, io.effectiveUid());
    assertEquals(
        FIXTURE_STARTUP_CONTEXT_UNAVAILABLE_1B156CA0,
        assertThrows(IOException.class, () -> io.serviceRootUid(ProcessHandle.current().pid()))
            .getMessage());
  }

  /** PT-OPS-ROOTCTX-011: the deadline query cannot silently use the readiness property set. */
  @Test
  void rootctx011NativeDeadlineUsesFixedPropertiesAndPreservesIoFailure() {
    byte[] vector =
        bytes(
            "Id=schubert-nk-web.service\n"
                + "InvocationID=11111111111111111111111111111111\n"
                + "MainPID=42\n"
                + "ExecMainStartTimestampMonotonic=900001\n");
    var process = new FakeProcess();
    process.output = new ByteArrayInputStream(vector);
    var io =
        new RootStartupContext.NativeIo(
            command -> {
              assertEquals(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=Id,InvocationID,MainPID,ExecMainStartTimestampMonotonic",
                      "schubert-nk-web.service"),
                  command);
              return process;
            });
    assertArrayEquals(
        vector, assertDoesNotThrow(() -> io.unitDeadline(RootStartupContext.Service.WEB)));
    assertEquals(0, process.destroyed);
    var failure = new IOException("PUBLIC_FIXTURE_QUERY_FAILURE");
    var failed =
        new RootStartupContext.NativeIo(
            command -> {
              throw failure;
            });
    assertSame(
        failure,
        assertThrows(IOException.class, () -> failed.unitDeadline(RootStartupContext.Service.API)));
    assertThrows(NullPointerException.class, () -> io.unitDeadline(null));
  }
}
