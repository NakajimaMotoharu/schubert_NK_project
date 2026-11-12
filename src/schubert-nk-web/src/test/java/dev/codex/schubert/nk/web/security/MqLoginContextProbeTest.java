package dev.codex.schubert.nk.web.security;

import static dev.codex.schubert.nk.web.security.MqLoginClientTest.header;
import static dev.codex.schubert.nk.web.security.MqLoginClientTest.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
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
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** UI232/234 independent IF-003 vectors; SSC-043/PG-D-102/PT-WEB-060..062. */
final class MqLoginContextProbeTest {
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_SYNTHETIC_SECRET_BCCB0977 = "synthetic-secret";
  static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-08T00:00:00.123456Z"), ZoneOffset.UTC);
  static final Duration WAIT = Duration.ofSeconds(2);
  private static final UUID ID = new UUID(0, 2);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));

  @Test
  void web060ProbeUsesFreshProtectedReadAndValidatesAllRecords() {
    for (String code : List.of(FIXTURE_0000_876EEFE0, "0200")) {
      for (int count : new int[] {0, 1, 10}) {
        JmsRequestReplyClient client = client();
        AtomicReference<byte[]> sent = new AtomicReference<>();
        var probe =
            probe(
                client,
                (id, body) -> {
                  assertEquals(ID, id);
                  assertNotEquals(new UUID(0, 1), id); // Initial Login uses a different ID.
                  byte[] expected = header("GAMREQ01", ID, 0, "", true);
                  put(expected, 113, "a".repeat(64));
                  assertArrayEquals(expected, body);
                  sent.set(body);
                  assertTrue(client.onReply(id, response(id, "a".repeat(64), code, count)));
                });
        assertTrue(probe.isActive(CONTEXT));
        assertArrayEquals(new byte[256], sent.get());
        assertEquals(0, client.pendingCount());
      }
    }
    assertFalse(receive(response(ID, "a".repeat(64), "0102", 0)));
  }

  @Test
  void web061ProbeRejectsMalformedAndFailedReplies() {
    byte[] valid = response(ID, "a".repeat(64), FIXTURE_0000_876EEFE0, 2);
    List<byte[]> bad = new ArrayList<>();
    bad.add(new byte[0]);
    bad.add(Arrays.copyOf(valid, 255));
    bad.add(Arrays.copyOf(valid, valid.length - 1));
    bad.add(Arrays.copyOf(valid, valid.length + 1));
    byte[] other = header("LOGRSP01", ID, 24, FIXTURE_0000_876EEFE0, false);
    put(other, 113, "a".repeat(64));
    bad.add(other);
    List<Consumer<byte[]>> mutations =
        List.of(
            b -> b[0] = 'X',
            b -> b[212] = 'X',
            b -> put(b, 60, new UUID(0, 99).toString()),
            b -> put(b, 113, "b".repeat(64)),
            b -> put(b, 193, "000011"),
            b -> put(b, 256, "000000001"),
            b -> put(b, 208, "9999"),
            b -> put(b, 265, "UNKNOWN     "),
            b -> Arrays.fill(b, 277, 533, (byte) ' '),
            b -> b[277] = (byte) 0xff,
            b -> b[536] = 'X',
            b -> put(b, 265 + 272 + 268, "000"));
    for (Consumer<byte[]> mutate : mutations) {
      byte[] candidate = valid.clone();
      mutate.accept(candidate);
      bad.add(candidate);
    }
    for (String code :
        List.of("0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001"))
      bad.add(response(ID, "a".repeat(64), code, 0));
    byte[] corruptInvalid = response(ID, "a".repeat(64), "0102", 0);
    put(corruptInvalid, 256, "000000001");
    bad.add(corruptInvalid);
    for (byte[] candidate : bad)
      fixed(assertThrows(MqLoginExchangeException.class, () -> receive(candidate)));
  }

  @Test
  void web062ProbeNullFaultsAndConcurrentCallsStayIsolated() throws Exception {
    JmsRequestReplyClient client = client();
    JmsRequestSender noSend = (id, body) -> fail("must not send");
    assertThrows(
        NullPointerException.class,
        () -> new MqLoginContextProbe(null, noSend, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new MqLoginContextProbe(client, null, CLOCK, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new MqLoginContextProbe(client, noSend, null, () -> ID, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new MqLoginContextProbe(client, noSend, CLOCK, null, WAIT));
    assertThrows(
        NullPointerException.class,
        () -> new MqLoginContextProbe(client, noSend, CLOCK, () -> ID, null));
    for (Duration invalid : List.of(Duration.ZERO, Duration.ofNanos(-1), WAIT.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MqLoginContextProbe(client, noSend, CLOCK, () -> ID, invalid));
    assertThrows(NullPointerException.class, () -> probe(client, noSend).isActive(null));
    assertThrows(
        NullPointerException.class,
        () -> new MqLoginContextProbe(client, noSend, CLOCK, () -> null, WAIT).isActive(CONTEXT));
    assertThrows(
        NullPointerException.class,
        () ->
            new MqLoginContextProbe(client, noSend, new FaultClock(null), () -> ID, WAIT)
                .isActive(CONTEXT));
    for (RuntimeException fault :
        List.of(
            new IllegalStateException("synthetic-clock"), new DateTimeException("synthetic-clock")))
      fixed(
          assertThrows(
              MqLoginExchangeException.class,
              () ->
                  new MqLoginContextProbe(client, noSend, new FaultClock(fault), () -> ID, WAIT)
                      .isActive(CONTEXT)));
    fixed(
        assertThrows(
            MqLoginExchangeException.class,
            () ->
                new MqLoginContextProbe(
                        client,
                        noSend,
                        CLOCK,
                        () -> {
                          throw new IllegalArgumentException("synthetic-id");
                        },
                        WAIT)
                    .isActive(CONTEXT)));
    for (int mode = 0; mode < 4; mode++) {
      int selected = mode;
      AtomicInteger sends = new AtomicInteger();
      AtomicReference<byte[]> owned = new AtomicReference<>();
      var probe =
          probe(
              client,
              (id, body) -> {
                sends.incrementAndGet();
                owned.set(body);
                switch (selected) {
                  case 0 -> throw new JMSException(FIXTURE_SYNTHETIC_SECRET_BCCB0977);
                  case 1 -> throw new JMSRuntimeException(FIXTURE_SYNTHETIC_SECRET_BCCB0977);
                  case 2 -> throw new IllegalStateException(FIXTURE_SYNTHETIC_SECRET_BCCB0977);
                  default -> throw new IllegalArgumentException(FIXTURE_SYNTHETIC_SECRET_BCCB0977);
                }
              });
      fixed(assertThrows(MqLoginExchangeException.class, () -> probe.isActive(CONTEXT)));
      assertEquals(1, sends.get());
      assertArrayEquals(new byte[256], owned.get());
      assertEquals(0, client.pendingCount());
    }
    AtomicInteger timedSends = new AtomicInteger();
    var timed =
        new MqLoginContextProbe(
            client,
            (id, body) -> timedSends.incrementAndGet(),
            CLOCK,
            () -> ID,
            Duration.ofNanos(1));
    fixed(assertThrows(MqLoginExchangeException.class, () -> timed.isActive(CONTEXT)));
    assertEquals(1, timedSends.get());
    assertEquals(0, client.pendingCount());
    try {
      Thread.currentThread().interrupt();
      fixed(
          assertThrows(
              MqLoginExchangeException.class,
              () -> probe(client, (id, body) -> {}).isActive(CONTEXT)));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    assertEquals(0, client.pendingCount());

    AtomicInteger ids = new AtomicInteger();
    AtomicInteger sends = new AtomicInteger();
    var concurrent =
        new MqLoginContextProbe(
            client,
            (id, body) -> {
              sends.incrementAndGet();
              String context =
                  new String(body, 113, 64, java.nio.charset.StandardCharsets.US_ASCII);
              assertTrue(client.onReply(id, response(id, context, FIXTURE_0000_876EEFE0, 1)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            WAIT);
    var workers = Executors.newFixedThreadPool(8);
    try {
      List<Future<?>> calls = new ArrayList<>();
      synchronized (concurrent) {
        for (int index = 0; index < 100; index++) {
          String context = String.format(Locale.ROOT, "%064x", index);
          calls.add(
              workers.submit(
                  () -> assertTrue(concurrent.isActive(AuthenticationContext.of(context)))));
        }
        for (Future<?> call : calls) call.get(10, TimeUnit.SECONDS);
      }
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(5, TimeUnit.SECONDS));
    }
    assertEquals(100, ids.get());
    assertEquals(100, sends.get());
    assertEquals(0, client.pendingCount());
  }

  private static boolean receive(byte[] response) {
    JmsRequestReplyClient client = client();
    AtomicInteger sends = new AtomicInteger();
    try {
      return probe(
              client,
              (id, b) -> {
                sends.incrementAndGet();
                assertTrue(client.onReply(id, response));
              })
          .isActive(CONTEXT);
    } finally {
      assertEquals(1, sends.get());
      assertEquals(0, client.pendingCount());
    }
  }

  static JmsRequestReplyClient client() {
    return new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
  }

  private static MqLoginContextProbe probe(JmsRequestReplyClient client, JmsRequestSender sender) {
    return new MqLoginContextProbe(client, sender, CLOCK, () -> ID, WAIT);
  }

  static void fixed(MqLoginExchangeException failure) {
    assertEquals(MqLoginExchangeException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("login exchange rejected", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  // UI234: nine-byte DATA,272-byte records, count0..10. Expected bytes independent of production.
  static byte[] response(UUID id, String context, String code, int count) {
    byte[] body = Arrays.copyOf(header("GAMRSP01", id, 9, code, false), 265 + 272 * count);
    Arrays.fill(body, 265, body.length, (byte) ' ');
    put(body, 113, context);
    put(body, 187, "000272");
    put(body, 193, String.format(Locale.ROOT, "%06d", count));
    put(body, 199, String.format(Locale.ROOT, "%09d", body.length));
    put(body, 256, String.format(Locale.ROOT, "%09d", count));
    for (int i = 0; i < count; i++) {
      put(body, 265 + 272 * i, "NUKITASHI1");
      put(body, 277 + 272 * i, "合成title");
      put(body, 533 + 272 * i, String.format(Locale.ROOT, "%03d", i + 1));
    }
    return body;
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
