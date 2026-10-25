package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.AbstractList;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** SS341/343; PT-OPS-ARCHPROC001..008. Commands/environment are independent literal oracles. */
final class BackupArchiveProcessTest {
  private static final String STOP_TYPES =
      "NIREIIRERRRREEEE" + "IIREIIRERRRREEEE" + "RRRRRRRRRRRRRRRR" + "EEEEEEEEEEEEEEEE";
  private static final String STOP_SUPPRESSED =
      "0000000001110111" + "0000000001110111" + "0111122212221222" + "0111122212221222";
  private static final String STOP_WINNER =
      "xx22xx2211111111" + "xx22xx2211111111" + "0000000000000000" + "0000000000000000";

  private static final class TerminalVector extends Process {
    final int index;
    final char stop;
    final char hold;
    final Throwable failure;
    final List<String> events;
    final String termEvent;
    final String confirmEvent;
    final CyclicBarrier barrier;
    boolean alive = true;
    boolean stopped;
    boolean observed;

    TerminalVector(
        int index,
        char stop,
        char hold,
        Throwable failure,
        List<String> events,
        CyclicBarrier barrier) {
      this.index = index;
      this.stop = stop;
      this.hold = hold;
      this.failure = failure;
      this.events = events;
      this.barrier = barrier;
      termEvent = "term" + index;
      confirmEvent = "confirm" + index;
    }

    public InputStream getInputStream() {
      return InputStream.nullInputStream();
    }

    public OutputStream getOutputStream() {
      return OutputStream.nullOutputStream();
    }

    public InputStream getErrorStream() {
      return InputStream.nullInputStream();
    }

    public int waitFor() {
      return 0;
    }

    public boolean waitFor(long time, TimeUnit unit) {
      assertEquals(5, time);
      assertEquals(TimeUnit.SECONDS, unit);
      return stop != 'I';
    }

    public int exitValue() {
      return 0;
    }

    public boolean isAlive() {
      if (stopped && !observed) {
        observed = true;
        events.add(confirmEvent);
        if (hold != 'N') raise(failure);
      }
      return alive;
    }

    public void destroy() {
      events.add(termEvent);
      stopped = true;
      alive = false;
      if (barrier != null && index == 0)
        try {
          barrier.await(10, TimeUnit.SECONDS);
        } catch (Exception failure) {
          throw new AssertionError(failure);
        }
      if (stop == 'R' || stop == 'E') raise(failure);
    }

    static void raise(Throwable failure) {
      if (failure instanceof RuntimeException runtime) throw runtime;
      throw (Error) failure;
    }
  }

  private static Throwable vectorFailure(char kind) {
    return kind == 'E'
        ? new LinkageError("synthetic terminal")
        : new IllegalStateException("synthetic terminal");
  }

  /**
   * PT-OPS-ARCHOWN001: 64 literal stop/cleanup precedence vectors, every child stopped before
   * holds.
   */
  @Test
  void archiveown001All64StopStatesMatchIndependentLiteralPrecedenceAndOrder() throws Exception {
    assertEquals(64, STOP_TYPES.length());
    assertEquals(64, STOP_SUPPRESSED.length());
    assertEquals(64, STOP_WINNER.length());
    char[] states = {'N', 'I', 'R', 'E'};
    for (int vector = 0; vector < 64; vector++) {
      var events = new ArrayList<String>(16);
      var processes = new ArrayList<Process>(3);
      for (int index = 0; index < 3; index++) {
        char kind = states[(vector >> (4 - index * 2)) & 3];
        processes.add(new TerminalVector(index, kind, 'N', vectorFailure(kind), events, null));
      }
      Throwable actual = null;
      try {
        new BackupArchiveProcess.TerminalPlan().close(processes);
      } catch (IOException | RuntimeException | Error failure) {
        actual = failure;
      }
      char type = STOP_TYPES.charAt(vector);
      if (type == 'N') assertNull(actual);
      else {
        assertNotNull(actual);
        if (type == 'I') assertInstanceOf(StorageIoException.class, actual);
        else {
          int winner = STOP_WINNER.charAt(vector) - '0';
          assertSame(((TerminalVector) processes.get(winner)).failure, actual);
        }
        assertEquals(STOP_SUPPRESSED.charAt(vector) - '0', actual.getSuppressed().length);
        for (Throwable secondary : actual.getSuppressed()) {
          assertInstanceOf(StorageIoException.class, secondary);
          assertNull(secondary.getCause());
        }
      }
      assertEquals(List.of("term0", "term1", "term2", "confirm0", "confirm1", "confirm2"), events);
      assertTrue(processes.stream().noneMatch(Process::isAlive));
    }
  }

  /**
   * PT-OPS-ARCHOWN002: 27 independent hold-primary vectors after all children have really ended.
   */
  @Test
  void archiveown002All27HoldStatesKeepFirstUnknownAndConfirmEveryRemainingChild()
      throws Exception {
    String types = "NRERRREEE" + "RRRRRRRRR" + "EEEEEEEEE";
    String suppressed = "000011011" + "011122122" + "011122122";
    String winners = "x22111111" + "000000000" + "000000000";
    assertEquals(27, types.length());
    assertEquals(27, suppressed.length());
    assertEquals(27, winners.length());
    char[] states = {'N', 'R', 'E'};
    for (int vector = 0; vector < 27; vector++) {
      var events = new ArrayList<String>(16);
      var processes = new ArrayList<Process>(3);
      for (int index = 0, divisor = 9; index < 3; index++, divisor /= 3) {
        char kind = states[vector / divisor % 3];
        processes.add(new TerminalVector(index, 'N', kind, vectorFailure(kind), events, null));
      }
      Throwable actual = null;
      try {
        new BackupArchiveProcess.TerminalPlan().close(processes);
      } catch (RuntimeException | Error failure) {
        actual = failure;
      }
      if (types.charAt(vector) == 'N') assertNull(actual);
      else {
        assertSame(((TerminalVector) processes.get(winners.charAt(vector) - '0')).failure, actual);
        assertEquals(suppressed.charAt(vector) - '0', actual.getSuppressed().length);
      }
      assertEquals(List.of("term0", "term1", "term2", "confirm0", "confirm1", "confirm2"), events);
    }
  }

  /**
   * PT-OPS-ARCHOWN003: unenumerable ownership enters the prebuilt pending port, never normal
   * success.
   */
  @Test
  void archiveown003UnknownCollectionNeverUnwindsAsConfirmedTerminal() {
    var failure = new LinkageError("synthetic collection observation");
    List<Process> broken =
        new AbstractList<>() {
          public Process get(int index) {
            throw failure;
          }

          public int size() {
            return 1;
          }
        };
    var holds = new AtomicInteger();
    var plan =
        new BackupArchiveProcess.TerminalPlan(
            first -> {
              assertSame(failure, first);
              holds.incrementAndGet();
            });
    assertSame(failure, assertThrows(LinkageError.class, () -> plan.close(broken)));
    assertEquals(1, holds.get());
    assertThrows(NullPointerException.class, () -> new BackupArchiveProcess.TerminalPlan(null));
    assertThrows(
        NullPointerException.class, () -> new BackupArchiveProcess.TerminalPlan().close(null));
  }

  /**
   * PT-OPS-ARCHOWN004: absence admission still waits for all three getters; cancellation is
   * restored.
   */
  @Test
  void archiveown004NullableGettersAndIdleChildrenPreserveAdmissionAndInterrupt() throws Exception {
    for (String absent : List.of("nullOut", "nullIn", "nullErr")) {
      var fixture = new Fixture();
      fixture.scenario = absent;
      refused(() -> fixture.runner.credentials(DIR, OUT, KEY, List.of("public")));
      var first = fixture.processes.getFirst();
      assertEquals(absent.equals("nullOut") ? 0 : 1, first.outAcquired);
      assertEquals(absent.equals("nullIn") ? 0 : 1, first.inAcquired);
      assertEquals(absent.equals("nullErr") ? 0 : 1, first.errAcquired);
      fixture.closed();
    }
    var events = new ArrayList<String>();
    var ended = new TerminalVector(0, 'N', 'N', vectorFailure('N'), events, null);
    ended.alive = false;
    Thread.currentThread().interrupt();
    try {
      new BackupArchiveProcess.TerminalPlan().close(Arrays.asList(null, ended));
      assertTrue(Thread.currentThread().isInterrupted());
      assertTrue(events.isEmpty());
    } finally {
      Thread.interrupted();
    }
    var primary = new IllegalStateException("synthetic first hold");
    var retainedEvents = new ArrayList<String>();
    var first = new TerminalVector(0, 'N', 'R', primary, retainedEvents, null);
    var last = new TerminalVector(2, 'N', 'N', vectorFailure('N'), retainedEvents, null);
    assertSame(
        primary,
        assertThrows(
            IllegalStateException.class,
            () -> new BackupArchiveProcess.TerminalPlan().close(Arrays.asList(first, null, last))));
    assertEquals(List.of("term0", "term2", "confirm0", "confirm2"), retainedEvents);
  }

  /**
   * PT-OPS-ARCHOWN005: repeated provider identities never cause self-suppression or raw new graph
   * entries.
   */
  @Test
  void archiveown005ExistingAndRepeatedUnknownKeepIdentityAndSanitizeOnlyLaterFailures()
      throws Exception {
    var primary = new IllegalStateException("synthetic");
    var prior = new IOException("synthetic existing");
    primary.addSuppressed(prior);
    var events = new ArrayList<String>();
    List<Process> processes =
        List.of(
            new TerminalVector(0, 'R', 'N', primary, events, null),
            new TerminalVector(1, 'R', 'N', primary, events, null),
            new TerminalVector(2, 'E', 'N', vectorFailure('E'), events, null));
    assertSame(
        primary,
        assertThrows(
            IllegalStateException.class,
            () -> new BackupArchiveProcess.TerminalPlan().close(processes)));
    assertEquals(3, primary.getSuppressed().length);
    assertSame(prior, primary.getSuppressed()[0]);
    for (int index = 1; index < 3; index++)
      assertInstanceOf(StorageIoException.class, primary.getSuppressed()[index]);
    assertEquals(List.of("term0", "term1", "term2", "confirm0", "confirm1", "confirm2"), events);
  }

  /** PT-OPS-ARCHOWN006: simultaneous plans cannot adopt or consume another call's processes. */
  @Test
  void archiveown006ParallelPlansNeverStopOrConfirmEachOthersProcesses() throws Exception {
    var barrier = new CyclicBarrier(2);
    try (var executor = Executors.newFixedThreadPool(2)) {
      var futures = new ArrayList<Future<List<String>>>();
      for (int size : List.of(1, 2))
        futures.add(
            executor.submit(
                () -> {
                  var events = new ArrayList<String>();
                  var processes = new ArrayList<Process>();
                  for (int index = 0; index < size; index++)
                    processes.add(
                        new TerminalVector(index, 'N', 'N', vectorFailure('N'), events, barrier));
                  new BackupArchiveProcess.TerminalPlan().close(processes);
                  return events;
                }));
      assertEquals(List.of("term0", "confirm0"), futures.get(0).get(15, TimeUnit.SECONDS));
      assertEquals(
          List.of("term0", "term1", "confirm0", "confirm1"),
          futures.get(1).get(15, TimeUnit.SECONDS));
    }
  }

  private static final Path DIR = Path.of("/proc/self/fd/101");
  private static final Path OUT = Path.of("/proc/self/fd/102");
  private static final Path KEY = Path.of("/proc/self/fd/103");
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
  void archproc009ToolWaitBorrowsRemainingParentTime() throws Exception {
    long[] now = {0};
    var parent = new MorningParentBudget(() -> now[0]);
    now[0] = 1_800_000_000_000L - 7;
    var fixture = new Fixture();
    var runner = new BackupArchiveProcess(fixture, fixture, fixture::clock, Optional.of(parent));
    runner.configuration(DIR, OUT, List.of("api.yml"));
    assertEquals(7L, fixture.waitLimits.getFirst());
    fixture.closed();
    now[0]++;
    assertEquals(6, parent.remainingNanos());
    now[0] = 1_800_000_000_000L;
    var expired = new Fixture();
    var refused = new BackupArchiveProcess(expired, expired, expired::clock, Optional.of(parent));
    assertThrows(IOException.class, () -> refused.configuration(DIR, OUT, List.of("api.yml")));
    assertTrue(expired.calls.isEmpty());
    assertThrows(
        NullPointerException.class,
        () -> new BackupArchiveProcess(fixture, (MorningParentBudget) null));
    var nativeRunner = new BackupArchiveProcess(fixture, MorningParentBudget.create());
    assertThrows(
        IOException.class,
        () -> nativeRunner.configuration(Path.of("/tmp/not-an-fd"), OUT, List.of("api.yml")));
  }

  @Test
  void verificationUsesOnlyActualRestoreListUnderOrdinaryIdentity() throws Exception {
    var f = new Fixture();
    f.uid = 992;
    f.runner.verifyDump(OUT, 992);
    assertEquals(List.of(List.of("/usr/bin/pg_restore", "--list", child(102))), f.calls.getFirst());
    assertEquals(1, f.calls.size());
    assertEquals(Optional.empty(), f.outputs.getFirst());
    assertEquals(
        Map.of("PATH", "/usr/bin:/bin", "LANG", "C", "LC_ALL", "C"), f.environments.getFirst());
    assertEquals(0, f.processes.getFirst().received.size());
    f.closed();
    for (long uid : new long[] {0, -1, 4294967296L, 991}) {
      var denied = new Fixture();
      denied.uid = 992;
      refused(() -> denied.runner.verifyDump(OUT, uid));
      assertTrue(denied.calls.isEmpty());
    }
    var noIdentity = new Fixture();
    noIdentity.uid = 0;
    refused(() -> noIdentity.runner.verifyDump(OUT, 992));
    assertTrue(noIdentity.calls.isEmpty());
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
    Path source = Files.createDirectory(temporary.resolve("source"));
    Path destination = Files.createDirectory(temporary.resolve("destination"));
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
    final List<Long> waitLimits = new ArrayList<>();
    final AtomicInteger ticks = new AtomicInteger();
    final BackupArchiveProcess runner = new BackupArchiveProcess(this, this, this::clock);
    long uid;
    List<Long> timeSequence = List.of();
    String scenario = "";
    int badProcess;
    boolean beforeTimeout;
    boolean stubborn;
    boolean holdInterrupt;
    boolean interruptOnHoldFault;
    boolean holdEmptyWait;
    boolean exitOnHoldFault;
    final List<Throwable> holdFaults = new ArrayList<>();
    final CountDownLatch terminalHoldEntered = new CountDownLatch(1);
    final CountDownLatch terminalRelease = new CountDownLatch(1);
    RuntimeException unknown;
    RuntimeException cleanupUnknown;

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
    int outAcquired;
    int inAcquired;
    int errAcquired;
    int outClosed;
    int inputClosed;
    int errClosed;
    volatile boolean alive = true;
    volatile boolean destroyed;
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
      fixture.waitLimits.add(unit.toNanos(timeout));
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
