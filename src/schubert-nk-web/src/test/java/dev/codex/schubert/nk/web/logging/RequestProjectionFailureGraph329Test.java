package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.springframework.mock.web.MockHttpServletRequest;

/** NK-MSG-002; SS312/332/351/354; BUG1592/YKT1345; PT-WEB-REQUEST-GRAPH329001..003. No I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class RequestProjectionFailureGraph329Test {
  @Test
  void request329001SqlGraphCannotBecomeOrdinaryLocalProjectionFailure() {
    for (int mode = 0; mode < 3; mode++) {
      var fatal = new AssertionError("PUBLIC fatal");
      var failure = graph(fatal, mode);
      try (var fixture =
          new WebRequestLogProducerTest.Fixture(
              WebRequestLogProducerTest.source(
                  () -> {
                    throw failure;
                  }))) {
        assertSame(fatal, assertThrows(AssertionError.class, () -> complete(fixture)));
        assertEquals(1, fixture.logger.entries.size());
        assertEquals(
            "PENDING",
            fixture
                .logger
                .entries
                .getFirst()
                .json()
                .getAsJsonObject("details")
                .get("projectionStatus")
                .getAsString());
      }
    }
  }

  @Test
  void request329002DisabledSuppressionRollbackGraphKeepsFatalAndStillCloses() {
    for (boolean primaryHasFatal : new boolean[] {false, true}) {
      var first = new AssertionError("PUBLIC primary graph fatal");
      var second = new AssertionError("PUBLIC rollback graph fatal");
      var primary = new NoSuppression(primaryHasFatal ? graph(first, 2) : null);
      var closes = new AtomicInteger();
      var rollbacks = new AtomicInteger();
      var commits = new AtomicInteger();
      var prepares = new AtomicInteger();
      var connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (object, method, args) ->
                      switch (method.getName()) {
                        case "setAutoCommit" -> null;
                        case "getAutoCommit" -> false;
                        case "prepareStatement" -> {
                          prepares.incrementAndGet();
                          throw primary;
                        }
                        case "rollback" -> {
                          rollbacks.incrementAndGet();
                          throw graph(second, 2);
                        }
                        case "close" -> {
                          closes.incrementAndGet();
                          yield null;
                        }
                        case "commit" -> {
                          commits.incrementAndGet();
                          yield null;
                        }
                        default ->
                            throw new AssertionError("Unexpected operation: " + method.getName());
                      });
      try (var fixture =
          new WebRequestLogProducerTest.Fixture(
              WebRequestLogProducerTest.source(() -> connection))) {
        assertSame(
            primaryHasFatal ? first : second,
            assertThrows(AssertionError.class, () -> complete(fixture)));
        assertEquals(1, fixture.logger.entries.size());
        assertEquals(1, closes.get());
        assertEquals(1, rollbacks.get());
        assertEquals(0, commits.get());
        assertEquals(1, prepares.get());
      }
    }
  }

  @Test
  void request329003NonFatalCycleKeepsExplicitFailedAuditAndOriginalHttpObservation() {
    try (var fixture =
        new WebRequestLogProducerTest.Fixture(
            WebRequestLogProducerTest.source(
                () -> {
                  throw graph(null, 3);
                }))) {
      complete(fixture);
      assertEquals(2, fixture.logger.entries.size());
      var json = fixture.logger.entries.getLast().json();
      assertEquals("FAILED", json.getAsJsonObject("details").get("projectionStatus").getAsString());
      assertEquals("WEB_REQUEST_LOG_PROJECTION_FAILED", json.get("errorCode").getAsString());
      assertEquals("WARN", json.get("level").getAsString());
      assertEquals(200, json.get("status").getAsInt());
      assertEquals(
          fixture.logger.entries.getFirst().json().get("messageId"), json.get("messageId"));
    }
  }

  private static void complete(WebRequestLogProducerTest.Fixture fixture) {
    var trace = WebRequestTraceTest.trace(new MockHttpServletRequest(), 72);
    trace.captureRoute("/login");
    fixture.producer.complete(trace, 200, 0, 0, "GET", Optional.of("127.0.0.1"));
  }

  private static SQLException graph(@Nullable AssertionError fatal, int mode) {
    var sql = new SQLException("PUBLIC SQL");
    var next = new SQLException("PUBLIC next");
    sql.setNextException(next);
    if (fatal == null) next.setNextException(sql);
    else if (mode == 0) sql.initCause(fatal);
    else if (mode == 1) sql.addSuppressed(fatal);
    else next.initCause(fatal);
    return sql;
  }

  private static final class NoSuppression extends RuntimeException {
    private static final long serialVersionUID = 1L;

    NoSuppression(@Nullable Throwable cause) {
      super("PUBLIC primary", cause, false, false);
    }
  }
}
