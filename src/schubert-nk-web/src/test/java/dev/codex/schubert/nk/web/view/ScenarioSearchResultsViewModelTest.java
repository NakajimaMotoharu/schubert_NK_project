package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.IntrospectionException;
import java.beans.Introspector;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** Independent literal oracles: PG198/FUN003/UI223,234/SS313/015010/PT-WEB206..213. */
class ScenarioSearchResultsViewModelTest {
  private static final String READER_USERNAME = "reader";
  private static final String SCENARIO_BODY_TEXT = "本文<&>";

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        READER_USERNAME, role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static ScenarioSearchRecord record(long id, boolean voice) {
    return record(
        id,
        voice,
        voice,
        voice,
        voice ? EntryType.DIALOGUE : EntryType.NARRATION,
        GameCode.NUKITASHI_1,
        17,
        SCENARIO_BODY_TEXT);
  }

  private static ScenarioSearchRecord record(
      long id,
      boolean voice,
      boolean audioId,
      boolean audioPath,
      EntryType type,
      GameCode game,
      int line,
      String body) {
    return new ScenarioSearchRecord(
        new EntryId(id),
        new ScriptFileId(23),
        game,
        voice ? Optional.of("章<script>") : Optional.empty(),
        line,
        type,
        voice ? Optional.of("話者<img>") : Optional.empty(),
        body,
        voice,
        audioId ? Optional.of(new AudioId(71)) : Optional.empty(),
        DisplayPath.of("文章/01.txt"),
        audioPath ? Optional.of(DisplayPath.of("音声/71.ogg")) : Optional.empty());
  }

  private static PagedResponseData data(int count) {
    return new PagedResponseData(1, 100, count, 1, count == 0 ? 0 : 1, count);
  }

  private static ScenarioSearchResultsViewModel page(List<ScenarioSearchRecord> rows) {
    return ScenarioSearchResultsViewModel.from(actor(UserRole.USER), data(rows.size()), rows);
  }

  @Test
  void web206LiteralRowsAndAudio() {
    for (var role : UserRole.values())
      for (var game : GameCode.values()) {
        var records =
            List.of(
                record(9, true, true, true, EntryType.DIALOGUE, game, 17, SCENARIO_BODY_TEXT),
                record(3, false));
        var result = ScenarioSearchResultsViewModel.from(actor(role), data(2), records);
        assertEquals(READER_USERNAME, result.getTopBar().getUsername());
        assertEquals(role == UserRole.USER ? "USER" : "ADMIN", result.getTopBar().getRole());
        assertEquals(
            List.of(9L, 3L),
            result.getRows().stream().map(ScenarioSearchResultsViewModel.Row::getEntryId).toList());
        var row = result.getRows().getFirst();
        assertEquals(23, row.getScriptFileId());
        assertEquals(game == GameCode.NUKITASHI_1 ? "NUKITASHI1" : "NUKITASHI2", row.getGame());
        assertEquals("章<script>", row.getChapterTitle());
        assertEquals(17, row.getLineNumber());
        assertEquals("セリフ", row.getEntryTypeLabel());
        assertEquals("話者<img>", row.getSpeaker());
        assertEquals(SCENARIO_BODY_TEXT, row.getBody());
        assertEquals("文章/01.txt", row.getScriptDisplayPath());
        assertEquals("/scenarios/23#entry-9", row.getScenarioHref());
        var audio = row.getAudio().orElseThrow();
        assertEquals(71, audio.getId());
        assertEquals("音声/71.ogg", audio.getDisplayPath());
        assertEquals("/audio/71", audio.getHref());
        assertEquals("/audio/71/download", audio.getDownloadHref());
        var silent = result.getRows().get(1);
        assertEquals("ナレーション", silent.getEntryTypeLabel());
        assertEquals("", silent.getChapterTitle());
        assertEquals("", silent.getSpeaker());
        assertTrue(silent.getAudio().isEmpty());
      }
  }

  @Test
  void web207PageBounds() {
    var values = new ArrayList<ScenarioSearchRecord>();
    for (int i = 1; i <= 100; i++) values.add(record(i, false));
    var empty = page(List.of());
    assertTrue(empty.getRows().isEmpty());
    assertTrue(empty.getPage().isEmpty());
    assertEquals(1, empty.getPage().getTotalPages());
    var first =
        ScenarioSearchResultsViewModel.from(
            actor(UserRole.USER), new PagedResponseData(1, 100, 201, 3, 1, 100), values);
    assertEquals(100, first.getRows().size());
    assertEquals(1, first.getPage().getFirstResult());
    assertEquals(100, first.getPage().getLastResult());
    var middle =
        ScenarioSearchResultsViewModel.from(
            actor(UserRole.USER), new PagedResponseData(2, 100, 201, 3, 101, 200), values);
    assertEquals(100, middle.getRows().size());
    assertEquals(2, middle.getPage().getEffectivePage());
    var last =
        ScenarioSearchResultsViewModel.from(
            actor(UserRole.USER),
            new PagedResponseData(3, 100, 201, 3, 201, 201),
            List.of(record(3, false)));
    assertEquals(1, last.getRows().size());
    assertEquals(201, last.getPage().getLastResult());
    var max =
        ScenarioSearchResultsViewModel.from(
            actor(UserRole.USER),
            new PagedResponseData(999999, 100, 99999801, 999999, 99999801, 99999801),
            List.of(record(999999999999L, false)));
    assertEquals(999999, max.getPage().getEffectivePage());
    assertEquals(99999801, max.getPage().getTotalCount());
    assertEquals("/scenarios/23#entry-999999999999", max.getRows().getFirst().getScenarioHref());
  }

  @Test
  void web208PageRecordMismatch() {
    var values = new ArrayList<ScenarioSearchRecord>();
    for (int i = 1; i <= 101; i++) values.add(record(i, false));
    for (int size : List.of(99, 101))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              ScenarioSearchResultsViewModel.from(
                  actor(UserRole.USER), data(100), values.subList(0, size)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ScenarioSearchResultsViewModel.from(
                actor(UserRole.USER), data(0), List.of(record(1, false))));
    for (int size : List.of(0, 2))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              ScenarioSearchResultsViewModel.from(
                  actor(UserRole.USER),
                  new PagedResponseData(3, 100, 201, 3, 201, 201),
                  values.subList(0, size)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ScenarioSearchResultsViewModel.from(
                actor(UserRole.USER),
                new PagedResponseData(1, 50, 1, 1, 1, 1),
                List.of(record(1, false))));
  }

  @Test
  void web209AudioAndLineInvariants() {
    for (boolean present : List.of(false, true))
      for (boolean id : List.of(false, true))
        for (boolean path : List.of(false, true)) {
          var record =
              record(1, present, id, path, EntryType.DIALOGUE, GameCode.NUKITASHI_1, 1, "x");
          if (present == id && present == path)
            assertEquals(
                present, page(List.of(record)).getRows().getFirst().getAudio().isPresent());
          else assertThrows(IllegalArgumentException.class, () -> page(List.of(record)));
        }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            page(
                List.of(
                    record(
                        1,
                        false,
                        false,
                        false,
                        EntryType.NARRATION,
                        GameCode.NUKITASHI_1,
                        0,
                        "x"))));
    assertEquals(
        99999999,
        page(List.of(
                record(
                    1,
                    false,
                    false,
                    false,
                    EntryType.NARRATION,
                    GameCode.NUKITASHI_1,
                    99999999,
                    "x")))
            .getRows()
            .getFirst()
            .getLineNumber());
  }

  @Test
  void web210NullAndOwnership() {
    assertThrows(
        NullPointerException.class,
        () -> ScenarioSearchResultsViewModel.from(null, data(0), List.of()));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioSearchResultsViewModel.from(actor(UserRole.USER), null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioSearchResultsViewModel.from(actor(UserRole.USER), data(0), null));
    assertThrows(
        NullPointerException.class, () -> page(Arrays.asList((ScenarioSearchRecord) null)));
    var input = new ArrayList<>(List.of(record(1, false)));
    var result = page(input);
    input.clear();
    assertEquals(1, result.getRows().size());
    assertEquals(SCENARIO_BODY_TEXT, result.getRows().getFirst().getBody());
    assertThrows(UnsupportedOperationException.class, () -> result.getRows().clear());
  }

  @Test
  void web211ClosedBeansAndRedaction() throws IntrospectionException {
    Map<Class<?>, Set<String>> expected =
        Map.of(
            ScenarioSearchResultsViewModel.class, Set.of("topBar", "page", "rows"),
            ScenarioSearchResultsViewModel.Row.class,
                Set.of(
                    "entryId",
                    "scriptFileId",
                    "game",
                    "chapterTitle",
                    "lineNumber",
                    "entryTypeLabel",
                    "speaker",
                    "body",
                    "scriptDisplayPath",
                    "scenarioHref",
                    "audio"),
            ScenarioSearchResultsViewModel.Audio.class,
                Set.of("id", "displayPath", "href", "downloadHref"));
    for (var item : expected.entrySet()) {
      var actual = new HashSet<String>();
      for (var property :
          Introspector.getBeanInfo(item.getKey(), Object.class).getPropertyDescriptors()) {
        actual.add(property.getName());
        assertNull(property.getWriteMethod());
      }
      assertEquals(item.getValue(), actual);
      for (var field : item.getKey().getDeclaredFields()) {
        assertFalse(field.getGenericType().getTypeName().contains(".protocol."));
        assertFalse(field.getGenericType().getTypeName().contains("SessionPrincipal"));
      }
    }
    var result = page(List.of(record(1, true)));
    assertEquals("ScenarioSearchResultsViewModel[REDACTED]", result.toString());
    assertEquals("ScenarioSearchRow[REDACTED]", result.getRows().getFirst().toString());
    assertEquals(
        "ScenarioSearchAudio[REDACTED]",
        result.getRows().getFirst().getAudio().orElseThrow().toString());
  }

  @Test
  void web212SyntheticEscaping() {
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(new StringTemplateResolver());
    var context = new Context();
    context.setVariable("page", page(List.of(record(9, true), record(3, false))));
    var dom =
        Jsoup.parse(
            engine.process(
                "<article th:each='row : ${page.rows}'><h2 th:text='${row.chapterTitle}'></h2><span th:text='${row.speaker}'></span><p th:text='${row.body}'></p><a th:href='${row.scenarioHref}'>開く</a><audio th:if='${row.audio.present}' th:src='${row.audio.orElseThrow().href}'></audio></article>",
                context));
    assertEquals("章<script>", dom.select("h2").first().text());
    assertEquals("話者<img>", dom.select("span").first().text());
    assertEquals(List.of(SCENARIO_BODY_TEXT, SCENARIO_BODY_TEXT), dom.select("p").eachText());
    assertTrue(dom.select("script,img").isEmpty());
    assertEquals(
        List.of("/scenarios/23#entry-9", "/scenarios/23#entry-3"),
        dom.select("a").eachAttr("href"));
    assertEquals(List.of("/audio/71"), dom.select("audio").eachAttr("src"));
  }

  @Test
  void web213ConcurrentProjection()
      throws InterruptedException, ExecutionException, TimeoutException {
    var executor = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Future<ScenarioSearchResultsViewModel>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            executor.submit(
                () ->
                    ScenarioSearchResultsViewModel.from(
                        new SessionPrincipal(
                            READER_USERNAME + n,
                            UserRole.USER,
                            AuthenticationContext.of("b".repeat(64)),
                            Instant.EPOCH),
                        data(1),
                        List.of(
                            record(
                                n + 1,
                                false,
                                false,
                                false,
                                EntryType.NARRATION,
                                GameCode.NUKITASHI_1,
                                1,
                                "本文" + n)))));
      }
      for (int i = 0; i < 64; i++) {
        var result = tasks.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(READER_USERNAME + i, result.getTopBar().getUsername());
        assertEquals("本文" + i, result.getRows().getFirst().getBody());
        assertEquals(i + 1, result.getRows().getFirst().getEntryId());
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
