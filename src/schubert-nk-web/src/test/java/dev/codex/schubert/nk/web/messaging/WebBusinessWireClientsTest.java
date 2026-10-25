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
import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRoleRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserStatusRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserUnlockRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import jakarta.jms.JMSException;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** NK-WEB001/UI232/234/235/236/SS323; PG-D-342; PT-WEB-S3WIRE001..008. */
class WebBusinessWireClientsTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-02T19:00:00.123456Z"), ZoneOffset.UTC);
  private static final UUID ID = new UUID(0, 1);
  private static final UUID TOKEN = new UUID(0, 2);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));
  private static final Duration WAIT = Duration.ofSeconds(2);
  private static final String RECEIPT = "0123456789ABCDEFGHJKMNPQRS";
  private static final String[] TYPES = {
    "QSB", "QSS", "QSD", "QDL", "NTS", "NTD", "NTC", "USR", "UDT", "UCR", "UST", "URL", "UPW",
    "ULK", "LOG", "AUD", "VID", "MED"
  };
  private static final int[] REQUEST = {
    4144, 384, 12, 48, 64, 12, 48, 96, 12, 372, 60, 68, 324, 60, 0, 16, 64, 72
  };
  private static final int[] RESPONSE = {
    64, 48, 8352, 24, 48, 8896, 32, 48, 320, 24, 24, 24, 24, 24, 24, 1024, 1808, 1024
  };
  private static final int[] RECORD = {0, 672, 0, 0, 624, 0, 0, 168, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

  @Test
  void wire001EighteenRequestsMatchIndependentUiByteOffsets() {
    for (String type : TYPES) {
      var f = new Fixture();
      f.reply =
          (id, body) -> {
            assertArrayEquals(request(type, id, CONTEXT.wireValue()), body, type);
            return response(type, "9000", id, CONTEXT.wireValue());
          };
      var result = f.facade(group(type)).apply(input(type), CONTEXT);
      assertEquals("9000", result.resultCode().wireValue());
      assertTrue(result.payload().isEmpty());
      assertEquals("ProtectedReadResponse[REDACTED]", result.toString());
      assertEquals(1, f.sent.size());
      f.erased();
    }
  }

  @Test
  void wire002AcceptanceAndIdempotentResultsRemainTyped() {
    for (String type : List.of("QSB", "QDL", "NTC", "UCR", "UST", "URL", "UPW", "ULK", "LOG"))
      for (String code : List.of("0000", "0200")) {
        var f = new Fixture();
        f.reply = (id, body) -> response(type, code, id, CONTEXT.wireValue());
        var result = f.facade(group(type)).apply(input(type), CONTEXT);
        assertEquals(code, result.resultCode().wireValue());
        var values = result.payload().orElseThrow();
        assertEquals(type + "RSP01", values.layoutId().value());
        assertTrue(values.records().isEmpty());
        assertFalse(values.toString().contains(CONTEXT.wireValue()));
        switch (type) {
          case "QSB" -> {
            var data = (QuestionSubmitResponseData) values.data();
            assertEquals(RECEIPT, data.receiptId());
            assertEquals(new QuestionId(1), data.questionId());
            assertEquals(Instant.parse("2026-10-02T19:00:00.123Z"), data.submittedAt());
          }
          case "QDL" ->
              assertEquals(
                  Instant.parse("2026-10-02T19:00:00.123Z"),
                  ((QuestionDeleteResponseData) values.data()).deletedAt());
          case "LOG" ->
              assertEquals(
                  Instant.parse("2026-10-02T19:00:00.123Z"),
                  ((LogoutResponseData) values.data()).sessionRevokedAt());
          case "NTC" -> {
            var data = (NotificationCancelResponseData) values.data();
            assertEquals(Optional.of(NotificationState.CANCELLED), data.updatedState());
            assertEquals(
                Optional.of(Instant.parse("2026-10-02T19:00:00.123Z")), data.cancelledAt());
          }
          default -> {
            var data = (UserMutationResponseData) values.data();
            assertEquals(new UserId(1), data.userId());
            assertEquals(3, data.updatedVersion());
          }
        }
        f.erased();
      }
  }

  @Test
  void wire003CapabilitiesAreClosedBeforeTransport() {
    for (String type : TYPES) {
      var f = new Fixture();
      for (int group = 0; group < 5; group++)
        if (group != group(type)) {
          var facade = f.facade(group);
          rejected(
              ProtectedReadWireException.Reason.INVALID_INPUT,
              () -> facade.apply(input(type), CONTEXT));
        }
      assertTrue(f.sent.isEmpty());
    }
  }

  @Test
  void wire004NullConfigurationAndInputNeverBecomeValidWork() {
    for (int group = 0; group < 5; group++) {
      var f = new Fixture();
      int selected = group;
      assertThrows(
          NullPointerException.class,
          () -> facade(selected, null, f.sender, CLOCK, () -> ID, WAIT));
      assertThrows(
          NullPointerException.class, () -> facade(selected, f.wire, null, CLOCK, () -> ID, WAIT));
      assertThrows(
          NullPointerException.class,
          () -> facade(selected, f.wire, f.sender, null, () -> ID, WAIT));
      assertThrows(
          NullPointerException.class, () -> facade(selected, f.wire, f.sender, CLOCK, null, WAIT));
      assertThrows(
          NullPointerException.class,
          () -> facade(selected, f.wire, f.sender, CLOCK, () -> ID, null));
      for (Duration bad : List.of(Duration.ZERO, Duration.ofNanos(-1), WAIT.plusNanos(1)))
        assertThrows(
            IllegalArgumentException.class,
            () -> facade(selected, f.wire, f.sender, CLOCK, () -> ID, bad));
      var client = f.facade(group);
      assertThrows(NullPointerException.class, () -> client.apply(null, CONTEXT));
      String type = List.of("QSB", "NTS", "USR", "LOG", "AUD").get(group);
      assertThrows(NullPointerException.class, () -> client.apply(input(type), null));
      assertTrue(f.sent.isEmpty());
    }
  }

  @Test
  void wire005AcceptanceRejectsWrongKindContextGenerationAndFiller() {
    var changes =
        List.<Consumer<byte[]>>of(
            b -> b[23] = 'S',
            b -> b[22] = 'Q',
            b -> put(b, 60, 36, new UUID(0, 9).toString()),
            b -> put(b, 113, 64, "b".repeat(64)),
            b -> put(b, 181, 6, "000063"),
            b -> put(b, 256, 26, "I".repeat(26)),
            b -> b[311] = 'x');
    for (var change : changes) {
      var f = new Fixture();
      f.reply =
          (id, body) -> {
            var result = response("QSB", "0000", id, CONTEXT.wireValue());
            change.accept(result);
            return result;
          };
      rejected(
          ProtectedReadWireException.Reason.INVALID_RESPONSE,
          () -> f.facade(0).apply(input("QSB"), CONTEXT));
      f.erased();
    }
    var f = new Fixture();
    f.reply = (id, body) -> response("LOG", "0000", id, CONTEXT.wireValue());
    rejected(
        ProtectedReadWireException.Reason.INVALID_RESPONSE,
        () -> f.facade(0).apply(input("QSB"), CONTEXT));
    f.erased();
  }

  @Test
  void wire006ErrorsTimeoutAndUnknownFailuresNeverRetry() {
    var wrongFiller = new Fixture();
    wrongFiller.reply =
        (id, body) -> {
          var result = response("NTD", "9000", id, CONTEXT.wireValue());
          result[403] = '0';
          return result;
        };
    rejected(
        ProtectedReadWireException.Reason.INVALID_RESPONSE,
        () -> wrongFiller.facade(1).apply(input("NTD"), CONTEXT));
    wrongFiller.erased();
    for (String type : TYPES) {
      for (String code : List.of("0100", "0102", "0103", "0104", "0105", "9000", "9001")) {
        var f = new Fixture();
        f.reply = (id, body) -> response(type, code, id, CONTEXT.wireValue());
        var result = f.facade(group(type)).apply(input(type), CONTEXT);
        assertEquals(code, result.resultCode().wireValue());
        assertTrue(result.payload().isEmpty());
        f.erased();
      }
      var f = new Fixture();
      var timeout =
          facade(
              group(type),
              f.wire,
              (id, body) -> f.sent.add(body),
              CLOCK,
              () -> ID,
              Duration.ofNanos(1));
      rejected(
          ProtectedReadWireException.Reason.UNAVAILABLE, () -> timeout.apply(input(type), CONTEXT));
      assertEquals(1, f.sent.size());
      f.erased();
      var error = new AssertionError("private");
      var unknown =
          facade(
              group(type),
              f.wire,
              (id, body) -> {
                f.sent.add(body);
                throw error;
              },
              CLOCK,
              () -> ID,
              WAIT);
      assertSame(
          error, assertThrows(AssertionError.class, () -> unknown.apply(input(type), CONTEXT)));
      f.erased();
      var checked =
          facade(
              group(type),
              f.wire,
              (id, body) -> {
                f.sent.add(body);
                throw new JMSException("private");
              },
              CLOCK,
              () -> ID,
              WAIT);
      rejected(
          ProtectedReadWireException.Reason.UNAVAILABLE, () -> checked.apply(input(type), CONTEXT));
      f.erased();
    }
  }

  @Test
  void wire007RetriesUseNewMessageIdsAndRetainOperationTokenOnly() {
    var f = new Fixture();
    var ids = new AtomicLong();
    var seen = new HashSet<UUID>();
    f.reply =
        (id, body) -> {
          assertTrue(seen.add(id));
          assertEquals(TOKEN.toString(), new String(body, 4352, 36, StandardCharsets.US_ASCII));
          return response("QSB", "0200", id, CONTEXT.wireValue());
        };
    var client = facade(0, f.wire, f.sender, CLOCK, () -> new UUID(0, ids.incrementAndGet()), WAIT);
    for (int n = 0; n < 3; n++)
      assertEquals(ResultCode.IDEMPOTENT_SUCCESS, client.apply(input("QSB"), CONTEXT).resultCode());
    assertEquals(3, seen.size());
    f.erased();
  }

  @Test
  void wire008ConcurrentFacadesKeepRepliesAndContextsSeparate() throws Exception {
    var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    var ids = new AtomicLong();
    var seen = ConcurrentHashMap.<UUID>newKeySet();
    var sent = new CopyOnWriteArrayList<byte[]>();
    JmsRequestSender sender =
        (id, body) -> {
          String type = new String(body, 11, 3, StandardCharsets.US_ASCII);
          String context = new String(body, 113, 64, StandardCharsets.US_ASCII);
          assertArrayEquals(request(type, id, context), body);
          assertTrue(seen.add(id));
          sent.add(body);
          assertTrue(wire.onReply(id, response(type, "9000", id, context)));
        };
    try (var pool = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int n = 0; n < 180; n++) {
        int item = n;
        tasks.add(
            pool.submit(
                () -> {
                  String type = TYPES[item % 18];
                  var client =
                      facade(
                          group(type),
                          wire,
                          sender,
                          CLOCK,
                          () -> new UUID(0, ids.incrementAndGet()),
                          WAIT);
                  var context =
                      AuthenticationContext.of(String.format(Locale.ROOT, "%064x", item + 1));
                  assertEquals("9000", client.apply(input(type), context).resultCode().wireValue());
                  return null;
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
    }
    assertEquals(180, seen.size());
    assertEquals(0, wire.pendingCount());
    sent.forEach(b -> assertArrayEquals(new byte[b.length], b));
  }

  private static int index(String type) {
    return Arrays.asList(TYPES).indexOf(type);
  }

  private static int group(String type) {
    int i = index(type);
    return i < 4 ? 0 : i < 7 ? 1 : i < 14 ? 2 : i == 14 ? 3 : 4;
  }

  private static BiFunction<
          TypedPayloadValues, AuthenticationContext, ProtectedReadWireClient.Result>
      facade(
          int group,
          JmsRequestReplyClient client,
          JmsRequestSender sender,
          Clock clock,
          Supplier<UUID> ids,
          Duration wait) {
    return switch (group) {
      case 0 -> new QuestionWireClient(client, sender, clock, ids, wait)::exchange;
      case 1 -> new NotificationWireClient(client, sender, clock, ids, wait)::exchange;
      case 2 -> new UserAdministrationWireClient(client, sender, clock, ids, wait)::exchange;
      case 3 -> new LogoutWireClient(client, sender, clock, ids, wait)::exchange;
      case 4 -> new MediaDescriptorWireClient(client, sender, clock, ids, wait)::exchange;
      default -> throw new AssertionError("fixture group");
    };
  }

  private static TypedPayloadValues input(String type) {
    PayloadData data =
        switch (type) {
          case "QSB" -> new QuestionSubmitRequestData("質問é", TOKEN);
          case "QSS" ->
              new QuestionSearchRequestData(
                  Optional.empty(),
                  Optional.empty(),
                  Optional.empty(),
                  Optional.empty(),
                  Optional.empty(),
                  1,
                  50);
          case "QSD" -> new QuestionDetailRequestData(new QuestionId(1));
          case "QDL" -> new QuestionDeleteRequestData(new QuestionId(1), TOKEN);
          case "NTS" ->
              new NotificationSearchRequestData(
                  Optional.empty(), Optional.empty(), Optional.empty(), 1, 50);
          case "NTD" -> new NotificationDetailRequestData(new NotificationId(1));
          case "NTC" -> new NotificationCancelRequestData(new NotificationId(1), TOKEN);
          case "USR" ->
              new UserSearchRequestData(
                  Optional.empty(), Optional.empty(), Optional.empty(), 1, 50);
          case "UDT" -> new UserDetailRequestData(new UserId(1));
          case "UCR" ->
              new UserCreateRequestData("user1", "TestPassword123!", UserRole.USER, true, TOKEN);
          case "UST" -> new UserStatusRequestData(new UserId(1), false, 3, TOKEN);
          case "URL" -> new UserRoleRequestData(new UserId(1), UserRole.ADMIN, 3, TOKEN);
          case "UPW" -> new PasswordResetRequestData(new UserId(1), "NewPassword123!", 3, TOKEN);
          case "ULK" -> new UserUnlockRequestData(new UserId(1), 3, TOKEN);
          case "LOG" -> new LogoutRequestData();
          case "AUD" -> new AudioDescriptorRequestData(new AudioId(1), ContentDisposition.INLINE);
          case "VID" -> new VideoDescriptorRequestData("opening");
          case "MED" -> new MusicDescriptorRequestData("track1", ContentDisposition.ATTACHMENT);
          default -> throw new AssertionError("fixture type");
        };
    return new TypedPayloadValues(new LayoutId(type + "REQ01"), data, List.of());
  }

  // Independent UI offsets/widths, no Production codec/catalog used for expected bytes.
  private static byte[] request(String type, UUID id, String context) {
    var b = header(type, true, "", id, context);
    switch (type) {
      case "QSB" -> {
        put(b, 256, 4096, "質問é");
        put(b, 4352, 36, TOKEN.toString());
      }
      case "QSS" -> {
        number(b, 622, 6, 1);
        number(b, 628, 3, 50);
      }
      case "NTS" -> {
        number(b, 302, 6, 1);
        number(b, 308, 3, 50);
      }
      case "USR" -> {
        number(b, 333, 6, 1);
        number(b, 339, 3, 50);
      }
      case "QSD", "NTD", "UDT" -> number(b, 256, 12, 1);
      case "QDL", "NTC" -> {
        number(b, 256, 12, 1);
        put(b, 268, 36, TOKEN.toString());
      }
      case "UCR" -> {
        put(b, 256, 64, "user1");
        put(b, 320, 256, "TestPassword123!");
        put(b, 576, 5, "USER");
        b[581] = '1';
        put(b, 582, 36, TOKEN.toString());
      }
      case "UST" -> {
        number(b, 256, 12, 1);
        b[268] = '0';
        number(b, 269, 9, 3);
        put(b, 278, 36, TOKEN.toString());
      }
      case "URL" -> {
        number(b, 256, 12, 1);
        put(b, 268, 5, "ADMIN");
        number(b, 273, 9, 3);
        put(b, 282, 36, TOKEN.toString());
      }
      case "UPW" -> {
        number(b, 256, 12, 1);
        put(b, 268, 256, "NewPassword123!");
        number(b, 524, 9, 3);
        put(b, 533, 36, TOKEN.toString());
      }
      case "ULK" -> {
        number(b, 256, 12, 1);
        number(b, 268, 9, 3);
        put(b, 277, 36, TOKEN.toString());
      }
      case "AUD" -> {
        number(b, 256, 12, 1);
        b[268] = 'I';
      }
      case "VID" -> put(b, 256, 64, "opening");
      case "MED" -> {
        put(b, 256, 64, "track1");
        b[320] = 'A';
      }
      case "LOG" -> {}
      default -> throw new AssertionError("fixture type");
    }
    return b;
  }

  private static byte[] response(String type, String code, UUID id, String context) {
    var b = header(type, false, code, id, context);
    boolean ok = code.equals("0000") || code.equals("0200");
    switch (type) {
      case "QSB" -> {
        put(b, 256, 26, ok ? RECEIPT : "");
        number(b, 282, 12, ok ? 1 : 0);
        put(b, 294, 17, ok ? "20261003040000123" : "0".repeat(17));
      }
      case "QDL", "LOG" -> put(b, 256, 17, ok ? "20261003040000123" : "0".repeat(17));
      case "NTC" -> {
        put(b, 256, 12, ok ? "CANCELLED" : "");
        put(b, 268, 17, ok ? "20261003040000123" : "");
      }
      case "UCR", "UST", "URL", "UPW", "ULK" -> {
        number(b, 256, 12, ok ? 1 : 0);
        number(b, 268, 9, ok ? 3 : 0);
      }
      case "QSS", "NTS", "USR" -> {
        for (int[] field : new int[][] {{0, 6}, {6, 3}, {9, 9}, {18, 6}, {24, 9}, {33, 9}})
          number(b, 256 + field[0], field[1], 0);
      }
      case "QSD" -> {
        number(b, 256, 12, 0);
        number(b, 8562, 17, 0);
      }
      case "NTD" -> {
        number(b, 256, 12, 0);
        number(b, 318, 17, 0);
      }
      case "UDT" -> {
        number(b, 256, 12, 0);
        number(b, 379, 17, 0);
        number(b, 396, 17, 0);
        number(b, 413, 17, 0);
        number(b, 430, 3, 0);
        number(b, 433, 9, 0);
      }
      case "AUD", "VID", "MED" -> number(b, 1088, 12, 0);
      default -> throw new AssertionError("fixture type");
    }
    return b;
  }

  private static byte[] header(String type, boolean request, String code, UUID id, String context) {
    int i = index(type);
    int data = request ? REQUEST[i] : RESPONSE[i];
    int record = request ? 0 : RECORD[i];
    var b = new byte[256 + data];
    Arrays.fill(b, (byte) ' ');
    put(b, 0, 8, "SCHBNK01");
    put(b, 8, 3, "001");
    put(b, 11, 8, type + (request ? "REQ01" : "RSP01"));
    put(b, 19, 3, "001");
    b[22] = (byte) (request ? 'Q' : 'S');
    b[23] = (byte) (type.equals("QSB") ? 'A' : 'S');
    put(b, 24, 36, (request ? id : new UUID(1, id.getLeastSignificantBits())).toString());
    put(b, 60, 36, id.toString());
    put(b, 96, 17, "20261003040000123");
    put(b, 113, 64, context);
    number(b, 177, 4, 256);
    number(b, 181, 6, data);
    number(b, 187, 6, record);
    number(b, 193, 6, 0);
    number(b, 199, 9, b.length);
    put(b, 208, 4, code);
    return b;
  }

  private static void put(byte[] b, int at, int length, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    assertTrue(bytes.length <= length);
    Arrays.fill(b, at, at + length, (byte) ' ');
    System.arraycopy(bytes, 0, b, at, bytes.length);
  }

  private static void number(byte[] b, int at, int length, long value) {
    put(b, at, length, String.format(Locale.ROOT, "%0" + length + "d", value));
  }

  private static void rejected(
      ProtectedReadWireException.Reason reason, org.junit.jupiter.api.function.Executable action) {
    var e = assertThrows(ProtectedReadWireException.class, action);
    assertEquals(reason, e.reason());
    assertEquals("protected read exchange rejected", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static final class Fixture {
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final List<byte[]> sent = new ArrayList<>();
    BiFunction<UUID, byte[], byte[]> reply =
        (id, b) -> response("QSB", "0000", id, CONTEXT.wireValue());
    final JmsRequestSender sender =
        (id, b) -> {
          sent.add(b);
          assertTrue(wire.onReply(id, reply.apply(id, b)));
        };

    BiFunction<TypedPayloadValues, AuthenticationContext, ProtectedReadWireClient.Result> facade(
        int group) {
      return WebBusinessWireClientsTest.facade(group, wire, sender, CLOCK, () -> ID, WAIT);
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      sent.forEach(b -> assertArrayEquals(new byte[b.length], b));
    }
  }
}
