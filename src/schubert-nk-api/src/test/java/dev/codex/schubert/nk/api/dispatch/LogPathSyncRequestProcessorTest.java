package dev.codex.schubert.nk.api.dispatch;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PG232/PT-JMS-017: closed Log-path layout registration, independent dispatch markers. */
final class LogPathSyncRequestProcessorTest {
  private static final String FIXTURE_LGNREQ01_217C66A4 = "LGNREQ01";
  private static final byte[] LOGIN_REPLY = "login-reply".getBytes(StandardCharsets.US_ASCII);
  private static final byte[] GAME_REPLY = "game-reply".getBytes(StandardCharsets.US_ASCII);
  private static final byte[] LOG_REPLY = "log-reply".getBytes(StandardCharsets.US_ASCII);

  @Test
  void exactThreeLayoutsReachOnlyTheirRegisteredProcessor() {
    var login = new AtomicInteger();
    var game = new AtomicInteger();
    var logs = new AtomicInteger();
    var router =
        new LogPathSyncRequestProcessor(
            ignored -> {
              login.incrementAndGet();
              return LOGIN_REPLY;
            },
            ignored -> {
              game.incrementAndGet();
              return GAME_REPLY;
            },
            ignored -> {
              logs.incrementAndGet();
              return LOG_REPLY;
            });
    assertArrayEquals(LOGIN_REPLY, router.process(request(FIXTURE_LGNREQ01_217C66A4, 384)));
    assertArrayEquals(GAME_REPLY, router.process(request("GAMREQ01", 0)));
    assertArrayEquals(LOG_REPLY, router.process(request("LGSREQ01", 656)));
    assertEquals(1, login.get());
    assertEquals(1, game.get());
    assertEquals(1, logs.get());
  }

  @Test
  void validButUnregisteredLayoutIsRetryableNotPermanentDlq() {
    var calls = new AtomicInteger();
    SyncRequestProcessor unexpected =
        ignored -> {
          calls.incrementAndGet();
          return new byte[0];
        };
    var router = new LogPathSyncRequestProcessor(unexpected, unexpected, unexpected);
    assertThrows(
        TemporaryInfrastructureException.class, () -> router.process(request("LOGREQ01", 0)));
    assertEquals(0, calls.get());
  }

  @Test
  void nullInputsAndNullReplyAreRejectedAtTheirBoundary() {
    SyncRequestProcessor reply = ignored -> LOGIN_REPLY;
    assertThrows(
        NullPointerException.class, () -> new LogPathSyncRequestProcessor(null, reply, reply));
    assertThrows(
        NullPointerException.class, () -> new LogPathSyncRequestProcessor(reply, null, reply));
    assertThrows(
        NullPointerException.class, () -> new LogPathSyncRequestProcessor(reply, reply, null));
    var router = new LogPathSyncRequestProcessor(ignored -> null, reply, reply);
    assertThrows(NullPointerException.class, () -> router.process(null));
    assertThrows(
        NullPointerException.class, () -> router.process(request(FIXTURE_LGNREQ01_217C66A4, 384)));
  }

  @Test
  void delegateFailureClassificationIsNotRewritten() {
    var permanent = new PermanentProtocolException("synthetic semantic rejection");
    var retryable = new TemporaryInfrastructureException();
    var router =
        new LogPathSyncRequestProcessor(
            ignored -> {
              throw permanent;
            },
            ignored -> {
              throw retryable;
            },
            ignored -> LOG_REPLY);
    assertEquals(
        permanent,
        assertThrows(
            PermanentProtocolException.class,
            () -> router.process(request(FIXTURE_LGNREQ01_217C66A4, 384))));
    assertEquals(
        retryable,
        assertThrows(
            TemporaryInfrastructureException.class, () -> router.process(request("GAMREQ01", 0))));
  }

  @Test
  void concurrentDispatchDoesNotShareMutableRoutingState() throws Exception {
    var login = new AtomicInteger();
    var game = new AtomicInteger();
    var logs = new AtomicInteger();
    var router =
        new LogPathSyncRequestProcessor(
            ignored -> {
              login.incrementAndGet();
              return LOGIN_REPLY;
            },
            ignored -> {
              game.incrementAndGet();
              return GAME_REPLY;
            },
            ignored -> {
              logs.incrementAndGet();
              return LOG_REPLY;
            });
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var futures = new java.util.ArrayList<java.util.concurrent.Future<byte[]>>();
      for (int index = 0; index < 96; index++) {
        final int selected = index % 3;
        futures.add(
            executor.submit(
                () ->
                    router.process(
                        switch (selected) {
                          case 0 -> request(FIXTURE_LGNREQ01_217C66A4, 384);
                          case 1 -> request("GAMREQ01", 0);
                          default -> request("LGSREQ01", 656);
                        })));
      }
      for (int index = 0; index < futures.size(); index++) {
        byte[] expected =
            switch (index % 3) {
              case 0 -> LOGIN_REPLY;
              case 1 -> GAME_REPLY;
              default -> LOG_REPLY;
            };
        assertArrayEquals(expected, futures.get(index).get());
      }
    }
    assertEquals(32, login.get());
    assertEquals(32, game.get());
    assertEquals(32, logs.get());
  }

  private static WireMessage<FixedPayload> request(String layout, int dataLength) {
    UUID id = UUID.fromString("00000000-0000-0000-0000-000000000001");
    var context =
        layout.equals(FIXTURE_LGNREQ01_217C66A4)
            ? Optional.<AuthenticationContext>empty()
            : Optional.of(AuthenticationContext.of("a".repeat(64)));
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            Instant.parse("2026-09-24T00:00:00Z"),
            context,
            256,
            dataLength,
            0,
            0,
            256 + dataLength,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(new byte[dataLength], 0, List.of()));
  }
}
