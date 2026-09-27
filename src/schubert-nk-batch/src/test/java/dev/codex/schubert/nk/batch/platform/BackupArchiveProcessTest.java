package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** SS341/343; PT-OPS-ARCHPROC001..008. Commands/environment are independent literal oracles. */
final class BackupArchiveProcessTest {
  private static final Path DIR = Path.of("/proc/self/fd/101"),
      OUT = Path.of("/proc/self/fd/102"),
      KEY = Path.of("/proc/self/fd/103");
  @TempDir Path temporary;

  private static String child(int fd) {
    return "/proc/" + ProcessHandle.current().pid() + "/fd/" + fd;
  }

  private static List<String> tar() {
    return List.of(
        "/usr/bin/tar",
        "--create",
        "--format=posix",
        "--numeric-owner",
        "--no-recursion",
        "--null",
        "--verbatim-files-from",
        "--directory=" + child(101),
        "--files-from=-");
  }

  private static void refused(Executable operation) {
    var e = assertThrows(IOException.class, operation);
    assertEquals("backup archive execution failed", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  @Test
  void fixedCommandAndEnvironment() throws Exception {
    var f = new Fixture();
    f.uid = 992;
    f.runner.dump(OUT, KEY, 992);
    assertEquals(
        List.of(
            "/usr/bin/pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--schema=schubert",
            "--schema=schubert_web_session",
            "--schema=schubert_meta",
            "--file=" + child(102),
            "schubert_nk"),
        f.calls.get(0).getFirst());
    assertEquals(List.of("/usr/bin/pg_restore", "--list", child(102)), f.calls.get(1).getFirst());
    assertEquals(
        Map.of(
            "PATH",
            "/usr/bin:/bin",
            "LANG",
            "C",
            "LC_ALL",
            "C",
            "PGHOST",
            "127.0.0.1",
            "PGPORT",
            "5432",
            "PGUSER",
            "schubert_backup",
            "PGDATABASE",
            "schubert_nk",
            "PGPASSFILE",
            child(103),
            "PGCONNECT_TIMEOUT",
            "5"),
        f.environments.getFirst());
    assertEquals(
        Map.of("PATH", "/usr/bin:/bin", "LANG", "C", "LC_ALL", "C"), f.environments.get(1));
    f.closed();
    f = new Fixture();
    f.runner.configuration(DIR, OUT, List.of("api.yml", "web.yml"));
    assertEquals(List.of(tar()), f.calls.getFirst());
    assertEquals(Optional.of(OUT), f.outputs.getFirst());
    assertArrayEquals(
        new byte[] {'a', 'p', 'i', '.', 'y', 'm', 'l', 0, 'w', 'e', 'b', '.', 'y', 'm', 'l', 0},
        f.processes.getFirst().received.toByteArray());
    f.closed();
  }

  @Test
  void inputAndNullContracts() throws Exception {
    for (Path bad :
        List.of(
            Path.of("/"),
            Path.of("/tmp/file"),
            Path.of("/proc/self/fd/0"),
            Path.of("/proc/self/fd/2"),
            Path.of("/proc/self/fd/03"),
            Path.of("/proc/self/fd/2147483648"),
            Path.of("/proc/self/fd/99999999999"),
            Path.of("/proc/self/fd/3/child"))) {
      var f = new Fixture();
      refused(() -> f.runner.configuration(bad, OUT, List.of("public")));
      assertTrue(f.processes.isEmpty());
    }
    for (List<String> bad :
        List.of(
            List.<String>of(),
            Collections.nCopies(33, "x"),
            List.of("x", "x"),
            List.of("../secret"),
            List.of("/absolute"),
            List.of("--option"),
            List.of("x\ny"),
            List.of("a".repeat(65)),
            List.of("é"))) refused(() -> new Fixture().runner.configuration(DIR, OUT, bad));
    var f = new Fixture();
    f.runner.configuration(DIR, OUT, List.of("a".repeat(64)));
    f.closed();
    assertThrows(NullPointerException.class, () -> new BackupArchiveProcess(null));
    assertThrows(NullPointerException.class, () -> new BackupArchiveProcess(f, null, () -> 0));
    assertThrows(NullPointerException.class, () -> new BackupArchiveProcess(f, f, null));
    assertThrows(NullPointerException.class, () -> f.runner.configuration(null, OUT, List.of("x")));
    assertThrows(NullPointerException.class, () -> f.runner.configuration(DIR, null, List.of("x")));
    assertThrows(NullPointerException.class, () -> f.runner.configuration(DIR, OUT, null));
    assertThrows(
        NullPointerException.class,
        () -> f.runner.configuration(DIR, OUT, Arrays.asList("x", null)));
    var list = new ArrayList<>(List.of("public"));
    var snapshot = new Fixture();
    snapshot.runner.configuration(DIR, OUT, list);
    list.clear();
    assertEquals(
        "public\0",
        snapshot
            .processes
            .getFirst()
            .received
            .toString(java.nio.charset.StandardCharsets.US_ASCII));
  }

  @Test
  void statusDeadlineAndCancellation() throws Exception {
    for (String variant : List.of("none", "interrupt", "runtime", "error")) {
      for (String operation : List.of("dump", "configuration", "credentials")) {
        var pending = new Fixture();
        pending.stubborn = true;
        pending.holdEmptyWait = true;
        pending.holdInterrupt = variant.equals("interrupt");
        Throwable expectedUnknown =
            variant.equals("error")
                ? new AssertionError("public primary")
                : new IllegalStateException("public primary");
        if (variant.equals("runtime") || variant.equals("error")) {
          pending.holdFaults.add(expectedUnknown);
          pending.holdFaults.add(new IllegalArgumentException("public secondary"));
          pending.holdFaults.add(new AssertionError("public secondary fatal"));
          pending.holdInterrupt = true;
          pending.interruptOnHoldFault = variant.equals("error");
        }
        if (operation.equals("dump")) pending.uid = 992;
        var borrowedReleased = new AtomicBoolean();
        var flagObserved = new AtomicBoolean();
        try (var executor = Executors.newSingleThreadExecutor()) {
          var result =
              executor.submit(
                  () -> {
                    try {
                      switch (operation) {
                        case "dump" -> pending.runner.dump(OUT, KEY, 992);
                        case "configuration" ->
                            pending.runner.configuration(DIR, OUT, List.of("public"));
                        case "credentials" ->
                            pending.runner.credentials(DIR, OUT, KEY, List.of("public"));
                        default -> throw new AssertionError("independent fixed operations");
                      }
                      return false;
                    } catch (IOException expected) {
                      return true;
                    } finally {
                      flagObserved.set(Thread.currentThread().isInterrupted());
                      borrowedReleased.set(true);
                    }
                  });
          try {
            assertTrue(
                pending.terminalHoldEntered.await(2, TimeUnit.SECONDS),
                "unconfirmed terminal must enter retained-capability hold");
            assertFalse(
                borrowedReleased.get(),
                "caller must not release/reuse borrowed FD before terminal");
            assertTrue(
                pending.processes.stream().allMatch(p -> p.destroyed),
                "all pipeline children get TERM before any indefinite hold");
          } finally {
            pending.terminalRelease.countDown();
          }
          if (variant.equals("runtime") || variant.equals("error")) {
            var thrown =
                assertThrows(ExecutionException.class, () -> result.get(5, TimeUnit.SECONDS));
            assertSame(
                expectedUnknown,
                thrown.getCause(),
                "first unknown identity has ResourceScope precedence");
          } else
            assertTrue(
                result.get(5, TimeUnit.SECONDS), "timeout remains non-success after terminal");
          assertTrue(borrowedReleased.get());
          assertEquals(!variant.equals("none"), flagObserved.get());
          pending.closed();
        }
      }
    }
    var endedUnknown = new Fixture();
    endedUnknown.stubborn = true;
    endedUnknown.exitOnHoldFault = true;
    var firstUnknown = new IllegalStateException("public terminal observation failure");
    endedUnknown.holdFaults.add(firstUnknown);
    assertSame(
        firstUnknown,
        assertThrows(
            IllegalStateException.class,
            () -> endedUnknown.runner.configuration(DIR, OUT, List.of("public"))));
    endedUnknown.closed();
    var cumulative = new Fixture();
    cumulative.uid = 992;
    cumulative.timeSequence =
        List.of(0L, 0L, TimeUnit.MINUTES.toNanos(29), TimeUnit.MINUTES.toNanos(30));
    refused(() -> cumulative.runner.dump(OUT, KEY, 992));
    assertEquals(1, cumulative.calls.size(), "expired budget must not start pg_restore");
    cumulative.closed();
    var pipeline = new Fixture();
    pipeline.timeSequence =
        List.of(0L, 0L, TimeUnit.MINUTES.toNanos(29), TimeUnit.MINUTES.toNanos(30));
    refused(() -> pipeline.runner.credentials(DIR, OUT, KEY, List.of("public")));
    assertFalse(pipeline.processes.get(0).destroyed);
    assertTrue(pipeline.processes.get(1).destroyed, "age shares the original pipeline budget");
    pipeline.closed();
    for (String scenario :
        List.of(
            "startIo",
            "exit",
            "timeout",
            "interrupt",
            "negativeClock",
            "expiredClock",
            "lateInterrupt",
            "wrongCount",
            "nullProcess")) {
      var f = new Fixture();
      f.scenario = scenario;
      try {
        refused(() -> f.runner.credentials(DIR, OUT, KEY, List.of("public")));
        f.closed();
      } finally {
        Thread.interrupted();
      }
    }
    var f = new Fixture();
    Thread.currentThread().interrupt();
    try {
      refused(() -> f.runner.configuration(DIR, OUT, List.of("x")));
      assertTrue(f.processes.isEmpty());
    } finally {
      Thread.interrupted();
    }
    Fixture current = new Fixture();
    current.scenario = "nullList";
    assertThrows(
        NullPointerException.class, () -> current.runner.configuration(DIR, OUT, List.of("x")));
  }

  @Test
  void everyStreamFailureAndCompoundOwnership() throws Exception {
    for (String failure :
        List.of(
            "getOut",
            "getIn",
            "getErr",
            "write",
            "closeOut",
            "closeIn",
            "closeErr",
            "nullOut",
            "nullIn",
            "nullErr"))
      for (int process : List.of(0, 1)) {
        if (process == 1 && failure.equals("write")) continue;
        var f = new Fixture();
        f.scenario = failure;
        f.badProcess = process;
        refused(() -> f.runner.credentials(DIR, OUT, KEY, List.of("public")));
        f.closed();
      }
    for (String where :
        List.of(
            "getOut",
            "getIn",
            "getErr",
            "write",
            "closeOut",
            "closeIn",
            "closeErr",
            "wait",
            "destroy")) {
      var f = new Fixture();
      f.scenario = where;
      f.unknown = new IllegalStateException("public sentinel");
      if (where.equals("destroy")) f.beforeTimeout = true;
      assertSame(
          f.unknown,
          assertThrows(
              IllegalStateException.class,
              () -> f.runner.credentials(DIR, OUT, KEY, List.of("public"))));
      f.closedStreams();
    }
    for (String scenario : List.of("terminateTimeout", "terminateInterrupt")) {
      var f = new Fixture();
      f.scenario = scenario;
      f.beforeTimeout = true;
      try {
        refused(() -> f.runner.credentials(DIR, OUT, KEY, List.of("public")));
        assertTrue(f.processes.stream().allMatch(p -> p.destroyed));
        f.closedStreams();
      } finally {
        Thread.interrupted();
      }
    }
    var f = new Fixture();
    f.scenario = "write";
    f.cleanupUnknown = new IllegalArgumentException("public cleanup sentinel");
    assertSame(
        f.cleanupUnknown,
        assertThrows(
            IllegalArgumentException.class,
            () -> f.runner.credentials(DIR, OUT, KEY, List.of("public"))));
    f.closedStreams();
  }

  @Test
  void encryptedPipelineIsNotPlaintextArtifact() throws Exception {
    var f = new Fixture();
    f.runner.credentials(DIR, OUT, KEY, List.of("db-password", "mq-password"));
    assertEquals(
        List.of(tar(), List.of("/usr/bin/age", "--encrypt", "--recipients-file", child(103))),
        f.calls.getFirst());
    assertEquals(Optional.of(OUT), f.outputs.getFirst());
    assertEquals(0, f.processes.get(1).received.size());
    assertArrayEquals(
        "db-password\0mq-password\0".getBytes(java.nio.charset.StandardCharsets.US_ASCII),
        f.processes.getFirst().received.toByteArray());
    assertEquals(1, f.processes.getFirst().inputClosed);
    assertEquals(1, f.processes.get(1).inputClosed);
    f.closed();
  }

  @Test
  void actorGatesAndDatabaseListFailure() throws Exception {
    for (long uid : List.of(0L, -1L, 0x100000000L)) {
      var f = new Fixture();
      refused(() -> f.runner.dump(OUT, KEY, uid));
      assertTrue(f.processes.isEmpty());
    }
    var f = new Fixture();
    f.uid = 991;
    Fixture mismatch = f;
    refused(() -> mismatch.runner.dump(OUT, KEY, 992));
    assertTrue(f.processes.isEmpty());
    f = new Fixture();
    f.uid = 992;
    Fixture role = f;
    refused(() -> role.runner.configuration(DIR, OUT, List.of("x")));
    refused(() -> role.runner.credentials(DIR, OUT, KEY, List.of("x")));
    f = new Fixture();
    f.uid = 992;
    f.scenario = "listExit";
    Fixture dump = f;
    refused(() -> dump.runner.dump(OUT, KEY, 992));
    assertEquals(2, f.calls.size());
    f.closed();
    f = new Fixture();
    f.uid = 0xffff_ffffL;
    f.runner.dump(OUT, KEY, 0xffff_ffffL);
    f.closed();
  }

  @Test
  void concurrentIndependentScopes() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
      var calls = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 16; i++)
        calls.add(
            () -> {
              var f = new Fixture();
              f.runner.credentials(DIR, OUT, KEY, List.of("public"));
              f.closed();
              return true;
            });
      for (var result : workers.invokeAll(calls)) assertTrue(result.get());
    }
  }

  @Test
  void actualNativePublicTarAndBuilder() throws Exception {
    Path source = Files.createDirectory(temporary.resolve("source")),
        destination = Files.createDirectory(temporary.resolve("destination"));
    Files.writeString(source.resolve("public.txt"), "PUBLIC_BACKUP_FIXTURE\n");
    Path archive = Files.createFile(destination.resolve("config.tar"));
    var security = new Fixture();
    var actual =
        new BackupArchiveProcess(security); // synthetic actor only; host fixture is nonsecret.
    try (var src = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), source);
        var dest = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), destination)) {
      src.atDirectory(
          directory ->
              dest.atExistingEntryHandle(
                  "config.tar",
                  file -> {
                    actual.configuration(directory, file, List.of("public.txt"));
                    return true;
                  }));
    }
    assertTrue(Files.size(archive) > 0);
    Process check =
        new ProcessBuilder("/usr/bin/tar", "--list", "--file=" + archive)
            .redirectError(ProcessBuilder.Redirect.DISCARD)
            .start();
    String listing =
        new String(
            check.getInputStream().readAllBytes(), java.nio.charset.StandardCharsets.US_ASCII);
    assertEquals(0, check.waitFor());
    assertEquals("public.txt\n", listing);
    check.getOutputStream().close();
    check.getErrorStream().close();
    check.getInputStream().close();
    var nativeStart = new BackupArchiveProcess.NativeStart();
    assertThrows(NullPointerException.class, () -> new BackupArchiveProcess.NativeStart(null));
    assertThrows(
        NullPointerException.class,
        () -> new BackupArchiveProcess.NativeStart(builders -> List.of(), null));
    assertThrows(
        NullPointerException.class, () -> new BackupArchiveProcess.NativeStart.PendingHold(null));
    var started = new AtomicInteger();
    var quarantined = new AtomicInteger();
    var guarded =
        new BackupArchiveProcess.NativeStart(
            builders -> {
              started.incrementAndGet();
              return List.of();
            },
            first -> quarantined.incrementAndGet());
    assertThrows(
        java.util.NoSuchElementException.class,
        () -> guarded.execute(List.of(), Map.of(), Optional.empty()));
    Thread.currentThread().interrupt();
    try {
      refused(() -> guarded.execute(List.of(List.of("/usr/bin/true")), Map.of(), Optional.empty()));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    assertEquals(0, started.get());
    assertEquals(0, quarantined.get());
    var marker = new AssertionError("public controlled quarantine exit");
    for (Throwable failure :
        List.of(
            new IOException("public"),
            new IllegalStateException("public"),
            new AssertionError("public"))) {
      var pending =
          new BackupArchiveProcess.NativeStart(
              builders -> {
                assertEquals(List.of("/usr/bin/true"), builders.getFirst().command());
                if (failure instanceof IOException io) throw io;
                if (failure instanceof Error fatal) throw fatal;
                throw (RuntimeException) failure;
              },
              first -> {
                assertSame(failure, first);
                quarantined.incrementAndGet();
                throw marker;
              });
      assertSame(
          marker,
          assertThrows(
              AssertionError.class,
              () ->
                  pending.execute(List.of(List.of("/usr/bin/true")), Map.of(), Optional.empty())));
    }
    assertEquals(3, quarantined.get());
    var returned =
        new BackupArchiveProcess.NativeStart(
            builders -> {
              throw new IOException("public");
            },
            first -> {});
    refused(() -> returned.execute(List.of(List.of("/usr/bin/true")), Map.of(), Optional.empty()));
    var pulses = new AtomicInteger();
    Thread.currentThread().interrupt();
    assertSame(
        marker,
        assertThrows(
            AssertionError.class,
            () ->
                new BackupArchiveProcess.NativeStart.PendingHold(
                        () -> {
                          assertFalse(
                              Thread.currentThread().isInterrupted(),
                              "interrupt does not release quarantine or cause park spin");
                          if (pulses.incrementAndGet() == 2) throw marker;
                          Thread.currentThread().interrupt();
                        })
                    .hold(marker)));
    assertEquals(2, pulses.get());
    var beganUnknown = new CountDownLatch(1);
    var returnedUnknown = new AtomicBoolean();
    var fixed =
        new BackupArchiveProcess.NativeStart(
            builders -> {
              beganUnknown.countDown();
              throw new IOException("public isolated spawn failure");
            });
    Thread held =
        new Thread(
            () -> {
              try {
                fixed.execute(List.of(List.of("/usr/bin/true")), Map.of(), Optional.empty());
              } catch (IOException failure) {
                returnedUnknown.set(true);
              } finally {
                returnedUnknown.set(true);
              }
            },
            "public-native-start-quarantine");
    held.setDaemon(true);
    held.start();
    assertTrue(beganUnknown.await(2, TimeUnit.SECONDS));
    held.interrupt();
    held.join(50);
    assertTrue(held.isAlive());
    assertFalse(
        returnedUnknown.get(), "fixed Production factory must not unwind borrowed callback");
    var processes =
        nativeStart.execute(
            List.of(List.of("/usr/bin/true")), Map.of("PATH", "/usr/bin:/bin"), Optional.empty());
    assertEquals(0, processes.getFirst().waitFor());
    for (Process p : processes) {
      p.getInputStream().close();
      p.getOutputStream().close();
      p.getErrorStream().close();
    }
  }

  private static final class Fixture implements InodeSecurityCalls, BackupArchiveProcess.Start {
    final List<List<List<String>>> calls = new ArrayList<>();
    final List<Map<String, String>> environments = new ArrayList<>();
    final List<Optional<Path>> outputs = new ArrayList<>();
    final List<FakeProcess> processes = new ArrayList<>();
    final AtomicInteger ticks = new AtomicInteger();
    final BackupArchiveProcess runner = new BackupArchiveProcess(this, this, this::clock);
    long uid;
    List<Long> timeSequence = List.of();
    String scenario = "";
    int badProcess;
    boolean beforeTimeout;
    boolean stubborn;
    boolean holdInterrupt, interruptOnHoldFault;
    boolean holdEmptyWait, exitOnHoldFault;
    final List<Throwable> holdFaults = new ArrayList<>();
    final CountDownLatch terminalHoldEntered = new CountDownLatch(1);
    final CountDownLatch terminalRelease = new CountDownLatch(1);
    RuntimeException unknown, cleanupUnknown;

    long clock() {
      int at = ticks.getAndIncrement();
      if (at < timeSequence.size()) return timeSequence.get(at);
      if (at > 0 && scenario.equals("negativeClock")) return -1;
      if (at > 0 && scenario.equals("expiredClock")) return TimeUnit.MINUTES.toNanos(30);
      return at;
    }

    @Override
    public List<Process> execute(
        List<List<String>> commands, Map<String, String> environment, Optional<Path> output)
        throws IOException {
      calls.add(commands);
      environments.add(environment);
      outputs.add(output);
      if (scenario.equals("startIo")) throw new IOException("private diagnostic");
      if (scenario.equals("nullList")) return null;
      int count = scenario.equals("wrongCount") ? 0 : commands.size();
      List<Process> result = new ArrayList<>();
      for (int i = 0; i < count; i++) {
        if (scenario.equals("nullProcess") && i == 0) {
          result.add(null);
          continue;
        }
        FakeProcess p = new FakeProcess(this, i);
        processes.add(p);
        result.add(p);
      }
      return result;
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public byte[] accessAcl(Path p, int maximum) {
      throw new AssertionError("file admission is caller responsibility");
    }

    @Override
    public boolean readOnlyFilesystem(Path p) {
      throw new AssertionError("file admission is caller responsibility");
    }

    void closedStreams() {
      for (var p : processes) {
        assertEquals(p.outAcquired, p.outClosed);
        assertEquals(p.inAcquired, p.inputClosed);
        assertEquals(p.errAcquired, p.errClosed);
      }
    }

    void closed() {
      closedStreams();
      for (var p : processes) assertFalse(p.alive);
    }
  }

  private static final class FakeProcess extends Process {
    final Fixture fixture;
    final int index;
    final ByteArrayOutputStream received = new ByteArrayOutputStream();
    int outAcquired, inAcquired, errAcquired, outClosed, inputClosed, errClosed;
    volatile boolean alive = true, destroyed;
    int terminalWaits;

    FakeProcess(Fixture f, int index) {
      fixture = f;
      this.index = index;
    }

    boolean selected(String point) {
      return index == fixture.badProcess && fixture.scenario.equals(point);
    }

    void event(String point) throws IOException {
      if (selected(point)) {
        if (fixture.unknown != null) throw fixture.unknown;
        throw new IOException("private diagnostic");
      }
      if (point.equals("closeErr") && index == 0 && fixture.cleanupUnknown != null)
        throw fixture.cleanupUnknown;
    }

    @Override
    public InputStream getInputStream() {
      if (selected("getOut")) {
        if (fixture.unknown != null) throw fixture.unknown;
        return null;
      }
      if (selected("nullOut")) return null;
      outAcquired++;
      return new ByteArrayInputStream(new byte[0]) {
        @Override
        public void close() throws IOException {
          outClosed++;
          event("closeOut");
        }
      };
    }

    @Override
    public OutputStream getOutputStream() {
      if (selected("getIn")) {
        if (fixture.unknown != null) throw fixture.unknown;
        return null;
      }
      if (selected("nullIn")) return null;
      inAcquired++;
      return new OutputStream() {
        @Override
        public void write(int b) throws IOException {
          event("write");
          received.write(b);
        }

        @Override
        public void close() throws IOException {
          inputClosed++;
          event("closeIn");
        }
      };
    }

    @Override
    public InputStream getErrorStream() {
      if (selected("getErr")) {
        if (fixture.unknown != null) throw fixture.unknown;
        return null;
      }
      if (selected("nullErr")) return null;
      errAcquired++;
      return new ByteArrayInputStream(new byte[0]) {
        @Override
        public void close() throws IOException {
          errClosed++;
          event("closeErr");
        }
      };
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
      if (fixture.stubborn) {
        if (!destroyed || ++terminalWaits == 1) return false;
        if (fixture.holdInterrupt && terminalWaits == 2) {
          Thread.currentThread().interrupt();
          throw new InterruptedException("public hold interruption");
        }
        if (fixture.holdEmptyWait) {
          fixture.holdEmptyWait = false;
          return false;
        }
        fixture.terminalHoldEntered.countDown();
        if (!fixture.terminalRelease.await(5, TimeUnit.SECONDS)) return false;
        alive = false;
        return true;
      }
      if (selected("wait") && fixture.unknown != null) throw fixture.unknown;
      if (selected("interrupt") || destroyed && fixture.scenario.equals("terminateInterrupt"))
        throw new InterruptedException("public");
      if (destroyed && fixture.scenario.equals("terminateTimeout")) return false;
      if (!destroyed && (fixture.beforeTimeout || selected("timeout"))) return false;
      alive = false;
      if (selected("lateInterrupt")) Thread.currentThread().interrupt();
      return true;
    }

    @Override
    public int waitFor() throws InterruptedException {
      waitFor(1, TimeUnit.SECONDS);
      return exitValue();
    }

    @Override
    public int exitValue() {
      return selected("exit") || fixture.calls.size() == 2 && fixture.scenario.equals("listExit")
          ? 1
          : 0;
    }

    @Override
    public boolean isAlive() {
      if (fixture.stubborn && destroyed && terminalWaits >= 1 && !fixture.holdFaults.isEmpty()) {
        Throwable failure = fixture.holdFaults.removeFirst();
        if (fixture.exitOnHoldFault) alive = false;
        if (fixture.interruptOnHoldFault) Thread.currentThread().interrupt();
        if (failure instanceof Error fatal) throw fatal;
        throw (RuntimeException) failure;
      }
      return alive;
    }

    @Override
    public void destroy() {
      destroyed = true;
      if (fixture.stubborn) return;
      if (selected("destroy") && fixture.unknown != null) throw fixture.unknown;
      alive = false;
    }
  }
}
