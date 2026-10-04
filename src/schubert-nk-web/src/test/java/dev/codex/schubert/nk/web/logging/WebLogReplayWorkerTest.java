package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-IDEM-012-W01: real background DB/JMS retry and bounded worker lifecycle. */
final class WebLogReplayWorkerTest {
  @TempDir Path root;
  private static final WebLogDispatcher.Report EMPTY = new WebLogDispatcher.Report(0, 0, 0, 0);

  @Test
  void rerun008HiddenFatalStopsWithoutFailedCycleAndSelfJoinRejects() throws Exception {
    for (boolean sql : new boolean[] {false, true}) {
      var worker =
          WebLogReplayWorker.start(
              () -> {
                Error fatal = new AssertionError("private fatal");
                if (sql) throw new SQLException("private", fatal);
                throw new IllegalStateException("private", fatal);
              },
              Duration.ofMillis(1),
              Duration.ofSeconds(1));
      try {
        await(worker::terminalFailureObserved);
        assertFalse(worker.running());
        assertEquals(0, worker.snapshot().failedCycles());
        assertEquals(0, worker.snapshot().completedCycles());
      } finally {
        worker.close();
      }
    }
    var owner = new java.util.concurrent.atomic.AtomicReference<WebLogReplayWorker>();
    var proceed = new CountDownLatch(1);
    var worker =
        WebLogReplayWorker.start(
            () -> {
              try {
                assertTrue(proceed.await(5, TimeUnit.SECONDS));
              } catch (InterruptedException unexpected) {
                throw new AssertionError(unexpected);
              }
              owner.get().close();
              return EMPTY;
            },
            Duration.ofMillis(1),
            Duration.ofSeconds(1));
    owner.set(worker);
    proceed.countDown();
    try {
      await(() -> worker.snapshot().failedCycles() == 1);
      assertFalse(worker.terminalFailureObserved());
    } finally {
      worker.close();
    }
  }

  @Test
  void rerun008SecondCloseMustJoinStillAliveWorkerRatherThanSucceed() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var exited = new CountDownLatch(1);
    var worker =
        WebLogReplayWorker.start(
            () -> {
              entered.countDown();
              try {
                while (release.getCount() != 0) {
                  try {
                    release.await();
                  } catch (InterruptedException ignored) {
                    /* synthetic noninterruptible provider */
                  }
                }
                return EMPTY;
              } finally {
                exited.countDown();
              }
            },
            Duration.ofMillis(1),
            Duration.ofMillis(1));
    assertTrue(entered.await(5, TimeUnit.SECONDS));
    try {
      assertThrows(IllegalStateException.class, worker::close);
      assertFalse(worker.running()); // requested is not termination; second close must prove it.
      assertThrows(IllegalStateException.class, worker::close);
      assertEquals(1, exited.getCount());
    } finally {
      release.countDown();
      assertTrue(exited.await(5, TimeUnit.SECONDS));
      worker.close();
    }
  }

  @Test
  void realOutboxRetriesInBackgroundAndSendsOnce() throws Exception {
    WebLogDatabaseFixture db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("db")));
    try (WebLogPayloadCodec codec = new WebLogPayloadCodec("test", new byte[32], null, null);
        ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0")) {
      var broker = WebLogMessageSenderTest.broker(Files.createDirectory(root.resolve("broker")));
      try (JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
          var consumer = observer.createConsumer(new ActiveMQQueue("nk.web.log::nk.web.log.q"))) {
        var repository = new WebLogOutboxRepository(() -> 0);
        var identity =
            new WebLogPayloadIdentity(
                UUID.fromString("00000000-0000-0000-0000-000000000012"),
                UUID.fromString("00000000-0000-0000-0000-000000000015"));
        try (Connection connection = db.transaction()) {
          assertTrue(
              repository.enqueue(
                  connection,
                  identity,
                  codec.encrypt(identity, WebLogPayloadCodecTest.goldenWire()),
                  Instant.now()));
          connection.commit();
        }
        AtomicInteger attempts = new AtomicInteger();
        var sender =
            new WebLogMessageSender(
                codec,
                () -> {
                  if (attempts.incrementAndGet() == 1) {
                    throw new JMSRuntimeException("synthetic-first-send-failure");
                  }
                  return factory.createContext(JMSContext.SESSION_TRANSACTED);
                });
        var dispatcher = new WebLogDispatcher(source(db), repository, sender, Clock.systemUTC());
        assertThrows(
            NullPointerException.class,
            () -> WebLogReplayWorker.start(dispatcher, null, 1, Duration.ofMillis(10)));
        assertThrows(
            IllegalArgumentException.class,
            () -> WebLogReplayWorker.start(dispatcher, "web-worker", 0, Duration.ofMillis(10)));
        assertThrows(
            IllegalArgumentException.class,
            () -> WebLogReplayWorker.start(dispatcher, "web-worker", 101, Duration.ofMillis(10)));
        try (WebLogReplayWorker worker =
            WebLogReplayWorker.start(dispatcher, "web-worker", 1, Duration.ofMillis(10))) {
          assertTrue(worker.running());
          assertFalse(worker.terminalFailureObserved());
          await(() -> "ERROR".equals(status(db)));
          assertEquals(1, attempts.get());
          await(() -> "SENT".equals(status(db)));
          assertNotNull(consumer.receive(5_000));
          assertNull(consumer.receive(100));
          assertEquals(2, attempts.get());
          assertTrue(worker.snapshot().completedCycles() >= 2);
          assertEquals(0, worker.snapshot().failedCycles());
        }
      } finally {
        broker.stop();
      }
    } finally {
      db.stop();
    }
  }

  @Test
  void temporarySqlAndRuntimeFailuresRecoverWithoutLeakingDetails() throws Exception {
    CountDownLatch threeCycles = new CountDownLatch(3);
    AtomicInteger calls = new AtomicInteger();
    try (WebLogReplayWorker worker =
        WebLogReplayWorker.start(
            () -> {
              int call = calls.incrementAndGet();
              threeCycles.countDown();
              if (call == 1) throw new SQLException("private-db-password", "08006");
              if (call == 2) throw new IllegalStateException("private-jms-password");
              return EMPTY;
            },
            Duration.ofMillis(10),
            Duration.ofSeconds(1))) {
      assertTrue(threeCycles.await(5, TimeUnit.SECONDS));
      await(() -> worker.snapshot().completedCycles() >= 1);
      var snapshot = worker.snapshot();
      assertEquals(2, snapshot.failedCycles());
      assertEquals(EMPTY, snapshot.last());
      assertFalse(snapshot.toString().contains("password"));
    }
  }

  @Test
  void fatalVmFailureMakesWorkerNotReadyWithoutExposingCause() throws Exception {
    WebLogReplayWorker worker =
        WebLogReplayWorker.start(
            () -> {
              throw new AssertionError("private-fatal-detail");
            },
            Duration.ofMillis(10),
            Duration.ofSeconds(1));
    try {
      await(worker::terminalFailureObserved);
      await(() -> !worker.running());
      assertEquals(0, worker.snapshot().failedCycles());
      assertFalse(worker.snapshot().toString().contains("fatal-detail"));
    } finally {
      worker.close();
    }
  }

  @Test
  void closeIsIdempotentAndRejectsInvalidInputs() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> WebLogReplayWorker.start(null, "worker", 1, Duration.ofMillis(10)));
    assertThrows(
        NullPointerException.class,
        () -> WebLogReplayWorker.start(() -> EMPTY, null, Duration.ofSeconds(1)));
    assertThrows(
        NullPointerException.class,
        () -> WebLogReplayWorker.start(() -> EMPTY, Duration.ofSeconds(1), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebLogReplayWorker.start(() -> EMPTY, Duration.ZERO, Duration.ofSeconds(1)));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebLogReplayWorker.start(() -> EMPTY, Duration.ofMinutes(2), Duration.ofSeconds(1)));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebLogReplayWorker.start(() -> EMPTY, Duration.ofMillis(1), Duration.ZERO));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebLogReplayWorker.start(() -> EMPTY, Duration.ofMillis(1), Duration.ofSeconds(6)));
    assertThrows(
        IllegalArgumentException.class, () -> new WebLogReplayWorker.Snapshot(-1, 0, EMPTY));
    assertThrows(
        IllegalArgumentException.class, () -> new WebLogReplayWorker.Snapshot(0, -1, EMPTY));
    assertThrows(NullPointerException.class, () -> new WebLogReplayWorker.Snapshot(0, 0, null));

    CountDownLatch first = new CountDownLatch(1);
    AtomicInteger calls = new AtomicInteger();
    WebLogReplayWorker worker =
        WebLogReplayWorker.start(
            () -> {
              calls.incrementAndGet();
              first.countDown();
              return EMPTY;
            },
            Duration.ofMillis(10),
            Duration.ofSeconds(1));
    assertTrue(first.await(5, TimeUnit.SECONDS));
    worker.close();
    assertFalse(worker.running());
    int before = calls.get();
    Thread.sleep(30);
    assertEquals(before, calls.get());
    worker.close();
  }

  @Test
  void boundedStopReportsUnresponsiveWorkerThenReleases() throws Exception {
    CountDownLatch entered = new CountDownLatch(1);
    CountDownLatch release = new CountDownLatch(1);
    CountDownLatch exited = new CountDownLatch(1);
    WebLogReplayWorker worker =
        WebLogReplayWorker.start(
            () -> {
              entered.countDown();
              try {
                while (release.getCount() != 0) {
                  try {
                    release.await();
                  } catch (InterruptedException ignored) {
                    // Synthetic noninterruptible provider: release in test cleanup.
                  }
                }
                return EMPTY;
              } finally {
                exited.countDown();
              }
            },
            Duration.ofMillis(10),
            Duration.ofMillis(1));
    assertTrue(entered.await(5, TimeUnit.SECONDS));
    try {
      IllegalStateException failure = assertThrows(IllegalStateException.class, worker::close);
      assertEquals("web log worker did not stop within its deadline", failure.getMessage());
      assertFalse(worker.running());
    } finally {
      release.countDown();
      assertTrue(exited.await(5, TimeUnit.SECONDS));
    }
    worker.close();
  }

  @Test
  void interruptedStopRestoresCallerFlag() throws Exception {
    CountDownLatch entered = new CountDownLatch(1);
    CountDownLatch release = new CountDownLatch(1);
    WebLogReplayWorker worker =
        WebLogReplayWorker.start(
            () -> {
              entered.countDown();
              try {
                release.await();
              } catch (InterruptedException ignored) {
                // The caller's interrupted join is the subject; worker is separately released.
              }
              return EMPTY;
            },
            Duration.ofMillis(10),
            Duration.ofSeconds(1));
    assertTrue(entered.await(5, TimeUnit.SECONDS));
    try {
      Thread.currentThread().interrupt();
      IllegalStateException failure = assertThrows(IllegalStateException.class, worker::close);
      assertEquals("web log worker stop was interrupted", failure.getMessage());
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
      release.countDown();
    }
    worker.close();
  }

  private static DataSource source(WebLogDatabaseFixture db) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (instance, method, args) -> {
              if (method.getName().equals("getConnection")) return db.web();
              throw new AssertionError("unexpected DataSource method");
            });
  }

  private static String status(WebLogDatabaseFixture db) throws SQLException {
    try (Connection connection = db.web();
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery("select status from schubert_web_session.web_log_outbox")) {
      assertTrue(rows.next());
      return rows.getString(1);
    }
  }

  private static void await(CheckedBoolean check) throws Exception {
    for (int attempt = 0; attempt < 500; attempt++) {
      if (check.get()) return;
      Thread.sleep(10);
    }
    assertTrue(check.get(), "background dispatch did not reach its expected state");
  }

  @FunctionalInterface
  private interface CheckedBoolean {
    boolean get() throws Exception;
  }
}
