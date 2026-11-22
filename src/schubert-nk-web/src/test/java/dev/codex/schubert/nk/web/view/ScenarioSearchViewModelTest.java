package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.SpeakerId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.IntrospectionException;
import java.beans.Introspector;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.stream.IntStream;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** Independent Current/UI/SS literal oracles; PG200/015014/PT-WEB222..229. */
class ScenarioSearchViewModelTest {
  private static final String PAGE_KEY = "page";
  private static final String GAME_FIELD_NAME = "game";
  private static final String SPEAKER_FIELD_NAME = "speaker";
  private static final String CHAPTER_FIELD_NAME = "chapter";
  private static final String ENTRY_TYPE_FIELD_NAME = "entry_type";
  private static final String VOICE_FIELD_NAME = "voice";
  private static final String INVALID_INPUT_MESSAGE = "入力値を確認してください。";

  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(
        name, role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static ScenarioSearchForm form(String q, String page) {
    return ScenarioSearchForm.bind(Map.of("q", List.of(q), PAGE_KEY, List.of(page)));
  }

  private static List<GameRecord> games() {
    return List.of(
        new GameRecord(GameCode.NUKITASHI_2, "title2", 1),
        new GameRecord(GameCode.NUKITASHI_1, "title1", 2));
  }

  private static List<SpeakerRecord> speakers() {
    return List.of(
        new SpeakerRecord(new SpeakerId(7), "乙", 9), new SpeakerRecord(new SpeakerId(3), "甲", 2));
  }

  private static ScenarioSearchRecord row(int id, String body) {
    return new ScenarioSearchRecord(
        new EntryId(id),
        new ScriptFileId(23),
        GameCode.NUKITASHI_1,
        Optional.empty(),
        id,
        EntryType.NARRATION,
        Optional.empty(),
        body,
        false,
        Optional.empty(),
        DisplayPath.of("scenario/23.txt"),
        Optional.empty());
  }

  private static PagedResponseData data(int page, long total) {
    return new PagedResponseData(
        page,
        100,
        total,
        (int) Math.max(1, (total + 99) / 100),
        total == 0 ? 0 : (page - 1L) * 100 + 1,
        Math.min(page * 100L, total));
  }

  private static List<ScenarioSearchRecord> rows(int page, int total) {
    int count = Math.min(100, Math.max(0, total - (page - 1) * 100));
    return IntStream.rangeClosed(1, count).mapToObj(i -> row(i, "body-" + i)).toList();
  }

  private static ScenarioSearchViewModel view(ScenarioSearchForm form, int page, int total) {
    return ScenarioSearchViewModel.success(
        actor("reader", UserRole.USER),
        form,
        games(),
        speakers(),
        data(page, total),
        rows(page, total));
  }

  @Test
  void web222SuccessfulSnapshot() {
    for (UserRole role : UserRole.values()) {
      var f =
          ScenarioSearchForm.bind(
              Map.of(
                  "q",
                  List.of("本文"),
                  GAME_FIELD_NAME,
                  List.of("NUKITASHI2"),
                  SPEAKER_FIELD_NAME,
                  List.of("乙"),
                  CHAPTER_FIELD_NAME,
                  List.of("章"),
                  ENTRY_TYPE_FIELD_NAME,
                  List.of("dialogue"),
                  VOICE_FIELD_NAME,
                  List.of("with")));
      var v =
          ScenarioSearchViewModel.success(
              actor("reader", role),
              f,
              games(),
              speakers(),
              data(1, 2),
              List.of(row(9, "first"), row(3, "second")));
      assertEquals("reader", v.getTopBar().getUsername());
      assertEquals(role.name(), v.getTopBar().getRole());
      assertEquals("schubert NK", v.getTopBar().getBrand());
      assertEquals(List.of("NUKITASHI2", "NUKITASHI1"), v.getGames());
      assertEquals(List.of("乙", "甲"), v.getSpeakers());
      assertTrue(v.getErrors().isEmpty());
      var filters = v.getFilters();
      assertEquals("本文", filters.getQ());
      assertEquals("NUKITASHI2", filters.getGame());
      assertEquals("乙", filters.getSpeaker());
      assertEquals("章", filters.getChapter());
      assertEquals("dialogue", filters.getEntryType());
      assertEquals("with", filters.getVoice());
      assertEquals(
          List.of(9L, 3L),
          v.getResults().orElseThrow().getRows().stream()
              .map(ScenarioSearchResultsViewModel.Row::getEntryId)
              .toList());
      assertEquals(
          List.of("first", "second"),
          v.getResults().orElseThrow().getRows().stream()
              .map(ScenarioSearchResultsViewModel.Row::getBody)
              .toList());
    }
  }

  @Test
  void web223PaginationUrls() {
    String prefix = "/search?q=&game=&speaker=&chapter=&entry_type=&voice=&page=";
    for (int total : new int[] {0, 1, 100}) {
      var v = view(form("", "1"), 1, total);
      assertTrue(v.getPreviousHref().isEmpty());
      assertTrue(v.getNextHref().isEmpty());
      assertEquals(total, v.getResults().orElseThrow().getPage().getTotalCount());
    }
    var first = view(form("", "1"), 1, 201);
    assertTrue(first.getPreviousHref().isEmpty());
    assertEquals(Optional.of(prefix + "2"), first.getNextHref());
    var middle = view(form("", "2"), 2, 201);
    assertEquals(Optional.of(prefix + "1"), middle.getPreviousHref());
    assertEquals(Optional.of(prefix + "3"), middle.getNextHref());
    var last = view(form("", "999999"), 3, 201);
    assertEquals(Optional.of(prefix + "2"), last.getPreviousHref());
    assertTrue(last.getNextHref().isEmpty());
  }

  @Test
  void web224QueryEncoding() {
    var f =
        ScenarioSearchForm.bind(
            Map.of(
                "q",
                List.of("a +&=\"#%日本😀"),
                GAME_FIELD_NAME,
                List.of("NUKITASHI1"),
                SPEAKER_FIELD_NAME,
                List.of("A&B"),
                CHAPTER_FIELD_NAME,
                List.of("x/y?"),
                ENTRY_TYPE_FIELD_NAME,
                List.of("narration"),
                VOICE_FIELD_NAME,
                List.of("without"),
                PAGE_KEY,
                List.of("2")));
    var v = view(f, 2, 201);
    String prefix =
        "/search?q=a%20%2B%26%3D%22%23%25%E6%97%A5%E6%9C%AC%F0%9F%98%80"
            + "&game=NUKITASHI1&speaker=A%26B&chapter=x%2Fy%3F&entry_type=narration&voice=without&page=";
    assertEquals(Optional.of(prefix + "1"), v.getPreviousHref());
    assertEquals(Optional.of(prefix + "3"), v.getNextHref());
  }

  @Test
  void web225ResponseBindingAndBounds() {
    assertThrows(IllegalArgumentException.class, () -> view(form("", "1"), 2, 101));
    var manyGames = new ArrayList<>(Collections.nCopies(10, games().getFirst()));
    var manySpeakers =
        new ArrayList<>(
            IntStream.range(0, 500)
                .mapToObj(i -> new SpeakerRecord(new SpeakerId(i + 1), "s" + i, 500 - i))
                .toList());
    var valid =
        ScenarioSearchViewModel.success(
            actor("r", UserRole.USER),
            form("", "1"),
            manyGames,
            manySpeakers,
            data(1, 0),
            List.of());
    assertEquals(10, valid.getGames().size());
    assertEquals(500, valid.getSpeakers().size());
    assertEquals("s499", valid.getSpeakers().getLast());
    manyGames.add(games().getFirst());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ScenarioSearchViewModel.success(
                actor("r", UserRole.USER),
                form("", "1"),
                manyGames,
                manySpeakers,
                data(1, 0),
                List.of()));
    manyGames.removeLast();
    manySpeakers.add(speakers().getFirst());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ScenarioSearchViewModel.success(
                actor("r", UserRole.USER),
                form("", "1"),
                manyGames,
                manySpeakers,
                data(1, 0),
                List.of()));
    assertThrows(IllegalArgumentException.class, () -> view(form("", "+1"), 1, 0));
  }

  @Test
  void web226InvalidFieldDisplay() {
    var f =
        ScenarioSearchForm.bind(
            Map.of(
                "q",
                List.of("a".repeat(257)),
                SPEAKER_FIELD_NAME,
                List.of("b".repeat(129)),
                CHAPTER_FIELD_NAME,
                List.of("c".repeat(257)),
                GAME_FIELD_NAME,
                List.of("wrong"),
                ENTRY_TYPE_FIELD_NAME,
                List.of("unknown"),
                VOICE_FIELD_NAME,
                List.of("bad"),
                PAGE_KEY,
                List.of("+1"),
                "unknown-private-name",
                List.of("private")));
    var v = ScenarioSearchViewModel.invalid(actor("r", UserRole.ADMIN), f);
    assertEquals(
        List.of(
            "form",
            "q",
            GAME_FIELD_NAME,
            SPEAKER_FIELD_NAME,
            CHAPTER_FIELD_NAME,
            ENTRY_TYPE_FIELD_NAME,
            VOICE_FIELD_NAME,
            PAGE_KEY),
        v.getErrors().stream().map(ScenarioSearchViewModel.FieldError::getName).toList());
    assertEquals(
        List.of(
            "入力項目を確認してください。",
            "本文はUTF-8で256 byte以内にしてください。",
            INVALID_INPUT_MESSAGE,
            "話者はUTF-8で128 byte以内にしてください。",
            "章タイトルはUTF-8で256 byte以内にしてください。",
            INVALID_INPUT_MESSAGE,
            INVALID_INPUT_MESSAGE,
            INVALID_INPUT_MESSAGE),
        v.getErrors().stream().map(ScenarioSearchViewModel.FieldError::getMessage).toList());
    assertEquals("a".repeat(257), v.getFilters().getQ());
    assertEquals(List.of("wrong"), v.getGames());
    assertEquals(List.of("b".repeat(129)), v.getSpeakers());
    assertTrue(v.getResults().isEmpty());
    assertTrue(v.getPreviousHref().isEmpty());
    assertTrue(v.getNextHref().isEmpty());
    var control = ScenarioSearchViewModel.invalid(actor("r", UserRole.USER), form("\n", "1"));
    assertEquals("使用できない文字が含まれています。", control.getErrors().getFirst().getMessage());
    assertEquals("", control.getFilters().getQ());
    assertTrue(control.getGames().isEmpty());
    assertTrue(control.getSpeakers().isEmpty());
    assertThrows(
        IllegalArgumentException.class,
        () -> ScenarioSearchViewModel.invalid(actor("r", UserRole.USER), form("", "1")));
  }

  @Test
  void web227NullAndOwnership() {
    var actor = actor("r", UserRole.USER);
    var f = form("", "1");
    var d = data(1, 1);
    assertThrows(
        NullPointerException.class,
        () ->
            ScenarioSearchViewModel.success(null, f, games(), speakers(), d, List.of(row(1, "x"))));
    assertThrows(
        NullPointerException.class,
        () ->
            ScenarioSearchViewModel.success(
                actor, null, games(), speakers(), d, List.of(row(1, "x"))));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioSearchViewModel.success(actor, f, null, speakers(), d, List.of(row(1, "x"))));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioSearchViewModel.success(actor, f, games(), null, d, List.of(row(1, "x"))));
    assertThrows(
        NullPointerException.class,
        () ->
            ScenarioSearchViewModel.success(
                actor, f, games(), speakers(), null, List.of(row(1, "x"))));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioSearchViewModel.success(actor, f, games(), speakers(), d, null));
    assertThrows(
        NullPointerException.class,
        () ->
            ScenarioSearchViewModel.success(
                actor, f, Arrays.asList((GameRecord) null), speakers(), d, List.of(row(1, "x"))));
    assertThrows(
        NullPointerException.class,
        () ->
            ScenarioSearchViewModel.success(
                actor, f, games(), Arrays.asList((SpeakerRecord) null), d, List.of(row(1, "x"))));
    assertThrows(
        NullPointerException.class,
        () ->
            ScenarioSearchViewModel.success(
                actor, f, games(), speakers(), d, Arrays.asList((ScenarioSearchRecord) null)));
    assertThrows(NullPointerException.class, () -> ScenarioSearchViewModel.invalid(actor, null));
    assertThrows(
        NullPointerException.class, () -> ScenarioSearchViewModel.invalid(null, form("", "+1")));
    var g = new ArrayList<>(games());
    var s = new ArrayList<>(speakers());
    var r = new ArrayList<>(List.of(row(1, "original")));
    var v = ScenarioSearchViewModel.success(actor, f, g, s, d, r);
    g.clear();
    s.clear();
    r.clear();
    assertEquals(2, v.getGames().size());
    assertEquals(2, v.getSpeakers().size());
    assertEquals("original", v.getResults().orElseThrow().getRows().getFirst().getBody());
    assertThrows(UnsupportedOperationException.class, () -> v.getGames().clear());
    assertThrows(UnsupportedOperationException.class, () -> v.getSpeakers().clear());
    assertThrows(UnsupportedOperationException.class, () -> v.getErrors().clear());
  }

  private static void beans(Class<?> type, Set<String> expected) throws IntrospectionException {
    var properties = Introspector.getBeanInfo(type, Object.class).getPropertyDescriptors();
    assertEquals(
        expected,
        Arrays.stream(properties)
            .map(p -> p.getName())
            .collect(java.util.stream.Collectors.toSet()));
    for (var p : properties) assertNull(p.getWriteMethod());
    for (var field : type.getDeclaredFields()) {
      assertFalse(field.getType().getName().startsWith("dev.codex.schubert.nk.protocol"));
      assertNotEquals(ScenarioSearchForm.class, field.getType());
      assertNotEquals(SessionPrincipal.class, field.getType());
    }
  }

  @Test
  void web228ClosedBeansAndRedaction() throws IntrospectionException {
    beans(
        ScenarioSearchViewModel.class,
        Set.of(
            "topBar",
            "filters",
            "games",
            "speakers",
            "errors",
            "results",
            "previousHref",
            "nextHref"));
    beans(
        ScenarioSearchViewModel.Filters.class,
        Set.of(
            "q",
            GAME_FIELD_NAME,
            SPEAKER_FIELD_NAME,
            CHAPTER_FIELD_NAME,
            "entryType",
            VOICE_FIELD_NAME));
    beans(ScenarioSearchViewModel.FieldError.class, Set.of("name", "message"));
    var v = view(form("<script>&\"", "1"), 1, 101);
    assertEquals("ScenarioSearchViewModel[REDACTED]", v.toString());
    assertEquals("SearchFilters[REDACTED]", v.getFilters().toString());
    var invalid = ScenarioSearchViewModel.invalid(actor("r", UserRole.USER), form("", "+1"));
    assertEquals("SearchFieldError[REDACTED]", invalid.getErrors().getFirst().toString());
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(new StringTemplateResolver());
    var context = new Context();
    context.setVariable(PAGE_KEY, v);
    var doc =
        Jsoup.parse(
            engine.process(
                "<p th:text='${page.filters.q}'></p><a"
                    + " th:href='${page.nextHref.orElseThrow()}'>次</a>",
                context));
    assertEquals("<script>&\"", doc.selectFirst("p").text());
    assertTrue(doc.select("script").isEmpty());
    assertEquals(
        "/search?q=%3Cscript%3E%26%22&game=&speaker=&chapter=&entry_type=&voice=&page=2",
        doc.selectFirst("a").attr("href"));
  }

  @Test
  void web229ConcurrentSnapshots()
      throws InterruptedException, ExecutionException, TimeoutException {
    var pool = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 1; i <= 64; i++) {
        int n = i;
        tasks.add(
            pool.submit(
                () -> {
                  var v =
                      ScenarioSearchViewModel.success(
                          actor("user-" + n, UserRole.USER),
                          form("q-" + n, "1"),
                          games(),
                          speakers(),
                          data(1, 1),
                          List.of(row(n, "body-" + n)));
                  assertEquals("user-" + n, v.getTopBar().getUsername());
                  assertEquals("q-" + n, v.getFilters().getQ());
                  assertEquals(
                      "body-" + n, v.getResults().orElseThrow().getRows().getFirst().getBody());
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
