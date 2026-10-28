package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-ROOTWAIT-SSC307-001..012: literal sequence/clock/identity oracles, no native authority. */
final class RootPendingWaitTest {
  private static final String FIXTURE_CLOCK_10_79F89E76 = "clock:10";
  private static final String FIXTURE_OWNER_1_2DF3970D = "owner:1";
  private static final String FIXTURE_READ_1_9B660CEF = "read:1";
  private static final String FIXTURE_OWNER_2_202E7B96 = "owner:2";
  private static final String FIXTURE_CLOCK_99_019E434D = "clock:99";
  private static final String FIXTURE_PAUSE_1_F203A93F = "pause:1";

  private static RootStartupContext.Snapshot self(ServiceConfigFiles.Service service) {
    var role = RootStartupContext.Service.valueOf(service.name());
    return new RootStartupContext.Snapshot(
        role,
        "31100027-3333-4333-8444-555555555555",
        "2".repeat(32),
        300,
        200,
        9,
        "/system.slice/" + role.unit());
  }

  private static StartupLaunchRecord record(ServiceConfigFiles.Service service, long pid) {
    return new StartupLaunchRecord(
        service,
        UUID.fromString("31100027-3333-4333-8444-555555555555"),
        UUID.fromString("31100027-4444-4333-8444-555555555555"),
        "a".repeat(64),
        "b".repeat(64),
        new MaintenanceOwnerFrame.Parent("2".repeat(32), pid, 200));
  }

  @Test
  void pending001ImmediateBothServicesHaveExactObservationOrder() throws Exception {
    for (var service : ServiceConfigFiles.Service.values()) {
      var io = new Fake(10, 11);
      io.launches = List.of(Optional.of(record(service, 300)));
      RootStartupPending.awaitLaunch(self(service), 100, io);
      assertEquals(
          List.of(
              FIXTURE_CLOCK_10_79F89E76,
              FIXTURE_OWNER_1_2DF3970D,
              FIXTURE_READ_1_9B660CEF,
              FIXTURE_OWNER_2_202E7B96,
              "clock:11"),
          io.events);
    }
    var boundary = new Fake(99, 99);
    RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, boundary);
    assertEquals(
        List.of(
            FIXTURE_CLOCK_99_019E434D,
            FIXTURE_OWNER_1_2DF3970D,
            FIXTURE_READ_1_9B660CEF,
            FIXTURE_OWNER_2_202E7B96,
            FIXTURE_CLOCK_99_019E434D),
        boundary.events);
  }

  @Test
  void pending002MissingTwiceUsesSameDeadlineAndExactOrder() throws Exception {
    var io = new Fake(1, 2, 3, 4);
    io.launches =
        List.of(
            Optional.empty(),
            Optional.empty(),
            Optional.of(record(ServiceConfigFiles.Service.API, 300)));
    RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io);
    assertEquals(
        List.of(
            "clock:1",
            FIXTURE_OWNER_1_2DF3970D,
            FIXTURE_READ_1_9B660CEF,
            FIXTURE_PAUSE_1_F203A93F,
            "clock:2",
            FIXTURE_OWNER_2_202E7B96,
            "read:2",
            "pause:2",
            "clock:3",
            "owner:3",
            "read:3",
            "owner:4",
            "clock:4"),
        io.events);
  }

  @Test
  void pending003EqualOrPastDeadlineRejectsBeforeOwner() {
    for (long value : new long[] {100, 101}) {
      var io = new Fake(value);
      unavailable(
          () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io));
      assertEquals(List.of("clock:" + value), io.events);
    }
  }

  @Test
  void pending004MissingCannotRestartOrExtendDeadline() {
    var io = new Fake(99, 100);
    io.launches = List.of(Optional.empty());
    unavailable(
        () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io));
    assertEquals(
        List.of(
            FIXTURE_CLOCK_99_019E434D,
            FIXTURE_OWNER_1_2DF3970D,
            FIXTURE_READ_1_9B660CEF,
            FIXTURE_PAUSE_1_F203A93F,
            "clock:100"),
        io.events);
  }

  @Test
  void pending005FinalDeadlineIsStrictAndAfterOwner() {
    for (long value : new long[] {100, 101}) {
      var io = new Fake(99, value);
      unavailable(
          () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io));
      assertEquals(
          List.of(
              FIXTURE_CLOCK_99_019E434D,
              FIXTURE_OWNER_1_2DF3970D,
              FIXTURE_READ_1_9B660CEF,
              FIXTURE_OWNER_2_202E7B96,
              "clock:" + value),
          io.events);
    }
  }

  @Test
  void pending006EitherOwnerFailureStopsWithoutLaterObservation() {
    for (int index : new int[] {1, 2}) {
      var io = new Fake(10);
      var failure = new IOException("PUBLIC_OWNER_FAILURE");
      io.failAt = "owner:" + index;
      io.failure = failure;
      assertSame(
          failure,
          assertThrows(
              IOException.class,
              () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io)));
      assertEquals(
          index == 1
              ? List.of(FIXTURE_CLOCK_10_79F89E76, FIXTURE_OWNER_1_2DF3970D)
              : List.of(
                  FIXTURE_CLOCK_10_79F89E76,
                  FIXTURE_OWNER_1_2DF3970D,
                  FIXTURE_READ_1_9B660CEF,
                  FIXTURE_OWNER_2_202E7B96),
          io.events);
    }
  }

  @Test
  void pending007UnknownClockOwnerReadAndPauseFailuresKeepIdentity() {
    for (String event :
        List.of(
            FIXTURE_CLOCK_10_79F89E76,
            FIXTURE_OWNER_1_2DF3970D,
            FIXTURE_READ_1_9B660CEF,
            FIXTURE_PAUSE_1_F203A93F)) {
      for (Throwable failure :
          List.of(
              new IOException("PUBLIC_IO"),
              new IllegalStateException("PUBLIC_RUNTIME"),
              new AssertionError("PUBLIC_ERROR"))) {
        if (event.equals(FIXTURE_PAUSE_1_F203A93F) && failure instanceof IOException) continue;
        var io = new Fake(10);
        io.failAt = event;
        io.failure = failure;
        if (event.equals(FIXTURE_PAUSE_1_F203A93F)) io.launches = List.of(Optional.empty());
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () ->
                    RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io)));
        assertEquals(event, io.events.getLast());
      }
    }
  }

  @Test
  void pending008WrongChildGenerationStopsBeforeSecondOwner() {
    var io = new Fake(10);
    io.launches = List.of(Optional.of(record(ServiceConfigFiles.Service.API, 301)));
    unavailable(
        () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io));
    assertEquals(
        List.of(FIXTURE_CLOCK_10_79F89E76, FIXTURE_OWNER_1_2DF3970D, FIXTURE_READ_1_9B660CEF),
        io.events);
  }

  @Test
  void pending009InterruptedPauseRestoresFlagAndRedactsCause() {
    boolean wasInterrupted = Thread.currentThread().isInterrupted();
    try {
      var io = new Fake(10);
      io.launches = List.of(Optional.empty());
      io.interrupt = true;
      IOException failure =
          assertThrows(
              IOException.class,
              () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io));
      assertEquals("root launch unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(
          List.of(
              FIXTURE_CLOCK_10_79F89E76,
              FIXTURE_OWNER_1_2DF3970D,
              FIXTURE_READ_1_9B660CEF,
              FIXTURE_PAUSE_1_F203A93F),
          io.events);
    } finally {
      Thread.interrupted();
      if (wasInterrupted) Thread.currentThread().interrupt();
    }
  }

  @Test
  void pending010NullBoundariesDoNotObserveNativeInputs() {
    var io = new Fake(10);
    assertThrows(NullPointerException.class, () -> RootStartupPending.awaitLaunch(null, 100, io));
    assertTrue(io.events.isEmpty());
    assertThrows(
        NullPointerException.class,
        () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, null));
    io.nullLaunch = true;
    assertThrows(
        NullPointerException.class,
        () -> RootStartupPending.awaitLaunch(self(ServiceConfigFiles.Service.API), 100, io));
    assertEquals(
        List.of(FIXTURE_CLOCK_10_79F89E76, FIXTURE_OWNER_1_2DF3970D, FIXTURE_READ_1_9B660CEF),
        io.events);
  }

  @Test
  void pending011OnlyMissingLaunchBecomesEmpty() throws Exception {
    var literal = record(ServiceConfigFiles.Service.API, 300);
    assertSame(literal, RootStartupPending.readLaunch(() -> literal).orElseThrow());
    for (var reason : StorageIoException.Reason.values()) {
      var failure = new StorageIoException(reason);
      if (reason == StorageIoException.Reason.MISSING) {
        assertEquals(
            Optional.empty(),
            RootStartupPending.readLaunch(
                () -> {
                  throw failure;
                }));
      } else {
        assertSame(
            failure,
            assertThrows(
                StorageIoException.class,
                () ->
                    RootStartupPending.readLaunch(
                        () -> {
                          throw failure;
                        })));
      }
    }
  }

  @Test
  void pending012ReadIdentityAndNullContractsStayFailures() {
    for (Throwable failure :
        List.of(
            new IOException("PUBLIC_IO"),
            new IllegalStateException("PUBLIC_RUNTIME"),
            new AssertionError("PUBLIC_ERROR"))) {
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () ->
                  RootStartupPending.readLaunch(
                      () -> {
                        if (failure instanceof IOException io) throw io;
                        if (failure instanceof RuntimeException runtime) throw runtime;
                        throw (Error) failure;
                      })));
    }
    assertThrows(NullPointerException.class, () -> RootStartupPending.readLaunch(null));
    assertThrows(NullPointerException.class, () -> RootStartupPending.readLaunch(() -> null));
  }

  private static void unavailable(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
  }

  private static final class Fake implements RootStartupPending.WaitIo {
    private final long[] ticks;
    private final List<String> events = new ArrayList<>();
    private List<Optional<StartupLaunchRecord>> launches =
        List.of(Optional.of(record(ServiceConfigFiles.Service.API, 300)));
    private int clocks;
    private int owners;
    private int reads;
    private int pauses;
    private String failAt = "";
    private @org.jspecify.annotations.Nullable Throwable failure;
    private boolean interrupt;
    private boolean nullLaunch;

    Fake(long... ticks) {
      this.ticks = ticks;
    }

    private void mark(String event) throws IOException {
      events.add(event);
      if (!event.equals(failAt)) return;
      if (failure instanceof IOException io) throw io;
      if (failure instanceof RuntimeException runtime) throw runtime;
      if (failure instanceof Error error) throw error;
      throw new AssertionError("fixture failure type");
    }

    @Override
    public long nowNanos() throws IOException {
      long value = ticks[clocks++];
      mark("clock:" + value);
      return value;
    }

    @Override
    public void requireOwner() throws IOException {
      mark("owner:" + ++owners);
    }

    @Override
    public Optional<StartupLaunchRecord> readLaunch() throws IOException {
      mark("read:" + ++reads);
      return nullLaunch ? null : launches.get(reads - 1);
    }

    @Override
    public void pause() throws InterruptedException {
      String event = "pause:" + ++pauses;
      events.add(event);
      if (interrupt) throw new InterruptedException("PUBLIC_INTERRUPTION_MARKER");
      if (event.equals(failAt)) {
        if (failure instanceof RuntimeException runtime) throw runtime;
        if (failure instanceof Error error) throw error;
        throw new AssertionError("fixture pause failure type");
      }
    }
  }
}
