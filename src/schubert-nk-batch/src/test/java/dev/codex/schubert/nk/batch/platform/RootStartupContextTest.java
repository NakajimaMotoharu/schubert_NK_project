package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-ROOTCTX-001..009; literal kernel/system manager vector, never production expected. */
final class RootStartupContextTest {
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

  static final class Fixture implements RootStartupContext.Io {
    long uid = 0, pid = 42;
    String fs = "proc", exe = "/usr/lib/systemd/systemd", boot = BOOT, inv = INV;
    String own = RootStartupContextTest.stat(42, "12345"),
        init = RootStartupContextTest.stat(1, "5");
    String group = "0::/system.slice/schubert-nk-api.service\n";
    String unit = RootStartupContextTest.unit(RootStartupContext.Service.API);
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
      return pid;
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
      return bytes(boot);
    }

    public byte[] stat(long p) throws IOException {
      check("stat");
      return bytes(p == 1 ? init : own);
    }

    public byte[] cgroup(long p) throws IOException {
      check("group");
      assertEquals(pid, p);
      return bytes(group);
    }

    public String invocation() {
      return inv;
    }

    public byte[] unit(RootStartupContext.Service s) throws IOException {
      check("unit");
      reads++;
      return bytes(drift && reads > 1 ? unit.replace(INV, "2".repeat(32)) : unit);
    }

    RootStartupContext context() {
      return new RootStartupContext(this);
    }
  }

  static void rejected(Fixture f) {
    IOException e =
        assertThrows(IOException.class, () -> f.context().capture(RootStartupContext.Service.API));
    assertEquals("startup context unavailable", e.getMessage());
    assertNull(e.getCause());
  }

  @Test
  void rootctx009CleanupOwnUnitNotMorningOrApi() throws Exception {
    var f = new Fixture();
    f.group = "0::/system.slice/schubert-nk-cleanup.service\n";
    f.unit =
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
    f.unit = f.unit.replace("MainPID=42", "MainPID=43");
    assertThrows(IOException.class, () -> context.recheck(snapshot));
    assertEquals(
        "startup context unavailable",
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
    f.unit =
        f.unit
            .replace("ActiveState=active", "ActiveState=activating")
            .replace("SubState=running", "SubState=start");
    assertEquals(s, assertDoesNotThrow(() -> f.context().capture(RootStartupContext.Service.API)));
    f.group = "0::/system.slice/schubert-nk-web.service\n";
    f.unit = unit(RootStartupContext.Service.WEB);
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
      f.boot = boot;
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
      f.pid = p;
      rejected(f);
    }
    var max = new Fixture();
    max.pid = 2147483647;
    max.own = stat(max.pid, "9223372036854775807");
    max.unit = max.unit.replace("MainPID=42", "MainPID=" + max.pid);
    assertEquals(
        Long.MAX_VALUE,
        assertDoesNotThrow(() -> max.context().capture(RootStartupContext.Service.API))
            .startTicks());
    for (String s :
        List.of(
            "",
            stat(43, "12345"),
            "42 foo\n",
            "42 (unclosed\n",
            "42 (x) R 1\n",
            stat(42, "0"),
            stat(42, "01"),
            stat(42, "9223372036854775808"),
            stat(42, "12345").trim(),
            stat(42, "12345").replace(" R ", " Z "),
            stat(42, "12345").replace(" R ", " R  "))) {
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
          Arrays.stream(f.unit.split("\n"))
                  .filter(x -> x.startsWith(key + "="))
                  .findFirst()
                  .orElseThrow()
              + "\n";
      f.unit = f.unit.replace(line, "");
      rejected(f);
      f = new Fixture();
      f.unit = f.unit + line;
      rejected(f);
      f = new Fixture();
      f.unit = f.unit.replace(line, key + "=invalid\n");
      rejected(f);
    }
    for (String extra : List.of("Extra=x\n", "\n", "badrow\n", "=value\n")) {
      var f = new Fixture();
      f.unit += extra;
      rejected(f);
    }
    var f = new Fixture();
    f.unit = f.unit.trim();
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
    f.boot = BOOT.replace('1', '2');
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
    for (String fail : List.of("fs", "exe", "boot", "stat", "group", "unit")) {
      var broken = new Fixture();
      broken.fail = fail;
      IOException e =
          assertThrows(
              IOException.class, () -> broken.context().capture(RootStartupContext.Service.API));
      assertEquals("startup context unavailable", e.getMessage());
      assertNull(e.getCause());
    }
  }

  static final class FakeProcess extends Process {
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
      if (bad == 1) q.done = false;
      if (bad == 2) q.exit = 1;
      if (bad == 3) q.interrupt = true;
      assertThrows(
          IOException.class,
          () -> new RootStartupContext.NativeIo(cmd -> q).unit(RootStartupContext.Service.WEB));
      assertEquals(1, q.destroyed);
      if (bad == 3) assertTrue(Thread.interrupted());
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
      if (position == 1)
        p.output =
            new ByteArrayInputStream(bytes("PUBLIC")) {
              @Override
              public void close() throws IOException {
                throw failure;
              }
            };
      if (position == 2)
        p.input =
            new ByteArrayOutputStream() {
              @Override
              public void close() throws IOException {
                throw failure;
              }
            };
      if (position == 3)
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
}
