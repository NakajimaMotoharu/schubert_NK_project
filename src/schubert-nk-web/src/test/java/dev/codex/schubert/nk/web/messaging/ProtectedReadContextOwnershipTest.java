package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuRequestData;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-JMS-CONTEXT001..006; SSC418/BUG3012,3013/YKT2541,2542; UI232/SS311,323,352. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class ProtectedReadContextOwnershipTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
  private static final UUID ID = new UUID(0, 1);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));
  private static final TypedPayloadValues INPUT =
      new TypedPayloadValues(new LayoutId("ANMREQ01"), new AnimationMenuRequestData(), List.of());

  @Test
  void context001EveryAcquiredBufferIsWipedOnDirectError() {
    for (int stage = 1; stage <= 3; stage++) {
      var fatal = new AssertionError("PUBLIC synthetic failure");
      var operations = new Operations(stage, fatal, -1);
      var fixture = new Fixture(operations);
      assertSame(fatal, assertThrows(AssertionError.class, fixture::exchange));
      assertEquals(stage, operations.calls);
      assertEquals(Math.min(stage - 1, 2), operations.owned.size());
      fixture.assertCleanup();
    }
  }

  @Test
  void context002WrappedErrorRetainsIdentityAfterBothBuffersAreWiped() {
    var fatal = new AssertionError("PUBLIC nested failure");
    var failure = new IllegalStateException("PUBLIC carrier", fatal);
    var operations = new Operations(3, failure, -1);
    var fixture = new Fixture(operations);
    assertSame(fatal, assertThrows(AssertionError.class, fixture::exchange));
    assertSame(fatal, failure.getCause());
    assertEquals(3, operations.calls);
    assertEquals(2, operations.owned.size());
    fixture.assertCleanup();
  }

  @Test
  void context003NonfatalComparisonKeepsFixedRedactedCatalog() {
    var operations = new Operations(3, new IllegalStateException("PUBLIC detail"), -1);
    var fixture = new Fixture(operations);
    assertRejected(fixture);
    assertEquals(3, operations.calls);
    assertEquals(2, operations.owned.size());
  }

  @Test
  void context004NullOperationsIsAnExplicitConstructionPrecondition() {
    var coordinator = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
    assertThrows(
        NullPointerException.class,
        () ->
            new ProtectedReadWireClient(
                Set.of("ANMREQ01"),
                coordinator,
                (id, bytes) -> {
                  throw new AssertionError("construction must not send");
                },
                CLOCK,
                () -> ID,
                Duration.ofSeconds(2),
                null));
    assertEquals(0, coordinator.pendingCount());
    assertEquals(0, coordinator.lateReplyCount());
  }

  @Test
  void context005NullReturnRejectsWithoutDereferenceOrComparison() {
    for (int stage = 1; stage <= 2; stage++) {
      var operations = new Operations(stage, null, -1);
      var fixture = new Fixture(operations);
      assertRejected(fixture);
      assertEquals(stage, operations.calls);
      assertEquals(stage - 1, operations.owned.size());
    }
  }

  @Test
  void context006InvalidWidthsAreWipedBeforeOwnershipTransfer() {
    for (int stage = 1; stage <= 2; stage++) {
      for (int width : new int[] {0, 63, 65}) {
        var operations = new Operations(stage, null, width);
        var fixture = new Fixture(operations);
        assertRejected(fixture);
        assertEquals(stage, operations.calls);
        assertEquals(stage, operations.owned.size());
        assertEquals(width, operations.owned.getLast().length);
      }
    }
  }

  private static void assertRejected(Fixture fixture) {
    var failure = assertThrows(ProtectedReadWireException.class, fixture::exchange);
    assertEquals(ProtectedReadWireException.Reason.INVALID_RESPONSE, failure.reason());
    assertEquals("protected read exchange rejected", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    fixture.assertCleanup();
  }

  private static final class Operations implements ProtectedReadWireClient.ContextOperations {
    private final int faultStage;
    private final @Nullable Throwable failure;
    private final int invalidWidth;
    private final List<byte[]> owned = new ArrayList<>();
    private int calls;

    Operations(int faultStage, @Nullable Throwable failure, int invalidWidth) {
      this.faultStage = faultStage;
      this.failure = failure;
      this.invalidWidth = invalidWidth;
    }

    @Override
    public byte @Nullable [] encode(AuthenticationContext context) {
      assertEquals("a".repeat(64), context.wireValue());
      calls++;
      if (calls == faultStage) {
        if (failure instanceof Error fatal) throw fatal;
        if (failure instanceof RuntimeException rejected) throw rejected;
        if (invalidWidth < 0) return null;
      }
      int width = calls == faultStage ? invalidWidth : 64;
      byte[] result = new byte[width];
      Arrays.fill(result, (byte) 'a');
      owned.add(result);
      return result;
    }

    @Override
    public boolean same(byte[] first, byte[] second) {
      calls++;
      assertArrayEquals("a".repeat(64).getBytes(StandardCharsets.US_ASCII), first);
      assertArrayEquals("a".repeat(64).getBytes(StandardCharsets.US_ASCII), second);
      if (failure instanceof Error fatal) throw fatal;
      if (failure instanceof RuntimeException rejected) throw rejected;
      throw new AssertionError("fault expected before successful comparison");
    }
  }

  private static final class Fixture {
    private final Operations operations;
    private final JmsRequestReplyClient coordinator =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
    private final List<byte[]> sent = new ArrayList<>();
    private final ProtectedReadWireClient wire;

    Fixture(Operations operations) {
      this.operations = operations;
      wire =
          new ProtectedReadWireClient(
              Set.of("ANMREQ01"),
              coordinator,
              (id, bytes) -> {
                assertEquals(ID, id);
                sent.add(bytes);
                coordinator.onReply(id, response());
              },
              CLOCK,
              () -> ID,
              Duration.ofSeconds(2),
              operations);
    }

    void exchange() {
      wire.exchange(INPUT, CONTEXT);
    }

    void assertCleanup() {
      assertEquals(1, sent.size());
      assertArrayEquals(new byte[256], sent.getFirst());
      for (byte[] bytes : operations.owned) assertArrayEquals(new byte[bytes.length], bytes);
      assertEquals(0, coordinator.pendingCount());
      assertEquals(0, coordinator.lateReplyCount());
    }
  }

  /** Independent UI232 byte offsets; no production codec constructs the response oracle. */
  private static byte[] response() {
    byte[] bytes = new byte[272];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, "SCHBNK01");
    put(bytes, 8, "001");
    put(bytes, 11, "ANMRSP01");
    put(bytes, 19, "001");
    put(bytes, 22, "S");
    put(bytes, 23, "S");
    put(bytes, 24, "00000000-0000-0001-0000-000000000001");
    put(bytes, 60, "00000000-0000-0000-0000-000000000001");
    put(bytes, 96, "20260920090000000");
    put(bytes, 113, "a".repeat(64));
    put(bytes, 177, "0256");
    put(bytes, 181, "000016");
    put(bytes, 187, "000000");
    put(bytes, 193, "000000");
    put(bytes, 199, "000000272");
    put(bytes, 208, "0000");
    put(bytes, 256, "0000000000");
    return bytes;
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }
}
