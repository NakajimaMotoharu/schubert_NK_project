package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * PG363/365/366; PT-OPS-BUCYCLE-001..006. Synthetic ports never claim real worker/archive
 * admission.
 */
final class MorningBackupUnitCycleTest {
  private static final class Retained extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }

  private static final class StartAttempt implements MorningBackupUnitCycle.StartAttempt {
    BackupUnitStartClient.Status status = BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
    int retire;
    int await;
    MorningBackupUnitCycle.ParentProof retirement = () -> {};

    public BackupUnitStartClient.Status status() {
      return status;
    }

    public BackupUnitStartClient.Status awaitClient() {
      await++;
      return status;
    }

    public void retireAfter(MorningBackupUnitCycle.ParentProof proof) throws IOException {
      retirement.verify();
      proof.verify();
      retire++;
    }
  }

  private static final class StopAttempt implements MorningBackupUnitCycle.StopAttempt {
    MaintenanceUnitStopClient.Status status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
    int await;

    public MaintenanceUnitStopClient.Status status() {
      return status;
    }

    public MaintenanceUnitStopClient.Status awaitClient() {
      await++;
      return status;
    }
  }

  @Test
  void bucycle001ExactParentOrderAndSingleRetirement() throws Exception {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    var stop = new StopAttempt();
    int[] observations = {0};
    var cycle =
        new MorningBackupUnitCycle(
            () -> events.add("root"),
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() {
                events.add("baseline");
                return "pre-start";
              }

              public boolean freshZero(Object baseline) {
                assertEquals("pre-start", baseline);
                events.add("receipt");
                return ++observations[0] == 2;
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> {
              events.add("stop");
              return stop;
            },
            () -> {
              events.add("terminal");
              return true;
            },
            () -> events.add("wait"),
            () -> fail("known complete cycle must not be retained"),
            budget());
    cycle.execute(() -> events.add("original-request"));
    assertEquals(
        List.of(
            "root",
            "baseline",
            "root",
            "start",
            "root",
            "receipt",
            "wait",
            "receipt",
            "root",
            "stop",
            "root",
            "terminal",
            "root",
            "original-request",
            "terminal",
            "root",
            "root"),
        events);
    assertEquals(1, start.retire);
    assertEquals(0, start.await);
    assertEquals(0, stop.await);
  }

  @Test
  void bucycle002UnknownStartAndStopNeverAdvanceUntilRealClientResult() throws Exception {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    start.status = BackupUnitStartClient.Status.UNKNOWN;
    var stop = new StopAttempt();
    stop.status = MaintenanceUnitStopClient.Status.UNKNOWN;
    int[] waits = {0};
    var cycle =
        cycle(
            events,
            start,
            stop,
            () -> {
              events.add("wait");
              if (++waits[0] == 2) {
                assertFalse(events.contains("stop"));
                start.status = BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
              }
              if (waits[0] == 4) {
                assertEquals(0, start.retire);
                stop.status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
              }
            },
            () -> fail("eventually reaped attempts must complete"));
    cycle.execute(() -> events.add("original-request"));
    assertEquals(4, waits[0]);
    assertEquals(2, start.await);
    assertEquals(2, stop.await);
    assertEquals(1, start.retire);
    assertTrue(events.indexOf("stop") > events.indexOf("receipt"));
    assertTrue(events.indexOf("original-request") > events.indexOf("terminal"));

    start.status = BackupUnitStartClient.Status.UNKNOWN;
    stop.status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
    int before = start.retire;
    var pendingEvents = new ArrayList<String>();
    var pending =
        cycle(
            pendingEvents,
            start,
            stop,
            () -> {
              if (start.await >= 4) throw new Retained();
            },
            () -> {
              pendingEvents.add("retain");
              throw new Retained();
            });
    assertThrows(Retained.class, () -> pending.execute(() -> fail("no proof")));
    assertEquals(before, start.retire);
    assertEquals("retain", pendingEvents.getLast());
  }

  @Test
  void bucycle003PostStartUncertaintyRetainsAndPreStartFailureDoesNotStart() {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    var stop = new StopAttempt();
    var brokenReceipt =
        new MorningBackupUnitCycle(
            () -> {},
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() {
                return "baseline";
              }

              public boolean freshZero(Object baseline) throws IOException {
                throw new IOException("untrusted receipt");
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> {
              events.add("stop");
              return stop;
            },
            () -> true,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            },
            budget());
    assertThrows(Retained.class, () -> brokenReceipt.execute(() -> fail("no proof")));
    assertEquals(List.of("start", "retain"), events);
    assertEquals(0, start.retire);

    events.clear();
    var beforeStart =
        new MorningBackupUnitCycle(
            () -> {},
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() throws IOException {
                throw new IOException("pre-start unavailable");
              }

              public boolean freshZero(Object baseline) {
                fail("no observe");
                return false;
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> stop,
            () -> true,
            () -> {},
            () -> fail("no retention before start"),
            budget());
    assertThrows(IOException.class, () -> beforeStart.execute(() -> {}));
    assertTrue(events.isEmpty());
  }

  @Test
  void bucycle004NonzeroAndRetireFailureNeverReturnSuccess() {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    var stop = new StopAttempt();
    start.status = BackupUnitStartClient.Status.CLIENT_EXITED_NONZERO;
    var failed =
        cycle(
            events,
            start,
            stop,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            });
    assertThrows(Retained.class, () -> failed.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "start", "terminal", "retain"), events);
    assertEquals(0, start.retire);

    events.clear();
    start.status = BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
    start.retirement =
        () -> {
          throw new IOException("uncertain marker retirement");
        };
    assertThrows(Retained.class, () -> failed.execute(() -> events.add("original-request")));
    assertEquals(0, start.retire);
    assertTrue(events.contains("stop"));
    assertEquals("retain", events.getLast());
    assertThrows(NullPointerException.class, () -> failed.execute(null));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningBackupUnitCycle(
                null,
                receipt(events),
                () -> start,
                () -> stop,
                () -> true,
                () -> {},
                () -> {},
                budget()));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningBackupUnitCycle(
                () -> {},
                receipt(events),
                () -> start,
                () -> stop,
                () -> true,
                () -> {},
                () -> {},
                null));
  }

  @Test
  void bucycle005UnknownStartFailureAndNullAfterStartCannotUnwindParent() {
    for (Throwable failure :
        List.of(
            new IOException("unresolved start delivery"),
            new StopGateException(StopGateFailure.COMMAND_FAILURE),
            new IllegalStateException("unresolved start delivery"),
            new AssertionError("unresolved start delivery"))) {
      var events = new ArrayList<String>();
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              receipt(events),
              () -> {
                events.add("start");
                if (failure instanceof IOException known) throw known;
                if (failure instanceof RuntimeException unknown) throw unknown;
                throw (Error) failure;
              },
              () -> {
                events.add("stop");
                fail("unknown start cannot stop");
                return null;
              },
              () -> true,
              () -> {},
              () -> {
                events.add("retain");
                throw new Retained();
              },
              budget());
      assertThrows(Retained.class, () -> cycle.execute(() -> fail("no proof")));
      assertEquals(List.of("baseline", "start", "retain"), events);
    }
    for (boolean nullAttempt : List.of(true, false)) {
      var events = new ArrayList<String>();
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              receipt(events),
              () -> {
                events.add("start");
                if (nullAttempt) return null;
                return new MorningBackupUnitCycle.StartAttempt() {
                  public BackupUnitStartClient.Status status() {
                    return null;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    fail("null status is not a pending client");
                    return null;
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof) {
                    fail("null status cannot retire");
                  }
                };
              },
              () -> {
                fail("null start cannot stop");
                return null;
              },
              () -> true,
              () -> {},
              () -> {
                events.add("retain");
                throw new Retained();
              },
              budget());
      assertThrows(Retained.class, () -> cycle.execute(() -> fail("no proof")));
      assertEquals(List.of("baseline", "start", "retain"), events);
    }
    var awaitEvents = new ArrayList<String>();
    var nullAwait =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(awaitEvents),
            () ->
                new MorningBackupUnitCycle.StartAttempt() {
                  public BackupUnitStartClient.Status status() {
                    return BackupUnitStartClient.Status.UNKNOWN;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    return null;
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof) {
                    fail("null await cannot retire");
                  }
                },
            () -> {
              fail("null await cannot stop");
              return null;
            },
            () -> true,
            () -> awaitEvents.add("wait"),
            () -> {
              awaitEvents.add("retain");
              throw new Retained();
            },
            budget());
    assertThrows(Retained.class, () -> nullAwait.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "wait", "retain"), awaitEvents);
  }

  @Test
  void bucycle006OneParentBudgetRejectsBeforeStartAndRetainsAfterStart() {
    final long deadline = 1_800_000_000_000L; // SS341: 30 * 60 * 10^9 ns.
    long[] now = {0};
    var parentBudget = new MorningParentBudget(() -> now[0]);
    var events = new ArrayList<String>();
    var before =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(events),
            () -> {
              events.add("start");
              return new StartAttempt();
            },
            StopAttempt::new,
            () -> true,
            () -> {},
            () -> fail("no start, no retention"),
            parentBudget);
    now[0] = deadline;
    assertThrows(IOException.class, () -> before.execute(() -> fail("no proof")));
    assertTrue(events.isEmpty());

    now[0] = 0;
    var start = new StartAttempt();
    var stop = new StopAttempt();
    events.clear();
    var afterStart =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(events),
            () -> {
              events.add("start");
              now[0] = deadline;
              return start;
            },
            () -> {
              fail("expired start cannot stop");
              return stop;
            },
            () -> true,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> afterStart.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "start", "retain"), events);
    assertEquals(0, start.retire);

    now[0] = 0;
    events.clear();
    var duringReceipt =
        new MorningBackupUnitCycle(
            () -> {},
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() {
                events.add("baseline");
                return "baseline";
              }

              public boolean freshZero(Object baseline) {
                assertEquals("baseline", baseline);
                now[0] = deadline;
                return false;
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> {
              fail("expired receipt cannot stop");
              return stop;
            },
            () -> true,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> duringReceipt.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "start", "retain"), events);
    assertEquals(0, start.retire);

    now[0] = 0;
    stop.status = MaintenanceUnitStopClient.Status.UNKNOWN;
    var duringStop =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(new ArrayList<>()),
            () -> start,
            () -> {
              now[0] = deadline;
              return stop;
            },
            () -> true,
            () -> fail("expired stop must not await client"),
            () -> {
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> duringStop.execute(() -> fail("no proof")));
    assertEquals(0, start.retire);

    now[0] = 0;
    stop.status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
    start.retirement = () -> now[0] = deadline;
    var beforeRetire =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(new ArrayList<>()),
            () -> start,
            () -> stop,
            () -> true,
            () -> {},
            () -> {
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> beforeRetire.execute(() -> fail("no proof")));
    assertEquals(0, start.retire);
  }

  private static MorningBackupUnitCycle.Receipt receipt(List<String> events) {
    return new MorningBackupUnitCycle.Receipt() {
      public Object capture() {
        events.add("baseline");
        return "baseline";
      }

      public boolean freshZero(Object baseline) {
        events.add("receipt");
        assertEquals("baseline", baseline);
        return true;
      }
    };
  }

  private static MorningBackupUnitCycle cycle(
      List<String> events,
      StartAttempt start,
      StopAttempt stop,
      MorningBackupUnitCycle.Wait wait,
      MorningBackupUnitCycle.Retain retain) {
    return new MorningBackupUnitCycle(
        () -> {},
        receipt(events),
        () -> {
          events.add("start");
          return start;
        },
        () -> {
          events.add("stop");
          return stop;
        },
        () -> {
          events.add("terminal");
          return true;
        },
        wait,
        retain,
        budget());
  }

  private static MorningParentBudget budget() {
    return new MorningParentBudget(() -> 0L);
  }
}
