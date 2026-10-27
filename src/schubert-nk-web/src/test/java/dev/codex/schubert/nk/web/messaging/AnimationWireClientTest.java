package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException.Reason;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** PG-D-206/PT-WEB238..245; FUN media/AUT/MQ/TST; UI232/235; SS311/312/321/322/323/352. */
class AnimationWireClientTest {
  private static final String ANIMATION_MENU_KIND = "ANM";
  private static final String MAIN_ANIMATION_KIND = "MAIN";
  private static final String OVA_ANIMATION_KIND = "OVA";
  private static final String SUCCESS_CODE = "0000";
  private static final String SYNTHETIC_FAILURE = "synthetic";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
  private static final Duration WAIT = Duration.ofSeconds(2);
  private static final UUID ID = new UUID(0, 1);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));

  @Test
  void web238AnimationRequests() {
    for (String type : List.of(ANIMATION_MENU_KIND, MAIN_ANIMATION_KIND, OVA_ANIMATION_KIND)) {
      var f = new Fixture();
      f.reply =
          (id, bytes) -> {
            var expected =
                header(
                    type.equals(ANIMATION_MENU_KIND) ? "ANMREQ01" : "ANLREQ01",
                    type.equals(ANIMATION_MENU_KIND) ? 0 : 16,
                    0,
                    0,
                    "",
                    id,
                    CONTEXT.wireValue());
            if (!type.equals(ANIMATION_MENU_KIND)) put(expected, 256, 16, type);
            assertArrayEquals(expected, bytes);
            return response(type, 0, SUCCESS_CODE, id, CONTEXT.wireValue());
          };
      assertEquals(ResultCode.SUCCESS, f.client.exchange(input(type), CONTEXT).resultCode());
      assertEquals(1, f.sent.size());
      f.erased();
    }
  }

  @Test
  void web239SuccessProfiles() {
    for (String type : List.of(ANIMATION_MENU_KIND, MAIN_ANIMATION_KIND, OVA_ANIMATION_KIND)) {
      for (int n :
          type.equals(ANIMATION_MENU_KIND) ? new int[] {0, 15, 999} : new int[] {0, 1, 50}) {
        for (String code : List.of(SUCCESS_CODE, "0200")) {
          var f = new Fixture();
          f.reply = (id, bytes) -> response(type, n, code, id, CONTEXT.wireValue());
          var result = f.client.exchange(input(type), CONTEXT);
          assertEquals(code, result.resultCode().wireValue());
          var payload = result.payload().orElseThrow();
          if (type.equals(ANIMATION_MENU_KIND)) {
            var data = (AnimationMenuResponseData) payload.data();
            assertEquals(n, data.mainSubtrackCount());
            assertEquals(0, data.ovaCount());
            assertFalse(data.openingPresent());
            assertEquals(n, data.totalFileCount());
            assertTrue(payload.records().isEmpty());
          } else {
            assertEquals(n, ((AnimationListResponseData) payload.data()).totalCount());
            assertEquals(n, payload.records().size());
            for (int i = 0; i < n; i++) {
              var r = (AnimationRecord) payload.records().get(i);
              assertEquals("video" + i, r.videoId());
              assertEquals("Title" + i, r.title());
              assertEquals(type, r.category().name());
              assertEquals("videos/" + i + ".mp4", r.displayPath().wireValue());
              assertEquals(1024 + i, r.fileByteLength());
              assertEquals(i + 1, r.displayOrder());
              assertEquals(Optional.empty(), r.parentMainId());
            }
          }
          f.erased();
        }
      }
    }
  }

  @Test
  void web240ErrorProfiles() {
    for (String type : List.of(ANIMATION_MENU_KIND, MAIN_ANIMATION_KIND, OVA_ANIMATION_KIND)) {
      for (String code :
          List.of("0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "9000", "9001")) {
        var f = new Fixture();
        f.reply = (id, bytes) -> response(type, 0, code, id, CONTEXT.wireValue());
        var result = f.client.exchange(input(type), CONTEXT);
        assertEquals(code, result.resultCode().wireValue());
        assertTrue(result.payload().isEmpty());
        f.erased();
        var invalid = new Fixture();
        invalid.reply =
            (id, b) -> {
              var body = response(type, 0, code, id, CONTEXT.wireValue());
              body[256] = '1';
              return body;
            };
        rejected(Reason.INVALID_RESPONSE, () -> invalid.client.exchange(input(type), CONTEXT));
        invalid.erased();
      }
    }
  }

  @Test
  void web241MalformedReplies() {
    var changes =
        List.<Consumer<byte[]>>of(
            b -> put(b, 11, 8, "ANMRSP01"),
            b -> put(b, 60, 36, new UUID(0, 99).toString()),
            b -> put(b, 113, 64, "b".repeat(64)),
            b -> put(b, 199, 9, "000000256"),
            b -> put(b, 208, 4, "9999"),
            b -> b[212] = 'x',
            b -> b[328] = (byte) 0xff,
            b -> put(b, 584, 16, "UNKNOWN"));
    for (var change : changes) {
      var f = new Fixture();
      f.reply =
          (id, bytes) -> {
            var body = response(MAIN_ANIMATION_KIND, 1, SUCCESS_CODE, id, CONTEXT.wireValue());
            change.accept(body);
            return body;
          };
      rejected(
          Reason.INVALID_RESPONSE, () -> f.client.exchange(input(MAIN_ANIMATION_KIND), CONTEXT));
      f.erased();
    }
    for (int length : new int[] {0, 255, 263, 46665}) {
      var f = new Fixture();
      f.reply = (id, bytes) -> new byte[length];
      rejected(
          Reason.INVALID_RESPONSE, () -> f.client.exchange(input(MAIN_ANIMATION_KIND), CONTEXT));
      f.erased();
    }
  }

  @Test
  void web242CapabilitiesAndNull() {
    var f = new Fixture();
    var game =
        new TypedPayloadValues(new LayoutId("GAMREQ01"), new GameListRequestData(), List.of());
    rejected(Reason.INVALID_INPUT, () -> f.client.exchange(game, CONTEXT));
    rejected(
        Reason.INVALID_INPUT,
        () ->
            f.client.exchange(
                new TypedPayloadValues(
                    new LayoutId("VIDREQ01"), new VideoDescriptorRequestData("video0"), List.of()),
                CONTEXT));
    var record =
        new AnimationRecord(
            "id", "title", AnimationCategory.MAIN, DisplayPath.of("a.mp4"), 1, Optional.empty(), 1);
    rejected(
        Reason.INVALID_INPUT,
        () ->
            f.client.exchange(
                new TypedPayloadValues(
                    new LayoutId("ANLREQ01"),
                    new AnimationListRequestData(AnimationListCategory.MAIN),
                    List.of(record)),
                CONTEXT));
    var scenario = new ScenarioWireClient(f.wire, f.sender, CLOCK, () -> ID, WAIT);
    assertEquals(
        ScenarioWireException.Reason.INVALID_INPUT,
        assertThrows(
                ScenarioWireException.class,
                () -> scenario.exchange(input(ANIMATION_MENU_KIND), CONTEXT))
            .reason());
    assertTrue(f.sent.isEmpty());
    assertThrows(NullPointerException.class, () -> f.client.exchange(null, CONTEXT));
    assertThrows(
        NullPointerException.class, () -> f.client.exchange(input(ANIMATION_MENU_KIND), null));
    assertThrows(
        NullPointerException.class,
        () -> new AnimationWireClient(null, f.sender, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new AnimationWireClient(f.wire, null, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new AnimationWireClient(f.wire, f.sender, null, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new AnimationWireClient(f.wire, f.sender, CLOCK, null, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new AnimationWireClient(f.wire, f.sender, CLOCK, () -> ID, null));
    assertThrows(NullPointerException.class, () -> new ProtectedReadWireException(null));
    assertThrows(
        NullPointerException.class,
        () -> new ProtectedReadWireClient(null, f.wire, f.sender, CLOCK, () -> ID, WAIT));
    for (Duration timeout : List.of(Duration.ZERO, Duration.ofNanos(-1), Duration.ofSeconds(3)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new AnimationWireClient(f.wire, f.sender, CLOCK, () -> ID, timeout));
    f.erased();
  }

  @Test
  void web243TransportFailures() {
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 2);
    for (JmsRequestSender sender :
        List.<JmsRequestSender>of(
            (id, b) -> {
              throw new JMSException(SYNTHETIC_FAILURE);
            },
            (id, b) -> {
              throw new JMSRuntimeException(SYNTHETIC_FAILURE);
            },
            (id, b) -> {
              throw new IllegalStateException(SYNTHETIC_FAILURE);
            },
            (id, b) -> {})) {
      var client = new AnimationWireClient(wire, sender, CLOCK, () -> ID, Duration.ofMillis(1));
      rejected(Reason.UNAVAILABLE, () -> client.exchange(input(ANIMATION_MENU_KIND), CONTEXT));
      assertEquals(0, wire.pendingCount());
    }
    var failure = new AssertionError(SYNTHETIC_FAILURE);
    var client =
        new AnimationWireClient(
            wire,
            (id, b) -> {
              throw failure;
            },
            CLOCK,
            () -> ID,
            WAIT);
    assertSame(
        failure,
        assertThrows(
            AssertionError.class, () -> client.exchange(input(ANIMATION_MENU_KIND), CONTEXT)));
    assertEquals(0, wire.pendingCount());
    var sends = new AtomicLong();
    var badClock =
        new AnimationWireClient(
            wire,
            (id, b) -> sends.incrementAndGet(),
            Clock.fixed(Instant.MAX, ZoneOffset.UTC),
            () -> ID,
            WAIT);
    rejected(Reason.UNAVAILABLE, () -> badClock.exchange(input(ANIMATION_MENU_KIND), CONTEXT));
    var badId =
        new AnimationWireClient(
            wire,
            (id, b) -> sends.incrementAndGet(),
            CLOCK,
            () -> {
              throw new IllegalStateException(SYNTHETIC_FAILURE);
            },
            WAIT);
    rejected(Reason.UNAVAILABLE, () -> badId.exchange(input(ANIMATION_MENU_KIND), CONTEXT));
    assertEquals(0, sends.get());
    assertThrows(
        NullPointerException.class,
        () ->
            new AnimationWireClient(wire, (id, b) -> {}, CLOCK, () -> null, WAIT)
                .exchange(input(ANIMATION_MENU_KIND), CONTEXT));
  }

  @Test
  void web244ConcurrentRequests() throws Exception {
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    var ids = new AtomicLong();
    var observed = ConcurrentHashMap.<UUID>newKeySet();
    var client =
        new AnimationWireClient(
            wire,
            (id, b) -> {
              assertTrue(observed.add(id));
              var type =
                  ascii(b, 11, 8).equals("ANMREQ01")
                      ? ANIMATION_MENU_KIND
                      : ascii(b, 256, 16).strip();
              assertTrue(wire.onReply(id, response(type, 0, SUCCESS_CODE, id, ascii(b, 113, 64))));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            WAIT);
    try (var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int index = i;
        futures.add(
            pool.submit(
                () -> {
                  var context =
                      AuthenticationContext.of(String.format(Locale.ROOT, "%064x", index + 1));
                  var result =
                      client.exchange(
                          input(index % 2 == 0 ? ANIMATION_MENU_KIND : OVA_ANIMATION_KIND),
                          context);
                  assertEquals(ResultCode.SUCCESS, result.resultCode());
                  assertEquals(
                      index % 2 == 0 ? "ANMRSP01" : "ANLRSP01",
                      result.payload().orElseThrow().layoutId().value());
                }));
      }
      for (var future : futures) future.get();
    }
    assertEquals(64, observed.size());
    assertEquals(0, wire.pendingCount());
  }

  @Test
  void web245OwnershipAndDiagnostics() {
    var f = new Fixture();
    var callerResponse = response(MAIN_ANIMATION_KIND, 1, SUCCESS_CODE, ID, CONTEXT.wireValue());
    put(callerResponse, 584, 16, "SUBTRACK");
    put(callerResponse, 1124, 64, "parent0");
    var original = callerResponse.clone();
    f.reply = (id, bytes) -> callerResponse;
    var result = f.client.exchange(input(MAIN_ANIMATION_KIND), CONTEXT);
    assertEquals("ProtectedReadResponse[REDACTED]", result.toString());
    var payload = result.payload().orElseThrow();
    assertThrows(UnsupportedOperationException.class, () -> payload.records().clear());
    assertFalse(payload.toString().contains(CONTEXT.wireValue()));
    assertEquals("video0", ((AnimationRecord) payload.records().getFirst()).videoId());
    assertEquals(
        AnimationCategory.SUBTRACK, ((AnimationRecord) payload.records().getFirst()).category());
    assertEquals(
        Optional.of("parent0"), ((AnimationRecord) payload.records().getFirst()).parentMainId());
    assertArrayEquals(original, callerResponse);
    Arrays.fill(callerResponse, (byte) 0);
    assertEquals("video0", ((AnimationRecord) payload.records().getFirst()).videoId());
    f.erased();
    for (Reason reason : Reason.values())
      rejected(
          reason,
          () -> {
            throw new ProtectedReadWireException(reason);
          });
  }

  private static TypedPayloadValues input(String type) {
    return type.equals(ANIMATION_MENU_KIND)
        ? new TypedPayloadValues(
            new LayoutId("ANMREQ01"), new AnimationMenuRequestData(), List.of())
        : new TypedPayloadValues(
            new LayoutId("ANLREQ01"),
            new AnimationListRequestData(AnimationListCategory.valueOf(type)),
            List.of());
  }

  private static byte[] response(String type, int n, String code, UUID id, String context) {
    boolean menu = type.equals(ANIMATION_MENU_KIND);
    boolean success = code.equals(SUCCESS_CODE) || code.equals("0200");
    var body =
        header(
            menu ? "ANMRSP01" : "ANLRSP01",
            menu ? 16 : 8,
            menu ? 0 : 928,
            menu ? 0 : n,
            code,
            id,
            context);
    if (menu) {
      number(body, 256, 3, success ? n : 0);
      number(body, 259, 3, 0);
      put(body, 262, 1, success ? "0" : "");
      number(body, 263, 3, success ? n : 0);
    } else {
      number(body, 256, 6, success ? n : 0);
      for (int i = 0; i < n; i++) {
        int start = 264 + i * 928;
        put(body, start, 64, "video" + i);
        put(body, start + 64, 256, "Title" + i);
        put(body, start + 320, 16, type);
        put(body, start + 336, 512, "videos/" + i + ".mp4");
        number(body, start + 848, 12, 1024 + i);
        number(body, start + 924, 4, i + 1);
      }
    }
    return body;
  }

  private static byte[] header(
      String layout, int data, int record, int count, String code, UUID id, String context) {
    var b = new byte[256 + data + record * count];
    Arrays.fill(b, (byte) ' ');
    put(b, 0, 8, "SCHBNK01");
    put(b, 8, 3, "001");
    put(b, 11, 8, layout);
    put(b, 19, 3, "001");
    put(b, 22, 1, code.isEmpty() ? "Q" : "S");
    put(b, 23, 1, "S");
    put(
        b,
        24,
        36,
        code.isEmpty() ? id.toString() : new UUID(1, id.getLeastSignificantBits()).toString());
    put(b, 60, 36, id.toString());
    put(b, 96, 17, "20260920090000000");
    put(b, 113, 64, context);
    number(b, 177, 4, 256);
    number(b, 181, 6, data);
    number(b, 187, 6, record);
    number(b, 193, 6, count);
    number(b, 199, 9, b.length);
    put(b, 208, 4, code);
    return b;
  }

  private static void put(byte[] b, int offset, int length, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    assertTrue(text.length <= length);
    Arrays.fill(b, offset, offset + length, (byte) ' ');
    System.arraycopy(text, 0, b, offset, text.length);
  }

  private static void number(byte[] b, int offset, int length, long n) {
    put(b, offset, length, String.format(Locale.ROOT, "%0" + length + "d", n));
  }

  private static String ascii(byte[] b, int start, int length) {
    return new String(b, start, length, StandardCharsets.US_ASCII);
  }

  private static void rejected(Reason reason, org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(ProtectedReadWireException.class, action);
    assertEquals(reason, failure.reason());
    assertEquals("protected read exchange rejected", failure.getMessage());
    assertNull(failure.getCause());
    failure.addSuppressed(new IllegalStateException(SYNTHETIC_FAILURE));
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final List<byte[]> sent = new ArrayList<>();
    BiFunction<UUID, byte[], byte[]> reply =
        (id, b) -> response(ANIMATION_MENU_KIND, 0, SUCCESS_CODE, id, CONTEXT.wireValue());
    final JmsRequestSender sender =
        (id, b) -> {
          sent.add(b);
          assertTrue(wire.onReply(id, reply.apply(id, b)));
        };
    final AnimationWireClient client = new AnimationWireClient(wire, sender, CLOCK, () -> ID, WAIT);

    void erased() {
      assertEquals(0, wire.pendingCount());
      sent.forEach(b -> assertArrayEquals(new byte[b.length], b));
    }
  }
}
