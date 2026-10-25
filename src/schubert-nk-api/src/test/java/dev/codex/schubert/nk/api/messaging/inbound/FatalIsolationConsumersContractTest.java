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

/** SS321§7/322§11; BUG1494/YKT1254; PT-JMS-ISO001..006. No real broker/DB/VM. */
final class FatalIsolationConsumersContractTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void iso001SyncCheckedIsolationFailureStopsWithoutAck() throws Exception {
    verify(0, true, 4);
  }

  @Test
  void iso002SyncRuntimeIsolationFailureStopsWithoutAck() throws Exception {
    verify(0, false, 4);
  }

  @Test
  void iso003QuestionCheckedIsolationFailureStopsWithoutAck() throws Exception {
    verify(1, true, 1);
  }

  @Test
  void iso004QuestionRuntimeIsolationFailureStopsWithoutAck() throws Exception {
    verify(1, false, 1);
  }

  @Test
  void iso005WebLogCheckedIsolationFailureStopsWithoutAck() throws Exception {
    verify(2, true, 1);
  }

  @Test
  void iso006WebLogRuntimeIsolationFailureStopsWithoutAck() throws Exception {
    verify(2, false, 1);
  }

  private static void verify(int kind, boolean checked, int count) throws Exception {
    var contexts = new ArrayList<FatalIsolationFixture>();
    var fatal = new AtomicInteger();
    var committed = new AtomicInteger();
    var business = new AtomicInteger();
    Supplier<JMSContext> factory =
        () -> {
          var fixture = new FatalIsolationFixture(checked);
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
                        CLOCK),
                    ignored -> committed.incrementAndGet(),
                    fatal::incrementAndGet);
            yield new Owner(runtime::close, runtime::ready);
          }
          case 1 -> {
            var runtime =
                QuestionWorkConsumers.start(
                    factory,
                    new QuestionWorkListener(event -> business.incrementAndGet(), CLOCK),
                    ignored -> committed.incrementAndGet(),
                    fatal::incrementAndGet);
            yield new Owner(runtime::close, runtime::ready);
          }
          case 2 -> {
            var runtime =
                WebLogConsumers.start(
                    factory,
                    new WebLogListener(event -> business.incrementAndGet(), CLOCK),
                    ignored -> committed.incrementAndGet(),
                    fatal::incrementAndGet);
            yield new Owner(runtime::close, runtime::ready);
          }
          default -> throw new AssertionError("finite three groups");
        };
    try (owner) {
      assertEquals(count, contexts.size());
      assertTrue(owner.ready().getAsBoolean());
      contexts.getFirst().deliver();
      assertAll(
          () -> assertFalse(owner.ready().getAsBoolean(), "permanent isolation failure must stop"),
          () -> assertEquals(1, fatal.get()),
          () -> assertEquals(0, committed.get()),
          () -> assertEquals(0, business.get()),
          () ->
              assertEquals(
                  1, contexts.stream().mapToInt(FatalIsolationFixture::metadataReads).sum()),
          () -> assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::rollbacks).sum()),
          () -> assertEquals(0, contexts.stream().mapToInt(FatalIsolationFixture::commits).sum()),
          () ->
              assertEquals(
                  0, contexts.stream().mapToInt(FatalIsolationFixture::unexpectedCalls).sum()));
      for (var fixture : contexts) fixture.deliver();
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::metadataReads).sum());
      assertEquals(1, contexts.stream().mapToInt(FatalIsolationFixture::rollbacks).sum());
      assertEquals(1, fatal.get());
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
