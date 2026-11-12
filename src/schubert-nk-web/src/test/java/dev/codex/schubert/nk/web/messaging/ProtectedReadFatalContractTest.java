package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuRequestData;
import jakarta.jms.JMSException;
import java.sql.SQLException;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** READ-FATAL001..008; BUG2561/YKT2359; UI232235/SS311312321352; public memory only. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class ProtectedReadFatalContractTest {
  private static final String PUBLIC = "PUBLIC fixture";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
  private static final UUID ID = new UUID(0, 1);
  private static final Duration WAIT = Duration.ofSeconds(2);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));

  @Test
  void fatal001SenderCauseRetainsIdentityWipesAndReleasesCapacity() {
    var fatal = new AssertionError(PUBLIC);
    var sql = new SQLException(PUBLIC);
    var next = new SQLException(PUBLIC, fatal);
    sql.setNextException(next);
    var failure = new IllegalStateException(PUBLIC, sql);
    var bytes = new AtomicReference<byte[]>();
    var sends = new AtomicInteger();
    var coordinator = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
    var wire =
        new AnimationWireClient(
            coordinator,
            (id, body) -> {
              assertEquals(ID, id);
              assertEquals(256, body.length);
              bytes.set(body);
              sends.incrementAndGet();
              throw failure;
            },
            CLOCK,
            () -> ID,
            WAIT);
    for (int attempt = 1; attempt <= 2; attempt++) {
      assertSame(fatal, assertThrows(AssertionError.class, () -> wire.exchange(input(), CONTEXT)));
      assertArrayEquals(new byte[256], bytes.get());
      assertEquals(0, coordinator.pendingCount());
      assertEquals(attempt, sends.get());
    }
    assertSame(sql, failure.getCause());
    assertSame(next, sql.getNextException());
    assertSame(fatal, next.getCause());
    assertEquals(0, coordinator.lateReplyCount());
  }

  @Test
  void fatal002JmsLinkedRetainsIdentityAndWipesAfterCheckedFailure() {
    var fatal = new AssertionError(PUBLIC);
    var linked = new IllegalArgumentException(PUBLIC, fatal);
    var failure = new JMSException(PUBLIC);
    failure.setLinkedException(linked);
    assertNull(failure.getCause());
    var bytes = new AtomicReference<byte[]>();
    var coordinator = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
    var wire =
        new AnimationWireClient(
            coordinator,
            (id, body) -> {
              bytes.set(body);
              throw failure;
            },
            CLOCK,
            () -> ID,
            WAIT);
    assertSame(fatal, assertThrows(AssertionError.class, () -> wire.exchange(input(), CONTEXT)));
    assertArrayEquals(new byte[256], bytes.get());
    assertEquals(0, coordinator.pendingCount());
    assertSame(linked, failure.getLinkedException());
    assertNull(failure.getCause());
  }

  @Test
  void fatal003IdentifierAndClockCallbacksCannotNormalizeWrappedError() {
    var fatal = new AssertionError(PUBLIC);
    var sends = new AtomicInteger();
    var coordinator = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
    var identifierWire =
        new AnimationWireClient(
            coordinator,
            (id, body) -> sends.incrementAndGet(),
            CLOCK,
            () -> {
              throw new IllegalStateException(PUBLIC, fatal);
            },
            WAIT);
    assertSame(
        fatal, assertThrows(AssertionError.class, () -> identifierWire.exchange(input(), CONTEXT)));
    Clock failingClock =
        new Clock() {
          @Override
          public ZoneId getZone() {
            return ZoneOffset.UTC;
          }

          @Override
          public Clock withZone(ZoneId zone) {
            throw new UnsupportedOperationException();
          }

          @Override
          public Instant instant() {
            throw new DateTimeException(PUBLIC, fatal);
          }
        };
    var clockWire =
        new AnimationWireClient(
            coordinator, (id, body) -> sends.incrementAndGet(), failingClock, () -> ID, WAIT);
    assertSame(
        fatal, assertThrows(AssertionError.class, () -> clockWire.exchange(input(), CONTEXT)));
    assertEquals(0, sends.get());
    assertEquals(0, coordinator.pendingCount());
  }

  @Test
  void fatal004NonfatalLinkedCycleKeepsFixedSecretFreeCatalogAndCleanup() {
    var failure = new JMSException(PUBLIC);
    var linked = new JMSException(PUBLIC);
    failure.setLinkedException(linked);
    linked.setLinkedException(failure);
    linked.addSuppressed(failure);
    var bytes = new AtomicReference<byte[]>();
    var coordinator = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
    var wire =
        new AnimationWireClient(
            coordinator,
            (id, body) -> {
              bytes.set(body);
              throw failure;
            },
            CLOCK,
            () -> ID,
            WAIT);
    var actual =
        assertThrows(ProtectedReadWireException.class, () -> wire.exchange(input(), CONTEXT));
    assertEquals(ProtectedReadWireException.Reason.UNAVAILABLE, actual.reason());
    assertEquals("protected read exchange rejected", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
    assertArrayEquals(new byte[256], bytes.get());
    assertEquals(0, coordinator.pendingCount());
    assertSame(linked, failure.getLinkedException());
    assertSame(failure, linked.getLinkedException());
  }

  @Test
  void fatal005CatalogConstructorsAndNullPreconditionsStayExplicit() {
    var cause = new IllegalStateException(PUBLIC);
    for (var reason : JmsRequestReplyException.Reason.values()) {
      var direct = new JmsRequestReplyException(reason, PUBLIC);
      assertSame(reason, direct.reason());
      assertEquals(PUBLIC, direct.getMessage());
      assertNull(direct.getCause());
      var wrapped = new JmsRequestReplyException(reason, PUBLIC, cause);
      assertSame(reason, wrapped.reason());
      assertSame(cause, wrapped.getCause());
      JmsRequestReplyException.preserveFatal(wrapped);
    }
    assertEquals(3, JmsRequestReplyException.Reason.values().length);
    assertThrows(NullPointerException.class, () -> new JmsRequestReplyException(null, PUBLIC));
    assertThrows(
        NullPointerException.class, () -> new JmsRequestReplyException(null, PUBLIC, cause));
    assertThrows(NullPointerException.class, () -> JmsRequestReplyException.preserveFatal(null));
  }

  @Test
  void fatal006FiniteBreadthFirstOrderPrefersCauseThenSuppressedThenCarriers() {
    var first = new AssertionError("PUBLIC first");
    var second = new AssertionError("PUBLIC second");
    var causeFirst = new IllegalStateException(PUBLIC, first);
    causeFirst.addSuppressed(second);
    assertSame(
        first, assertThrows(Error.class, () -> JmsRequestReplyException.preserveFatal(causeFirst)));
    var nested = new IllegalStateException(PUBLIC, first);
    var breadthFirst = new IllegalStateException(PUBLIC, nested);
    breadthFirst.addSuppressed(second);
    assertSame(
        second,
        assertThrows(Error.class, () -> JmsRequestReplyException.preserveFatal(breadthFirst)));
    var sql = new SQLException(PUBLIC);
    sql.addSuppressed(first);
    sql.setNextException(new SQLException(PUBLIC, second));
    assertSame(first, assertThrows(Error.class, () -> JmsRequestReplyException.preserveFatal(sql)));
    var jms = new JMSException(PUBLIC);
    jms.addSuppressed(first);
    jms.setLinkedException(new IllegalStateException(PUBLIC, second));
    assertSame(first, assertThrows(Error.class, () -> JmsRequestReplyException.preserveFatal(jms)));
    assertSame(
        first, assertThrows(Error.class, () -> JmsRequestReplyException.preserveFatal(first)));
  }

  @Test
  void fatal007NonfatalMixedCyclesAreFiniteWithoutGraphMutation() {
    var root = new IllegalStateException(PUBLIC);
    var alias = new IllegalArgumentException(PUBLIC, root);
    root.initCause(alias);
    root.addSuppressed(alias);
    alias.addSuppressed(root);
    var sql = new SQLException(PUBLIC);
    sql.setNextException(sql);
    var jms = new JMSException(PUBLIC);
    jms.setLinkedException(jms);
    root.addSuppressed(sql);
    root.addSuppressed(jms);
    JmsRequestReplyException.preserveFatal(root);
    assertSame(alias, root.getCause());
    assertSame(root, alias.getCause());
    assertSame(sql, sql.getNextException());
    assertSame(jms, jms.getLinkedException());
    assertEquals(List.of(alias, sql, jms), List.of(root.getSuppressed()));
    assertEquals(List.of(root), List.of(alias.getSuppressed()));
  }

  @Test
  void fatal008DeepLinkedGraphIsIterativeAndNextRequestDirectErrorStillCleansUp() {
    var fatal = new AssertionError(PUBLIC);
    Exception nested = new IllegalStateException(PUBLIC, fatal);
    for (int index = 0; index < 1024; index++) {
      var link = new JMSException(PUBLIC);
      link.setLinkedException(nested);
      nested = link;
    }
    Exception root = nested;
    assertSame(
        fatal, assertThrows(Error.class, () -> JmsRequestReplyException.preserveFatal(root)));
    var coordinator = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
    var bytes = new AtomicReference<byte[]>();
    var wire =
        new AnimationWireClient(
            coordinator,
            (id, body) -> {
              bytes.set(body);
              throw fatal;
            },
            CLOCK,
            () -> ID,
            WAIT);
    assertSame(fatal, assertThrows(Error.class, () -> wire.exchange(input(), CONTEXT)));
    assertArrayEquals(new byte[256], bytes.get());
    assertEquals(0, coordinator.pendingCount());
    assertTrue(coordinator.lateReplyCount() == 0);
  }

  private static TypedPayloadValues input() {
    return new TypedPayloadValues(
        new LayoutId("ANMREQ01"), new AnimationMenuRequestData(), List.of());
  }
}
