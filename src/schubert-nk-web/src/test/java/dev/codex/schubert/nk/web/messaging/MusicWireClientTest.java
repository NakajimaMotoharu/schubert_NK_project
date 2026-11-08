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
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.PairRole;
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
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** PG210/PT-WEB254..261/FUN007/AUT/MQ/UI232,235/SS311,312,321,323,352. */
class MusicWireClientTest {
  private static final String MUSIC_CATEGORY_KIND = "MCT";
  private static final String MUSIC_SECTION_KIND = "MCS";
  private static final String MUSIC_TRACK_KIND = "MTR";
  private static final String GAME_SECTION = "ゲーム";
  private static final String SUCCESS_CODE = "0000";
  private static final String SYNTHETIC_FAILURE = "synthetic";
  private static final String PAIR_KEY = "pair0";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
  private static final Duration WAIT = Duration.ofSeconds(2);
  private static final UUID ID = new UUID(0, 1);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));

  @Test
  void web254Requests() {
    for (String type : List.of(MUSIC_CATEGORY_KIND, MUSIC_SECTION_KIND, MUSIC_TRACK_KIND)) {
      var f = new Fixture();
      f.reply =
          (id, b) -> {
            var expected =
                header(
                    type + "REQ01",
                    type.equals(MUSIC_CATEGORY_KIND)
                        ? 0
                        : type.equals(MUSIC_SECTION_KIND) ? 64 : 192,
                    0,
                    0,
                    "",
                    id,
                    CONTEXT.wireValue());
            if (!type.equals(MUSIC_CATEGORY_KIND)) put(expected, 256, 64, "曲");
            if (type.equals(MUSIC_TRACK_KIND)) put(expected, 320, 128, GAME_SECTION);
            assertArrayEquals(expected, b);
            return response(type, 0, SUCCESS_CODE, id, CONTEXT.wireValue());
          };
      assertEquals(ResultCode.SUCCESS, f.client.exchange(input(type), CONTEXT).resultCode());
      assertEquals(1, f.sent.size());
      f.erased();
    }
  }

  @Test
  void web255SuccessProfiles() {
    for (String type : List.of(MUSIC_CATEGORY_KIND, MUSIC_SECTION_KIND, MUSIC_TRACK_KIND))
      for (int n :
          new int[] {
            0,
            1,
            type.equals(MUSIC_CATEGORY_KIND) ? 20 : type.equals(MUSIC_SECTION_KIND) ? 100 : 200
          })
        for (String code : List.of(SUCCESS_CODE, "0200")) {
          var f = new Fixture();
          f.reply = (id, b) -> response(type, n, code, id, CONTEXT.wireValue());
          var result = f.client.exchange(input(type), CONTEXT);
          assertEquals(code, result.resultCode().wireValue());
          var p = result.payload().orElseThrow();
          assertEquals(type + "RSP01", p.layoutId().value());
          assertEquals(n, p.records().size());
          if (type.equals(MUSIC_CATEGORY_KIND))
            assertEquals(n, ((MusicCategoryResponseData) p.data()).totalCount());
          else if (type.equals(MUSIC_SECTION_KIND))
            assertEquals(n, ((MusicSectionResponseData) p.data()).totalCount());
          else assertEquals(n, ((MusicTrackResponseData) p.data()).totalCount());
          for (int i = 0; i < n; i++) {
            if (type.equals(MUSIC_CATEGORY_KIND)) {
              var v = (MusicCategoryRecord) p.records().get(i);
              assertEquals("分類" + i, v.category());
              assertEquals(i + 1, v.trackCount());
            } else if (type.equals(MUSIC_SECTION_KIND)) {
              var v = (MusicSectionRecord) p.records().get(i);
              assertEquals("区分" + i, v.section());
              assertEquals(i + 1, v.trackCount());
            } else {
              var v = (MusicTrackRecord) p.records().get(i);
              assertEquals("track" + i, v.trackId());
              assertEquals("曲名" + i, v.title());
              assertEquals("曲", v.category());
              assertEquals(GAME_SECTION, v.section());
              assertEquals("music/" + i + ".mp3", v.displayPath().wireValue());
              assertEquals(1024 + i, v.fileByteLength());
              assertEquals(i + 1, v.displayOrder());
              assertEquals(Optional.empty(), v.pairKey());
              assertEquals(PairRole.NONE, v.pairRole());
            }
          }
          f.erased();
        }
  }

  @Test
  void web256ErrorProfiles() {
    for (String type : List.of(MUSIC_CATEGORY_KIND, MUSIC_SECTION_KIND, MUSIC_TRACK_KIND))
      for (String code :
          List.of("0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "9000", "9001")) {
        var f = new Fixture();
        f.reply = (id, b) -> response(type, 0, code, id, CONTEXT.wireValue());
        var result = f.client.exchange(input(type), CONTEXT);
        assertEquals(code, result.resultCode().wireValue());
        assertTrue(result.payload().isEmpty());
        f.erased();
        var bad = new Fixture();
        bad.reply =
            (id, b) -> {
              var out = response(type, 0, code, id, CONTEXT.wireValue());
              out[256] = '1';
              return out;
            };
        rejected(Reason.INVALID_RESPONSE, () -> bad.client.exchange(input(type), CONTEXT));
        bad.erased();
      }
  }

  @Test
  void web257MalformedReplies() {
    var changes =
        List.<Consumer<byte[]>>of(
            b -> put(b, 11, 8, "MCTRSP01"),
            b -> put(b, 60, 36, new UUID(0, 99).toString()),
            b -> put(b, 113, 64, "b".repeat(64)),
            b -> put(b, 199, 9, "000000256"),
            b -> put(b, 208, 4, "9999"),
            b -> b[212] = 'x',
            b -> b[336] = (byte) 0xff,
            b -> number(b, 256, 9, 2),
            b -> put(b, 1564, 1, "X"),
            b -> put(b, 1564, 1, "M"),
            b -> number(b, 1296, 12, 0),
            b -> b[1569] = 'x');
    for (var change : changes) {
      var f = new Fixture();
      f.reply =
          (id, b) -> {
            var out = response(MUSIC_TRACK_KIND, 1, SUCCESS_CODE, id, CONTEXT.wireValue());
            change.accept(out);
            return out;
          };
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input(MUSIC_TRACK_KIND), CONTEXT));
      f.erased();
    }
    for (int length : new int[] {0, 255, 263, 262673}) {
      var f = new Fixture();
      f.reply = (id, b) -> new byte[length];
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input(MUSIC_TRACK_KIND), CONTEXT));
      f.erased();
    }
    var order = new Fixture();
    order.reply =
        (id, b) -> {
          var out = response(MUSIC_TRACK_KIND, 2, SUCCESS_CODE, id, CONTEXT.wireValue());
          number(out, 1565, 4, 2);
          number(out, 2877, 4, 1);
          return out;
        };
    rejected(
        Reason.INVALID_RESPONSE, () -> order.client.exchange(input(MUSIC_TRACK_KIND), CONTEXT));
    order.erased();
  }

  @Test
  void web258CapabilitiesAndNull() {
    var f = new Fixture();
    for (var p :
        List.of(
            new TypedPayloadValues(
                new LayoutId("ANMREQ01"), new AnimationMenuRequestData(), List.of()),
            new TypedPayloadValues(
                new LayoutId("MEDREQ01"),
                new MusicDescriptorRequestData("track0", ContentDisposition.INLINE),
                List.of()),
            new TypedPayloadValues(
                new LayoutId("MCTREQ01"),
                new MusicCategoryRequestData(),
                List.of(new MusicCategoryRecord("曲", 1))))) {
      rejected(Reason.INVALID_INPUT, () -> f.client.exchange(p, CONTEXT));
    }
    assertTrue(f.sent.isEmpty());
    assertThrows(NullPointerException.class, () -> f.client.exchange(null, CONTEXT));
    assertThrows(
        NullPointerException.class, () -> f.client.exchange(input(MUSIC_CATEGORY_KIND), null));
    assertThrows(
        NullPointerException.class,
        () -> new MusicWireClient(null, f.sender, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class, () -> new MusicWireClient(f.wire, null, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new MusicWireClient(f.wire, f.sender, null, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class, () -> new MusicWireClient(f.wire, f.sender, CLOCK, null, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new MusicWireClient(f.wire, f.sender, CLOCK, () -> ID, null));
    for (var duration : List.of(Duration.ZERO, Duration.ofNanos(-1), Duration.ofSeconds(3)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MusicWireClient(f.wire, f.sender, CLOCK, () -> ID, duration));
    f.erased();
  }

  @Test
  void web259TransportFailures() {
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
      var client = new MusicWireClient(wire, sender, CLOCK, () -> ID, Duration.ofMillis(1));
      rejected(Reason.UNAVAILABLE, () -> client.exchange(input(MUSIC_CATEGORY_KIND), CONTEXT));
      assertEquals(0, wire.pendingCount());
    }
    var failure = new AssertionError(SYNTHETIC_FAILURE);
    var client =
        new MusicWireClient(
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
            AssertionError.class, () -> client.exchange(input(MUSIC_CATEGORY_KIND), CONTEXT)));
    assertEquals(0, wire.pendingCount());
    var sends = new AtomicLong();
    var badClock =
        new MusicWireClient(
            wire,
            (id, b) -> sends.incrementAndGet(),
            Clock.fixed(Instant.MAX, ZoneOffset.UTC),
            () -> ID,
            WAIT);
    rejected(Reason.UNAVAILABLE, () -> badClock.exchange(input(MUSIC_CATEGORY_KIND), CONTEXT));
    var badId =
        new MusicWireClient(
            wire,
            (id, b) -> sends.incrementAndGet(),
            CLOCK,
            () -> {
              throw new IllegalStateException(SYNTHETIC_FAILURE);
            },
            WAIT);
    rejected(Reason.UNAVAILABLE, () -> badId.exchange(input(MUSIC_CATEGORY_KIND), CONTEXT));
    assertEquals(0, sends.get());
    assertThrows(
        NullPointerException.class,
        () ->
            new MusicWireClient(wire, (id, b) -> {}, CLOCK, () -> null, WAIT)
                .exchange(input(MUSIC_CATEGORY_KIND), CONTEXT));
  }

  @Test
  void web260ConcurrentRequests() throws Exception {
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    var ids = new AtomicLong();
    var observed = ConcurrentHashMap.<UUID>newKeySet();
    var client =
        new MusicWireClient(
            wire,
            (id, b) -> {
              assertTrue(observed.add(id));
              assertTrue(
                  wire.onReply(
                      id, response(ascii(b, 11, 3), 0, SUCCESS_CODE, id, ascii(b, 113, 64))));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            WAIT);
    var pool = Executors.newFixedThreadPool(8);
    try {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () -> {
                  String type =
                      List.of(MUSIC_CATEGORY_KIND, MUSIC_SECTION_KIND, MUSIC_TRACK_KIND).get(n % 3);
                  var result =
                      client.exchange(
                          input(type),
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)));
                  assertEquals(ResultCode.SUCCESS, result.resultCode());
                  assertEquals(type + "RSP01", result.payload().orElseThrow().layoutId().value());
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(64, observed.size());
    assertEquals(0, wire.pendingCount());
  }

  @Test
  void web261OwnershipAndDiagnostics() {
    var f = new Fixture();
    var caller = response(MUSIC_TRACK_KIND, 3, SUCCESS_CODE, ID, CONTEXT.wireValue());
    put(caller, 1308, 256, PAIR_KEY);
    put(caller, 1564, 1, "M");
    put(caller, 2620, 256, PAIR_KEY);
    put(caller, 2876, 1, "I");
    var original = caller.clone();
    f.reply = (id, b) -> caller;
    var result = f.client.exchange(input(MUSIC_TRACK_KIND), CONTEXT);
    assertEquals("ProtectedReadResponse[REDACTED]", result.toString());
    var p = result.payload().orElseThrow();
    assertThrows(UnsupportedOperationException.class, () -> p.records().clear());
    assertFalse(p.toString().contains(CONTEXT.wireValue()));
    assertEquals(PairRole.MAIN, ((MusicTrackRecord) p.records().get(0)).pairRole());
    assertEquals(PairRole.INSTRUMENTAL, ((MusicTrackRecord) p.records().get(1)).pairRole());
    assertEquals(Optional.of(PAIR_KEY), ((MusicTrackRecord) p.records().get(0)).pairKey());
    assertEquals(Optional.of(PAIR_KEY), ((MusicTrackRecord) p.records().get(1)).pairKey());
    assertEquals(PairRole.NONE, ((MusicTrackRecord) p.records().get(2)).pairRole());
    assertArrayEquals(original, caller);
    Arrays.fill(caller, (byte) 0);
    assertEquals("track0", ((MusicTrackRecord) p.records().getFirst()).trackId());
    f.erased();
    for (Reason reason : Reason.values())
      rejected(
          reason,
          () -> {
            throw new ProtectedReadWireException(reason);
          });
  }

  private static TypedPayloadValues input(String type) {
    PayloadData data =
        switch (type) {
          case MUSIC_CATEGORY_KIND -> new MusicCategoryRequestData();
          case MUSIC_SECTION_KIND -> new MusicSectionRequestData("曲");
          default -> new MusicTrackRequestData("曲", GAME_SECTION);
        };
    return new TypedPayloadValues(new LayoutId(type + "REQ01"), data, List.of());
  }

  private static byte[] response(String type, int n, String code, UUID id, String context) {
    int data = type.equals(MUSIC_TRACK_KIND) ? 16 : 8;
    int record =
        type.equals(MUSIC_CATEGORY_KIND) ? 72 : type.equals(MUSIC_SECTION_KIND) ? 136 : 1312;
    var b = header(type + "RSP01", data, record, n, code, id, context);
    number(b, 256, type.equals(MUSIC_TRACK_KIND) ? 9 : 6, n);
    for (int i = 0; i < n; i++) {
      int at = 256 + data + i * record;
      if (type.equals(MUSIC_CATEGORY_KIND)) {
        put(b, at, 64, "分類" + i);
        number(b, at + 64, 6, i + 1);
      } else if (type.equals(MUSIC_SECTION_KIND)) {
        put(b, at, 128, "区分" + i);
        number(b, at + 128, 6, i + 1);
      } else {
        put(b, at, 64, "track" + i);
        put(b, at + 64, 256, "曲名" + i);
        put(b, at + 320, 64, "曲");
        put(b, at + 384, 128, GAME_SECTION);
        put(b, at + 512, 512, "music/" + i + ".mp3");
        number(b, at + 1024, 12, 1024 + i);
        put(b, at + 1292, 1, "N");
        number(b, at + 1293, 4, i + 1);
      }
    }
    return b;
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
        (id, b) -> response(MUSIC_CATEGORY_KIND, 0, SUCCESS_CODE, id, CONTEXT.wireValue());
    final JmsRequestSender sender =
        (id, b) -> {
          sent.add(b);
          assertTrue(wire.onReply(id, reply.apply(id, b)));
        };
    final MusicWireClient client = new MusicWireClient(wire, sender, CLOCK, () -> ID, WAIT);

    void erased() {
      assertEquals(0, wire.pendingCount());
      sent.forEach(b -> assertArrayEquals(new byte[b.length], b));
    }
  }
}
