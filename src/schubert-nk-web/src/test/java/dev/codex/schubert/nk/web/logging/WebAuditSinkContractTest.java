package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;

/** SS312 section11/351 section3.1; PT-F03-LOG001..004: no real DB, HTTP or worker startup. */
final class WebAuditSinkContractTest {
  @Test
  void log001DisabledAndRuntimeBrokenSinksSignalOnceAndNeverOpenDb() {
    for (int mode : new int[] {0, 1, 2, 3}) {
      var logger = new Sink();
      logger.enabled = mode != 0;
      logger.queryFailure = mode == 1 ? new IllegalStateException("synthetic sink fault") : null;
      logger.writeFailure =
          mode == 2
              ? new IllegalStateException("synthetic sink fault")
              : mode == 3 ? new NullPointerException("synthetic sink null") : null;
      var notifications = new AtomicInteger();
      try (var fixture = new Fixture(logger, notifications::incrementAndGet)) {
        for (int status : new int[] {200, 400, 500}) {
          fixture.producer.complete(
              WebRequestTraceTest.trace(new MockHttpServletRequest(), 71),
              status,
              0,
              0,
              "GET",
              Optional.of("127.0.0.1"));
        }
        fixture.producer.metadataInvalid();
        assertEquals(4, notifications.get());
        assertEquals(0, fixture.opened.get());
        assertTrue(logger.messages.isEmpty());
      }
    }
  }

  @Test
  void log002TerminalCallbackRuntimeIsBoundedAndFatalIdentityIsPreserved() {
    var logger = new Sink();
    logger.enabled = false;
    var calls = new AtomicInteger();
    var raw = new NullPointerException("synthetic callback secret must not escape");
    try (var fixture =
        new Fixture(
            logger,
            () -> {
              calls.incrementAndGet();
              throw raw;
            })) {
      var actual = assertThrows(IllegalStateException.class, fixture.producer::metadataInvalid);
      assertEquals("request audit terminal signal failed", actual.getMessage());
      assertNull(actual.getCause());
      assertEquals(0, actual.getSuppressed().length);
      assertEquals(1, calls.get());
      assertEquals(0, fixture.opened.get());
    }
    var fatal = new AssertionError("synthetic fatal callback");
    try (var fixture =
        new Fixture(
            logger,
            () -> {
              throw fatal;
            })) {
      assertSame(fatal, assertThrows(AssertionError.class, fixture.producer::metadataInvalid));
      assertEquals(0, fixture.opened.get());
    }
  }

  @Test
  void log003LoggerErrorsRemainFatalRatherThanSuccessfulOrRetried() {
    for (boolean query : List.of(false, true)) {
      var logger = new Sink();
      var fatal = new AssertionError("synthetic logger fatal");
      if (query) logger.queryFailure = fatal;
      else logger.writeFailure = fatal;
      var terminal = new AtomicInteger();
      try (var fixture = new Fixture(logger, terminal::incrementAndGet)) {
        assertSame(fatal, assertThrows(AssertionError.class, fixture.producer::metadataInvalid));
        assertEquals(0, terminal.get());
        assertEquals(0, fixture.opened.get());
        assertTrue(logger.messages.isEmpty());
      }
    }
  }

  @Test
  void log004HealthyMetadataSinkUsesOnlyTheFixedSafeFailureEvent() {
    var logger = new Sink();
    var terminal = new AtomicInteger();
    try (var fixture = new Fixture(logger, terminal::incrementAndGet)) {
      fixture.producer.metadataInvalid();
      assertEquals(0, terminal.get());
      assertEquals(0, fixture.opened.get());
      assertEquals(List.of(Level.WARNING), logger.levels);
      assertEquals(1, logger.messages.size());
      assertEquals(
          JsonParser.parseString(
              "{\"timestamp\":\"2026-10-20T00:00:00.000Z\",\"service\":\"WEB\",\"appVersion\":\"pt-1\",\"configVersion\":\"cfg-1\",\"level\":\"WARN\",\"category\":\"SYSTEM\",\"action\":\"INTEGRITY_FAILED\",\"outcome\":\"UNKNOWN\",\"errorCode\":\"WEB_REQUEST_LOG_METADATA_INVALID\"}"),
          JsonParser.parseString(logger.messages.getFirst()));
    }
  }

  private static final class Fixture implements AutoCloseable {
    final AtomicInteger opened = new AtomicInteger();
    final WebLogPayloadCodec codec = new WebLogPayloadCodec("v1", new byte[32], null, null);
    final WebRequestLogProducer producer;

    Fixture(Logger logger, Runnable terminal) {
      var database =
          WebRequestLogProducerTest.source(
              () -> {
                opened.incrementAndGet();
                throw new AssertionError("DB must not open");
              });
      producer =
          new WebRequestLogProducer(
              database,
              codec,
              new WebLogOutboxRepository(() -> 0),
              logger,
              Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC),
              () -> new UUID(0, 1),
              "pt-1",
              "cfg-1",
              terminal);
    }

    @Override
    public void close() {
      codec.close();
    }
  }

  private static final class Sink implements Logger {
    boolean enabled = true;
    Throwable queryFailure;
    Throwable writeFailure;
    final List<String> messages = new ArrayList<>();
    final List<Level> levels = new ArrayList<>();

    @Override
    public String getName() {
      return "finite synthetic audit sink";
    }

    @Override
    public boolean isLoggable(Level level) {
      fail(queryFailure);
      return enabled;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String text, Throwable failure) {
      throw new AssertionError("raw Throwable must not be logged");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String text, Object... args) {
      fail(writeFailure);
      assertTrue(args == null || args.length == 0);
      levels.add(level);
      messages.add(text);
    }

    private static void fail(Throwable failure) {
      if (failure instanceof RuntimeException runtime) throw runtime;
      if (failure instanceof Error fatal) throw fatal;
    }
  }
}
