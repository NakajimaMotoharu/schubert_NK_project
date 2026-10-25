package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.web.messaging.ScenarioWireException.Reason;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** NK-WEB-001/NK-SCN-001/PT-WEB-166..173; UI232/234; SS311/321/322/323/352; PG-D-118. */
class ScenarioWireClientTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-09T00:00:00.123987Z"), ZoneOffset.UTC);
  private static final Duration WAIT = Duration.ofSeconds(2);
  private static final UUID ID = new UUID(0, 1);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));
  private static final String[] TYPES = {"GAM", "SPK", "SRC", "RTE", "SCF", "SCN"};
  private static final int[] DATA = {9, 9, 48, 9, 88, 1728};
  private static final int[] RECORD = {272, 152, 5584, 72, 800, 4800};
  private static final int[] MAX = {10, 500, 100, 50, 500, 200};

  @Test
  void web166SixRequestsMatchIndependentWire() {
    for (String type : TYPES) {
      var f = new Fixture();
      byte[] expected = request(type, ID, CONTEXT.wireValue());
      f.reply =
          (id, bytes) -> {
            assertArrayEquals(expected, bytes);
            return response(type, 1, "0000", id, CONTEXT.wireValue());
          };
      var input = input(type);
      var result = f.client.exchange(input, CONTEXT);
      assertEquals(ResultCode.SUCCESS, result.resultCode());
      assertEquals(type + "RSP01", result.payload().orElseThrow().layoutId().value());
      assertEquals(1, result.payload().orElseThrow().records().size());
      assertEquals(input(type), input);
      assertEquals(1, f.sent.size());
      f.erased();
    }
    var f = new Fixture();
    f.reply =
        (id, bytes) -> {
          assertArrayEquals(spaces(12), Arrays.copyOfRange(bytes, 256, 268));
          return response("SPK", 0, "0000", id, CONTEXT.wireValue());
        };
    f.client.exchange(
        new TypedPayloadValues(
            new LayoutId("SPKREQ01"), new SpeakerListRequestData(Optional.empty()), List.of()),
        CONTEXT);
    f.erased();
  }

  @Test
  void web167SixSuccessResponsesDecodeWithoutRetainingSecrets() {
    for (int kind = 0; kind < TYPES.length; kind++) {
      String type = TYPES[kind];
      for (int n : new int[] {0, 1, MAX[kind]}) {
        for (String code : List.of("0000", "0200")) {
          var f = new Fixture();
          f.reply = (id, bytes) -> response(type, n, code, id, CONTEXT.wireValue());
          var result = f.client.exchange(input(type), CONTEXT);
          assertEquals(
              code.equals("0000") ? ResultCode.SUCCESS : ResultCode.IDEMPOTENT_SUCCESS,
              result.resultCode());
          var payload = result.payload().orElseThrow();
          assertEquals(n, payload.records().size());
          assertEquals("ScenarioResponse[REDACTED]", result.toString());
          assertFalse(payload.toString().contains(CONTEXT.wireValue()));
          assertThrows(
              UnsupportedOperationException.class,
              () -> payload.records().add(new GameRecord(GameCode.NUKITASHI_1, "x", 1)));
          for (int index = 0; index < n; index++) {
            var record = payload.records().get(index);
            switch (type) {
              case "GAM" -> {
                var r = (GameRecord) record;
                assertEquals(index + 1, r.displayOrder());
                assertEquals("Game" + index, r.title());
              }
              case "SPK" -> {
                var r = (SpeakerRecord) record;
                assertEquals("Speaker" + index, r.speakerName());
              }
              case "SRC" -> {
                var r = (ScenarioSearchRecord) record;
                assertEquals("body" + index, r.bodyText());
              }
              case "RTE" -> {
                var r = (RouteRecord) record;
                assertEquals(index + 1, r.prefix());
                assertEquals("未分類", r.routeName());
              }
              case "SCF" -> {
                var r = (ScenarioFileRecord) record;
                assertEquals("Title" + index, r.displayTitle());
              }
              case "SCN" -> {
                var r = (ScenarioEntryRecord) record;
                assertEquals(index + 1, r.entrySequence());
                assertEquals("body" + index, r.bodyText());
              }
              default -> fail("fixture type");
            }
          }
          f.erased();
        }
      }
    }
    for (int n : new int[] {1, 201, 10000}) {
      var f = new Fixture();
      f.reply = (id, bytes) -> fileResponse(id, CONTEXT.wireValue(), n);
      var result = f.client.exchange(input("SCN"), CONTEXT);
      var data = (ScenarioDetailResponseData) result.payload().orElseThrow().data();
      assertEquals(n, data.fileRecordCount());
      assertEquals(n * 4800L, data.fileByteLength());
      assertEquals(0, result.payload().orElseThrow().records().size());
      f.erased();
    }
  }

  @Test
  void web168ApprovedErrorsNeverExposeSuccessPayload() {
    for (String type : TYPES)
      for (String code :
          List.of("0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "9000", "9001")) {
        var f = new Fixture();
        f.reply = (id, bytes) -> response(type, 0, code, id, CONTEXT.wireValue());
        var result = f.client.exchange(input(type), CONTEXT);
        assertEquals(code, result.resultCode().wireValue());
        assertTrue(result.payload().isEmpty());
        f.erased();
        var corrupt = new Fixture();
        corrupt.reply =
            (id, bytes) -> {
              var reply = response(type, 0, code, id, CONTEXT.wireValue());
              reply[256] = '1';
              return reply;
            };
        rejected(Reason.INVALID_RESPONSE, () -> corrupt.client.exchange(input(type), CONTEXT));
        corrupt.erased();
      }
  }

  @Test
  void web169MalformedUncorrelatedAndForeignResponsesReject() {
    var changes = new ArrayList<Consumer<byte[]>>();
    changes.add(b -> put(b, 0, 8, "BADPROTO"));
    changes.add(b -> put(b, 8, 3, "002"));
    changes.add(b -> put(b, 11, 8, "GAMREQ01"));
    changes.add(b -> put(b, 19, 3, "002"));
    changes.add(b -> b[22] = 'Q');
    changes.add(b -> b[23] = 'I');
    changes.add(b -> put(b, 24, 36, "not-a-uuid"));
    changes.add(b -> put(b, 60, 36, new UUID(0, 2).toString()));
    changes.add(b -> put(b, 96, 17, "20261399000000000"));
    changes.add(b -> put(b, 113, 64, "b".repeat(64)));
    changes.add(b -> put(b, 113, 64, ""));
    changes.add(b -> put(b, 177, 4, "0255"));
    changes.add(b -> put(b, 181, 6, "000008"));
    changes.add(b -> put(b, 187, 6, "000271"));
    changes.add(b -> put(b, 193, 6, "000002"));
    changes.add(b -> put(b, 199, 9, "000000536"));
    changes.add(b -> put(b, 208, 4, "9999"));
    changes.add(b -> b[212] = 'x');
    changes.add(b -> put(b, 256, 9, "000000002"));
    changes.add(b -> put(b, 265, 12, "UNKNOWN"));
    changes.add(b -> b[277] = (byte) 0xff);
    changes.add(b -> put(b, 277, 256, "e\u0301"));
    changes.add(b -> b[536] = 'x');
    for (var change : changes) {
      var f = new Fixture();
      f.reply =
          (id, bytes) -> {
            var r = response("GAM", 1, "0000", id, CONTEXT.wireValue());
            change.accept(r);
            return r;
          };
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input("GAM"), CONTEXT));
      f.erased();
    }
    for (int delta : new int[] {-1, 1}) {
      var f = new Fixture();
      f.reply =
          (id, bytes) -> {
            var valid = response("GAM", 1, "0000", id, CONTEXT.wireValue());
            return Arrays.copyOf(valid, valid.length + delta);
          };
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input("GAM"), CONTEXT));
      f.erased();
    }
    var wrong = new Fixture();
    wrong.reply = (id, bytes) -> response("SPK", 0, "0000", id, CONTEXT.wireValue());
    rejected(Reason.INVALID_RESPONSE, () -> wrong.client.exchange(input("GAM"), CONTEXT));
    var order = new Fixture();
    order.reply =
        (id, bytes) -> {
          var r = response("RTE", 2, "0000", id, CONTEXT.wireValue());
          put(r, 265 + 72, 2, "01");
          return r;
        };
    rejected(Reason.INVALID_RESPONSE, () -> order.client.exchange(input("RTE"), CONTEXT));
  }

  @Test
  void web170InputAndConfigurationFaultsNeverSend() {
    var f = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioWireClient(null, f.sender, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioWireClient(f.wire, null, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioWireClient(f.wire, f.sender, null, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioWireClient(f.wire, f.sender, CLOCK, null, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioWireClient(f.wire, f.sender, CLOCK, () -> ID, null));
    for (Duration bad : List.of(Duration.ZERO, Duration.ofNanos(-1), WAIT.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new ScenarioWireClient(f.wire, f.sender, CLOCK, () -> ID, bad));
    new ScenarioWireClient(f.wire, f.sender, CLOCK, () -> ID, Duration.ofNanos(1));
    assertThrows(NullPointerException.class, () -> f.client.exchange(null, CONTEXT));
    assertThrows(NullPointerException.class, () -> f.client.exchange(input("GAM"), null));
    assertThrows(NullPointerException.class, () -> new ScenarioWireException(null));
    var bad =
        List.of(
            new TypedPayloadValues(new LayoutId("LOGREQ01"), new LogoutRequestData(), List.of()),
            new TypedPayloadValues(
                new LayoutId("GAMRSP01"), new GameListResponseData(0), List.of()),
            new TypedPayloadValues(
                new LayoutId("GAMREQ01"),
                new RouteListRequestData(GameCode.NUKITASHI_1),
                List.of()),
            new TypedPayloadValues(
                new LayoutId("GAMREQ01"),
                new GameListRequestData(),
                List.of(new GameRecord(GameCode.NUKITASHI_1, "x", 1))),
            new TypedPayloadValues(
                new LayoutId("SRCREQ01"),
                new ScenarioSearchRequestData(
                    Optional.of("x".repeat(257)),
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    1,
                    100),
                List.of()),
            new TypedPayloadValues(
                new LayoutId("SRCREQ01"),
                new ScenarioSearchRequestData(
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    0,
                    100),
                List.of()));
    for (var request : bad)
      rejected(Reason.INVALID_INPUT, () -> f.client.exchange(request, CONTEXT));
    var failedId =
        new ScenarioWireClient(
            f.wire,
            f.sender,
            CLOCK,
            () -> {
              throw new IllegalStateException("private");
            },
            WAIT);
    rejected(Reason.UNAVAILABLE, () -> failedId.exchange(input("GAM"), CONTEXT));
    var nullId = new ScenarioWireClient(f.wire, f.sender, CLOCK, () -> null, WAIT);
    assertThrows(NullPointerException.class, () -> nullId.exchange(input("GAM"), CONTEXT));
    for (Clock clock :
        List.of(
            Clock.fixed(Instant.MAX, ZoneOffset.UTC),
            new Clock() {
              @Override
              public ZoneId getZone() {
                return ZoneOffset.UTC;
              }

              @Override
              public Clock withZone(ZoneId zone) {
                return this;
              }

              @Override
              public Instant instant() {
                throw new DateTimeException("private");
              }
            })) {
      var faulty = new ScenarioWireClient(f.wire, f.sender, clock, () -> ID, WAIT);
      rejected(Reason.UNAVAILABLE, () -> faulty.exchange(input("GAM"), CONTEXT));
    }
    assertTrue(f.sent.isEmpty());
  }

  @Test
  void web171TransportFailuresDoNotRetryOrLeakPending() throws Exception {
    for (Exception exception :
        List.of(
            new JMSException("private"),
            new JMSRuntimeException("private"),
            new IllegalArgumentException("private"),
            new IllegalStateException("private"))) {
      var f = new Fixture();
      var sender =
          new ScenarioWireClient(
              f.wire,
              (id, bytes) -> {
                f.sent.add(bytes);
                if (exception instanceof JMSException checked) throw checked;
                throw (RuntimeException) exception;
              },
              CLOCK,
              () -> ID,
              WAIT);
      rejected(Reason.UNAVAILABLE, () -> sender.exchange(input("GAM"), CONTEXT));
      assertEquals(1, f.sent.size());
      f.erased();
    }
    var f = new Fixture();
    var timeout =
        new ScenarioWireClient(
            f.wire, (id, bytes) -> f.sent.add(bytes), CLOCK, () -> ID, Duration.ofNanos(1));
    rejected(Reason.UNAVAILABLE, () -> timeout.exchange(input("GAM"), CONTEXT));
    assertFalse(f.wire.onReply(ID, response("GAM", 0, "0000", ID, CONTEXT.wireValue())));
    f.erased();
    Thread.currentThread().interrupt();
    try {
      var interrupted =
          new ScenarioWireClient(
              f.wire, (id, bytes) -> f.sent.add(bytes), CLOCK, () -> new UUID(0, 2), WAIT);
      rejected(Reason.UNAVAILABLE, () -> interrupted.exchange(input("GAM"), CONTEXT));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    f.erased();
    var npe = new NullPointerException("private");
    var failedProvider =
        new ScenarioWireClient(
            f.wire,
            (id, bytes) -> {
              f.sent.add(bytes);
              throw npe;
            },
            CLOCK,
            () -> ID,
            WAIT);
    assertSame(
        npe,
        assertThrows(
            NullPointerException.class, () -> failedProvider.exchange(input("GAM"), CONTEXT)));
    f.erased();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
    var sends = new AtomicInteger();
    var one =
        new ScenarioWireClient(
            wire,
            (id, bytes) -> {
              sends.incrementAndGet();
              entered.countDown();
              try {
                assertTrue(release.await(5, TimeUnit.SECONDS));
              } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IllegalStateException("fixture interrupted");
              }
              assertTrue(wire.onReply(id, response("GAM", 0, "0000", id, CONTEXT.wireValue())));
            },
            CLOCK,
            () -> ID,
            WAIT);
    try (var pool = Executors.newSingleThreadExecutor()) {
      var first = pool.submit(() -> one.exchange(input("GAM"), CONTEXT));
      assertTrue(entered.await(5, TimeUnit.SECONDS));
      try {
        rejected(Reason.UNAVAILABLE, () -> one.exchange(input("GAM"), CONTEXT));
      } finally {
        release.countDown();
      }
      assertEquals(ResultCode.SUCCESS, first.get(5, TimeUnit.SECONDS).resultCode());
    }
    assertEquals(1, sends.get());
    assertEquals(0, wire.pendingCount());
  }

  @Test
  void web172ConcurrentQueriesKeepContextsAndRepliesSeparate() throws Exception {
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    var ids = new AtomicLong();
    var active = new ThreadLocal<String>();
    var seen = ConcurrentHashMap.<UUID>newKeySet();
    var sent = new CopyOnWriteArrayList<byte[]>();
    var client =
        new ScenarioWireClient(
            wire,
            (id, bytes) -> {
              String context = active.get();
              assertNotNull(context);
              assertEquals(context, ascii(bytes, 113, 64));
              assertTrue(seen.add(id));
              String type = ascii(bytes, 11, 3);
              assertArrayEquals(request(type, id, context), bytes);
              sent.add(bytes);
              assertTrue(wire.onReply(id, response(type, 1, "0000", id, context)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            WAIT);
    try (var pool = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int n = 0; n < 100; n++) {
        int index = n;
        tasks.add(
            pool.submit(
                () -> {
                  String context = String.format(Locale.ROOT, "%064x", index + 1);
                  active.set(context);
                  try {
                    String type = TYPES[index % 6];
                    var result = client.exchange(input(type), AuthenticationContext.of(context));
                    assertEquals(type + "RSP01", result.payload().orElseThrow().layoutId().value());
                    assertEquals(1, result.payload().orElseThrow().records().size());
                  } finally {
                    active.remove();
                  }
                  return null;
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
    }
    assertEquals(100, seen.size());
    assertEquals(100, sent.size());
    assertEquals(0, wire.pendingCount());
    sent.forEach(bytes -> assertArrayEquals(new byte[bytes.length], bytes));
  }

  @Test
  void web173ResponseBoundsAndCallerOwnershipRemainExact() {
    for (int i = 0; i < TYPES.length; i++) {
      String type = TYPES[i];
      for (int size :
          new int[] {0, 255, 256 + DATA[i] - 1, 256 + DATA[i] + RECORD[i] * MAX[i] + 1, 1000001}) {
        var f = new Fixture();
        f.reply = (id, bytes) -> spaces(size);
        rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input(type), CONTEXT));
        f.erased();
      }
      var f = new Fixture();
      byte[] original = response(type, 1, "0000", ID, CONTEXT.wireValue());
      byte[] expected = original.clone();
      f.reply = (id, bytes) -> original;
      var result = f.client.exchange(input(type), CONTEXT);
      assertArrayEquals(expected, original);
      Arrays.fill(original, (byte) 0);
      assertEquals(type + "RSP01", result.payload().orElseThrow().layoutId().value());
      assertEquals(1, result.payload().orElseThrow().records().size());
      f.erased();
    }
  }

  private static TypedPayloadValues input(String type) {
    PayloadData data =
        switch (type) {
          case "GAM" -> new GameListRequestData();
          case "SPK" -> new SpeakerListRequestData(Optional.of(GameCode.NUKITASHI_1));
          case "SRC" ->
              new ScenarioSearchRequestData(
                  Optional.of("keyword"),
                  Optional.of(GameCode.NUKITASHI_1),
                  Optional.of("speaker"),
                  Optional.of("chapter"),
                  Optional.empty(),
                  Optional.empty(),
                  1,
                  100);
          case "RTE" -> new RouteListRequestData(GameCode.NUKITASHI_1);
          case "SCF" -> new ScenarioFileListRequestData(GameCode.NUKITASHI_1, 1);
          case "SCN" -> new ScenarioDetailRequestData(new ScriptFileId(1));
          default -> throw new AssertionError("fixture type");
        };
    return new TypedPayloadValues(new LayoutId(type + "REQ01"), data, List.of());
  }

  private static byte[] request(String type, UUID id, String context) {
    int length =
        switch (type) {
          case "GAM" -> 0;
          case "SPK", "RTE", "SCN" -> 12;
          case "SCF" -> 14;
          case "SRC" -> 672;
          default -> throw new AssertionError();
        };
    byte[] body = header(type + "REQ01", length, 0, 0, "", id, context);
    switch (type) {
      case "SPK", "RTE" -> put(body, 256, 12, "NUKITASHI1");
      case "SCF" -> {
        put(body, 256, 12, "NUKITASHI1");
        number(body, 268, 2, 1);
      }
      case "SCN" -> number(body, 256, 12, 1);
      case "SRC" -> {
        put(body, 256, 256, "keyword");
        put(body, 512, 12, "NUKITASHI1");
        put(body, 524, 128, "speaker");
        put(body, 652, 256, "chapter");
        number(body, 919, 6, 1);
        number(body, 925, 3, 100);
      }
      default -> {}
    }
    return body;
  }

  private static byte[] response(
      String type, int count, String code, UUID correlation, String context) {
    int kind = Arrays.asList(TYPES).indexOf(type);
    byte[] body =
        header(type + "RSP01", DATA[kind], RECORD[kind], count, code, correlation, context);
    boolean success = code.equals("0000") || code.equals("0200");
    switch (type) {
      case "GAM", "SPK", "RTE" -> number(body, 256, 9, success ? count : 0);
      case "SRC" -> {
        number(body, 256, 6, success ? 1 : 0);
        number(body, 262, 3, success ? 100 : 0);
        number(body, 265, 9, success ? count : 0);
        number(body, 274, 6, success ? 1 : 0);
        number(body, 280, 9, success && count > 0 ? 1 : 0);
        number(body, 289, 9, success ? count : 0);
      }
      case "SCF" -> {
        put(body, 256, 12, success ? "NUKITASHI1" : "");
        number(body, 268, 2, success ? 1 : 0);
        put(body, 270, 64, success ? "共通ルート" : "");
        number(body, 334, 9, success ? count : 0);
      }
      case "SCN" -> {
        number(body, 256, 12, success ? 1 : 0);
        put(body, 268, 12, success ? "NUKITASHI1" : "");
        put(body, 280, 256, success ? "Title" : "");
        put(body, 536, 512, success ? "game/01.txt" : "");
        put(body, 1584, 1, success ? "I" : "");
        number(body, 1877, 12, 0);
        number(body, 1953, 6, 0);
        number(body, 1959, 9, 0);
      }
      default -> throw new AssertionError();
    }
    for (int n = 0; n < count; n++) {
      int offset = 256 + DATA[kind] + n * RECORD[kind];
      switch (type) {
        case "GAM" -> {
          put(body, offset, 12, "NUKITASHI1");
          put(body, offset + 12, 256, "Game" + n);
          number(body, offset + 268, 3, n + 1);
        }
        case "SPK" -> {
          number(body, offset, 12, n + 1);
          put(body, offset + 12, 128, "Speaker" + n);
          number(body, offset + 140, 9, 1000 - n);
        }
        case "RTE" -> {
          number(body, offset, 2, n + 1);
          put(body, offset + 2, 64, "未分類");
          number(body, offset + 66, 6, 1);
        }
        case "SCF" -> {
          number(body, offset, 12, n + 1);
          put(body, offset + 12, 256, "Title" + n);
          put(body, offset + 268, 512, "game/" + n + ".txt");
          number(body, offset + 780, 6, n);
        }
        case "SRC" -> {
          number(body, offset, 12, n + 1);
          number(body, offset + 12, 12, 1);
          put(body, offset + 24, 12, "NUKITASHI1");
          number(body, offset + 292, 8, n + 1);
          put(body, offset + 300, 10, "narration");
          put(body, offset + 438, 4096, "body" + n);
          put(body, offset + 4534, 1, "0");
          put(body, offset + 4547, 512, "game/01.txt");
        }
        case "SCN" -> {
          number(body, offset, 12, n + 1);
          number(body, offset + 12, 6, n + 1);
          number(body, offset + 18, 8, n + 1);
          put(body, offset + 26, 10, "narration");
          put(body, offset + 164, 4096, "body" + n);
          number(body, offset + 4260, 3, 0);
        }
        default -> throw new AssertionError();
      }
    }
    return body;
  }

  private static byte[] fileResponse(UUID id, String context, int n) {
    var body = response("SCN", 0, "0000", id, context);
    put(body, 1584, 1, "F");
    put(body, 1585, 36, new UUID(0, 9).toString());
    put(body, 1621, 256, "20260909/" + new UUID(0, 9) + ".ready");
    number(body, 1877, 12, n * 4800L);
    put(body, 1889, 64, "b".repeat(64));
    number(body, 1953, 6, 4800);
    number(body, 1959, 9, n);
    return body;
  }

  private static byte[] header(
      String layout,
      int data,
      int record,
      int count,
      String code,
      UUID correlation,
      String context) {
    var body = spaces(256 + data + record * count);
    put(body, 0, 8, "SCHBNK01");
    put(body, 8, 3, "001");
    put(body, 11, 8, layout);
    put(body, 19, 3, "001");
    put(body, 22, 1, code.isEmpty() ? "Q" : "S");
    put(body, 23, 1, "S");
    put(
        body,
        24,
        36,
        code.isEmpty()
            ? correlation.toString()
            : new UUID(1, correlation.getLeastSignificantBits()).toString());
    put(body, 60, 36, correlation.toString());
    put(body, 96, 17, "20260909090000123");
    put(body, 113, 64, context);
    number(body, 177, 4, 256);
    number(body, 181, 6, data);
    number(body, 187, 6, record);
    number(body, 193, 6, count);
    number(body, 199, 9, body.length);
    put(body, 208, 4, code);
    return body;
  }

  private static byte[] spaces(int length) {
    var bytes = new byte[length];
    Arrays.fill(bytes, (byte) ' ');
    return bytes;
  }

  private static String ascii(byte[] value, int start, int length) {
    return new String(value, start, length, StandardCharsets.US_ASCII);
  }

  private static void put(byte[] body, int offset, int length, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    assertTrue(bytes.length <= length);
    Arrays.fill(body, offset, offset + length, (byte) ' ');
    System.arraycopy(bytes, 0, body, offset, bytes.length);
  }

  private static void number(byte[] body, int offset, int length, long value) {
    put(body, offset, length, String.format(Locale.ROOT, "%0" + length + "d", value));
  }

  private static void rejected(Reason expected, org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(ScenarioWireException.class, action);
    assertEquals(expected, failure.reason());
    assertEquals("scenario exchange rejected", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    failure.addSuppressed(new IllegalStateException("private"));
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final List<byte[]> sent = new ArrayList<>();
    BiFunction<UUID, byte[], byte[]> reply =
        (id, bytes) -> response("GAM", 0, "0000", id, CONTEXT.wireValue());
    final JmsRequestSender sender =
        (id, bytes) -> {
          sent.add(bytes);
          assertTrue(wire.onReply(id, reply.apply(id, bytes)));
        };
    final ScenarioWireClient client = new ScenarioWireClient(wire, sender, CLOCK, () -> ID, WAIT);

    void erased() {
      assertEquals(0, wire.pendingCount());
      sent.forEach(bytes -> assertArrayEquals(new byte[bytes.length], bytes));
    }
  }
}
