package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.messaging.inbound.FatalIsolationFixture;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS322§11; BUG1494/YKT1254; PT-JMS-ISO007..008. Shared finite fixture, no provider/DB. */
final class ReplyFatalIsolationContractTest {
  @Test
  void iso007ReplyCheckedIsolationFailureStopsWithoutAck() {
    verify(true);
  }

  @Test
  void iso008ReplyRuntimeIsolationFailureStopsWithoutAck() {
    verify(false);
  }

  private static void verify(boolean checked) {
    var fixture = new FatalIsolationFixture(checked);
    var fatal = new AtomicInteger();
    var committed = new AtomicInteger();
    var clock = Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);
    try (var runtime =
        ArtemisReplyConsumers.start(
            fixture::context,
            new ArtemisReplyConsumer(
                new JmsRequestReplyClient(),
                new JmsReplyDecoder(),
                new ArtemisReplyDlqSender(clock)),
            ignored -> committed.incrementAndGet(),
            fatal::incrementAndGet)) {
      assertTrue(runtime.ready());
      fixture.deliver();
      assertAll(
          () -> assertFalse(runtime.ready(), "permanent reply isolation failure must stop"),
          () -> assertTrue(runtime.terminalFailureObserved()),
          () -> assertEquals(1, fatal.get()),
          () -> assertEquals(0, committed.get()),
          () -> assertEquals(1, fixture.metadataReads()),
          () -> assertEquals(1, fixture.rollbacks()),
          () -> assertEquals(0, fixture.commits()),
          () -> assertEquals(0, fixture.unexpectedCalls()));
      fixture.deliver();
      assertEquals(1, fixture.metadataReads());
      assertEquals(1, fixture.rollbacks());
      assertEquals(1, fatal.get());
      assertEquals(0, fixture.closes());
    }
    assertEquals(1, fixture.closes());
  }
}
