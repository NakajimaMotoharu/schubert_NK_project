package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BooleanSupplier;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** RERUN008A..E: actual empty SQL coordinator and independent scheduler/ownership latches. */
final class RevocationRetryWorkerTest {
  @TempDir Path root;

  @Test
  void nativeBudget002ZeroIsBoundedAndActualJoinRetainsUnknownWorker() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var owner = new AtomicReference<Thread>();
    var worker =
        RevocationRetryWorker.start(
            () -> {
              owner.set(Thread.currentThread());
              entered.countDown();
              while (release.getCount() != 0) {
                try {
                  release.await();
                } catch (InterruptedException ignored) {
                  /* held vendor */
                }
              }
            },
            Duration.ofMillis(1),
            Duration.ofMillis(1));
    assertTrue(entered.await(5, TimeUnit.SECONDS));
    try {
      assertThrows(NullPointerException.class, () -> worker.closeWithin(null));
      assertThrows(IllegalArgumentException.class, () -> worker.closeWithin(Duration.ofNanos(-1)));
      assertThrows(
          IllegalArgumentException.class,
          () -> worker.closeWithin(Duration.ofSeconds(30).plusNanos(1)));
      assertTrue(worker.running());
      assertThrows(IllegalStateException.class, () -> worker.closeWithin(Duration.ZERO));
      assertThrows(IllegalStateException.class, () -> worker.closeWithin(Duration.ofMillis(1)));
      assertTrue(owner.get().isAlive());
      assertFalse(worker.running());
    } finally {
      release.countDown();
      worker.closeWithin(Duration.ofSeconds(30));
    }
    assertFalse(owner.get().isAlive());
    worker.closeWithin(Duration.ZERO);
  }

  @Test
  void rerun008aPublicCoordinatorOwnsNoOuterDbKeyOrBroker() throws Exception {
    var db = new WebLogDatabaseFixture(root);
    try (var codec = new RevocationPayloadCodec("revoke", new byte[32], null, null)) {
      var clock = Clock.systemUTC();
      var replies = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 12);
      var wire =
          new LogoutWireClient(
              replies,
              (id, body) -> fail("empty SQL must never send"),
              clock,
              UUID::randomUUID,
              Duration.ofSeconds(2));
      var source =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (p, m, a) -> {
                    if (m.getName().equals("getConnection")) return db.web();
                    throw new AssertionError("unexpected DataSource operation");
                  });
      var coordinator = new RevocationRetryCoordinator(source, codec, wire, clock);
      try (var worker = RevocationRetryWorker.start(coordinator, Duration.ofMillis(1))) {
        await(() -> worker.snapshot().completedCycles() > 0);
        assertTrue(worker.running());
        assertFalse(worker.terminalFailureObserved());
        assertEquals(0, worker.snapshot().failedCycles());
      }
      assertEquals(RevocationRetryCoordinator.Outcome.EMPTY, coordinator.dispatchOne());
      assertEquals(0, replies.pendingCount());
    } finally {
      db.stop();
    }
  }

  @Test
  void rerun008bTransientFailureRecoveryAndFatalTerminalNeverExposeProvider() throws Exception {
    var calls = new AtomicInteger();
    try (var worker =
        RevocationRetryWorker.start(
            () -> {
              if (calls.incrementAndGet() == 1) throw new IllegalStateException("private provider");
            },
            Duration.ofMillis(1),
            Duration.ofSeconds(1))) {
      await(() -> worker.snapshot().completedCycles() > 0);
      assertEquals(1, worker.snapshot().failedCycles());
      assertFalse(worker.snapshot().toString().contains("private"));
      assertFalse(worker.terminalFailureObserved());
    }
    for (boolean nested : new boolean[] {false, true}) {
      var worker =
          RevocationRetryWorker.start(
              () -> {
                if (nested)
                  throw new IllegalStateException("private", new AssertionError("private fatal"));
                throw new AssertionError("private fatal");
              },
              Duration.ofMillis(1),
              Duration.ofSeconds(1));
      try {
        await(worker::terminalFailureObserved);
        assertFalse(worker.running());
        assertEquals(0, worker.snapshot().completedCycles());
        assertEquals(0, worker.snapshot().failedCycles());
      } finally {
        worker.close();
      }
      worker.close();
    }
  }

  @Test
  void rerun008cUnknownJoinRepeatedJoinAndInterruptedOwnerRemainUnknown() throws Exception {
    for (boolean interruptOwner : new boolean[] {false, true}) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var observed = new AtomicReference<Thread>();
      var worker =
          RevocationRetryWorker.start(
              () -> {
                observed.set(Thread.currentThread());
                entered.countDown();
                while (release.getCount() != 0) {
                  try {
                    release.await();
                  } catch (InterruptedException ignored) {
                    /* synthetic provider ignores interruption */
                  }
                }
              },
              Duration.ofMillis(1),
              Duration.ofMillis(1));
      assertTrue(entered.await(5, TimeUnit.SECONDS));
      try {
        if (interruptOwner) Thread.currentThread().interrupt();
        var error = assertThrows(IllegalStateException.class, worker::close);
        assertEquals(
            interruptOwner
                ? "revocation worker stop was interrupted"
                : "revocation worker did not stop within its deadline",
            error.getMessage());
        assertEquals(interruptOwner, Thread.currentThread().isInterrupted());
        Thread.interrupted();
        assertThrows(IllegalStateException.class, worker::close);
        assertTrue(observed.get().isAlive());
        assertFalse(worker.running());
      } finally {
        Thread.interrupted();
        release.countDown();
        observed.get().join(5000);
        assertFalse(observed.get().isAlive());
        worker.close();
      }
    }
  }

  @Test
  void rerun008dSelfJoinRejectsWithoutDeadlockThenExternalJoinConfirms() throws Exception {
    var owner = new AtomicReference<RevocationRetryWorker>();
    var proceed = new CountDownLatch(1);
    var observed = new AtomicReference<Thread>();
    var worker =
        RevocationRetryWorker.start(
            () -> {
              observed.set(Thread.currentThread());
              try {
                assertTrue(proceed.await(5, TimeUnit.SECONDS));
              } catch (InterruptedException unexpected) {
                throw new AssertionError(unexpected);
              }
              owner.get().close();
            },
            Duration.ofMillis(1),
            Duration.ofSeconds(1));
    owner.set(worker);
    proceed.countDown();
    try {
      await(() -> worker.snapshot().failedCycles() == 1);
      assertEquals(0, worker.snapshot().completedCycles());
      assertFalse(worker.terminalFailureObserved());
    } finally {
      worker.close();
    }
    assertFalse(observed.get().isAlive());
  }

  @Test
  void rerun008eNullBoundsAndSnapshotInvariants() {
    assertThrows(
        NullPointerException.class, () -> RevocationRetryWorker.start(null, Duration.ofMillis(1)));
    assertThrows(
        NullPointerException.class,
        () -> RevocationRetryWorker.start(null, Duration.ofMillis(1), Duration.ofMillis(1)));
    assertThrows(
        NullPointerException.class,
        () -> RevocationRetryWorker.start(() -> {}, null, Duration.ofMillis(1)));
    assertThrows(
        NullPointerException.class,
        () -> RevocationRetryWorker.start(() -> {}, Duration.ofMillis(1), null));
    for (Duration interval : new Duration[] {Duration.ZERO, Duration.ofMinutes(1).plusNanos(1)})
      assertThrows(
          IllegalArgumentException.class,
          () -> RevocationRetryWorker.start(() -> {}, interval, Duration.ofMillis(1)));
    for (Duration timeout : new Duration[] {Duration.ZERO, Duration.ofSeconds(5).plusNanos(1)})
      assertThrows(
          IllegalArgumentException.class,
          () -> RevocationRetryWorker.start(() -> {}, Duration.ofMillis(1), timeout));
    assertThrows(IllegalArgumentException.class, () -> new RevocationRetryWorker.Snapshot(-1, 0));
    assertThrows(IllegalArgumentException.class, () -> new RevocationRetryWorker.Snapshot(0, -1));
    assertEquals(0, new RevocationRetryWorker.Snapshot(0, 0).completedCycles());
  }

  private static void await(BooleanSupplier observed) throws Exception {
    long end = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
    while (!observed.getAsBoolean()) {
      if (System.nanoTime() >= end) fail("bounded worker observation timed out");
      Thread.sleep(2);
    }
  }
}
