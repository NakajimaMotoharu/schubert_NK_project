package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSContext;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** SS322§11; PG-D444/445/BUG1501/YKT1261; TERM001..003/005/006, finite memory ports only. */
final class CommittedTerminalAdmissionContractTest {
  @Test
  void term001SyncCommitStopsAllFourContextAdmissions() throws Exception {
    verify(0, 4);
  }

  @Test
  void term002QuestionCommitStopsFurtherAdmissions() throws Exception {
    verify(1, 1);
  }

  @Test
  void term003WebLogCommitStopsFurtherAdmissions() throws Exception {
    verify(2, 1);
  }

  @Test
  void term005SyncTwoInFlightCommittedCallbacksSignalOnce() throws Exception {
    verifyTwoInFlight(false);
  }

  @Test
  void term006SyncTwoInFlightIsolationFailuresSignalOnce() throws Exception {
    verifyTwoInFlight(true);
  }

  private static void verifyTwoInFlight(boolean isolationFailure) throws Exception {
    var contexts = new ArrayList<FatalIsolationFixture>();
    var protocol = new AtomicInteger();
    var fatal = new AtomicInteger();
    var business = new AtomicInteger();
    var entered = new java.util.concurrent.CyclicBarrier(2);
    Runnable rendezvous =
        () -> {
          try {
            entered.await(5, java.util.concurrent.TimeUnit.SECONDS);
          } catch (InterruptedException failure) {
            Thread.currentThread().interrupt();
            throw new AssertionError("independent context rendezvous interrupted", failure);
          } catch (java.util.concurrent.BrokenBarrierException
              | java.util.concurrent.TimeoutException failure) {
            throw new AssertionError("two independent contexts must already be in flight", failure);
          }
        };
    Supplier<JMSContext> factory =
        () -> {
          var fixture = new FatalIsolationFixture(false, isolationFailure);
          if (isolationFailure) fixture.onFirstRollback(rendezvous);
          else fixture.onFirstCommit(rendezvous);
          contexts.add(fixture);
          return fixture.context();
        };
    try (var runtime =
        SyncRequestConsumers.start(
            factory,
            new SyncRequestListener(
                request -> {
                  business.incrementAndGet();
                  return new byte[0];
                },
                Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC)),
            ignored -> protocol.incrementAndGet(),
            fatal::incrementAndGet)) {
      assertEquals(4, contexts.size());
      assertTrue(runtime.ready());
      // One worker per context, never concurrent callbacks on the same JMS session.
      try (var executor = java.util.concurrent.Executors.newFixedThreadPool(2)) {
        var first = executor.submit(contexts.get(0)::deliver);
        var second = executor.submit(contexts.get(1)::deliver);
        first.get(10, java.util.concurrent.TimeUnit.SECONDS);
        second.get(10, java.util.concurrent.TimeUnit.SECONDS);
      }
      assertFalse(runtime.ready());
      assertTrue(runtime.terminalFailureObserved());
      assertEquals(2, contexts.stream().mapToInt(FatalIsolationFixture::metadataReads).sum());
      assertEquals(
          isolationFailure ? 0 : 2, contexts.stream().mapToInt(FatalIsolationFixture::sends).sum());
      assertEquals(
          isolationFailure ? 0 : 2,
          contexts.stream().mapToInt(FatalIsolationFixture::commits).sum());
      assertEquals(
          isolationFailure ? 2 : 0,
          contexts.stream().mapToInt(FatalIsolationFixture::rollbacks).sum());
      assertEquals(isolationFailure ? 0 : 1, protocol.get());
      assertEquals(isolationFailure ? 1 : 0, fatal.get());
      assertEquals(0, business.get());
      for (var context : contexts) context.deliver();
      assertEquals(2, contexts.stream().mapToInt(FatalIsolationFixture::metadataReads).sum());
      assertEquals(
          isolationFailure ? 0 : 2,
          contexts.stream().mapToInt(FatalIsolationFixture::commits).sum());
      assertEquals(
          isolationFailure ? 2 : 0,
          contexts.stream().mapToInt(FatalIsolationFixture::rollbacks).sum());
      assertEquals(isolationFailure ? 0 : 1, protocol.get());
      assertEquals(isolationFailure ? 1 : 0, fatal.get());
      assertEquals(0, contexts.stream().mapToInt(FatalIsolationFixture::unexpectedCalls).sum());
      assertEquals(0, contexts.stream().mapToInt(FatalIsolationFixture::closes).sum());
    }
    assertEquals(4, contexts.stream().mapToInt(FatalIsolationFixture::closes).sum());
  }

  private static void verify(int kind, int count) throws Exception {
    var contexts = new ArrayList<FatalIsolationFixture>();
    var protocol = new AtomicInteger();
    var fatal = new AtomicInteger();
    var business = new AtomicInteger();
    var clock = Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);
    Supplier<JMSContext> factory =
        () -> {
          var fixture = new FatalIsolationFixture(false, false);
          contexts.add(fixture);
          return fixture.context();
        };
    Owner owner =
        switch (kind) {
          case 0 -> {
            var runtime =
                SyncRequestConsumers.start(
                    factory,
                    new SyncRequestListener(
                        request -> {
                          business.incrementAndGet();
                          return new byte[0];
                        },
                        clock),
                    ignored -> protocol.incrementAndGet(),
                    fatal::incrementAndGet);
            yield new Owner(runtime::close, runtime::ready);
          }
          case 1 -> {
            var runtime =
                QuestionWorkConsumers.start(
                    factory,
                    new QuestionWorkListener(event -> business.incrementAndGet(), clock),
                    ignored -> protocol.incrementAndGet(),
                    fatal::incrementAndGet);
            yield new Owner(runtime::close, runtime::ready);
          }
          case 2 -> {
            var runtime =
                WebLogConsumers.start(
                    factory,
                    new WebLogListener(event -> business.incrementAndGet(), clock),
                    ignored -> protocol.incrementAndGet(),
                    fatal::incrementAndGet);
            yield new Owner(runtime::close, runtime::ready);
          }
          default -> throw new AssertionError("finite three groups");
        };
    try (owner) {
      assertEquals(count, contexts.size());
      assertTrue(owner.ready().getAsBoolean());
      contexts.getFirst().deliver();
      assertFalse(owner.ready().getAsBoolean());
      assertEquals(1, protocol.get());
      assertEquals(0, fatal.get());
      assertEquals(0, business.get());
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::metadataReads).sum());
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::sends).sum());
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::commits).sum());
      assertEquals(0, contexts.stream().mapToInt(FatalIsolationFixture::rollbacks).sum());
      for (var context : contexts) context.deliver();
      assertAll(
          () ->
              assertEquals(
                  1, contexts.stream().mapToInt(FatalIsolationFixture::metadataReads).sum()),
          () -> assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::sends).sum()),
          () -> assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::commits).sum()),
          () -> assertEquals(1, protocol.get()),
          () -> assertEquals(0, fatal.get()),
          () -> assertEquals(0, business.get()),
          () -> assertEquals(0, contexts.stream().mapToInt(FatalIsolationFixture::rollbacks).sum()),
          () ->
              assertEquals(
                  0, contexts.stream().mapToInt(FatalIsolationFixture::unexpectedCalls).sum()));
      // After the terminal publication, independent Sync contexts must observe the same halt.
      // Each context has at most one worker, preserving the JMS single-thread context contract.
      try (var executor = java.util.concurrent.Executors.newFixedThreadPool(count)) {
        var work = contexts.stream().map(c -> executor.submit(c::deliver)).toList();
        for (var result : work) result.get(5, java.util.concurrent.TimeUnit.SECONDS);
      }
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::metadataReads).sum());
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::commits).sum());
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::sends).sum());
      assertEquals(1, protocol.get());
      assertEquals(0, fatal.get());
      assertEquals(0, business.get());
      assertEquals(0, contexts.stream().mapToInt(FatalIsolationFixture::unexpectedCalls).sum());
      assertEquals(0, contexts.stream().mapToInt(FatalIsolationFixture::closes).sum());
    }
    assertEquals(count, contexts.stream().mapToInt(FatalIsolationFixture::closes).sum());
  }

  private record Owner(Runnable closeAction, BooleanSupplier ready) implements AutoCloseable {
    @Override
    public void close() {
      closeAction.run();
    }
  }
}
