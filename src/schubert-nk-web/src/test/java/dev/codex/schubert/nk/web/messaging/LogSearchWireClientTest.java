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
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.protocol.layout.semantic.SpeakerId;
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

/** PG213/PT-WEB270..277/FUN008/AUT/MON/MQ/UI232,234,235/SS311,312,321,323,352. */
class LogSearchWireClientTest {
  private static final String FIXTURE_LGSREQ01_A99ED320 = "LGSREQ01";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_SEARCH_F32C67A7 = "/search";
  private static final String FIXTURE_SYNTHETIC_85DA8434 = "synthetic";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
  private static final Duration WAIT = Duration.ofSeconds(2);
  private static final UUID ID = new UUID(0, 1);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));

  @Test
  void web270Requests() {
    var f = new Fixture();
    f.reply =
        (id, b) -> {
          var expected = header(FIXTURE_LGSREQ01_A99ED320, 656, 0, 0, "", id, CONTEXT.wireValue());
          number(expected, 890, 6, 1);
          number(expected, 896, 3, 100);
          assertArrayEquals(expected, b);
          return response(0, false, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue());
        };
    assertEquals(ResultCode.SUCCESS, f.client.exchange(input(), CONTEXT).resultCode());
    assertEquals(1, f.sent.size());
    f.erased();
    String[] types = {"ACTION", "REQUEST", "SECURITY", "MQ", "SYSTEM", "BATCH"};
    String[] levels = {"INFO", "WARN", "ERROR"};
    for (String type : types)
      for (String level : levels) {
        var one = new Fixture();
        one.reply =
            (id, b) -> {
              var expected =
                  header(FIXTURE_LGSREQ01_A99ED320, 656, 0, 0, "", id, CONTEXT.wireValue());
              put(expected, 256, 256, "キーワード");
              put(expected, 512, 16, type);
              put(expected, 528, 64, "action");
              put(expected, 592, 256, FIXTURE_SEARCH_F32C67A7);
              put(expected, 848, 8, level);
              put(expected, 856, 17, "20260901090000000");
              put(expected, 873, 17, "20261002090000000");
              number(expected, 890, 6, 999999);
              number(expected, 896, 3, 100);
              assertArrayEquals(expected, b);
              return response(0, false, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue());
            };
        var data =
            new LogSearchRequestData(
                Optional.of("キーワード"),
                Optional.of(LogType.valueOf(type)),
                Optional.of("action"),
                Optional.of(FIXTURE_SEARCH_F32C67A7),
                Optional.of(LogLevel.valueOf(level)),
                Optional.of(Instant.parse("2026-09-01T00:00:00Z")),
                Optional.of(Instant.parse("2026-10-02T00:00:00Z")),
                999999,
                100);
        assertEquals(
            ResultCode.SUCCESS,
            one.client
                .exchange(
                    new TypedPayloadValues(
                        new LayoutId(FIXTURE_LGSREQ01_A99ED320), data, List.of()),
                    CONTEXT)
                .resultCode());
        assertEquals(1, one.sent.size());
        one.erased();
      }
  }

  @Test
  void web271SuccessProfiles() {
    for (int n : new int[] {0, 1, 100})
      for (boolean optional : List.of(false, true))
        for (String code : List.of(FIXTURE_0000_876EEFE0, "0200")) {
          var f = new Fixture();
          f.reply = (id, b) -> response(n, optional, code, id, CONTEXT.wireValue());
          var result = f.client.exchange(input(), CONTEXT);
          assertEquals(code, result.resultCode().wireValue());
          var p = result.payload().orElseThrow();
          var data = (PagedResponseData) p.data();
          assertEquals(1, data.effectivePage());
          assertEquals(100, data.pageSize());
          assertEquals(n, data.totalCount());
          assertEquals(1, data.totalPages());
          assertEquals(n == 0 ? 0 : 1, data.firstResult());
          assertEquals(n, data.lastResult());
          assertEquals(n, p.records().size());
          for (int i = 0; i < n; i++) {
            var v = (LogRecord) p.records().get(i);
            assertEquals(100 - i, v.logId().value());
            assertEquals(Instant.parse("2026-09-20T01:02:03.004Z"), v.occurredAt());
            assertEquals(LogType.REQUEST, v.logType());
            assertEquals(LogLevel.INFO, v.level());
            assertEquals("message" + i, v.message());
            assertEquals(optional ? Optional.of("search") : Optional.empty(), v.action());
            assertEquals(
                optional ? Optional.of(new UUID(0, 1)) : Optional.empty(), v.httpRequestId());
            assertEquals(
                optional ? Optional.of(new UUID(0, 2)) : Optional.empty(), v.businessMessageId());
            assertEquals(
                optional ? Optional.of(new UUID(0, 3)) : Optional.empty(), v.correlationId());
            assertEquals(optional ? Optional.of("GET") : Optional.empty(), v.httpMethod());
            assertEquals(
                optional ? Optional.of(FIXTURE_SEARCH_F32C67A7) : Optional.empty(), v.path());
            assertEquals(
                optional ? Optional.of(new HttpStatusCode(200)) : Optional.empty(), v.httpStatus());
            assertEquals(
                optional ? Optional.of(new ElapsedMilliseconds(123)) : Optional.empty(),
                v.elapsedMs());
            assertEquals(optional ? Optional.of("127.0.0.1") : Optional.empty(), v.remoteAddress());
            assertEquals(optional ? Optional.of("{}") : Optional.empty(), v.details());
          }
          f.erased();
        }
  }

  @Test
  void web272ErrorProfiles() {
    for (String code :
        List.of("0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "9000", "9001")) {
      var f = new Fixture();
      f.reply = (id, b) -> response(0, false, code, id, CONTEXT.wireValue());
      var result = f.client.exchange(input(), CONTEXT);
      assertEquals(code, result.resultCode().wireValue());
      assertTrue(result.payload().isEmpty());
      f.erased();
      var bad = new Fixture();
      bad.reply =
          (id, b) -> {
            var out = response(0, false, code, id, CONTEXT.wireValue());
            out[256] = '1';
            return out;
          };
      rejected(Reason.INVALID_RESPONSE, () -> bad.client.exchange(input(), CONTEXT));
      bad.erased();
    }
  }

  @Test
  void web273MalformedReplies() {
    for (var change :
        List.<Consumer<byte[]>>of(
            b -> put(b, 11, 8, "MCTRSP01"),
            b -> put(b, 60, 36, new UUID(0, 99).toString()),
            b -> put(b, 113, 64, "b".repeat(64)),
            b -> Arrays.fill(b, 113, 177, (byte) ' '),
            b -> put(b, 199, 9, "000000256"),
            b -> put(b, 208, 4, "9999"),
            b -> b[212] = 'x',
            b -> b[421] = (byte) 0xff,
            b -> put(b, 333, 16, "UNKNOWN"),
            b -> put(b, 349, 8, "UNKNOWN"),
            b -> number(b, 262, 3, 50),
            b -> number(b, 289, 9, 2),
            b -> b[2386] = 'x')) {
      var f = new Fixture();
      f.reply =
          (id, b) -> {
            var out = response(1, true, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue());
            change.accept(out);
            return out;
          };
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input(), CONTEXT));
      f.erased();
    }
    for (int length : new int[] {0, 255, 303, 209105}) {
      var f = new Fixture();
      f.reply = (id, b) -> new byte[length];
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input(), CONTEXT));
      f.erased();
    }
    for (boolean wrongLayout : List.of(true, false)) {
      var f = new Fixture();
      f.reply =
          (id, b) ->
              wrongLayout
                  ? header("MCTRSP01", 8, 72, 1, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue())
                  : Arrays.copyOf(
                      response(0, false, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue()), 305);
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input(), CONTEXT));
      f.erased();
    }
  }

  @Test
  void web274CapabilitiesAndNull() {
    var f = new Fixture();
    rejected(
        Reason.INVALID_INPUT,
        () ->
            f.client.exchange(
                new TypedPayloadValues(
                    new LayoutId(FIXTURE_LGSREQ01_A99ED320),
                    input().data(),
                    List.of(new SpeakerRecord(new SpeakerId(1), FIXTURE_SYNTHETIC_85DA8434, 1))),
                CONTEXT));
    for (String layout : List.of("ANMREQ01", "MCTREQ01", "WLGEVT01")) {
      var request = new TypedPayloadValues(new LayoutId(layout), input().data(), List.of());
      rejected(Reason.INVALID_INPUT, () -> f.client.exchange(request, CONTEXT));
    }
    for (var data :
        List.of(
            new LogSearchRequestData(
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                0,
                100),
            new LogSearchRequestData(
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                1,
                50),
            new LogSearchRequestData(
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.of(Instant.parse("2026-09-01T00:00:00Z")),
                Optional.of(Instant.parse("2026-10-03T00:00:00Z")),
                1,
                100),
            new LogSearchRequestData(
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.of(Instant.parse("2026-09-02T00:00:00Z")),
                Optional.of(Instant.parse("2026-09-01T00:00:00Z")),
                1,
                100))) {
      rejected(
          Reason.INVALID_INPUT,
          () ->
              f.client.exchange(
                  new TypedPayloadValues(new LayoutId(FIXTURE_LGSREQ01_A99ED320), data, List.of()),
                  CONTEXT));
    }
    assertTrue(f.sent.isEmpty());
    assertThrows(NullPointerException.class, () -> f.client.exchange(null, CONTEXT));
    assertThrows(NullPointerException.class, () -> f.client.exchange(input(), null));
    assertThrows(
        NullPointerException.class,
        () -> new LogSearchWireClient(null, f.sender, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new LogSearchWireClient(f.wire, null, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new LogSearchWireClient(f.wire, f.sender, null, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new LogSearchWireClient(f.wire, f.sender, CLOCK, null, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new LogSearchWireClient(f.wire, f.sender, CLOCK, () -> ID, null));
    for (var duration : List.of(Duration.ZERO, Duration.ofNanos(-1), Duration.ofSeconds(3)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new LogSearchWireClient(f.wire, f.sender, CLOCK, () -> ID, duration));
    f.erased();
  }

  @Test
  void web275TransportFailures() {
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 2);
    for (JmsRequestSender sender :
        List.<JmsRequestSender>of(
            (id, b) -> {
              throw new JMSException(FIXTURE_SYNTHETIC_85DA8434);
            },
            (id, b) -> {
              throw new JMSRuntimeException(FIXTURE_SYNTHETIC_85DA8434);
            },
            (id, b) -> {
              throw new IllegalStateException(FIXTURE_SYNTHETIC_85DA8434);
            },
            (id, b) -> {})) {
      var client = new LogSearchWireClient(wire, sender, CLOCK, () -> ID, Duration.ofMillis(1));
      rejected(Reason.UNAVAILABLE, () -> client.exchange(input(), CONTEXT));
      assertEquals(0, wire.pendingCount());
    }
    var failure = new AssertionError(FIXTURE_SYNTHETIC_85DA8434);
    var client =
        new LogSearchWireClient(
            wire,
            (id, b) -> {
              throw failure;
            },
            CLOCK,
            () -> ID,
            WAIT);
    assertSame(
        failure, assertThrows(AssertionError.class, () -> client.exchange(input(), CONTEXT)));
    assertEquals(0, wire.pendingCount());
    var sends = new AtomicLong();
    var badClock =
        new LogSearchWireClient(
            wire,
            (id, b) -> sends.incrementAndGet(),
            Clock.fixed(Instant.MAX, ZoneOffset.UTC),
            () -> ID,
            WAIT);
    rejected(Reason.UNAVAILABLE, () -> badClock.exchange(input(), CONTEXT));
    var badId =
        new LogSearchWireClient(
            wire,
            (id, b) -> sends.incrementAndGet(),
            CLOCK,
            () -> {
              throw new IllegalStateException(FIXTURE_SYNTHETIC_85DA8434);
            },
            WAIT);
    rejected(Reason.UNAVAILABLE, () -> badId.exchange(input(), CONTEXT));
    assertEquals(0, sends.get());
    assertThrows(
        NullPointerException.class,
        () ->
            new LogSearchWireClient(wire, (id, b) -> {}, CLOCK, () -> null, WAIT)
                .exchange(input(), CONTEXT));
  }

  @Test
  void web276ConcurrentRequests() throws Exception {
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    var ids = new AtomicLong();
    var observed = ConcurrentHashMap.<UUID>newKeySet();
    var client =
        new LogSearchWireClient(
            wire,
            (id, b) -> {
              assertTrue(observed.add(id));
              assertEquals(FIXTURE_LGSREQ01_A99ED320, ascii(b, 11, 8));
              assertTrue(
                  wire.onReply(
                      id, response(0, false, FIXTURE_0000_876EEFE0, id, ascii(b, 113, 64))));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            WAIT);
    try (var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () -> {
                  var result =
                      client.exchange(
                          input(),
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)));
                  assertEquals(ResultCode.SUCCESS, result.resultCode());
                  assertEquals("LGSRSP01", result.payload().orElseThrow().layoutId().value());
                }));
      }
      for (var future : futures) future.get();
    }
    assertEquals(64, observed.size());
    assertEquals(0, wire.pendingCount());
  }

  @Test
  void web277OwnershipAndDiagnostics() {
    var f = new Fixture();
    var caller = response(1, true, FIXTURE_0000_876EEFE0, ID, CONTEXT.wireValue());
    var original = caller.clone();
    f.reply = (id, b) -> caller;
    var result = f.client.exchange(input(), CONTEXT);
    assertEquals("ProtectedReadResponse[REDACTED]", result.toString());
    var p = result.payload().orElseThrow();
    assertThrows(UnsupportedOperationException.class, () -> p.records().clear());
    assertFalse(p.toString().contains(CONTEXT.wireValue()));
    assertEquals("message0", ((LogRecord) p.records().getFirst()).message());
    assertArrayEquals(original, caller);
    Arrays.fill(caller, (byte) 0);
    assertEquals("message0", ((LogRecord) p.records().getFirst()).message());
    f.erased();
    for (Reason reason : Reason.values())
      rejected(
          reason,
          () -> {
            throw new ProtectedReadWireException(reason);
          });
  }

  private static TypedPayloadValues input() {
    return new TypedPayloadValues(
        new LayoutId(FIXTURE_LGSREQ01_A99ED320),
        new LogSearchRequestData(
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            1,
            100),
        List.of());
  }

  private static byte[] response(int n, boolean optional, String code, UUID id, String context) {
    boolean success = code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200");
    int count = success ? n : 0;
    var b = header("LGSRSP01", 48, 2088, count, code, id, context);
    number(b, 256, 6, success ? 1 : 0);
    number(b, 262, 3, success ? 100 : 0);
    number(b, 265, 9, count);
    number(b, 274, 6, success ? 1 : 0);
    number(b, 280, 9, count == 0 ? 0 : 1);
    number(b, 289, 9, count);
    for (int i = 0; i < count; i++) {
      int at = 304 + i * 2088;
      number(b, at, 12, 100 - i);
      put(b, at + 12, 17, "20260920100203004");
      put(b, at + 29, 16, "REQUEST");
      put(b, at + 45, 8, "INFO");
      put(b, at + 117, 512, "message" + i);
      if (optional) {
        put(b, at + 53, 64, "search");
        put(b, at + 629, 36, new UUID(0, 1).toString());
        put(b, at + 665, 36, new UUID(0, 2).toString());
        put(b, at + 701, 36, new UUID(0, 3).toString());
        put(b, at + 737, 8, "GET");
        put(b, at + 745, 256, FIXTURE_SEARCH_F32C67A7);
        put(b, at + 1001, 3, "200");
        put(b, at + 1004, 9, "123");
        put(b, at + 1013, 45, "127.0.0.1");
        put(b, at + 1058, 1024, "{}");
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
    failure.addSuppressed(new IllegalStateException(FIXTURE_SYNTHETIC_85DA8434));
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final List<byte[]> sent = new ArrayList<>();
    BiFunction<UUID, byte[], byte[]> reply =
        (id, b) -> response(0, false, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue());
    final JmsRequestSender sender =
        (id, b) -> {
          sent.add(b);
          assertTrue(wire.onReply(id, reply.apply(id, b)));
        };
    final LogSearchWireClient client = new LogSearchWireClient(wire, sender, CLOCK, () -> ID, WAIT);

    void erased() {
      assertEquals(0, wire.pendingCount());
      sent.forEach(b -> assertArrayEquals(new byte[b.length], b));
    }
  }
}
