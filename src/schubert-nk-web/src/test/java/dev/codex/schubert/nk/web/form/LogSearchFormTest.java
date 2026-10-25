package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.web.form.LogSearchForm.Code;
import dev.codex.schubert.nk.web.form.LogSearchForm.Field;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PG214/PT-WEB278..285/SSC073/UI222,225,235/SS313,352. */
class LogSearchFormTest {
  private static LogSearchForm form(String key, String value) {
    return LogSearchForm.bind(Map.of(key, List.of(value)));
  }

  @Test
  void web278DefaultsAndFilters() {
    var empty = LogSearchForm.bind(Map.of());
    assertTrue(empty.isValid());
    assertTrue(empty.getIssues().isEmpty());
    assertEquals(1, empty.getPage());
    var request = empty.toRequest();
    assertEquals(1, request.page());
    assertEquals(100, request.pageSize());
    assertTrue(request.keyword().isEmpty());
    assertTrue(request.logType().isEmpty());
    assertTrue(request.action().isEmpty());
    assertTrue(request.path().isEmpty());
    assertTrue(request.level().isEmpty());
    assertTrue(request.fromAt().isEmpty());
    assertTrue(request.toAt().isEmpty());
    for (String type : List.of("ACTION", "REQUEST", "SECURITY", "MQ", "SYSTEM", "BATCH"))
      for (String level : List.of("INFO", "WARN", "ERROR")) {
        var full =
            LogSearchForm.bind(
                Map.of(
                    "q",
                    List.of(" e\u0301 "),
                    "log_type",
                    List.of(" " + type + " "),
                    "action",
                    List.of(" search "),
                    "path",
                    List.of(" /search "),
                    "level",
                    List.of(level),
                    "from",
                    List.of("2026-09-20T09:00"),
                    "to",
                    List.of("2026-09-20T10:00"),
                    "page",
                    List.of("002")));
        assertTrue(full.isValid());
        var p = full.toRequest();
        assertEquals(Optional.of("é"), p.keyword());
        assertEquals(type, p.logType().orElseThrow().name());
        assertEquals(level, p.level().orElseThrow().name());
        assertEquals(Optional.of("search"), p.action());
        assertEquals(Optional.of("/search"), p.path());
        assertEquals(2, p.page());
        assertEquals(100, p.pageSize());
        assertEquals(Optional.of(Instant.parse("2026-09-20T00:00:00Z")), p.fromAt());
        assertEquals(Optional.of(Instant.parse("2026-09-20T01:00:00Z")), p.toAt());
        assertEquals("é", full.getValues().get(Field.Q));
      }
  }

  @Test
  void web279TextAndBinding() {
    for (var entry : Map.of("q", 256, "action", 64, "path", 256).entrySet()) {
      int n = entry.getValue();
      assertTrue(form(entry.getKey(), "x".repeat(n)).isValid());
      assertTrue(form(entry.getKey(), "あ".repeat(n / 3) + "x".repeat(n % 3)).isValid());
      var bad = form(entry.getKey(), "x".repeat(n + 1));
      assertFalse(bad.isValid());
      assertTrue(bad.getIssues().containsValue(Code.LENGTH));
      assertEquals(
          n + 1,
          bad.getValues().get(Field.valueOf(entry.getKey().toUpperCase(Locale.ROOT))).length());
    }
    assertEquals(Code.BINDING, form("unknown", "x").getIssues().get(Field.FORM));
    for (String key : List.of("q", "log_type", "action", "path", "level", "from", "to", "page")) {
      for (var list : List.<List<String>>of(List.of(), List.of("a", "b"))) {
        var f = LogSearchForm.bind(Map.of(key, list));
        assertFalse(f.isValid());
        assertTrue(f.getIssues().containsValue(Code.BINDING));
      }
    }
  }

  @Test
  void web280Characters() {
    // BUG-225: surrounding whitespace must not erase the terminal-surrogate boundary.
    for (String key : List.of("q", "log_type", "action", "path", "level", "from", "to", "page")) {
      var f = form(key, "\ud800");
      assertFalse(f.isValid());
      assertEquals(Code.CHARACTERS, f.getIssues().get(Field.valueOf(key.toUpperCase(Locale.ROOT))));
      assertTrue(f.getValues().get(Field.valueOf(key.toUpperCase(Locale.ROOT))).isEmpty());
    }
    for (String key : List.of("q", "log_type", "action", "path", "level", "from", "to", "page"))
      for (String value : List.of("\r", "\n", "\t", "\0", "\ud800", "\ud800x", "\udc00")) {
        var f = form(key, " " + value + " ");
        assertFalse(f.isValid());
        assertTrue(f.getIssues().containsValue(Code.CHARACTERS));
        assertTrue(f.getValues().get(Field.valueOf(key.toUpperCase(Locale.ROOT))).isEmpty());
      }
    assertTrue(form("q", "😀").isValid());
    assertEquals(Optional.of("😀"), form("q", "😀").toRequest().keyword());
    assertTrue(form("q", "😀".repeat(64)).isValid());
    assertEquals(Code.LENGTH, form("q", "😀".repeat(65)).getIssues().get(Field.Q));
  }

  @Test
  void web281PageAndEnums() {
    for (String value : List.of("", " ", "0", "-0", "-1", "-2147483648")) {
      var f = form("page", value);
      assertTrue(f.isValid());
      assertEquals(1, f.getPage());
    }
    assertEquals(999999, form("page", "999999").getPage());
    assertEquals(1, form("page", "0001").getPage());
    for (String value :
        List.of("+1", "1.0", "1e2", "１", "1000000", "2147483648", "-2147483649", "-", "x")) {
      var f = form("page", value);
      assertEquals(Code.VALUE, f.getIssues().get(Field.PAGE));
      assertThrows(IllegalStateException.class, f::toRequest);
    }
    for (String value : List.of("request", "UNKNOWN"))
      assertEquals(Code.VALUE, form("log_type", value).getIssues().get(Field.LOG_TYPE));
    for (String value : List.of("warn", "DEBUG"))
      assertEquals(Code.VALUE, form("level", value).getIssues().get(Field.LEVEL));
  }

  @Test
  void web282Dates() {
    var cases =
        Map.of(
            "2026-09-20T09:00", "2026-09-20T00:00:00Z",
            "2026-09-20T09:00:01", "2026-09-20T00:00:01Z",
            "2026-09-20T09:00:01.1", "2026-09-20T00:00:01.100Z",
            "2026-09-20T09:00:01.12", "2026-09-20T00:00:01.120Z",
            "2026-09-20T09:00:01.123", "2026-09-20T00:00:01.123Z",
            "2024-02-29T09:00", "2024-02-29T00:00:00Z",
            "0001-01-01T09:00", "0001-01-01T00:00:00Z",
            "9999-12-31T23:59:59.999", "9999-12-31T14:59:59.999Z");
    for (var entry : cases.entrySet())
      for (String key : List.of("from", "to")) {
        var f = form(key, entry.getKey());
        assertTrue(f.isValid(), entry.getKey());
        assertEquals(
            Optional.of(Instant.parse(entry.getValue())),
            key.equals("from") ? f.toRequest().fromAt() : f.toRequest().toAt());
      }
    for (String text :
        List.of(
            "0000-01-01T00:00",
            "2025-02-29T00:00",
            "2026-13-01T00:00",
            "2026-09-31T00:00",
            "2026-09-20T24:00",
            "2026-09-20T00:60",
            "2026-09-20T00:00:60",
            "2026-09-20T00:00:00.1234",
            "2026-09-20",
            "2026-09-20 00:00",
            "2026-09-20T00:00Z",
            "2026-09-20T00:00+09:00",
            "2026-9-20T00:00",
            "2026-09-20T00:00:00.",
            "+2026-09-20T00:00")) {
      var f = form("from", text);
      assertEquals(Code.VALUE, f.getIssues().get(Field.FROM), text);
      assertThrows(IllegalStateException.class, f::toRequest);
    }
    assertTrue(form("from", " ").isValid());
    assertTrue(form("to", "").toRequest().toAt().isEmpty());
  }

  @Test
  void web283DateRange() {
    for (String to : List.of("2026-09-01T09:00", "2026-10-02T09:00")) {
      var f = LogSearchForm.bind(Map.of("from", List.of("2026-09-01T09:00"), "to", List.of(to)));
      assertTrue(f.isValid());
    }
    for (String to : List.of("2026-09-01T08:59:59.999", "2026-10-02T09:00:00.001")) {
      var f = LogSearchForm.bind(Map.of("from", List.of("2026-09-01T09:00"), "to", List.of(to)));
      assertEquals(Code.RANGE, f.getIssues().get(Field.TO));
      assertThrows(IllegalStateException.class, f::toRequest);
    }
    var bad = LogSearchForm.bind(Map.of("from", List.of("bad"), "to", List.of("2026-09-01T09:00")));
    assertEquals(Map.of(Field.FROM, Code.VALUE), bad.getIssues());
    bad = LogSearchForm.bind(Map.of("from", List.of("2026-09-01T09:00"), "to", List.of("bad")));
    assertEquals(Map.of(Field.TO, Code.VALUE), bad.getIssues());
  }

  @Test
  void web284NullOwnershipAndRedaction() {
    assertThrows(NullPointerException.class, () -> LogSearchForm.bind(null));
    var nullKey = new HashMap<String, List<String>>();
    nullKey.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> LogSearchForm.bind(nullKey));
    var nullList = new HashMap<String, List<String>>();
    nullList.put("q", null);
    assertThrows(NullPointerException.class, () -> LogSearchForm.bind(nullList));
    var nullItem = new ArrayList<String>();
    nullItem.add(null);
    assertThrows(NullPointerException.class, () -> LogSearchForm.bind(Map.of("q", nullItem)));
    var list = new ArrayList<>(List.of("private-input"));
    var original = new HashMap<String, List<String>>();
    original.put("q", list);
    var f = LogSearchForm.bind(original);
    list.set(0, "changed");
    original.clear();
    assertEquals("private-input", f.getValues().get(Field.Q));
    assertEquals(Optional.of("private-input"), f.toRequest().keyword());
    assertThrows(UnsupportedOperationException.class, () -> f.getValues().clear());
    assertThrows(UnsupportedOperationException.class, () -> f.getIssues().clear());
    assertEquals("LogSearchForm[REDACTED]", f.toString());
    assertFalse(f.toString().contains("private-input"));
    var error =
        assertThrows(IllegalStateException.class, () -> form("level", "private-input").toRequest());
    assertEquals("invalid log search form", error.getMessage());
  }

  @Test
  void web285ConcurrentBinding() throws Exception {
    var shared = Map.of("level", List.of("WARN"));
    try (var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () -> {
                  var inputs = new HashMap<>(shared);
                  inputs.put("q", List.of("q" + n));
                  inputs.put("page", List.of(Integer.toString(n + 1)));
                  inputs.put("from", List.of("2026-09-20T09:00"));
                  var f = LogSearchForm.bind(inputs);
                  assertTrue(f.isValid());
                  assertEquals(Optional.of("q" + n), f.toRequest().keyword());
                  assertEquals(n + 1, f.getPage());
                  assertEquals(Optional.of(LogLevel.WARN), f.toRequest().level());
                  assertEquals(
                      Optional.of(Instant.parse("2026-09-20T00:00:00Z")), f.toRequest().fromAt());
                  return null;
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    }
    assertEquals(Map.of("level", List.of("WARN")), shared);
  }
}
