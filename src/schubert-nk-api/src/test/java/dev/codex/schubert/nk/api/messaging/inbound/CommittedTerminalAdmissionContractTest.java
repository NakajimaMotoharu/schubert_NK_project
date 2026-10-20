package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.*;

import jakarta.jms.JMSContext;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** SS322§11; PG-D444/BUG1501/YKT1261; PT-JMS-TERM001..003, finite memory ports only. */
final class CommittedTerminalAdmissionContractTest {
  @Test
  void term001SyncCommitStopsAllFourContextAdmissions() {
    verify(0, 4);
  }

  @Test
  void term002QuestionCommitStopsFurtherAdmissions() {
    verify(1, 1);
  }

  @Test
  void term003WebLogCommitStopsFurtherAdmissions() {
    verify(2, 1);
  }

  private static void verify(int kind, int count) {
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
