package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.Introspector;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** NK-WEB001/SCR008,009/FUN006/UI223,235/SS313,323/PG204/PT-WEB230..237. */
class AnimationViewModelTest {
  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "reader",
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  private static AnimationRecord record(
      String id, AnimationCategory category, Optional<String> parent, int order) {
    return new AnimationRecord(
        id,
        "title-" + id,
        category,
        DisplayPath.of("video/" + id.replace('/', '_') + ".mp4"),
        1048576,
        parent,
        order);
  }

  private static AnimationListViewModel list(
      AnimationListCategory category, List<AnimationRecord> records) {
    return AnimationListViewModel.from(
        actor(UserRole.USER), category, new AnimationListResponseData(records.size()), records);
  }

  private static List<AnimationRecord> main() {
    return List.of(
        record("sub-b", AnimationCategory.SUBTRACK, Optional.of("main-b"), 1),
        record("main-a", AnimationCategory.MAIN, Optional.empty(), 2),
        record("main-b", AnimationCategory.MAIN, Optional.empty(), 3),
        record("sub-a", AnimationCategory.SUBTRACK, Optional.of("main-a"), 4),
        record("main-c", AnimationCategory.MAIN, Optional.empty(), 5));
  }

  @Test
  void web230AnimationMenuCounts() {
    int[][] vectors = {
      {15, 4, 1, 20}, {0, 0, 0, 0}, {999, 0, 0, 999}, {998, 0, 1, 999}, {0, 999, 0, 999}
    };
    for (var role : UserRole.values())
      for (int[] v : vectors) {
        var m =
            AnimationMenuViewModel.from(
                actor(role), new AnimationMenuResponseData(v[0], v[1], v[2] == 1, v[3]));
        assertEquals(v[0], m.getMainCount());
        assertEquals(v[1], m.getOvaCount());
        assertEquals(v[2] == 1, m.isOpeningPresent());
        assertEquals(v[3], m.getTotalCount());
        assertEquals("reader", m.getTopBar().getUsername());
        assertEquals(role.wireValue(), m.getTopBar().getRole());
        assertEquals("AnimationMenuViewModel[REDACTED]", m.toString());
      }
    for (var data :
        List.of(
            new AnimationMenuResponseData(15, 4, true, 19),
            new AnimationMenuResponseData(0, 0, false, 1),
            new AnimationMenuResponseData(999, 999, true, 999)))
      assertThrows(
          IllegalArgumentException.class,
          () -> AnimationMenuViewModel.from(actor(UserRole.USER), data));
  }

  @Test
  void web231MainGrouping() {
    var m = list(AnimationListCategory.MAIN, main());
    assertEquals("メインパート一覧", m.getTitle());
    assertEquals("main", m.getSection());
    assertEquals(5, m.getTotalCount());
    assertEquals(
        List.of("title-main-a", "title-main-b", "title-main-c"),
        m.getRows().stream().map(r -> r.getMain().getTitle()).toList());
    assertEquals(
        List.of("title-sub-b", "title-main-a", "title-main-b", "title-sub-a", "title-main-c"),
        m.getVideos().stream().map(AnimationListViewModel.Video::getTitle).toList());
    assertEquals(
        "/animation/videos/sub-a", m.getRows().get(0).getSubtrack().orElseThrow().getHref());
    assertEquals(
        "/animation/videos/sub-b", m.getRows().get(1).getSubtrack().orElseThrow().getHref());
    assertTrue(m.getRows().get(2).getSubtrack().isEmpty());
    assertEquals("メインパート", m.getRows().get(0).getMain().getCategory());
    assertEquals("video/main-a.mp4", m.getRows().get(0).getMain().getDisplayPath());
    assertEquals(1048576, m.getRows().get(0).getMain().getByteSize());
  }

  @Test
  void web232OvaAndBounds() {
    for (var category : AnimationListCategory.values())
      for (int count : new int[] {0, 4, 50}) {
        var records = new ArrayList<AnimationRecord>();
        for (int i = 0; i < count; i++)
          records.add(
              record(
                  "v" + i,
                  category == AnimationListCategory.MAIN
                      ? AnimationCategory.MAIN
                      : AnimationCategory.OVA,
                  Optional.empty(),
                  i + 1));
        var m = list(category, records);
        assertEquals(count, m.getTotalCount());
        assertEquals(count, m.getVideos().size());
        assertEquals(category == AnimationListCategory.MAIN ? count : 0, m.getRows().size());
        if (category == AnimationListCategory.OVA) {
          assertEquals("OVA一覧", m.getTitle());
          assertEquals("ova", m.getSection());
        }
        if (count > 0) {
          assertEquals("title-v0", m.getVideos().getFirst().getTitle());
          assertEquals("title-v" + (count - 1), m.getVideos().getLast().getTitle());
          assertEquals(
              category == AnimationListCategory.OVA ? "OVA" : "メインパート",
              m.getVideos().getFirst().getCategory());
        }
      }
    var tooMany = new ArrayList<AnimationRecord>();
    for (int i = 0; i < 51; i++)
      tooMany.add(record("v" + i, AnimationCategory.OVA, Optional.empty(), i + 1));
    assertThrows(IllegalArgumentException.class, () -> list(AnimationListCategory.OVA, tooMany));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            AnimationListViewModel.from(
                actor(UserRole.USER),
                AnimationListCategory.MAIN,
                new AnimationListResponseData(0),
                main()));
  }

  @Test
  void web233RejectInconsistentGroups() {
    var main = record("main", AnimationCategory.MAIN, Optional.empty(), 1);
    var sub = record("sub", AnimationCategory.SUBTRACK, Optional.of("main"), 2);
    var ova = record("ova", AnimationCategory.OVA, Optional.empty(), 1);
    for (var records :
        List.of(
            List.of(ova),
            List.of(main, main),
            List.of(sub),
            List.of(record("sub", AnimationCategory.SUBTRACK, Optional.empty(), 1)),
            List.of(record("main", AnimationCategory.MAIN, Optional.of("parent"), 1)),
            List.of(main, sub, record("sub2", AnimationCategory.SUBTRACK, Optional.of("main"), 3)),
            List.of(main, sub, record("sub2", AnimationCategory.SUBTRACK, Optional.of("sub"), 3)),
            List.of(
                new AnimationRecord(
                    "main",
                    "title",
                    AnimationCategory.MAIN,
                    DisplayPath.of("video/a.mp4"),
                    0,
                    Optional.empty(),
                    1))))
      assertThrows(IllegalArgumentException.class, () -> list(AnimationListCategory.MAIN, records));
    assertThrows(
        IllegalArgumentException.class, () -> list(AnimationListCategory.OVA, List.of(main)));
    assertThrows(
        IllegalArgumentException.class, () -> list(AnimationListCategory.OVA, List.of(sub)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            list(
                AnimationListCategory.OVA,
                List.of(record("ova", AnimationCategory.OVA, Optional.of("main"), 1))));
    for (String id : List.of("", ".", "..")) {
      var r =
          new AnimationRecord(
              id,
              "title",
              AnimationCategory.MAIN,
              DisplayPath.of("video/a.mp4"),
              1,
              Optional.empty(),
              1);
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> list(AnimationListCategory.MAIN, List.of(r)));
      assertEquals("invalid animation link ID", failure.getMessage());
    }
  }

  @Test
  void web234NullAndOwnership() {
    var actor = actor(UserRole.USER);
    var counts = new AnimationMenuResponseData(0, 0, false, 0);
    assertThrows(NullPointerException.class, () -> AnimationMenuViewModel.from(null, counts));
    assertThrows(NullPointerException.class, () -> AnimationMenuViewModel.from(actor, null));
    var data = new AnimationListResponseData(0);
    assertThrows(
        NullPointerException.class,
        () -> AnimationListViewModel.from(null, AnimationListCategory.MAIN, data, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> AnimationListViewModel.from(actor, null, data, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> AnimationListViewModel.from(actor, AnimationListCategory.MAIN, null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> AnimationListViewModel.from(actor, AnimationListCategory.MAIN, data, null));
    assertThrows(
        NullPointerException.class,
        () ->
            AnimationListViewModel.from(
                actor, AnimationListCategory.MAIN, data, Arrays.asList((AnimationRecord) null)));
    var original = new ArrayList<>(main());
    var m = list(AnimationListCategory.MAIN, original);
    original.clear();
    assertEquals(5, m.getVideos().size());
    assertEquals(3, m.getRows().size());
    assertThrows(UnsupportedOperationException.class, () -> m.getVideos().clear());
    assertThrows(UnsupportedOperationException.class, () -> m.getRows().clear());
  }

  @Test
  void web235ClosedBeansAndRedaction() throws Exception {
    var m = list(AnimationListCategory.MAIN, main());
    closed(m);
    closed(
        AnimationMenuViewModel.from(
            actor(UserRole.USER), new AnimationMenuResponseData(15, 4, true, 20)));
    assertEquals("AnimationListViewModel[REDACTED]", m.toString());
    for (var video : m.getVideos()) assertEquals("AnimationVideo[REDACTED]", video.toString());
    for (var row : m.getRows()) assertEquals("AnimationRow[REDACTED]", row.toString());
    var r =
        new AnimationRecord(
            "日本/a?#%",
            "title",
            AnimationCategory.OVA,
            DisplayPath.of("video/a.mp4"),
            999999999999L,
            Optional.empty(),
            1);
    var special = list(AnimationListCategory.OVA, List.of(r)).getVideos().getFirst();
    assertEquals("/animation/videos/%E6%97%A5%E6%9C%AC%2Fa%3F%23%25", special.getHref());
    assertEquals(999999999999L, special.getByteSize());
  }

  @Test
  void web236SyntheticHtmlEscaping() {
    String text = "<img src=x onerror=alert(1)>";
    var actor =
        new SessionPrincipal(
            text,
            UserRole.USER,
            actor(UserRole.USER).authenticationContext(),
            actor(UserRole.USER).loginAt());
    var record =
        new AnimationRecord(
            "v1",
            text,
            AnimationCategory.OVA,
            DisplayPath.of("folder/<img>.mp4"),
            1,
            Optional.empty(),
            1);
    var m =
        AnimationListViewModel.from(
            actor, AnimationListCategory.OVA, new AnimationListResponseData(1), List.of(record));
    var engine = new SpringTemplateEngine();
    var resolver = new StringTemplateResolver();
    resolver.setTemplateMode("HTML");
    engine.setTemplateResolver(resolver);
    var dom =
        Jsoup.parse(
            engine.process(
                "<h1 th:text=\"\u0024{page.topBar.username}\"></h1><p th:text=\"\u0024{page.videos[0].title}\"></p><span th:text=\"\u0024{page.videos[0].displayPath}\"></span><a th:href=\"\u0024{page.videos[0].href}\">open</a>",
                new Context(Locale.ROOT, Map.of("page", m))));
    assertEquals(text, dom.select("h1").text());
    assertEquals(text, dom.select("p").text());
    assertEquals("folder/<img>.mp4", dom.select("span").text());
    assertEquals("/animation/videos/v1", dom.select("a").attr("href"));
    assertTrue(dom.select("img,script,[onerror]").isEmpty());
  }

  @Test
  void web237ConcurrentProjection() throws Exception {
    try (var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            executor.submit(
                () -> {
                  var actor =
                      new SessionPrincipal(
                          "reader" + n,
                          UserRole.USER,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          actor(UserRole.USER).loginAt());
                  var menu =
                      AnimationMenuViewModel.from(
                          actor, new AnimationMenuResponseData(n, 0, false, n));
                  assertEquals(n, menu.getTotalCount());
                  assertEquals("reader" + n, menu.getTopBar().getUsername());
                  var m =
                      AnimationListViewModel.from(
                          actor,
                          AnimationListCategory.MAIN,
                          new AnimationListResponseData(5),
                          main());
                  assertEquals("reader" + n, m.getTopBar().getUsername());
                  assertEquals(
                      "/animation/videos/sub-a",
                      m.getRows().getFirst().getSubtrack().orElseThrow().getHref());
                  return null;
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
    }
  }

  private static void closed(Object value) throws Exception {
    if (value instanceof String
        || value instanceof Integer
        || value instanceof Long
        || value instanceof Boolean) return;
    if (value instanceof List<?> list) {
      for (Object child : list) closed(child);
      return;
    }
    if (value instanceof Optional<?> optional) {
      if (optional.isPresent()) closed(optional.orElseThrow());
      return;
    }
    assertTrue(
        Set.of(
                AnimationMenuViewModel.class,
                AnimationListViewModel.class,
                AnimationListViewModel.Video.class,
                AnimationListViewModel.Row.class,
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
