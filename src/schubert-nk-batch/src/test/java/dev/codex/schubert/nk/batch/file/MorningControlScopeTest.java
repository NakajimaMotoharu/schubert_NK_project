package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.LinuxFileLock;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/SSC105/PG341; PT-OPS-MCTRL001-007. */
final class MorningControlScopeTest {
  private static final class HeldM implements MorningControlScope.Exclusive {
    final List<String> events;
    final AtomicBoolean held = new AtomicBoolean();
    boolean available = true;

    HeldM(List<String> events) {
      this.events = events;
    }

    @Override
    public <T> Optional<T> execute(LinuxFileLock.Operation<T> operation) throws IOException {
      events.add("M-enter");
      if (!available) return Optional.empty();
      held.set(true);
      try {
        return Optional.of(operation.execute());
      } finally {
        held.set(false);
        events.add("M-close");
      }
    }
  }

  private static final class HeldA implements MorningControlScope.StartupExclusive {
    final List<String> events;
    final AtomicBoolean held = new AtomicBoolean();
    boolean available = true;

    HeldA(List<String> events) {
      this.events = events;
    }

    @Override
    public <T> Optional<T> execute(LinuxFileLock.StartupOperation<T> operation) throws IOException {
      events.add("A-enter");
      if (!available) return Optional.empty();
      held.set(true);
      try {
        return Optional.of(operation.execute(128));
      } finally {
        held.set(false);
        events.add("A-close");
      }
    }
  }

  @Test
  void mctrl001StopsUnderMThenFreshObservesInsideA() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    int result =
        MorningControlScope.execute(
            () -> events.add("root"),
            m,
            () -> {
              assertTrue(m.held.get());
              assertFalse(a.held.get());
              events.add("stop-eight");
            },
            a,
            () -> {
              assertTrue(m.held.get());
              assertTrue(a.held.get());
              events.add("fresh-eight");
            },
            () -> {
              assertTrue(m.held.get());
              assertTrue(a.held.get());
              events.add("trusted-work");
              return 7;
            });
    assertEquals(7, result);
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "fresh-eight",
            "root",
            "trusted-work",
            "root",
            "A-close",
            "root",
            "M-close",
            "root"),
        events);
    assertFalse(m.held.get());
    assertFalse(a.held.get());
  }

  @Test
  void mctrl002BusyMStartsNoStopOrA() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    m.available = false;
    assertEquals(
        "Morning control scope unavailable",
        assertThrows(
                IOException.class,
                () ->
                    MorningControlScope.execute(
                        () -> events.add("root"),
                        m,
                        () -> fail("no stop"),
                        new HeldA(events),
                        () -> fail("no terminals"),
                        () -> fail("no work")))
            .getMessage());
    assertEquals(List.of("root", "M-enter"), events);
  }

  @Test
  void mctrl003StopRefusalNeverAcquiresAAndClosesM() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var failure = new IOException("public stop refused");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.execute(
                    () -> events.add("root"),
                    m,
                    () -> {
                      assertTrue(m.held.get());
                      throw failure;
                    },
                    new HeldA(events),
                    () -> fail("no terminals"),
                    () -> fail("no work"))));
    assertEquals(List.of("root", "M-enter", "root", "M-close"), events);
    assertFalse(m.held.get());
  }

  @Test
  void mctrl004BusyAAfterStopStartsNoWork() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    a.available = false;
    assertEquals(
        "Morning control scope unavailable",
        assertThrows(
                IOException.class,
                () ->
                    MorningControlScope.execute(
                        () -> events.add("root"),
                        m,
                        () -> events.add("stop-eight"),
                        a,
                        () -> fail("no A terminal observation"),
                        () -> fail("no work")))
            .getMessage());
    assertEquals(
        List.of("root", "M-enter", "root", "stop-eight", "root", "A-enter", "M-close"), events);
    assertFalse(m.held.get());
    assertFalse(a.held.get());
  }

  @Test
  void mctrl005PostARecheckFailurePreventsWorkAndClosesBoth() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var failure = new IOException("public fresh terminal failed");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.execute(
                    () -> events.add("root"),
                    m,
                    () -> events.add("stop-eight"),
                    a,
                    () -> {
                      assertTrue(m.held.get() && a.held.get());
                      throw failure;
                    },
                    () -> fail("no change before fresh eight"))));
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "A-close",
            "M-close"),
        events);
  }

  @Test
  void mctrl006WorkFailureAndNullContractsDoNotBecomeSuccess() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var failure = new IllegalStateException("public work failure");
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningControlScope.execute(
                    () -> {},
                    m,
                    () -> {},
                    a,
                    () -> {},
                    () -> {
                      throw failure;
                    })));
    assertFalse(m.held.get());
    assertFalse(a.held.get());
    assertThrows(
        NullPointerException.class,
        () -> MorningControlScope.execute(() -> {}, m, () -> {}, a, () -> {}, () -> null));
    assertThrows(NullPointerException.class, () -> MorningControlScope.execute(null));
    assertThrows(
        NullPointerException.class,
        () -> MorningControlScope.execute(() -> {}, m, () -> {}, a, () -> {}, null));
    assertThrows(
        NullPointerException.class,
        () -> MorningControlScope.execute(null, m, () -> {}, a, () -> {}, () -> true));
  }

  @Test
  void mctrl007UnresolvedStopKeepsMAndNeverAcquiresA() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var workers = Executors.newSingleThreadExecutor()) {
      var result =
          workers.submit(
              () ->
                  MorningControlScope.execute(
                      () -> {},
                      m,
                      () -> {
                        entered.countDown();
                        try {
                          assertTrue(release.await(2, TimeUnit.SECONDS));
                        } catch (InterruptedException interrupted) {
                          Thread.currentThread().interrupt();
                          throw new IOException("test stop interrupted");
                        }
                      },
                      a,
                      () -> {},
                      () -> true));
      try {
        assertTrue(entered.await(2, TimeUnit.SECONDS));
        assertTrue(m.held.get());
        assertFalse(a.held.get());
        assertFalse(result.isDone());
      } finally {
        release.countDown();
      }
      assertTrue(result.get(2, TimeUnit.SECONDS));
      assertFalse(m.held.get());
      assertFalse(a.held.get());
    }
  }
}
