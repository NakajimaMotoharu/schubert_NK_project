package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.Introspector;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
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

/** SCR011/012/FUN007/UI223,235/SS313,323,352/PG208/PT-WEB246..253. */
class MusicHierarchyViewModelTest {
  private static final String FIXTURE_READER = "reader";
  private static final String FIXTURE_BGM = "BGM";
  private static final String FIXTURE_GAME_SECTION = "ゲーム";
  private static final String EXPECTED_TRACK_COUNT_PROPERTY = "trackCount";
  private static final String EXPECTED_HREF_PROPERTY = "href";
  private static final String FIXTURE_ESCAPED_TEXT = "<b>&";
  private static final int EXPECTED_CATEGORY_LIMIT = 20;
  private static final int EXPECTED_SECTION_LIMIT = 100;

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        FIXTURE_READER,
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  private static List<MusicCategoryRecord> categories() {
    return List.of(
        new MusicCategoryRecord("曲", 29),
        new MusicCategoryRecord(FIXTURE_BGM, 99),
        new MusicCategoryRecord("その他", 1));
  }

  private static List<MusicSectionRecord> sections() {
    return List.of(
        new MusicSectionRecord(FIXTURE_GAME_SECTION, 10),
        new MusicSectionRecord("アニメ", 15),
        new MusicSectionRecord("キャラクターソング", 4));
  }

  private static MusicCategoryViewModel categories(List<MusicCategoryRecord> r) {
    return MusicCategoryViewModel.from(
        actor(UserRole.USER), new MusicCategoryResponseData(r.size()), r);
  }

  private static MusicSectionViewModel sections(String category, List<MusicSectionRecord> r) {
    return MusicSectionViewModel.from(
        actor(UserRole.USER), category, new MusicSectionResponseData(r.size()), r);
  }

  @Test
  void web246CategorySnapshot() {
    for (var role : UserRole.values()) {
      var m =
          MusicCategoryViewModel.from(actor(role), new MusicCategoryResponseData(3), categories());
      assertEquals(129, m.getTrackCount());
      assertEquals(FIXTURE_READER, m.getTopBar().getUsername());
      assertEquals(
          switch (role) {
            case USER -> "USER";
            case ADMIN -> "ADMIN";
          },
          m.getTopBar().getRole());
      assertEquals(
          List.of("曲", FIXTURE_BGM, "その他"),
          m.getCategories().stream().map(MusicCategoryViewModel.Card::getName).toList());
      assertEquals(
          List.of(29, 99, 1),
          m.getCategories().stream().map(MusicCategoryViewModel.Card::getTrackCount).toList());
      assertEquals(
          List.of("/music/%E6%9B%B2", "/music/BGM", "/music/%E3%81%9D%E3%81%AE%E4%BB%96"),
          m.getCategories().stream().map(MusicCategoryViewModel.Card::getHref).toList());
    }
  }

  @Test
  void web247SectionSnapshot() {
    for (var role : UserRole.values()) {
      var m =
          MusicSectionViewModel.from(actor(role), "曲", new MusicSectionResponseData(3), sections());
      assertEquals("曲", m.getCategory());
      assertEquals(29, m.getTrackCount());
      assertEquals(
          switch (role) {
            case USER -> "USER";
            case ADMIN -> "ADMIN";
          },
          m.getTopBar().getRole());
      assertEquals(
          List.of(FIXTURE_GAME_SECTION, "アニメ", "キャラクターソング"),
          m.getSections().stream().map(MusicSectionViewModel.Card::getName).toList());
      assertEquals(
          List.of(10, 15, 4),
          m.getSections().stream().map(MusicSectionViewModel.Card::getTrackCount).toList());
      assertEquals(
          "/music/%E6%9B%B2/%E3%82%B2%E3%83%BC%E3%83%A0", m.getSections().getFirst().getHref());
    }
  }

  @Test
  void web248SizeAndCountBounds() {
    for (int n : new int[] {0, 1, 20, 21}) {
      var r = new ArrayList<MusicCategoryRecord>();
      for (int i = 0; i < n; i++) r.add(new MusicCategoryRecord("cat" + i, 999999));
      if (n > EXPECTED_CATEGORY_LIMIT)
        assertThrows(IllegalArgumentException.class, () -> categories(r));
      else {
        var m = categories(r);
        assertEquals(n, m.getCategories().size());
        assertEquals(n * 999999, m.getTrackCount());
      }
    }
    for (int n : new int[] {0, 1, 100, 101}) {
      var r = new ArrayList<MusicSectionRecord>();
      for (int i = 0; i < n; i++) r.add(new MusicSectionRecord("section" + i, 999999));
      if (n > EXPECTED_SECTION_LIMIT)
        assertThrows(IllegalArgumentException.class, () -> sections(FIXTURE_BGM, r));
      else {
        var m = sections(FIXTURE_BGM, r);
        assertEquals(n, m.getSections().size());
        assertEquals(n * 999999, m.getTrackCount());
      }
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicCategoryViewModel.from(
                actor(UserRole.USER), new MusicCategoryResponseData(1), List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicSectionViewModel.from(
                actor(UserRole.USER), FIXTURE_BGM, new MusicSectionResponseData(1), List.of()));
  }

  @Test
  void web249DuplicateAndSegment() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            categories(
                List.of(
                    new MusicCategoryRecord(FIXTURE_BGM, 1),
                    new MusicCategoryRecord(FIXTURE_BGM, 2))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            sections(
                "曲",
                List.of(
                    new MusicSectionRecord(FIXTURE_GAME_SECTION, 1),
                    new MusicSectionRecord(FIXTURE_GAME_SECTION, 2))));
    for (var bad : List.of("", ".", "..")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> categories(List.of(new MusicCategoryRecord(bad, 0))));
      assertThrows(IllegalArgumentException.class, () -> sections(bad, List.of()));
      assertThrows(
          IllegalArgumentException.class,
          () -> sections("曲", List.of(new MusicSectionRecord(bad, 0))));
    }
    var name = " 日本/a?#% ";
    assertEquals(
        name,
        categories(List.of(new MusicCategoryRecord(name, 0))).getCategories().getFirst().getName());
    assertEquals(
        "/music/%20%E6%97%A5%E6%9C%AC%2Fa%3F%23%25%20",
        categories(List.of(new MusicCategoryRecord(name, 0))).getCategories().getFirst().getHref());
    assertEquals(
        "/music/%20%E6%97%A5%E6%9C%AC%2Fa%3F%23%25%20/%20%E6%97%A5%E6%9C%AC%2Fa%3F%23%25%20",
        sections(name, List.of(new MusicSectionRecord(name, 0)))
            .getSections()
            .getFirst()
            .getHref());
  }

  @Test
  void web250NullAndOwnership() {
    var actor = actor(UserRole.USER);
    var cd = new MusicCategoryResponseData(0);
    var sd = new MusicSectionResponseData(0);
    assertThrows(
        NullPointerException.class, () -> MusicCategoryViewModel.from(null, cd, List.of()));
    assertThrows(
        NullPointerException.class, () -> MusicCategoryViewModel.from(actor, null, List.of()));
    assertThrows(NullPointerException.class, () -> MusicCategoryViewModel.from(actor, cd, null));
    assertThrows(
        NullPointerException.class,
        () -> MusicCategoryViewModel.from(actor, cd, Arrays.asList((MusicCategoryRecord) null)));
    assertThrows(
        NullPointerException.class,
        () -> MusicSectionViewModel.from(null, FIXTURE_BGM, sd, List.of()));
    assertThrows(
        NullPointerException.class, () -> MusicSectionViewModel.from(actor, null, sd, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> MusicSectionViewModel.from(actor, FIXTURE_BGM, null, List.of()));
    assertThrows(
        NullPointerException.class, () -> MusicSectionViewModel.from(actor, FIXTURE_BGM, sd, null));
    assertThrows(
        NullPointerException.class,
        () ->
            MusicSectionViewModel.from(
                actor, FIXTURE_BGM, sd, Arrays.asList((MusicSectionRecord) null)));
    var a = new ArrayList<>(categories());
    var b = new ArrayList<>(sections());
    var c = categories(a);
    var s = sections("曲", b);
    a.clear();
    b.clear();
    assertEquals(3, c.getCategories().size());
    assertEquals(3, s.getSections().size());
    assertThrows(UnsupportedOperationException.class, () -> c.getCategories().clear());
    assertThrows(UnsupportedOperationException.class, () -> s.getSections().clear());
  }

  @Test
  void web251ClosedBeansAndRedaction() throws Exception {
    var c = categories(categories());
    var s = sections("曲", sections());
    properties(c, Set.of("topBar", "categories", EXPECTED_TRACK_COUNT_PROPERTY));
    properties(s, Set.of("topBar", "category", "sections", EXPECTED_TRACK_COUNT_PROPERTY));
    properties(
        c.getCategories().getFirst(),
        Set.of("name", EXPECTED_HREF_PROPERTY, EXPECTED_TRACK_COUNT_PROPERTY));
    properties(
        s.getSections().getFirst(),
        Set.of("name", EXPECTED_HREF_PROPERTY, EXPECTED_TRACK_COUNT_PROPERTY));
    assertEquals("MusicCategoryViewModel[REDACTED]", c.toString());
    assertEquals("MusicSectionViewModel[REDACTED]", s.toString());
    assertEquals("MusicCategoryCard[REDACTED]", c.getCategories().getFirst().toString());
    assertEquals("MusicSectionCard[REDACTED]", s.getSections().getFirst().toString());
    for (var type :
        List.of(
            MusicCategoryViewModel.class,
            MusicSectionViewModel.class,
            MusicCategoryViewModel.Card.class,
            MusicSectionViewModel.Card.class))
      for (var field : type.getDeclaredFields())
        assertTrue(
            Set.of(TopBarViewModel.class, String.class, int.class, List.class)
                .contains(field.getType()));
  }

  @Test
  void web252SyntheticHtmlEscaping() {
    var p =
        new SessionPrincipal(
            FIXTURE_ESCAPED_TEXT,
            UserRole.USER,
            actor(UserRole.USER).authenticationContext(),
            actor(UserRole.USER).loginAt());
    var c =
        MusicCategoryViewModel.from(
            p,
            new MusicCategoryResponseData(1),
            List.of(new MusicCategoryRecord(FIXTURE_ESCAPED_TEXT, 1)));
    var s =
        MusicSectionViewModel.from(
            p,
            FIXTURE_ESCAPED_TEXT,
            new MusicSectionResponseData(1),
            List.of(new MusicSectionRecord(FIXTURE_ESCAPED_TEXT, 1)));
    var resolver = new StringTemplateResolver();
    resolver.setTemplateMode("HTML");
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var context = new Context(Locale.JAPAN, Map.of("category", c, "section", s));
    var dom =
        Jsoup.parse(
            engine.process(
                "<div><span th:text='${category.topBar.username}'></span><a id='c'"
                    + " th:href='${category.categories[0].href}'"
                    + " th:text='${category.categories[0].name}'></a><a id='s'"
                    + " th:href='${section.sections[0].href}'"
                    + " th:text='${section.sections[0].name}'></a></div>",
                context));
    assertEquals(FIXTURE_ESCAPED_TEXT, dom.select("span").text());
    assertEquals(FIXTURE_ESCAPED_TEXT, dom.select("#c").text());
    assertEquals(FIXTURE_ESCAPED_TEXT, dom.select("#s").text());
    assertEquals("/music/%3Cb%3E%26", dom.select("#c").attr(EXPECTED_HREF_PROPERTY));
    assertEquals("/music/%3Cb%3E%26/%3Cb%3E%26", dom.select("#s").attr(EXPECTED_HREF_PROPERTY));
    assertTrue(dom.select("b,script").isEmpty());
    assertFalse(dom.html().contains("a".repeat(64)));
  }

  @Test
  void web253ConcurrentProjection() throws Exception {
    var records = categories();
    var sections = sections();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            pool.submit(
                () -> {
                  var p =
                      new SessionPrincipal(
                          FIXTURE_READER + n,
                          UserRole.USER,
                          actor(UserRole.USER).authenticationContext(),
                          actor(UserRole.USER).loginAt());
                  var c = MusicCategoryViewModel.from(p, new MusicCategoryResponseData(3), records);
                  var s =
                      MusicSectionViewModel.from(
                          p, "category" + n, new MusicSectionResponseData(3), sections);
                  assertEquals(FIXTURE_READER + n, c.getTopBar().getUsername());
                  assertEquals(FIXTURE_READER + n, s.getTopBar().getUsername());
                  assertEquals(129, c.getTrackCount());
                  assertEquals(29, s.getTrackCount());
                  assertEquals(
                      "/music/category" + n + "/%E3%82%B2%E3%83%BC%E3%83%A0",
                      s.getSections().getFirst().getHref());
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(categories(), records);
    assertEquals(sections(), sections);
  }

  private static void properties(Object bean, Set<String> expected) throws Exception {
    var actual = new HashSet<String>();
    for (var property :
        Introspector.getBeanInfo(bean.getClass(), Object.class).getPropertyDescriptors())
      actual.add(property.getName());
    assertEquals(expected, actual);
  }
}
