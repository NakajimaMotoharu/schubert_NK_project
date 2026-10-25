package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
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
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** Independent UI232/234 byte vectors; PG-D-101/PT-WEB-054..059. No production oracle. */
final class MqLoginClientTest {
  private static final UUID ID = new UUID(0, 1);
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);
  private static final Duration WAIT = Duration.ofSeconds(2);

  @Test
  void web054RequestAndSuccessMatchIndependentWire() {
    String[][] inputs = {
      {" Alice ", "p", "127.0.0.1", "Alice", "p", "USER"},
      {" A\u0301 ", "e\u0301", "2001:db8::1", "Á", "é", "ADMIN"},
      {"İ".repeat(32), "x".repeat(256), "::1", "İ".repeat(32), "x".repeat(256), "USER"},
      {"A".repeat(64), "é".repeat(128), "255.255.255.255", "A".repeat(64), "é".repeat(128), "ADMIN"}
    };
    for (String[] input : inputs) {
      JmsRequestReplyClient client = client();
      AtomicReference<byte[]> handed = new AtomicReference<>();
      MqLoginClient service =
          service(
              client,
              (id, wire) -> {
                assertEquals(ID, id);
                assertArrayEquals(request(id, input[3], input[4], input[2]), wire);
                handed.set(wire);
                assertTrue(client.onReply(id, success(id, input[3], input[5], "a".repeat(64))));
              });
      char[] password = input[1].toCharArray();
      MqLoginClient.Reply result = service.exchange(input[0], password, input[2]);
      assertEquals(ResultCode.SUCCESS, result.code());
      assertEquals(input[3], result.data().username().orElseThrow());
      assertEquals(UserRole.valueOf(input[5]), result.data().role().orElseThrow());
      assertEquals(
          "a".repeat(64), result.data().authenticationContextId().orElseThrow().wireValue());
      assertEquals(
          Instant.parse("2026-09-08T00:00:00.123Z"), result.data().issuedAt().orElseThrow());
      assertEquals(
          Instant.parse("2026-09-08T08:00:00.123Z"), result.data().expiresAt().orElseThrow());
      assertEquals(0, result.data().retryAfterSeconds());
      assertEquals(0, result.data().remainingAttempts());
      assertTrue(result.data().userMessage().isEmpty());
      assertEquals("LoginReply[REDACTED]", result.toString());
      assertEquals("LoginResponseData[REDACTED]", result.data().toString());
      assertArrayEquals(new char[password.length], password);
      assertArrayEquals(new byte[640], handed.get());
      assertEquals(0, client.pendingCount());
    }
    assertEquals(
        "ALICE",
        reply(success(ID, "ALICE", "USER", "b".repeat(64)), "alice")
            .data()
            .username()
            .orElseThrow());
    byte[] replay = success(ID, "alice", "ADMIN", "d".repeat(64));
    put(replay, 208, "0200");
    MqLoginClient.Reply replayed = reply(replay, "alice");
    assertEquals(ResultCode.IDEMPOTENT_SUCCESS, replayed.code());
    assertEquals(UserRole.ADMIN, replayed.data().role().orElseThrow());
    assertEquals(
        Instant.parse("2026-09-08T00:00:00.123Z"), replayed.data().issuedAt().orElseThrow());
    assertEquals(
        "d".repeat(64), replayed.data().authenticationContextId().orElseThrow().wireValue());
  }

  @Test
  void web055ErrorProfilesRemainDistinct() {
    for (String code : List.of("0101", "0106", "9000")) {
      for (String message : List.of("", "現在処理できません。", "é".repeat(128))) {
        int retry = code.equals("0106") ? 900 : 0;
        MqLoginClient.Reply result = reply(error(ID, code, retry, message), "alice");
        assertEquals(code, result.code().wireValue());
        assertEquals(retry, result.data().retryAfterSeconds());
        assertEquals(0, result.data().remainingAttempts());
        assertEquals(message, result.data().userMessage().orElse(""));
        assertTrue(result.data().username().isEmpty());
        assertTrue(result.data().role().isEmpty());
        assertTrue(result.data().authenticationContextId().isEmpty());
        assertTrue(result.data().issuedAt().isEmpty());
        assertTrue(result.data().expiresAt().isEmpty());
      }
    }
    assertEquals(0, reply(error(ID, "0106", 0, ""), "alice").data().retryAfterSeconds());
  }

  @Test
  void web056InputAndNullContractsNeverSendSecrets() {
    JmsRequestReplyClient client = client();
    AtomicInteger sent = new AtomicInteger();
    JmsRequestSender sender = (id, body) -> sent.incrementAndGet();
    MqLoginClient service = service(client, sender);
    assertThrows(
        NullPointerException.class, () -> new MqLoginClient(null, sender, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class, () -> new MqLoginClient(client, null, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class, () -> new MqLoginClient(client, sender, null, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class, () -> new MqLoginClient(client, sender, CLOCK, null, WAIT));
    assertThrows(
        NullPointerException.class, () -> new MqLoginClient(client, sender, CLOCK, () -> ID, null));
    for (Duration bad : List.of(Duration.ZERO, Duration.ofNanos(-1), WAIT.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MqLoginClient(client, sender, CLOCK, () -> ID, bad));
    assertThrows(NullPointerException.class, () -> new MqLoginExchangeException(null));
    assertThrows(NullPointerException.class, () -> service.exchange("alice", null, "::1"));
    for (boolean nullUsername : List.of(true, false)) {
      char[] secret = "synthetic".toCharArray();
      assertThrows(
          NullPointerException.class,
          () ->
              service.exchange(nullUsername ? null : "alice", secret, nullUsername ? "::1" : null));
      assertArrayEquals(new char[secret.length], secret);
    }
    for (String username :
        List.of("", " ", "\u2003", "x".repeat(65), "é".repeat(33), "a\u0000b", "\ud800", "\udc00"))
      invalid(service, username, "p", "::1");
    for (String password :
        List.of("", "p ", "p\n", "\ud800", "\udc00", "x".repeat(257), "é".repeat(129)))
      invalid(service, "alice", password, "::1");
    for (String address :
        List.of(
            "",
            "localhost",
            "example.invalid",
            "1.2.3.999",
            "127.0.0.1:80",
            "::xyz",
            "fe80::1%1",
            "[fe80::1%1]")) invalid(service, "alice", "p", address);
    assertEquals(0, sent.get());
    assertEquals(0, client.pendingCount());
    MqLoginExchangeException fixed =
        new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);
    fixed.addSuppressed(new IllegalArgumentException("synthetic-sensitive"));
    assertEquals(0, fixed.getSuppressed().length);
    assertThrows(
        IllegalStateException.class,
        () -> fixed.initCause(new IllegalStateException("synthetic-sensitive")));
  }

  @Test
  void web057MalformedOrUncorrelatedRepliesNeverAuthenticate() {
    byte[] valid = success(ID, "alice", "USER", "a".repeat(64));
    List<byte[]> bad = new ArrayList<>();
    bad.add(new byte[0]);
    bad.add(Arrays.copyOf(valid, 255));
    bad.add(Arrays.copyOf(valid, 687));
    bad.add(Arrays.copyOf(valid, 689));
    bad.add(header("LOGRSP01", ID, 24, "0000", false));
    // LOGRSP has a required header context; valid unrelated layout must still be rejected.
    put(bad.getLast(), 113, "b".repeat(64));
    List<Consumer<byte[]>> mutations =
        List.of(
            b -> b[0] = 'X',
            b -> b[22] = 'Q',
            b -> b[23] = 'A',
            b -> b[212] = 'X',
            b -> put(b, 60, new UUID(0, 2).toString()),
            b -> put(b, 208, "9999"),
            b -> put(b, 113, "a".repeat(64)),
            b -> put(b, 256 + 64, "ROOT "),
            b -> b[256 + 69] = 'Z',
            b -> b[256] = (byte) 0xff,
            b -> Arrays.fill(b, 256, 320, (byte) ' '),
            b -> Arrays.fill(b, 256 + 64, 256 + 69, (byte) ' '),
            b -> Arrays.fill(b, 256 + 69, 256 + 133, (byte) ' '),
            b -> Arrays.fill(b, 256 + 133, 256 + 150, (byte) ' '),
            b -> Arrays.fill(b, 256 + 150, 256 + 167, (byte) ' '),
            b -> put(b, 256 + 150, "20260908090000123"),
            b -> put(b, 256 + 167, "000001"),
            b -> put(b, 256 + 173, "001"),
            b -> b[256 + 176] = 'X',
            b -> put(b, 256, "other"));
    for (Consumer<byte[]> mutation : mutations) {
      byte[] candidate = valid.clone();
      mutation.accept(candidate);
      bad.add(candidate);
    }
    for (String code : List.of("0100", "0102", "0103", "0104", "0105", "0107", "9001")) {
      byte[] candidate = valid.clone();
      put(candidate, 208, code);
      bad.add(candidate);
    }
    byte[] leakingError = error(ID, "0101", 0, "");
    put(leakingError, 256 + 69, "a".repeat(64));
    bad.add(leakingError);
    bad.add(error(ID, "0101", 1, ""));
    bad.add(error(ID, "0106", 901, ""));
    byte[] invalidReplay = error(ID, "0200", 0, "");
    bad.add(invalidReplay);
    byte[] wrongReplayUser = success(ID, "other", "USER", "a".repeat(64));
    put(wrongReplayUser, 208, "0200");
    bad.add(wrongReplayUser);
    for (byte[] candidate : bad) {
      MqLoginExchangeException failure =
          assertThrows(MqLoginExchangeException.class, () -> reply(candidate, "alice"));
      fixed(failure, MqLoginExchangeException.Reason.UNAVAILABLE);
    }
  }

  @Test
  void web058TransportFaultsDoNotBecomeBadCredentials() throws Exception {
    for (int mode = 0; mode < 4; mode++) {
      int selected = mode;
      JmsRequestReplyClient client = client();
      AtomicReference<byte[]> handed = new AtomicReference<>();
      AtomicInteger sends = new AtomicInteger();
      MqLoginClient service =
          service(
              client,
              (id, bytes) -> {
                handed.set(bytes);
                sends.incrementAndGet();
                switch (selected) {
                  case 0 -> throw new JMSException("synthetic-sensitive");
                  case 1 -> throw new JMSRuntimeException("synthetic-sensitive");
                  case 2 -> throw new IllegalStateException("synthetic-sensitive");
                  default -> throw new IllegalArgumentException("synthetic-sensitive");
                }
              });
      unavailable(service);
      assertEquals(1, sends.get());
      assertArrayEquals(new byte[640], handed.get());
      assertEquals(0, client.pendingCount());
    }
    JmsRequestReplyClient timed = client();
    AtomicInteger sends = new AtomicInteger();
    unavailable(
        new MqLoginClient(
            timed, (id, b) -> sends.incrementAndGet(), CLOCK, () -> ID, Duration.ofNanos(1)));
    assertEquals(1, sends.get());
    assertEquals(0, timed.pendingCount());
    assertFalse(timed.onReply(ID, error(ID, "9000", 0, "")));
    assertEquals(1, timed.lateReplyCount());
    try {
      Thread.currentThread().interrupt();
      unavailable(service(timed, (id, b) -> {}));
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(0, timed.pendingCount());
    } finally {
      Thread.interrupted();
    }
    for (RuntimeException failure :
        List.of(
            new IllegalStateException("clock-sensitive"),
            new DateTimeException("clock-sensitive"))) {
      unavailable(
          new MqLoginClient(
              client(), (id, b) -> fail("must not send"), new FaultClock(failure), () -> ID, WAIT));
    }
    unavailable(
        new MqLoginClient(
            client(),
            (id, b) -> fail("must not send"),
            CLOCK,
            () -> {
              throw new IllegalStateException("uuid-sensitive");
            },
            WAIT));
    char[] password = {'p'};
    assertThrows(
        NullPointerException.class,
        () ->
            new MqLoginClient(client(), (id, b) -> fail("must not send"), CLOCK, () -> null, WAIT)
                .exchange("alice", password, "::1"));
    assertArrayEquals(new char[1], password);
    char[] nullClockPassword = {'p'};
    assertThrows(
        NullPointerException.class,
        () ->
            new MqLoginClient(
                    client(),
                    (id, b) -> fail("must not send"),
                    new FaultClock(null),
                    () -> ID,
                    WAIT)
                .exchange("alice", nullClockPassword, "::1"));
    assertArrayEquals(new char[1], nullClockPassword);

    JmsRequestReplyClient bounded =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
    CountDownLatch sent = new CountDownLatch(1);
    CountDownLatch release = new CountDownLatch(1);
    try (var workers = Executors.newVirtualThreadPerTaskExecutor()) {
      Future<MqLoginClient.Reply> first =
          workers.submit(
              () ->
                  service(
                          bounded,
                          (id, b) -> {
                            sent.countDown();
                            try {
                              assertTrue(release.await(5, TimeUnit.SECONDS));
                            } catch (InterruptedException e) {
                              Thread.currentThread().interrupt();
                              throw new IllegalStateException(e);
                            }
                            assertTrue(
                                bounded.onReply(id, success(id, "alice", "USER", "a".repeat(64))));
                          })
                      .exchange("alice", new char[] {'p'}, "::1"));
      try {
        assertTrue(sent.await(5, TimeUnit.SECONDS));
        unavailable(
            new MqLoginClient(
                bounded,
                (id, b) -> fail("capacity must not send"),
                CLOCK,
                () -> new UUID(0, 2),
                WAIT));
      } finally {
        release.countDown();
      }
      assertEquals(ResultCode.SUCCESS, first.get(5, TimeUnit.SECONDS).code());
      assertEquals(0, bounded.pendingCount());
    }
  }

  @Test
  void web059ConcurrentLoginsKeepIdentityAndOwnership() throws Exception {
    AtomicInteger ids = new AtomicInteger();
    JmsRequestReplyClient client = client();
    AtomicInteger sends = new AtomicInteger();
    List<byte[]> buffers = java.util.Collections.synchronizedList(new ArrayList<>());
    MqLoginClient service =
        new MqLoginClient(
            client,
            (id, body) -> {
              sends.incrementAndGet();
              buffers.add(body);
              String username = new String(body, 256, 64, StandardCharsets.UTF_8).stripTrailing();
              assertEquals(id.toString(), new String(body, 60, 36, StandardCharsets.US_ASCII));
              assertTrue(client.onReply(id, success(id, username, "USER", "c".repeat(64))));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            WAIT);
    try (var workers = Executors.newFixedThreadPool(8)) {
      List<Future<?>> results = new ArrayList<>();
      synchronized (service) {
        for (int index = 0; index < 100; index++) {
          String name = "user" + index;
          results.add(
              workers.submit(
                  () -> {
                    char[] password = {'p'};
                    MqLoginClient.Reply result = service.exchange(name, password, "::1");
                    assertEquals(name, result.data().username().orElseThrow());
                    assertEquals(UserRole.USER, result.data().role().orElseThrow());
                    assertEquals(
                        "c".repeat(64),
                        result.data().authenticationContextId().orElseThrow().wireValue());
                    assertArrayEquals(new char[1], password);
                  }));
        }
        for (Future<?> result : results) result.get(10, TimeUnit.SECONDS);
      }
    }
    assertEquals(100, sends.get());
    assertEquals(100, ids.get());
    assertEquals(0, client.pendingCount());
    assertEquals(0, client.lateReplyCount());
    for (byte[] buffer : buffers) assertArrayEquals(new byte[640], buffer);
  }

  private static void invalid(
      MqLoginClient service, String username, String password, String address) {
    char[] consumed = password.toCharArray();
    fixed(
        assertThrows(
            MqLoginExchangeException.class, () -> service.exchange(username, consumed, address)),
        MqLoginExchangeException.Reason.INVALID_INPUT);
    assertArrayEquals(new char[consumed.length], consumed);
  }

  private static void unavailable(MqLoginClient service) {
    char[] consumed = {'p'};
    fixed(
        assertThrows(
            MqLoginExchangeException.class, () -> service.exchange("alice", consumed, "::1")),
        MqLoginExchangeException.Reason.UNAVAILABLE);
    assertArrayEquals(new char[1], consumed);
  }

  private static void fixed(
      MqLoginExchangeException failure, MqLoginExchangeException.Reason reason) {
    assertEquals(reason, failure.reason());
    assertEquals("login exchange rejected", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static JmsRequestReplyClient client() {
    return new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
  }

  private static MqLoginClient service(JmsRequestReplyClient client, JmsRequestSender sender) {
    return new MqLoginClient(client, sender, CLOCK, () -> ID, WAIT);
  }

  private static MqLoginClient.Reply reply(byte[] body, String username) {
    JmsRequestReplyClient client = client();
    AtomicInteger sent = new AtomicInteger();
    try {
      return service(
              client,
              (id, bytes) -> {
                sent.incrementAndGet();
                assertTrue(client.onReply(id, body));
              })
          .exchange(username, new char[] {'p'}, "::1");
    } finally {
      assertEquals(1, sent.get());
      assertEquals(0, client.pendingCount());
    }
  }

  private static byte[] request(UUID id, String username, String password, String address) {
    byte[] body = header("LGNREQ01", id, 384, "", true);
    put(body, 256, username);
    put(body, 320, password);
    put(body, 576, address);
    return body;
  }

  static byte[] success(UUID id, String username, String role, String context) {
    byte[] body = header("LGNRSP01", id, 432, "0000", false);
    put(body, 256, username);
    put(body, 320, role);
    put(body, 325, context);
    put(body, 389, "20260908090000123");
    put(body, 406, "20260908170000123");
    put(body, 423, "000000000");
    return body;
  }

  static byte[] error(UUID id, String code, int retry, String message) {
    byte[] body = header("LGNRSP01", id, 432, code, false);
    put(body, 423, String.format(java.util.Locale.ROOT, "%06d000", retry));
    put(body, 432, message);
    return body;
  }

  // Literal UI232 offsets; header/data expected lengths are not obtained from production metadata.
  static byte[] header(String layout, UUID id, int dataLength, String code, boolean request) {
    byte[] body = new byte[256 + dataLength];
    Arrays.fill(body, (byte) ' ');
    put(body, 0, "SCHBNK01001" + layout + "001" + (request ? "QS" : "SS"));
    put(body, 24, (request ? id : new UUID(1, 9)).toString());
    put(body, 60, id.toString());
    put(body, 96, "20260908090000123");
    put(
        body,
        177,
        String.format(java.util.Locale.ROOT, "0256%06d000000000000%09d", dataLength, body.length));
    put(body, 208, code);
    return body;
  }

  static void put(byte[] body, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, body, offset, bytes.length);
  }

  private static final class FaultClock extends Clock {
    private final RuntimeException failure;

    FaultClock(RuntimeException failure) {
      this.failure = failure;
    }

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
      if (failure != null) throw failure;
      return null;
    }
  }
}
