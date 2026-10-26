package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.scenario.GameRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.Introspector;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** Independent literals; NK-WEB-001/FUN004/UI223,234/SS313/PG193/PT-WEB-182..193;015006. */
class ScenarioHierarchyViewModelTest {
  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "reader",
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-20T00:00:00Z"));
  }

  private static List<GameRecord> games() {
    return List.of(
        new GameRecord(GameCode.NUKITASHI_1, "NUKITASHI", 1),
        new GameRecord(GameCode.NUKITASHI_2, "NUKITASHI2", 2));
  }

  private static List<RouteRecord> routes() {
    return List.of(
        new RouteRecord(0, "未分類", 1),
        new RouteRecord(1, "共通ルート", 7),
        new RouteRecord(99, "未分類", 999999));
  }

  private static List<ScenarioFileRecord> files() {
    return List.of(
        new ScenarioFileRecord(new ScriptFileId(1), "第一章", DisplayPath.of("文章/T/01.utf8.txt"), 0),
        new ScenarioFileRecord(
            new ScriptFileId(999999999999L), "最終章", DisplayPath.of("文章/T/99.utf8.txt"), 999999));
  }

  @Test
  void web182GameDisplay() {
    for (var role : UserRole.values()) {
      var page = GameListViewModel.from(actor(role), games());
      assertEquals("reader", page.getTopBar().getUsername());
      assertEquals(
          switch (role) {
            case USER -> "USER";
            case ADMIN -> "ADMIN";
          },
          page.getTopBar().getRole());
      assertEquals(
          List.of("NUKITASHI1", "NUKITASHI2"),
          page.getGames().stream().map(GameListViewModel.Card::getCode).toList());
      assertEquals(
          List.of("NUKITASHI", "NUKITASHI2"),
          page.getGames().stream().map(GameListViewModel.Card::getTitle).toList());
      assertEquals(
          List.of("/scenarios/NUKITASHI1", "/scenarios/NUKITASHI2"),
          page.getGames().stream().map(GameListViewModel.Card::getHref).toList());
    }
  }

  @Test
  void web183RouteDisplay() {
    for (var game : GameCode.values()) {
      var page = RouteListViewModel.from(actor(UserRole.USER), game, routes());
      String literal = game == GameCode.NUKITASHI_1 ? "NUKITASHI1" : "NUKITASHI2";
      assertEquals(literal, page.getGame());
      assertEquals("/scenarios", page.getUpHref());
      assertEquals("reader", page.getTopBar().getUsername());
      assertEquals(
          List.of("00", "01", "99"),
          page.getRoutes().stream().map(RouteListViewModel.Card::getPrefix).toList());
      assertEquals(
          List.of("未分類", "共通ルート", "未分類"),
          page.getRoutes().stream().map(RouteListViewModel.Card::getRouteName).toList());
      assertEquals(
          List.of("00: 未分類", "01: 共通ルート", "99: 未分類"),
          page.getRoutes().stream().map(RouteListViewModel.Card::getTitle).toList());
      assertEquals(
          List.of(1, 7, 999999),
          page.getRoutes().stream().map(RouteListViewModel.Card::getFileCount).toList());
      assertEquals(
          List.of(
              "/scenarios/" + literal + "/00",
              "/scenarios/" + literal + "/01",
              "/scenarios/" + literal + "/99"),
          page.getRoutes().stream().map(RouteListViewModel.Card::getHref).toList());
    }
  }

  @Test
  void web184FileDisplay() {
    var page =
        ScenarioFileListViewModel.from(
            actor(UserRole.ADMIN), GameCode.NUKITASHI_2, 1, "共通ルート", files());
    assertEquals("ADMIN", page.getTopBar().getRole());
    assertEquals("NUKITASHI2", page.getGame());
    assertEquals("01", page.getPrefix());
    assertEquals("共通ルート", page.getRouteName());
    assertEquals("01: 共通ルート", page.getTitle());
    assertEquals("/scenarios/NUKITASHI2", page.getUpHref());
    assertEquals(
        List.of(1L, 999999999999L),
        page.getFiles().stream().map(ScenarioFileListViewModel.Card::getId).toList());
    assertEquals(
        List.of("第一章", "最終章"),
        page.getFiles().stream().map(ScenarioFileListViewModel.Card::getDisplayTitle).toList());
    assertEquals(
        List.of("文章/T/01.utf8.txt", "文章/T/99.utf8.txt"),
        page.getFiles().stream().map(ScenarioFileListViewModel.Card::getDisplayPath).toList());
    assertEquals(
        List.of(0, 999999),
        page.getFiles().stream().map(ScenarioFileListViewModel.Card::getEntryCount).toList());
    assertEquals(
        List.of("/scenarios/1", "/scenarios/999999999999"),
        page.getFiles().stream().map(ScenarioFileListViewModel.Card::getHref).toList());
  }

  @Test
  void web185NullBoundaries() {
    var p = actor(UserRole.USER);
    var g = GameCode.NUKITASHI_1;
    assertThrows(NullPointerException.class, () -> GameListViewModel.from(null, games()));
    assertThrows(NullPointerException.class, () -> GameListViewModel.from(p, null));
    assertThrows(
        NullPointerException.class,
        () -> GameListViewModel.from(p, Arrays.asList((GameRecord) null)));
    assertThrows(NullPointerException.class, () -> RouteListViewModel.from(null, g, routes()));
    assertThrows(NullPointerException.class, () -> RouteListViewModel.from(p, null, routes()));
    assertThrows(NullPointerException.class, () -> RouteListViewModel.from(p, g, null));
    assertThrows(
        NullPointerException.class,
        () -> RouteListViewModel.from(p, g, Arrays.asList((RouteRecord) null)));
    assertThrows(
        NullPointerException.class, () -> ScenarioFileListViewModel.from(null, g, 1, "r", files()));
    assertThrows(
        NullPointerException.class, () -> ScenarioFileListViewModel.from(p, null, 1, "r", files()));
    assertThrows(
        NullPointerException.class, () -> ScenarioFileListViewModel.from(p, g, 1, null, files()));
    assertThrows(
        NullPointerException.class, () -> ScenarioFileListViewModel.from(p, g, 1, "r", null));
    assertThrows(
        NullPointerException.class,
        () ->
            ScenarioFileListViewModel.from(p, g, 1, "r", Arrays.asList((ScenarioFileRecord) null)));
  }

  @Test
  void web186PrefixBoundaries() {
    for (int prefix : new int[] {-1, 100, Integer.MIN_VALUE, Integer.MAX_VALUE})
      fixed(
          "invalid route prefix",
          () ->
              ScenarioFileListViewModel.from(
                  actor(UserRole.USER), GameCode.NUKITASHI_1, prefix, "未分類", List.of()));
    assertEquals(
        "00",
        ScenarioFileListViewModel.from(
                actor(UserRole.USER), GameCode.NUKITASHI_1, 0, "未分類", List.of())
            .getPrefix());
    assertEquals(
        "99",
        ScenarioFileListViewModel.from(
                actor(UserRole.USER), GameCode.NUKITASHI_1, 99, "未分類", List.of())
            .getPrefix());
  }

  @Test
  void web187SnapshotOwnership() {
    var p = actor(UserRole.USER);
    var g = GameCode.NUKITASHI_1;
    var gs = new ArrayList<>(games());
    var rs = new ArrayList<>(routes());
    var fs = new ArrayList<>(files());
    var a = GameListViewModel.from(p, gs);
    var b = RouteListViewModel.from(p, g, rs);
    var c = ScenarioFileListViewModel.from(p, g, 1, "共通ルート", fs);
    gs.clear();
    rs.clear();
    fs.clear();
    assertEquals(2, a.getGames().size());
    assertEquals(3, b.getRoutes().size());
    assertEquals(2, c.getFiles().size());
    assertThrows(UnsupportedOperationException.class, () -> a.getGames().clear());
    assertThrows(UnsupportedOperationException.class, () -> b.getRoutes().clear());
    assertThrows(UnsupportedOperationException.class, () -> c.getFiles().clear());
  }

  @Test
  void web188ClosedBeanContract() throws Exception {
    var p = actor(UserRole.USER);
    var g = GameCode.NUKITASHI_1;
    closed(GameListViewModel.from(p, games()));
    closed(RouteListViewModel.from(p, g, routes()));
    closed(ScenarioFileListViewModel.from(p, g, 1, "共通ルート", files()));
  }

  @Test
  void web189SyntheticEscaping() {
    String text = "<img src=x onerror=alert(1)>";
    var engine = new SpringTemplateEngine();
    var resolver = new StringTemplateResolver();
    resolver.setTemplateMode("HTML");
    engine.setTemplateResolver(resolver);
    var p = actor(UserRole.USER);
    var g = GameCode.NUKITASHI_1;
    var a = GameListViewModel.from(p, List.of(new GameRecord(g, text, 1)));
    var b = RouteListViewModel.from(p, g, List.of(new RouteRecord(1, text, 1)));
    String path = "folder/<img>.txt";
    var c =
        ScenarioFileListViewModel.from(
            p,
            g,
            1,
            text,
            List.of(new ScenarioFileRecord(new ScriptFileId(1), text, DisplayPath.of(path), 1)));
    String[] templates = {
      "<span th:text=\"${page.games[0].title}\"></span>",
      "<span th:text=\"${page.routes[0].routeName}\"></span>",
      "<span th:text=\"${page.files[0].displayTitle}\"></span>",
      "<span th:text=\"${page.files[0].displayPath}\"></span>"
    };
    Object[] models = {a, b, c, c};
    String[] expected = {text, text, text, path};
    for (int i = 0; i < models.length; i++) {
      var dom =
          Jsoup.parse(
              engine.process(templates[i], new Context(Locale.ROOT, Map.of("page", models[i]))));
      assertEquals(expected[i], dom.select("span").text());
      assertTrue(dom.select("img,script").isEmpty());
    }
  }

  @Test
  void web190ConcurrentProjection() throws Exception {
    try (var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 100; i++) {
        final int n = i;
        tasks.add(
            executor.submit(
                () -> {
                  var p = actor(UserRole.USER);
                  var g = GameCode.NUKITASHI_1;
                  assertEquals(
                      "NUKITASHI",
                      GameListViewModel.from(p, games()).getGames().getFirst().getTitle());
                  assertEquals(
                      "01: 共通ルート",
                      RouteListViewModel.from(p, g, routes()).getRoutes().get(1).getTitle());
                  assertEquals(
                      String.format(Locale.ROOT, "%02d", n),
                      ScenarioFileListViewModel.from(p, g, n, "未分類", files()).getPrefix());
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
    }
  }

  @Test
  void web191ListSizeBoundaries() {
    var p = actor(UserRole.USER);
    var g = GameCode.NUKITASHI_1;
    assertTrue(GameListViewModel.from(p, List.of()).getGames().isEmpty());
    assertTrue(RouteListViewModel.from(p, g, List.of()).getRoutes().isEmpty());
    assertTrue(ScenarioFileListViewModel.from(p, g, 1, "r", List.of()).getFiles().isEmpty());
    assertEquals(
        10,
        GameListViewModel.from(p, Collections.nCopies(10, games().getFirst())).getGames().size());
    assertEquals(
        50,
        RouteListViewModel.from(p, g, Collections.nCopies(50, routes().getFirst()))
            .getRoutes()
            .size());
    assertEquals(
        500,
        ScenarioFileListViewModel.from(p, g, 1, "r", Collections.nCopies(500, files().getFirst()))
            .getFiles()
            .size());
    fixed(
        "invalid game list size",
        () -> GameListViewModel.from(p, Collections.nCopies(11, games().getFirst())));
    fixed(
        "invalid route list size",
        () -> RouteListViewModel.from(p, g, Collections.nCopies(51, routes().getFirst())));
    fixed(
        "invalid file list size",
        () ->
            ScenarioFileListViewModel.from(
                p, g, 1, "r", Collections.nCopies(501, files().getFirst())));
  }

  @Test
  void web192PreserveSourceOrder() {
    var p = actor(UserRole.USER);
    var g = GameCode.NUKITASHI_1;
    assertEquals(
        List.of("NUKITASHI2", "NUKITASHI"),
        GameListViewModel.from(p, games().reversed()).getGames().stream()
            .map(GameListViewModel.Card::getTitle)
            .toList());
    assertEquals(
        List.of("99", "01", "00"),
        RouteListViewModel.from(p, g, routes().reversed()).getRoutes().stream()
            .map(RouteListViewModel.Card::getPrefix)
            .toList());
    assertEquals(
        List.of("最終章", "第一章"),
        ScenarioFileListViewModel.from(p, g, 1, "未知名", files().reversed()).getFiles().stream()
            .map(ScenarioFileListViewModel.Card::getDisplayTitle)
            .toList());
    assertEquals(
        "任意API表示名",
        RouteListViewModel.from(p, g, List.of(new RouteRecord(1, "任意API表示名", 1)))
            .getRoutes()
            .getFirst()
            .getRouteName());
  }

  @Test
  void web193RedactedDiagnostics() {
    var p = actor(UserRole.USER);
    var g = GameCode.NUKITASHI_1;
    var a = GameListViewModel.from(p, games());
    var b = RouteListViewModel.from(p, g, routes());
    var c = ScenarioFileListViewModel.from(p, g, 1, "r", files());
    assertEquals("GameListViewModel[REDACTED]", a.toString());
    assertEquals("GameCard[REDACTED]", a.getGames().getFirst().toString());
    assertEquals("RouteListViewModel[REDACTED]", b.toString());
    assertEquals("RouteCard[REDACTED]", b.getRoutes().getFirst().toString());
    assertEquals("ScenarioFileListViewModel[REDACTED]", c.toString());
    assertEquals("ScenarioFileCard[REDACTED]", c.getFiles().getFirst().toString());
  }

  private static void fixed(String message, org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(IllegalArgumentException.class, operation);
    assertEquals(message, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void closed(Object value) throws Exception {
    if (value instanceof String || value instanceof Integer || value instanceof Long) return;
    if (value instanceof List<?> list) {
      for (Object child : list) closed(child);
      return;
    }
    assertTrue(
        Set.of(
                GameListViewModel.class,
                GameListViewModel.Card.class,
                RouteListViewModel.class,
                RouteListViewModel.Card.class,
                ScenarioFileListViewModel.class,
                ScenarioFileListViewModel.Card.class,
                TopBarViewModel.class)
            .contains(value.getClass()));
    var properties =
        Introspector.getBeanInfo(value.getClass(), Object.class).getPropertyDescriptors();
    assertTrue(properties.length > 0);
    for (var property : properties) {
      assertNull(property.getWriteMethod());
      Object child = property.getReadMethod().invoke(value);
      assertNotNull(child);
      closed(child);
    }
  }
}
