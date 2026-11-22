package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.VoiceCondition;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm.Code;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

/** Independent UI/SS literals, PG199/SSC072/015012/PT-WEB214..221. */
class ScenarioSearchFormTest {
  private static final String GAME_FIELD = "game";
  private static final String SPEAKER_FIELD = "speaker";
  private static final String ENTRY_TYPE_FIELD = "entry_type";
  private static final String VOICE_FIELD = "voice";
  private static final String PAGE_FIELD = "page";

  private static ScenarioSearchForm one(String key, String value) {
    return ScenarioSearchForm.bind(Map.of(key, List.of(value)));
  }

  private static void issue(String key, String value, Field field, Code code) {
    var form = one(key, value);
    assertFalse(form.isValid());
    assertEquals(code, form.getIssues().get(field));
    assertThrows(IllegalStateException.class, form::toRequest);
  }

  @Test
  void web214CanonicalRequest() {
    var empty = ScenarioSearchForm.bind(Map.of());
    assertTrue(empty.isValid());
    assertEquals(1, empty.getPage());
    assertTrue(empty.getIssues().isEmpty());
    var e = empty.toRequest();
    assertEquals(Optional.empty(), e.bodyKeyword());
    assertEquals(Optional.empty(), e.gameCode());
    assertEquals(Optional.empty(), e.speakerName());
    assertEquals(Optional.empty(), e.chapterTitle());
    assertEquals(Optional.empty(), e.entryType());
    assertEquals(Optional.empty(), e.voiceCondition());
    assertEquals(1, e.page());
    assertEquals(100, e.pageSize());
    for (int index = 0; index < 2; index++) {
      var f =
          ScenarioSearchForm.bind(
              Map.of(
                  "q",
                  List.of(" e\u0301 "),
                  GAME_FIELD,
                  List.of(index == 0 ? " NUKITASHI1 " : "NUKITASHI2"),
                  SPEAKER_FIELD,
                  List.of(" 話者 "),
                  "chapter",
                  List.of(" 章 "),
                  ENTRY_TYPE_FIELD,
                  List.of(index == 0 ? "dialogue" : "narration"),
                  VOICE_FIELD,
                  List.of(index == 0 ? "with" : "without"),
                  PAGE_FIELD,
                  List.of(" 12 ")));
      assertTrue(f.isValid());
      var r = f.toRequest();
      assertEquals(Optional.of("é"), r.bodyKeyword());
      assertEquals(
          Optional.of(index == 0 ? GameCode.NUKITASHI_1 : GameCode.NUKITASHI_2), r.gameCode());
      assertEquals(Optional.of("話者"), r.speakerName());
      assertEquals(Optional.of("章"), r.chapterTitle());
      assertEquals(
          Optional.of(index == 0 ? EntryType.DIALOGUE : EntryType.NARRATION), r.entryType());
      assertEquals(
          Optional.of(index == 0 ? VoiceCondition.PRESENT : VoiceCondition.ABSENT),
          r.voiceCondition());
      assertEquals(12, r.page());
      assertEquals(100, r.pageSize());
    }
    assertEquals(8, Field.values().length);
    assertEquals(4, Code.values().length);
  }

  @Test
  void web215ByteBoundaries() {
    for (var item :
        Map.of("q", Field.Q, SPEAKER_FIELD, Field.SPEAKER, "chapter", Field.CHAPTER).entrySet()) {
      int limit = item.getKey().equals(SPEAKER_FIELD) ? 128 : 256;
      for (int length : new int[] {limit - 1, limit}) {
        String input = "a".repeat(length);
        var f = one(item.getKey(), input);
        assertTrue(f.isValid());
        assertEquals(input, f.getValues().get(item.getValue()));
        assertNotNull(f.toRequest());
      }
      issue(item.getKey(), "a".repeat(limit + 1), item.getValue(), Code.LENGTH);
      String nfc = "e\u0301".repeat(limit / 2);
      var f = one(item.getKey(), " " + nfc + " ");
      assertTrue(f.isValid());
      assertEquals("é".repeat(limit / 2), f.getValues().get(item.getValue()));
      issue(item.getKey(), nfc + "a", item.getValue(), Code.LENGTH);
    }
    assertTrue(one("q", "😀".repeat(64)).isValid());
    issue("q", "😀".repeat(64) + "a", Field.Q, Code.LENGTH);
  }

  @Test
  void web216UnicodeAndEnums() {
    for (String bad : List.of("\r", "\n", "\t", "\u0000", "x\r", "\uD800", "\uD800x", "\uDC00")) {
      issue("q", bad, Field.Q, Code.CHARACTERS);
      issue(GAME_FIELD, bad, Field.GAME, Code.CHARACTERS);
      issue(PAGE_FIELD, bad, Field.PAGE, Code.CHARACTERS);
    }
    for (String key : List.of(GAME_FIELD, ENTRY_TYPE_FIELD, VOICE_FIELD)) {
      Field field =
          Map.of(
                  GAME_FIELD,
                  Field.GAME,
                  ENTRY_TYPE_FIELD,
                  Field.ENTRY_TYPE,
                  VOICE_FIELD,
                  Field.VOICE)
              .get(key);
      issue(key, "unknown", field, Code.VALUE);
      issue(key, "Ａ", field, Code.VALUE);
    }
    var html = one("q", "<script>\"&'😀");
    assertTrue(html.isValid());
    assertEquals(Optional.of("<script>\"&'😀"), html.toRequest().bodyKeyword());
  }

  @Test
  void web217BindingAllowlist() {
    for (String name : List.of("", "Q", "owner", "_csrf", "page[]")) {
      var f = one(name, "x");
      assertEquals(Map.of(Field.FORM, Code.BINDING), f.getIssues());
      assertThrows(IllegalStateException.class, f::toRequest);
    }
    for (String name :
        List.of(
            "q", GAME_FIELD, SPEAKER_FIELD, "chapter", ENTRY_TYPE_FIELD, VOICE_FIELD, PAGE_FIELD)) {
      for (List<String> values : List.of(List.<String>of(), List.of("a", "b"))) {
        var f = ScenarioSearchForm.bind(Map.of(name, values));
        assertFalse(f.isValid());
        assertEquals(1, f.getIssues().size());
        assertTrue(f.getIssues().containsValue(Code.BINDING));
      }
    }
  }

  @Test
  void web218PageBoundaries() {
    var valid =
        Map.of(
            "",
            1,
            "0",
            1,
            "-1",
            1,
            "-2147483648",
            1,
            "1",
            1,
            "999999",
            999999,
            "00012",
            12,
            "-0",
            1,
            " 2 ",
            2);
    valid.forEach(
        (input, expected) -> {
          var f = one(PAGE_FIELD, input);
          assertTrue(f.isValid(), input);
          assertEquals(expected.intValue(), f.getPage());
          assertEquals(expected.intValue(), f.toRequest().page());
        });
    for (String bad :
        List.of(
            "1000000",
            "2147483647",
            "2147483648",
            "-2147483649",
            "+1",
            "-",
            "1.0",
            "1e2",
            "１",
            "1 2",
            "9".repeat(300))) issue(PAGE_FIELD, bad, Field.PAGE, Code.VALUE);
  }

  @Test
  void web219InvalidCannotRequest() {
    var f =
        ScenarioSearchForm.bind(
            Map.of(
                "q",
                List.of("x".repeat(257)),
                GAME_FIELD,
                List.of("wrong"),
                VOICE_FIELD,
                List.of("present"),
                PAGE_FIELD,
                List.of("+1"),
                "owner",
                List.of("secret")));
    assertEquals(
        Map.of(
            Field.Q,
            Code.LENGTH,
            Field.GAME,
            Code.VALUE,
            Field.VOICE,
            Code.VALUE,
            Field.PAGE,
            Code.VALUE,
            Field.FORM,
            Code.BINDING),
        f.getIssues());
    var ex = assertThrows(IllegalStateException.class, f::toRequest);
    assertEquals("invalid search form", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
    assertEquals("ScenarioSearchForm[REDACTED]", f.toString());
  }

  @Test
  void web220NullOwnershipRedaction() {
    assertThrows(NullPointerException.class, () -> ScenarioSearchForm.bind(null));
    var map = new HashMap<String, List<String>>();
    map.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> ScenarioSearchForm.bind(map));
    map.clear();
    map.put("q", null);
    assertThrows(NullPointerException.class, () -> ScenarioSearchForm.bind(map));
    map.put("q", Arrays.asList((String) null));
    assertThrows(NullPointerException.class, () -> ScenarioSearchForm.bind(map));
    var input = new ArrayList<>(List.of("private-value"));
    map.put("q", input);
    var f = ScenarioSearchForm.bind(map);
    input.clear();
    map.clear();
    assertEquals(Optional.of("private-value"), f.toRequest().bodyKeyword());
    assertThrows(UnsupportedOperationException.class, () -> f.getValues().clear());
    assertThrows(UnsupportedOperationException.class, () -> f.getIssues().put(Field.Q, Code.VALUE));
    assertEquals("ScenarioSearchForm[REDACTED]", f.toString());
  }

  @Test
  void web221ConcurrentValidation()
      throws InterruptedException, ExecutionException, TimeoutException {
    var pool = Executors.newFixedThreadPool(8);
    try {
      var futures = new ArrayList<Future<?>>();
      for (int i = 1; i <= 64; i++) {
        int n = i;
        futures.add(
            pool.submit(
                () -> {
                  var f =
                      ScenarioSearchForm.bind(
                          Map.of("q", List.of("body-" + n), PAGE_FIELD, List.of("" + n)));
                  assertTrue(f.isValid());
                  assertEquals(Optional.of("body-" + n), f.toRequest().bodyKeyword());
                  assertEquals(n, f.toRequest().page());
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
