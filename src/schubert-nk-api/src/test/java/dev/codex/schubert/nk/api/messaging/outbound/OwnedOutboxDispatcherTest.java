package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.*;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.time.Clock;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Owned thread lifecycle at real dispatch/open boundary, not a synthetic covered run method. */
class OwnedOutboxDispatcherTest {
  @Test
  void outbox005AssemblyStartsNoClaimsAndStartCloseAreSingleOwner() throws Exception {
    var attempts = new CountDownLatch(1);
    var d =
        dispatcher(
            () -> {
              attempts.countDown();
              throw new SQLException("fixture");
            });
    var owned = OwnedOutboxDispatcher.create(d, "pt");
    try {
      assertFalse(owned.healthy());
      assertEquals(1, attempts.getCount());
      assertThrows(IllegalStateException.class, owned::wake);
      owned.start();
      assertThrows(IllegalStateException.class, owned::start);
      assertTrue(attempts.await(3, TimeUnit.SECONDS));
    } finally {
      owned.close();
    }
    assertThrows(IllegalStateException.class, owned::start);
    var unstarted = OwnedOutboxDispatcher.create(d, "pt");
    unstarted.close();
    unstarted.close();
    assertThrows(IllegalStateException.class, unstarted::start);
    assertFalse(unstarted.healthy());
  }

  @Test
  void outbox001TemporaryDbAndRuntimeFailureRetryClosedAndNullBoundaries() throws Exception {
    for (boolean sql : new boolean[] {true, false}) {
      CountDownLatch attempts = new CountDownLatch(2);
      var owned =
          OwnedOutboxDispatcher.start(
              dispatcher(
                  () -> {
                    attempts.countDown();
                    if (sql) throw new SQLException("synthetic-private-provider");
                    throw new IllegalStateException("synthetic-private-provider");
                  }),
              "pt");
      try {
        assertTrue(owned.healthy());
        owned.wake();
        assertTrue(attempts.await(3, TimeUnit.SECONDS));
        assertTrue(owned.healthy());
      } finally {
        owned.close();
      }
      assertFalse(owned.healthy());
      owned.close();
      assertThrows(IllegalStateException.class, owned::wake);
    }
    var d =
        dispatcher(
            () -> {
              throw new SQLException("fixture");
            });
    assertThrows(NullPointerException.class, () -> OwnedOutboxDispatcher.start(null, "pt"));
    assertThrows(NullPointerException.class, () -> OwnedOutboxDispatcher.start(d, null));
    assertThrows(IllegalArgumentException.class, () -> OwnedOutboxDispatcher.start(d, " "));
    assertThrows(
        IllegalArgumentException.class, () -> OwnedOutboxDispatcher.start(d, "x".repeat(65)));
  }

  @Test
  void outbox002CloseJoinsInFlightDispatchBeforeOwnerCanReleaseDependencies() throws Exception {
    CountDownLatch entered = new CountDownLatch(1), release = new CountDownLatch(1);
    var owned =
        OwnedOutboxDispatcher.start(
            dispatcher(
                () -> {
                  entered.countDown();
                  try {
                    release.await();
                  } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                  }
                  throw new SQLException("fixture");
                }),
            "pt");
    try (var executor = Executors.newSingleThreadExecutor()) {
      assertTrue(entered.await(3, TimeUnit.SECONDS));
      var closing =
          executor.submit(
              () -> {
                Thread.currentThread().interrupt();
                owned.close();
                boolean preserved = Thread.currentThread().isInterrupted();
                Thread.interrupted();
                return preserved;
              });
      assertThrows(TimeoutException.class, () -> closing.get(50, TimeUnit.MILLISECONDS));
      release.countDown();
      assertTrue(closing.get(3, TimeUnit.SECONDS));
      assertFalse(owned.healthy());
    } finally {
      release.countDown();
      owned.close();
    }
  }

  @Test
  void outbox003FatalIdentityIsNotNormalAndOnlyFixedRedactedStderrEscapes() throws Exception {
    CountDownLatch entered = new CountDownLatch(1);
    Error fatal = new AssertionError("synthetic-private-provider-key");
    var previous = System.err;
    var output = new ByteArrayOutputStream();
    try (var capturing = new PrintStream(output, true, StandardCharsets.UTF_8)) {
      System.setErr(capturing);
      var owned =
          OwnedOutboxDispatcher.start(
              dispatcher(
                  () -> {
                    entered.countDown();
                    throw fatal;
                  }),
              "pt");
      try {
        assertTrue(entered.await(3, TimeUnit.SECONDS));
      } finally {
        owned.close();
      }
      assertFalse(owned.healthy());
      assertThrows(IllegalStateException.class, owned::wake);
      assertEquals(
          "NK_API_OUTBOX_FATAL" + System.lineSeparator(), output.toString(StandardCharsets.UTF_8));
    } finally {
      System.setErr(previous);
    }
  }

  @Test
  void outbox004InterruptAndSelfJoinNeverLoseLifetimeOrInterruptState() throws Exception {
    CountDownLatch entered = new CountDownLatch(1);
    AtomicReference<Thread> thread = new AtomicReference<>();
    var owned =
        OwnedOutboxDispatcher.start(
            dispatcher(
                () -> {
                  thread.set(Thread.currentThread());
                  entered.countDown();
                  Thread.currentThread().interrupt();
                  throw new SQLException("fixture");
                }),
            "pt");
    try {
      assertTrue(entered.await(3, TimeUnit.SECONDS));
      thread.get().join(3000);
      assertFalse(thread.get().isAlive());
      assertTrue(thread.get().isInterrupted());
      assertFalse(owned.healthy());
      assertThrows(IllegalStateException.class, owned::wake);
      Thread.currentThread().interrupt();
      owned.close();
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
      owned.close();
    }

    CountDownLatch gate = new CountDownLatch(1), completed = new CountDownLatch(1);
    AtomicReference<OwnedOutboxDispatcher> reference = new AtomicReference<>();
    var self =
        OwnedOutboxDispatcher.start(
            dispatcher(
                () -> {
                  try {
                    gate.await();
                  } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                  }
                  assertThrows(IllegalStateException.class, reference.get()::close);
                  completed.countDown();
                  throw new SQLException("fixture");
                }),
            "pt");
    try {
      reference.set(self);
      gate.countDown();
      assertTrue(completed.await(3, TimeUnit.SECONDS));
    } finally {
      gate.countDown();
      self.close();
    }
  }

  static OutboxDispatcher dispatcher(SqlConnectionProvider open) {
    return new OutboxDispatcher(
        open,
        () -> {
          throw new AssertionError("JMS must not open without DB claim");
        },
        new JdbcOutboxRepository(() -> 0),
        new OutboxJmsSender(),
        Clock.systemUTC());
  }
}
