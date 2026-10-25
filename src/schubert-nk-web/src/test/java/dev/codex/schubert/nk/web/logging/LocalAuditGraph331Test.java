package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import jakarta.jms.JMSException;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.lang.reflect.Proxy;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** MON003/UI235252/SS312351354/SSC331; PT-WEB-LOCAL331001..004; BUG1601/YKT1354. */
final class LocalAuditGraph331Test {
  @Test
  void local331001LoggerGraphSignalsOnceBeforeOriginalFatalWithoutAnyProjection() {
    for (int edge = 0; edge < 4; edge++) {
      for (boolean duringCheck : new boolean[] {false, true}) {
        var fatal = new AssertionError("PUBLIC chosen logger fatal");
        try (var state = new Fixture()) {
          state.logFailure = graph(fatal, edge);
          state.duringCheck = duringCheck;
          Throwable actual = state.execute();
          state.verify(duringCheck ? 0 : 1, 1);
          assertTrue(actual == fatal);
        }
      }
    }
  }

  @Test
  void local331002TerminalGraphCannotBecomeFixedOrdinaryCatalog() {
    for (int edge = 0; edge < 4; edge++) {
      for (boolean disabled : new boolean[] {false, true}) {
        var fatal = new AssertionError("PUBLIC chosen callback fatal");
        try (var state = new Fixture()) {
          state.enabled = !disabled;
          if (!disabled) state.logFailure = new IllegalStateException("PRIVATE_LOGGER_CANARY");
          state.signalFailure = graph(fatal, edge);
          Throwable actual = state.execute();
          state.verify(disabled ? 0 : 1, 1);
          assertTrue(actual == fatal);
        }
      }
    }
  }

  @Test
  void local331003CallbackThenLoggerGraphPriorityAndAliasesAreIndependent() {
    for (int callbackKind = 0; callbackKind < 3; callbackKind++) {
      var local = new AssertionError("PUBLIC local fatal");
      var callback = new AssertionError("PUBLIC callback fatal");
      try (var state = new Fixture()) {
        state.logFailure = graph(local, 1);
        state.signalFailure =
            callbackKind == 0
                ? new IllegalStateException("PRIVATE_SIGNAL_CANARY")
                : callbackKind == 1 ? graph(callback, 2) : state.logFailure;
        Throwable actual = state.execute();
        state.verify(1, 1);
        assertTrue(actual == (callbackKind == 1 ? callback : local));
      }
    }
  }

  @Test
  void local331004OrdinaryCyclesDisabledSuccessAndDirectErrorRulesStayUnchanged() {
    try (var state = new Fixture()) {
      assertNull(state.execute());
      state.verify(1, 0);
      var json = JsonParser.parseString(state.message).getAsJsonObject();
      assertEquals("2026-10-22T00:00:00.000Z", json.get("timestamp").getAsString());
      assertEquals("WEB", json.get("service").getAsString());
      assertEquals("INTEGRITY_FAILED", json.get("action").getAsString());
      assertEquals("UNKNOWN", json.get("outcome").getAsString());
      assertEquals("WEB_REQUEST_LOG_METADATA_INVALID", json.get("errorCode").getAsString());
    }
    try (var state = new Fixture()) {
      state.enabled = false;
      assertNull(state.execute());
      state.verify(0, 1);
    }
    var first = new JMSException("PRIVATE_CYCLE_CANARY");
    var second = new JMSException("PRIVATE_CYCLE_CANARY");
    first.setLinkedException(second);
    second.setLinkedException(first);
    var cycle = new RuntimeException("PRIVATE_LOGGER_CANARY", first);
    try (var state = new Fixture()) {
      state.logFailure = cycle;
      assertNull(state.execute());
      state.verify(1, 1);
      assertEquals(0, cycle.getSuppressed().length);
    }
    for (boolean disabled : new boolean[] {false, true}) {
      try (var state = new Fixture()) {
        state.enabled = !disabled;
        if (!disabled) state.logFailure = cycle;
        state.signalFailure = cycle;
        Throwable actual = state.execute();
        state.verify(disabled ? 0 : 1, 1);
        var fixed = assertInstanceOf(IllegalStateException.class, actual);
        assertEquals("request audit terminal signal failed", fixed.getMessage());
        assertNull(fixed.getCause());
        assertEquals(0, fixed.getSuppressed().length);
        assertEquals(0, cycle.getSuppressed().length);
      }
    }
    for (boolean duringCheck : new boolean[] {false, true}) {
      var direct = new AssertionError("PUBLIC direct logger fatal");
      try (var state = new Fixture()) {
        state.duringCheck = duringCheck;
        state.directLog = direct;
        state.directSignal = new AssertionError("PUBLIC must not signal");
        Throwable actual = state.execute();
        state.verify(duringCheck ? 0 : 1, 0);
        assertSame(direct, actual);
      }
    }
    var directCallback = new AssertionError("PUBLIC direct callback fatal");
    try (var state = new Fixture()) {
      state.logFailure = graph(new AssertionError("PUBLIC nested local"), 0);
      state.directSignal = directCallback;
      Throwable actual = state.execute();
      state.verify(1, 1);
      assertSame(directCallback, actual);
    }
  }

  private static RuntimeException graph(Error fatal, int edge) {
    if (edge == 0) return new RuntimeException("PRIVATE_GRAPH_CANARY", fatal);
    if (edge == 1) {
      var failure = new RuntimeException("PRIVATE_GRAPH_CANARY");
      failure.addSuppressed(fatal);
      return failure;
    }
    if (edge == 2) {
      var linked = new JMSException("PRIVATE_GRAPH_CANARY");
      linked.setLinkedException(new Exception(fatal));
      return new RuntimeException("PRIVATE_GRAPH_CANARY", linked);
    }
    var sql = new SQLException("PRIVATE_GRAPH_CANARY");
    sql.setNextException(new SQLException("PRIVATE_GRAPH_CANARY", fatal));
    return new RuntimeException("PRIVATE_GRAPH_CANARY", sql);
  }

  private static final class Fixture implements AutoCloseable, Logger {
    final List<String> events = new ArrayList<>();
    final WebLogPayloadCodec codec =
        new WebLogPayloadCodec("public-fixture", new byte[32], null, null);
    @Nullable RuntimeException logFailure;
    @Nullable RuntimeException signalFailure;
    @Nullable Error directLog;
    @Nullable Error directSignal;
    boolean enabled = true;
    boolean duringCheck;
    int checks;
    int logs;
    int signals;
    int db;
    int identifiers;
    int unexpected;
    String message = "";

    @Nullable Throwable execute() {
      DataSource database =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (instance, method, args) -> {
                    if (method.getName().equals("getConnection")) db++;
                    else unexpected++;
                    throw new AssertionError("PUBLIC unexpected database operation");
                  });
      var producer =
          new WebRequestLogProducer(
              database,
              codec,
              new WebLogOutboxRepository(() -> 0),
              this,
              Clock.fixed(Instant.parse("2026-10-22T00:00:00Z"), ZoneOffset.UTC),
              () -> {
                identifiers++;
                throw new AssertionError("PUBLIC unexpected identifier");
              },
              "pt-public",
              "config-public",
              () -> {
                events.add("terminal");
                signals++;
                if (directSignal != null) throw directSignal;
                if (signalFailure != null) throw signalFailure;
              });
      try {
        producer.metadataInvalid();
        return null;
      } catch (Throwable failure) {
        return failure;
      }
    }

    void verify(int expectedLogs, int expectedSignals) {
      assertEquals(0, unexpected);
      assertEquals(0, db);
      assertEquals(0, identifiers);
      assertEquals(1, checks);
      assertEquals(expectedLogs, logs);
      assertEquals(expectedSignals, signals);
      var expected = new ArrayList<>(List.of("check"));
      if (expectedLogs == 1) expected.add("log");
      if (expectedSignals == 1) expected.add("terminal");
      assertEquals(expected, events);
      assertFalse(message.contains("PRIVATE_"));
      if (expectedLogs == 1)
        assertTrue(message.contains("\"errorCode\":\"WEB_REQUEST_LOG_METADATA_INVALID\""));
    }

    @Override
    public String getName() {
      return "public-local-audit-fixture";
    }

    @Override
    public boolean isLoggable(Level level) {
      events.add("check");
      checks++;
      if (duringCheck) logFault();
      return enabled;
    }

    private void logFault() {
      if (directLog != null) throw directLog;
      if (logFailure != null) throw logFailure;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      events.add("log");
      logs++;
      message = format;
      if (bundle != null || parameters != null) {
        unexpected++;
        throw new AssertionError("PUBLIC unexpected primitive arguments");
      }
      logFault();
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Throwable failure) {
      unexpected++;
      throw new AssertionError("PUBLIC Throwable must not reach sink");
    }

    @Override
    public void close() {
      codec.close();
    }
  }
}
