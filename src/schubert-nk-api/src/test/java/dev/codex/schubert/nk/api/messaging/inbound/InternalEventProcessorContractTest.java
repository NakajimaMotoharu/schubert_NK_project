package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** MQ-006/MQ-007; UI213/231; SS312/SSC153; NK-MSG-001/003: pure default port only. */
final class InternalEventProcessorContractTest {
  /** PT-JMS-PORT001: one synchronous SAM call with the original event, for either delivery. */
  @Test
  void defaultForwardsSameEventOnce() {
    var original = event();
    for (int count : new int[] {1, 4}) {
      var observed = new ArrayList<WireMessage<FixedPayload>>();
      InternalEventProcessor processor = observed::add;
      processor.process(original, delivery(count));
      assertEquals(1, observed.size());
      assertSame(original, observed.getFirst());
    }
  }

  /** PT-JMS-PORT002: reject null before invoking any business code. */
  @Test
  void nullEventNeverReachesBusiness() {
    var calls = new AtomicInteger();
    InternalEventProcessor processor = ignored -> calls.incrementAndGet();
    var metadata = delivery(1);
    assertThrows(NullPointerException.class, () -> processor.process(null, metadata));
    assertEquals(0, calls.get());
  }

  /** PT-JMS-PORT003: delivery is required even for a legacy SAM implementation. */
  @Test
  void nullDeliveryNeverReachesBusiness() {
    var calls = new AtomicInteger();
    InternalEventProcessor processor = ignored -> calls.incrementAndGet();
    var original = event();
    assertThrows(NullPointerException.class, () -> processor.process(original, null));
    assertEquals(0, calls.get());
  }

  /** PT-JMS-PORT004: a default port neither normalizes nor retries a failing callback. */
  @Test
  void delegateFailuresKeepIdentityAndAreNotRetried() {
    var original = event();
    var metadata = delivery(4);
    for (RuntimeException failure :
        new RuntimeException[] {
          new IllegalStateException("synthetic callback failure"),
          new NullPointerException("synthetic callback null failure")
        }) {
      var calls = new AtomicInteger();
      InternalEventProcessor processor =
          ignored -> {
            calls.incrementAndGet();
            throw failure;
          };
      assertSame(
          failure,
          assertThrows(RuntimeException.class, () -> processor.process(original, metadata)));
      assertEquals(1, calls.get());
    }
    var fatal = new LinkageError("synthetic fatal callback identity");
    var calls = new AtomicInteger();
    InternalEventProcessor processor =
        ignored -> {
          calls.incrementAndGet();
          throw fatal;
        };
    assertSame(
        fatal, assertThrows(LinkageError.class, () -> processor.process(original, metadata)));
    assertEquals(1, calls.get());
  }

  private static DeliveryMetadata delivery(int count) {
    return new DeliveryMetadata(count, "ID:public-synthetic-port", Instant.EPOCH);
  }

  private static WireMessage<FixedPayload> event() {
    // Opaque typed model, not a real wire, credential or dispatched business operation.
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("QWKREQ01"),
            1,
            MessageKind.EVENT,
            InteractionKind.INTERNAL,
            UUID.fromString("00000000-0000-0000-0000-000000000003"),
            UUID.fromString("00000000-0000-0000-0000-000000000001"),
            Instant.EPOCH,
            Optional.empty(),
            256,
            64,
            0,
            0,
            320,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(new byte[64], 0, List.of()));
  }
}
