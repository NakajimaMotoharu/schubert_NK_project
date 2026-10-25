package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.time.Clock;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Owned thread lifecycle at real dispatch/open boundary, not a synthetic covered run method. */
class OwnedOutboxDispatcherTest {
  @Test
  void graph322001NestedFatalStopsOwnedWorkerBeforeAnotherDispatch() throws Exception {
    var previous = System.err;
    var output = new ByteArrayOutputStream();
    try (var capturing = new PrintStream(output, true, StandardCharsets.UTF_8)) {
      System.setErr(capturing);
      for (int kind = 0; kind < 6; kind++) {
        Error fatal = new LinkageError("synthetic graph fatal");
        Throwable graph = graph322(fatal, kind);
        var entered = new CountDownLatch(1);
        var attempts = new java.util.concurrent.atomic.AtomicInteger();
        var thread = new AtomicReference<Thread>();
        var owned =
            OwnedOutboxDispatcher.start(
                dispatcher(
                    () -> {
                      thread.set(Thread.currentThread());
                      attempts.incrementAndGet();
                      entered.countDown();
                      if (graph instanceof SQLException sql) throw sql;
                      throw (RuntimeException) graph;
                    }),
                "pt");
        try {
          assertTrue(entered.await(3, TimeUnit.SECONDS));
          thread.get().join(1000);
          assertFalse(thread.get().isAlive(), "nested fatal must terminate the exact owned worker");
          assertFalse(owned.healthy());
          assertEquals(1, attempts.get(), "fatal graph never authorizes another DB claim");
          assertThrows(IllegalStateException.class, owned::wake);
        } finally {
          owned.close();
        }
      }
      assertEquals(
          ("NK_API_OUTBOX_FATAL" + System.lineSeparator()).repeat(6),
          output.toString(StandardCharsets.UTF_8));
    } finally {
      System.setErr(previous);
    }
    Throwable ordinary = graph322(new SQLException("synthetic ordinary leaf"), 4);
    var retried = new CountDownLatch(2);
    var owned =
        OwnedOutboxDispatcher.start(
            dispatcher(
                () -> {
                  retried.countDown();
                  throw (RuntimeException) ordinary;
                }),
            "pt");
    try {
      assertTrue(retried.await(3, TimeUnit.SECONDS));
      assertTrue(owned.healthy(), "nonfatal cyclic graph keeps existing ordinary retry");
    } finally {
      owned.close();
    }
  }

  /** Independent fixed Throwable graph; never invokes the Production classifier. */
  static Throwable graph322(Throwable leaf, int kind) {
    switch (kind) {
      case 0 -> {
        var sql = new SQLException("synthetic primary");
        sql.addSuppressed(leaf);
        return sql;
      }
      case 1 -> {
        return new IllegalStateException("synthetic cause", leaf);
      }
      case 2 -> {
        var jms = new jakarta.jms.JMSException("synthetic linked");
        jms.setLinkedException(new Exception("synthetic linked leaf", leaf));
        return new IllegalStateException("synthetic outer", jms);
      }
      case 3 -> {
        var sql = new SQLException("synthetic next");
        sql.setNextException(new SQLException("synthetic next leaf", leaf));
        return new IllegalStateException("synthetic outer", sql);
      }
      case 4 -> {
        var first = new IllegalStateException("synthetic first");
        var second = new IllegalStateException("synthetic second", first);
        first.initCause(second);
        first.addSuppressed(second);
        second.addSuppressed(leaf);
        return first;
      }
      default -> {
        var first = new IllegalStateException("synthetic provider cycle");
        var jms = new jakarta.jms.JMSException("synthetic provider");
        jms.setLinkedException(first);
        var sql = new SQLException("synthetic next cycle");
        sql.setNextException(sql);
        sql.addSuppressed(leaf);
        jms.initCause(sql);
        first.initCause(jms);
        return first;
      }
    }
  }

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
    CountDownLatch entered = new CountDownLatch(1);
    CountDownLatch release = new CountDownLatch(1);
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

    CountDownLatch gate = new CountDownLatch(1);
    CountDownLatch completed = new CountDownLatch(1);
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
