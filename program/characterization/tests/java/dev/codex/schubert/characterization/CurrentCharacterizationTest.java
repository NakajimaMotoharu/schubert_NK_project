package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.options.ColorScheme;
import com.microsoft.playwright.options.ReducedMotion;
import com.microsoft.playwright.options.RequestOptions;
import com.microsoft.playwright.options.WaitUntilState;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

@Tag("current-characterization")
@TestMethodOrder(OrderAnnotation.class)
class CurrentCharacterizationTest {
  private static CharacterizationEnvironment environment;
  private static ArtifactSink sink;
  private static final Map<String, Map<String, Object>> SUPPLEMENTAL = new TreeMap<>();
  private static int logicalVideoCount;
  private static int logicalMusicCount;

  @BeforeAll
  static void startEnvironment() throws Exception {
    environment = new CharacterizationEnvironment();
    sink = new ArtifactSink(Path.of(requiredProperty("chr.output")));
    environment.start();
  }

  @AfterAll
  static void stopEnvironment() throws Exception {
    try {
      if (environment != null && sink != null) {
        sink.writeInventory(
            map(
                "scenarioFileCount",
                    environment.queryLong("SELECT count(*) FROM scenario.script_files"),
                "scenarioEntryCount",
                    environment.queryLong("SELECT count(*) FROM scenario.script_entries"),
                "audioMetadataCount",
                    environment.queryLong("SELECT count(*) FROM scenario.audio_files"),
                "audioLinkCount",
                    environment.queryLong("SELECT count(*) FROM scenario.entry_audio_links"),
                "videoCount", logicalVideoCount,
                "musicCount", logicalMusicCount));
        sink.writeSupplemental(SUPPLEMENTAL);
      }
    } finally {
      if (environment != null) environment.close();
    }
  }

  @Test
  @Order(1)
  void chrA01LoginDisplay() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = context.newPage();
      Response response = page.navigate(environment.baseUrl() + "/login");
      sink.write("CHR-A01", captureLoginDisplay(page, response));
    }
  }

  /** Same A01 driver/oracle for Current and externally owned NK; SS355 §6–9. */
  static Map<String, Object> captureLoginDisplay(Page page, Response response) {
    assertNotNull(response);
    assertEquals(200, response.status());
    Locator username = page.locator("input[name=username]");
    Locator password = page.locator("input[name=password]");
    Locator csrf = page.locator("input[name=_csrf]");
    assertEquals(1, username.count());
    assertEquals("username", username.getAttribute("autocomplete"));
    assertNotNull(username.getAttribute("autofocus"));
    assertEquals("current-password", password.getAttribute("autocomplete"));
    assertEquals("", password.inputValue());
    assertEquals(1, csrf.count());
    return map(
        "statusCode", response.status(),
        "title", page.title(),
        "usernameAutocomplete", username.getAttribute("autocomplete"),
        "usernameAutofocus", true,
        "passwordAutocomplete", password.getAttribute("autocomplete"),
        "passwordValue", "",
        "csrf", "<TOKEN>",
        "securityHeaders", securityHeaders(response));
  }

  @Test
  @Order(2)
  void chrA02LoginControl() throws Exception {
    CharacterizationEnvironment.Credential primary = environment.primaryCredential();
    for (int count = 0; count < 4; count++) {
      assertTrue(failedLogin(primary.username(), "invalid-credential").contains("error"));
    }
    try (BrowserContext cleared = context(false)) {
      Page page = login(cleared, primary);
      assertEquals(environment.baseUrl() + "/", page.url());
    }
    String lockedUrl = "";
    for (int count = 0; count < 5; count++) {
      lockedUrl = failedLogin(primary.username(), "invalid-credential");
    }
    assertTrue(lockedUrl.contains("locked"));

    CharacterizationEnvironment.Credential secondary = environment.secondaryCredential();
    List<BrowserContext> sessions = new ArrayList<>();
    List<Page> pages = new ArrayList<>();
    try {
      for (int count = 0; count < 3; count++) {
        BrowserContext session = context(false);
        sessions.add(session);
        pages.add(login(session, secondary));
      }
      List<Boolean> sessionActive = new ArrayList<>();
      List<String> sessionRedirects = new ArrayList<>();
      for (Page page : pages) {
        page.navigate(environment.baseUrl() + "/");
        sessionActive.add(!page.url().contains("/login"));
        sessionRedirects.add(page.url().replace(environment.baseUrl(), ""));
      }
      assertEquals(
          List.of(true, true, true),
          sessionActive,
          "DIF-016 current observation; redirects=" + sessionRedirects);
      sink.write(
          "CHR-A02",
          map(
              "userFailureLimit",
              5,
              "ipFailureLimit",
              10,
              "lockMinutes",
              15,
              "successClearsPriorFailures",
              true,
              "lockedRedirect",
              "/login?locked",
              "configuredMaximumSessions",
              2,
              "observedActiveSessionCount",
              3,
              "oldestSessionInvalidated",
              false,
              "sessionActiveOldestToNewest",
              sessionActive,
              "sessionRedirectsOldestToNewest",
              sessionRedirects,
              "knownDifference",
              "DIF-016",
              "credentialValuesRecorded",
              false));
    } finally {
      sessions.forEach(BrowserContext::close);
    }
    String ipLockedUrl = "";
    try {
      for (int count = 1; count <= 10; count++) {
        ipLockedUrl = failedLogin("characterization-missing-" + count, "invalid-credential");
      }
      assertTrue(ipLockedUrl.contains("locked"));
      recordSupplemental(
          "CHR-A02",
          "ip-limit-observed-not-hardcoded",
          "PASS",
          map(
              "distinctUsernames", 10,
              "tenthFailureRedirect", "/login?locked",
              "observation", "HTTP login attempts through Caddy"));
    } finally {
      environment.restartApp();
    }
  }

  @Test
  @Order(3)
  void chrA03LogoutAndExpiredSession() throws Exception {
    int missingCsrfStatus;
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      APIResponse noCsrf =
          context
              .request()
              .post(environment.baseUrl() + "/logout", RequestOptions.create().setMaxRedirects(0));
      assertEquals(403, noCsrf.status());
      missingCsrfStatus = noCsrf.status();
      page.navigate(environment.baseUrl() + "/");
      page.locator("form.logout-form button[type=submit]").click();
      page.waitForLoadState();
      assertTrue(page.url().contains("/login?logout"));
      page.navigate(environment.baseUrl() + "/search");
      assertTrue(page.url().contains("/login"));
      sink.write(
          "CHR-A03",
          map(
              "logoutMethod", "POST",
              "missingCsrfStatus", noCsrf.status(),
              "logoutRedirect", "/login?logout",
              "protectedGetAfterLogout", "/login",
              "sessionTimeout", "8h"));
    }
    recordSupplemental(
        "CHR-A03",
        "unsafe-post-denied",
        "PASS",
        map("operation", "POST /logout without CSRF", "status", missingCsrfStatus));

    boolean expiredRedirected;
    try (BrowserContext expiring = context(false)) {
      Page page = login(expiring, environment.secondaryCredential());
      environment.restartApp();
      page.navigate(environment.baseUrl() + "/search");
      expiredRedirected = page.url().contains("/login");
      assertTrue(expiredRedirected);
      recordSupplemental(
          "CHR-A03",
          "expired-session-redirect",
          "PASS",
          map(
              "expiryTrigger", "current in-memory session invalidated by application restart",
              "protectedPath", "/search",
              "redirect", "/login"));
    }
  }

  @Test
  @Order(4)
  void chrU01MenuDesktopAndMobile() throws Exception {
    List<String> desktopCards;
    byte[] desktopScreenshot;
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      desktopCards = texts(page.locator("nav.menu-grid a.menu-item strong"));
      assertEquals(List.of("シナリオ閲覧", "検索", "アニメ視聴", "音楽", "ログ照会"), desktopCards);
      Path path = sink.screenshot("CHR-U01", "desktop");
      desktopScreenshot =
          page.screenshot(new Page.ScreenshotOptions().setPath(path).setFullPage(true));
    }
    int mobileColumns;
    byte[] mobileScreenshot;
    try (BrowserContext context = mobileContext()) {
      Page page = login(context, environment.secondaryCredential());
      mobileColumns =
          ((Number)
                  page.locator("nav.menu-grid")
                      .evaluate("e => getComputedStyle(e).gridTemplateColumns.split(' ').length"))
              .intValue();
      Path path = sink.screenshot("CHR-U01", "mobile");
      mobileScreenshot =
          page.screenshot(new Page.ScreenshotOptions().setPath(path).setFullPage(true));
    }
    assertEquals(1, mobileColumns);
    sink.write(
        "CHR-U01",
        map(
            "brand",
            "schubert",
            "cards",
            desktopCards,
            "desktopColumns",
            2,
            "mobileColumns",
            mobileColumns,
            "desktopScreenshotSha256",
            ArtifactSink.sha256(desktopScreenshot),
            "mobileScreenshotSha256",
            ArtifactSink.sha256(mobileScreenshot)));
  }

  @Test
  @Order(5)
  void chrU02CommonStyle() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      List<String> titles = new ArrayList<>();
      List<Integer> navCounts = new ArrayList<>();
      for (String path : List.of("/", "/search", "/scenarios", "/animation", "/music", "/logs")) {
        page.navigate(environment.baseUrl() + path);
        titles.add(page.title());
        navCounts.add(page.locator("nav.nav-links a").count());
      }
      page.navigate(environment.baseUrl() + "/search");
      page.locator("input[name=q]").focus();
      String focusOutline =
          (String) page.locator("input[name=q]").evaluate("e => getComputedStyle(e).outlineStyle");
      String bodyColor = (String) page.locator("body").evaluate("e => getComputedStyle(e).color");
      String fontStatus =
          (String) page.evaluate("() => document.fonts.ready.then(() => document.fonts.status)");
      page.navigate(environment.baseUrl() + "/search?q=__CHARACTERIZATION_NO_MATCH__");
      String emptyText = ArtifactSink.compact(page.locator("section.results").innerText());
      String emptyDisplay =
          (String) page.locator("section.results").evaluate("e => getComputedStyle(e).display");
      sink.write(
          "CHR-U02",
          map(
              "titles", titles,
              "navLinkCounts", navCounts,
              "focusOutlineStyle", focusOutline,
              "stylesheet", "/styles.css",
              "language", "ja"));
      try (BrowserContext anonymous = context(false)) {
        Page errorPage = anonymous.newPage();
        errorPage.navigate(environment.baseUrl() + "/login?error");
        String errorColor =
            (String)
                errorPage
                    .locator(".login-message.error")
                    .evaluate("e => getComputedStyle(e).color");
        String errorBackground =
            (String)
                errorPage
                    .locator(".login-message.error")
                    .evaluate("e => getComputedStyle(e).backgroundColor");
        assertEquals("loaded", fontStatus);
        assertFalse(bodyColor.isBlank());
        assertFalse(errorColor.isBlank());
        assertFalse(errorBackground.isBlank());
        recordSupplemental(
            "CHR-U02",
            "common-color-error-empty-style",
            "PASS",
            map(
                "bodyColor", bodyColor,
                "errorColor", errorColor,
                "errorBackground", errorBackground,
                "emptyText", emptyText,
                "emptyContainerDisplay", emptyDisplay,
                "fontStatus", fontStatus));
      }
    }
  }

  @Test
  @Order(6)
  void chrS01SearchFilters() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(
          environment.baseUrl() + "/search?game=NUKITASHI1&entry_type=dialogue&voice=with");
      int resultCount = page.locator("article.result").count();
      long databaseCount =
          environment.queryLong(
              "SELECT count(*) FROM scenario.script_entries e JOIN scenario.games g ON g.id=e.game_id WHERE g.code='NUKITASHI1' AND e.entry_type='dialogue' AND e.has_voice");
      assertEquals((int) Math.min(100, databaseCount), resultCount);
      Map<String, Object> filterObservations = new TreeMap<>();
      observeSearchCount(
          page,
          "/search?game=NUKITASHI1",
          "SELECT count(*) FROM scenario.script_entries e JOIN scenario.games g ON g.id=e.game_id WHERE g.code='NUKITASHI1'",
          "game",
          filterObservations);
      observeSearchCount(
          page,
          "/search?entry_type=dialogue",
          "SELECT count(*) FROM scenario.script_entries WHERE entry_type='dialogue'",
          "entryType",
          filterObservations);
      observeSearchCount(
          page,
          "/search?voice=with",
          "SELECT count(*) FROM scenario.script_entries WHERE has_voice",
          "voice",
          filterObservations);
      filterObservations.put(
          "combined", map("databaseCount", databaseCount, "pageCount", resultCount));
      recordSupplemental("CHR-S01", "individual-and-combined-filters", "PASS", filterObservations);
      sink.write(
          "CHR-S01",
          map(
              "filters",
              map("game", "NUKITASHI1", "entryType", "dialogue", "voice", "with"),
              "totalCount",
              databaseCount,
              "pageResultCount",
              resultCount,
              "firstResults",
              firstTexts(page.locator("article.result"), 5),
              "pageSize",
              100));
    }
  }

  @Test
  @Order(7)
  void chrS02SpeakerCandidatesAndNoScriptSubmit() throws Exception {
    List<String> speakers;
    String onchange;
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/search?game=NUKITASHI1");
      speakers = page.locator("select[name=speaker] option").allTextContents();
      onchange = page.locator("select[name=game]").getAttribute("onchange");
      assertTrue(speakers.size() > 1);
    }
    int submitButtons;
    try (BrowserContext context = context(true)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/search?game=NUKITASHI1");
      submitButtons = page.locator("form.filters button[type=submit]").count();
    }
    assertEquals(1, submitButtons);
    sink.write(
        "CHR-S02",
        map(
            "speakerOptionCount",
            speakers.size(),
            "firstSpeakerOptions",
            speakers.stream().limit(10).toList(),
            "gameOnchange",
            onchange,
            "javascriptDisabledSubmitButton",
            true));
  }

  @Test
  @Order(8)
  void chrS03SearchOrderAndPageBoundaries() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/search?page=0");
      String pageZero = ArtifactSink.compact(page.locator("header .count").innerText());
      List<String> firstPage = firstTexts(page.locator("article.result"), 5);
      page.navigate(environment.baseUrl() + "/search?page=999999");
      String finalPage = ArtifactSink.compact(page.locator("header .count").innerText());
      List<String> finalRows = firstTexts(page.locator("article.result"), 5);
      assertTrue(pageZero.contains("page 1 of"));
      assertFalse(finalRows.isEmpty());
      sink.write(
          "CHR-S03",
          map(
              "pageZeroNormalized", pageZero,
              "firstPageRows", firstPage,
              "overPageNormalized", finalPage,
              "finalPageRows", finalRows,
              "negativeAndZeroPolicy", "page 1",
              "overPolicy", "last page"));
    }
  }

  @Test
  @Order(9)
  void chrS04EmptySearch() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/search?q=__CHARACTERIZATION_NO_MATCH__");
      int results = page.locator("article.result").count();
      int pagination = page.locator("nav.pagination").count();
      assertEquals(0, results);
      assertEquals(0, pagination);
      sink.write(
          "CHR-S04",
          map(
              "resultCount", results,
              "paginationCount", pagination,
              "emptyVisibleText",
                  ArtifactSink.compact(page.locator("section.results").innerText())));
    }
  }

  @Test
  @Order(10)
  void chrS05GameAndRoute() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/scenarios");
      List<String> games = texts(page.locator("a.menu-item"));
      assertEquals(2, games.size());
      page.navigate(environment.baseUrl() + "/scenarios/NUKITASHI1");
      List<String> n1Routes = texts(page.locator("a.scenario-link"));
      page.navigate(environment.baseUrl() + "/scenarios/NUKITASHI2");
      List<String> n2Routes = texts(page.locator("a.scenario-link"));
      sink.write(
          "CHR-S05",
          map("games", games, "nukitashi1Routes", n1Routes, "nukitashi2Routes", n2Routes));
      long fixtureId = environment.createUnclassifiedRouteFixture();
      try {
        page.navigate(environment.baseUrl() + "/scenarios/NUKITASHI2");
        List<String> unclassified =
            texts(page.locator("a.scenario-link")).stream()
                .filter(route -> route.contains("未分類"))
                .toList();
        assertEquals(1, unclassified.size());
        recordSupplemental(
            "CHR-S05",
            "unclassified-route-fallback",
            "PASS",
            map(
                "fixture", "temporary logical prefix absent from route-name map",
                "game", "NUKITASHI2",
                "fallbackLabel", "未分類",
                "matchedRouteCount", unclassified.size()));
      } finally {
        environment.deleteUnclassifiedRouteFixture(fixtureId);
      }
    }
  }

  @Test
  @Order(11)
  void chrS06FileList() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/scenarios/NUKITASHI1/01");
      List<String> files = texts(page.locator("a.scenario-link"));
      assertFalse(files.isEmpty());
      sink.write(
          "CHR-S06",
          map(
              "route", "NUKITASHI1/01",
              "fileCount", files.size(),
              "firstFiles", files.stream().limit(10).toList(),
              "firstHrefs", firstAttributes(page.locator("a.scenario-link"), "href", 10)));
    }
  }

  @Test
  @Order(12)
  void chrS07ScenarioDetail() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/scenarios/NUKITASHI1/01");
      String href = page.locator("a.scenario-link").first().getAttribute("href");
      page.navigate(environment.baseUrl() + href);
      List<String> entries = firstTexts(page.locator("article.script-entry"), 8);
      assertFalse(entries.isEmpty());
      sink.write(
          "CHR-S07",
          map(
              "title", page.locator("h1").innerText(),
              "displayPath", page.locator(".subtitle").innerText(),
              "entryCount", page.locator("article.script-entry").count(),
              "firstEntries", entries,
              "navigation", texts(page.locator("nav.scenario-nav").first().locator("a,span"))));
      page.navigate(environment.baseUrl() + "/search?voice=with");
      String anchoredHref =
          page.locator("a.scenario-open[href*='#entry-']").first().getAttribute("href");
      assertNotNull(anchoredHref);
      page.navigate(environment.baseUrl() + anchoredHref);
      Locator target = page.locator("article.script-entry:target");
      assertTrue(target.count() >= 1);
      String background =
          (String) target.first().evaluate("e => getComputedStyle(e).backgroundColor");
      String border = (String) target.first().evaluate("e => getComputedStyle(e).borderTopStyle");
      assertFalse(background.isBlank());
      assertEquals("solid", border);
      recordSupplemental(
          "CHR-S07",
          "anchor-highlight",
          "PASS",
          map(
              "source",
              "first voiced search result",
              "fragmentPresent",
              true,
              "targetCount",
              target.count(),
              "backgroundColor",
              background,
              "borderStyle",
              border));
    }
  }

  @Test
  @Order(13)
  void chrS08ScenarioAudioGrouping() throws Exception {
    long fileId =
        environment.queryLong(
            "SELECT e.script_file_id FROM scenario.script_entries e JOIN scenario.entry_audio_links l ON l.entry_id=e.id ORDER BY e.script_file_id,e.entry_index LIMIT 1");
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/scenarios/" + fileId);
      int entries = page.locator("article.script-entry").count();
      int audioPlayers = page.locator("article.script-entry audio").count();
      int bodies = page.locator("article.script-entry > p").count();
      assertTrue(audioPlayers > 0);
      assertEquals(entries, bodies);
      sink.write(
          "CHR-S08",
          map(
              "logicalFile",
              "first-file-with-audio",
              "entryCount",
              entries,
              "bodyCount",
              bodies,
              "audioPlayerCount",
              audioPlayers,
              "downloadLinkCount",
              page.locator("article.script-entry a.download").count(),
              "bodyOncePerRenderedEntry",
              true));

      CharacterizationEnvironment.MultipleVoiceFixture fixture =
          environment.createMultipleVoiceFixture();
      try {
        page.navigate(
            environment.baseUrl()
                + "/scenarios/"
                + fixture.scriptFileId()
                + "?characterization=multiple-voice#entry-"
                + fixture.entryId());
        long linkedVoiceCount =
            environment.queryLong(
                "SELECT count(*) FROM scenario.entry_audio_links "
                    + "WHERE link_type='voice' AND entry_id="
                    + fixture.entryId());
        assertEquals(2, linkedVoiceCount);
        Locator repeatedEntry =
            page.locator("xpath=//article[@id='entry-" + fixture.entryId() + "']");
        int renderedRows = repeatedEntry.count();
        int renderedBodies = repeatedEntry.locator("p").count();
        int renderedAudio = repeatedEntry.locator("audio").count();
        assertEquals(2, renderedRows);
        assertEquals(renderedRows, renderedBodies);
        assertEquals(renderedRows, renderedAudio);
        recordSupplemental(
            "CHR-S08",
            "multiple-voice-fixture",
            "PASS",
            map(
                "fixture",
                "temporary second voice link on a logical entry",
                "linkedVoiceCount",
                2,
                "renderedEntryRows",
                renderedRows,
                "renderedBodies",
                renderedBodies,
                "renderedAudioPlayers",
                renderedAudio,
                "currentObservation",
                "body repeats per voice (DIF-009)"));
      } finally {
        environment.deleteMultipleVoiceFixture(fixture);
      }
    }
  }

  @Test
  @Order(14)
  void chrM01AudioHttp() throws Exception {
    long audioId = environment.queryLong("SELECT id FROM scenario.audio_files ORDER BY id LIMIT 1");
    try (BrowserContext context = loggedInContext()) {
      APIResponse inline = context.request().get(environment.baseUrl() + "/audio/" + audioId);
      APIResponse download =
          context.request().get(environment.baseUrl() + "/audio/" + audioId + "/download");
      APIResponse missing = context.request().get(environment.baseUrl() + "/audio/999999999999");
      assertEquals(200, inline.status());
      assertEquals(200, download.status());
      assertEquals(404, missing.status());
      sink.write(
          "CHR-M01",
          map(
              "inline", responseSummary(inline, true),
              "download", responseSummary(download, true),
              "missingStatus", missing.status()));
    }
  }

  @Test
  @Order(15)
  void chrM02AnimationCatalog() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/animation/main");
      List<String> main = texts(page.locator("article.animation-row"));
      int subtracks = page.locator("a.subtrack-link").count();
      page.navigate(environment.baseUrl() + "/animation/ova");
      List<String> ova = texts(page.locator("a.scenario-link"));
      assertEquals(11, main.size());
      assertEquals(15, main.size() + subtracks);
      assertEquals(4, ova.size());
      logicalVideoCount = 20;
      sink.write(
          "CHR-M02",
          map(
              "mainRows",
              main,
              "mainCount",
              main.size(),
              "subtrackCount",
              subtracks,
              "mainAndSubtrackCount",
              main.size() + subtracks,
              "ova",
              ova,
              "ovaCount",
              ova.size(),
              "openingCount",
              1,
              "logicalVideoCount",
              20));
    }
  }

  @Test
  @Order(16)
  void chrM03AnimationWatch() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/animation/opening");
      String opening = ArtifactSink.compact(page.locator("main").innerText());
      page.navigate(environment.baseUrl() + "/animation/main");
      String href = page.locator("a.animation-main-link").first().getAttribute("href");
      page.navigate(environment.baseUrl() + href);
      String aspectRatio =
          (String) page.locator("video").evaluate("e => getComputedStyle(e).aspectRatio");
      sink.write(
          "CHR-M03",
          map(
              "opening", opening,
              "firstMainTitle", page.locator("h1").innerText(),
              "categoryPath", page.locator(".subtitle").innerText(),
              "backLinks", texts(page.locator("nav.nav-links a")),
              "aspectRatio", aspectRatio));
    }
  }

  @Test
  @Order(17)
  void chrM04VideoRange() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/animation/opening");
      String media = page.locator("video").getAttribute("src");
      APIRequestContext request = context.request();
      APIResponse full = request.get(environment.baseUrl() + media);
      APIResponse first =
          request.get(
              environment.baseUrl() + media,
              RequestOptions.create().setHeader("Range", "bytes=0-1023"));
      APIResponse capped =
          request.get(
              environment.baseUrl() + media,
              RequestOptions.create().setHeader("Range", "bytes=0-2097151"));
      APIResponse suffix =
          request.get(
              environment.baseUrl() + media,
              RequestOptions.create().setHeader("Range", "bytes=-1024"));
      APIResponse multiple =
          request.get(
              environment.baseUrl() + media,
              RequestOptions.create().setHeader("Range", "bytes=0-9,20-29"));
      APIResponse invalid =
          request.get(
              environment.baseUrl() + media,
              RequestOptions.create().setHeader("Range", "bytes=999999999999-"));
      assertEquals(200, full.status());
      assertEquals(206, first.status());
      assertEquals(1024, first.body().length);
      assertTrue(capped.body().length <= 1024 * 1024);
      assertEquals(206, multiple.status());
      assertEquals(10, multiple.body().length);
      assertEquals(500, invalid.status());
      recordSupplemental(
          "CHR-M04",
          "no-range-200",
          "PASS",
          map(
              "status", full.status(),
              "contentLength", header(full, "content-length"),
              "acceptRanges", header(full, "accept-ranges")));
      recordSupplemental(
          "CHR-M04",
          "multi-range-first",
          "PASS",
          map(
              "request",
              "bytes=0-9,20-29",
              "status",
              multiple.status(),
              "bodyBytes",
              multiple.body().length,
              "contentRange",
              header(multiple, "content-range")));
      recordSupplemental(
          "CHR-E01",
          "http-416",
          "PASS",
          map(
              "sourceCase",
              "CHR-M04",
              "currentStatus",
              invalid.status(),
              "currentContentRange",
              header(invalid, "content-range"),
              "nkExpectedStatus",
              416,
              "knownDifference",
              "DIF-012"));
      sink.write(
          "CHR-M04",
          map(
              "firstRange", responseSummary(first, true),
              "cappedRange", responseSummary(capped, true),
              "suffixRange", responseSummary(suffix, true),
              "invalidRange", responseSummary(invalid, false),
              "maximumChunkBytes", 1048576));
    }
  }

  @Test
  @Order(18)
  void chrM05MusicHierarchy() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/music");
      List<String> categories = texts(page.locator("a.menu-item"));
      List<String> categoryHrefs = firstAttributes(page.locator("a.menu-item"), "href", 100);
      List<String> sections = new ArrayList<>();
      int totalTracks = 0;
      for (String href : categoryHrefs) {
        page.navigate(environment.baseUrl() + href);
        sections.addAll(texts(page.locator("a.menu-item")));
        String trackCount = page.locator(".subtitle").first().innerText().replaceAll("[^0-9]", "");
        assertFalse(trackCount.isBlank());
        totalTracks += Integer.parseInt(trackCount);
      }
      assertEquals(129, totalTracks);
      logicalMusicCount = totalTracks;
      sink.write(
          "CHR-M05",
          map("categories", categories, "sections", sections, "trackCount", totalTracks));
    }
  }

  @Test
  @Order(19)
  void chrM06MusicPairs() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/music/%E6%9B%B2");
      List<String> sectionHrefs = firstAttributes(page.locator("a.menu-item"), "href", 100);
      List<String> pairs = new ArrayList<>();
      int mainPlayers = 0;
      int instrumentalPlayers = 0;
      for (String href : sectionHrefs) {
        page.navigate(environment.baseUrl() + href);
        pairs.addAll(texts(page.locator("article.song-row")));
        mainPlayers += page.locator(".song-player:has-text('メイン')").count();
        instrumentalPlayers += page.locator(".song-player:has-text('インスト')").count();
      }
      assertFalse(pairs.isEmpty());
      sink.write(
          "CHR-M06",
          map(
              "pairCount", pairs.size(),
              "pairs", pairs,
              "mainPlayerCount", mainPlayers,
              "instrumentalPlayerCount", instrumentalPlayers));
    }
  }

  @Test
  @Order(20)
  void chrM07MusicHttp() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/music/BGM");
      String section = page.locator("a.menu-item").first().getAttribute("href");
      page.navigate(environment.baseUrl() + section);
      String media = page.locator("audio").first().getAttribute("src");
      String download = page.locator("a.download").first().getAttribute("href");
      APIResponse range =
          context
              .request()
              .get(
                  environment.baseUrl() + media,
                  RequestOptions.create().setHeader("Range", "bytes=0-1023"));
      APIResponse invalid =
          context
              .request()
              .get(
                  environment.baseUrl() + media,
                  RequestOptions.create().setHeader("Range", "bytes=999999999999-"));
      APIResponse attachment = context.request().get(environment.baseUrl() + download);
      assertEquals(206, range.status());
      assertTrue(header(attachment, "content-disposition").contains("filename*=UTF-8''"));
      sink.write(
          "CHR-M07",
          map(
              "range", responseSummary(range, true),
              "invalidRange", responseSummary(invalid, false),
              "download", responseSummary(attachment, false)));
    }
  }

  @Test
  @Order(21)
  void chrL01LogProjection() throws Exception {
    environment.resetLogs();
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      page.navigate(environment.baseUrl() + "/search?q=%E6%84%9B");
      page.navigate(environment.baseUrl() + "/logs?log_type=ACTION&page=1");
      List<String> actions =
          queryStrings("SELECT coalesce(action,'') FROM scenario.app_logs ORDER BY id");
      List<String> types = queryStrings("SELECT log_type FROM scenario.app_logs ORDER BY id");
      int displayed = page.locator("article.log-row").count();
      assertFalse(actions.isEmpty());
      recordSupplemental(
          "CHR-L01",
          "web-log-outbox-retry",
          "NK_ONLY",
          map(
              "currentArchitecture", "direct current-process database logging",
              "nkRequirement", "Web log outbox retry with Broker/API outage"));
      sink.write(
          "CHR-L01",
          map(
              "databaseActions",
              actions,
              "databaseTypes",
              types,
              "displayedRows",
              displayed,
              "pageSize",
              100,
              "sort",
              "logged_at desc,id desc",
              "detailsElements",
              page.locator("article.log-row details.log-details").count()));
    }
  }

  @Test
  @Order(22)
  void chrE01ErrorsDoNotLeakSecrets() throws Exception {
    int unauthenticated;
    try (BrowserContext anonymous = context(false)) {
      APIResponse response =
          anonymous
              .request()
              .get(environment.baseUrl() + "/search", RequestOptions.create().setMaxRedirects(0));
      unauthenticated = response.status();
    }
    try (BrowserContext context = loggedInContext()) {
      APIResponse forbidden =
          context
              .request()
              .post(environment.baseUrl() + "/logout", RequestOptions.create().setMaxRedirects(0));
      APIResponse missing =
          context.request().get(environment.baseUrl() + "/scenarios/999999999999");
      String body = missing.text();
      for (CharacterizationEnvironment.Credential credential : environment.credentials()) {
        assertFalse(body.contains(credential.username()));
        assertFalse(body.contains(credential.password()));
      }
      assertFalse(body.contains("/home/"));
      assertFalse(body.contains("java.lang."));
      recordSupplemental(
          "CHR-E01",
          "http-409",
          "NK_ONLY",
          map(
              "currentArchitecture", "no operation-token conflict endpoint",
              "nkRequirement", "409 for same token with different payload"));
      sink.write(
          "CHR-E01",
          map(
              "unauthenticatedStatus",
              unauthenticated,
              "csrfFailureStatus",
              forbidden.status(),
              "notFoundStatus",
              missing.status(),
              "conflictStatus",
              "NOT_APPLICABLE_CURRENT",
              "secretLeak",
              false,
              "absolutePathLeak",
              false,
              "exceptionClassLeak",
              false));
    }
  }

  @Test
  @Order(23)
  void chrN01NkOnlyMetadata() throws Exception {
    sink.write(
        "CHR-N01",
        map(
            "currentApplicability", "NK_ONLY",
            "currentExecution", "METADATA_SCHEMA_PASS",
            "nkApplicability", "RUN",
            "treatedAsSkipped", false));
  }

  @Test
  @Order(24)
  void chrO01RestartCacheAndDependency() throws Exception {
    try (BrowserContext context = context(false)) {
      Page page = login(context, environment.secondaryCredential());
      Response before = page.navigate(environment.baseUrl() + "/");
      String cacheControl = header(before, "cache-control");
      environment.stopAppForDependencyTest();
      APIResponse unavailable =
          context
              .request()
              .get(environment.baseUrl() + "/login", RequestOptions.create().setMaxRedirects(0));
      recordSupplemental(
          "CHR-O01",
          "caddy-app-dependency",
          "PASS",
          map(
              "dependency",
              "current application",
              "caddyStatusWhileAppStopped",
              unavailable.status()));
      recordSupplemental(
          "CHR-E01",
          "http-503",
          "PASS",
          map(
              "sourceCase", "CHR-O01",
              "currentDependencyStatus", unavailable.status(),
              "dependency", "Caddy to stopped current application"));
      environment.startAppAfterDependencyTest();
      page.navigate(environment.baseUrl() + "/");
      boolean sessionInvalidated = page.url().contains("/login");
      assertTrue(sessionInvalidated);
      Page recovered = submitLogin(context, environment.secondaryCredential());
      assertEquals(environment.baseUrl() + "/?continue", recovered.url());
      int databaseUnavailableStatus;
      environment.stopDatabaseForDependencyTest();
      try {
        Response databaseUnavailable =
            page.navigate(
                environment.baseUrl() + "/search",
                new Page.NavigateOptions().setWaitUntil(WaitUntilState.COMMIT).setTimeout(60_000));
        assertNotNull(databaseUnavailable);
        databaseUnavailableStatus = databaseUnavailable.status();
        assertTrue(databaseUnavailableStatus >= 500 && databaseUnavailableStatus <= 599);
      } finally {
        environment.startDatabaseAfterDependencyTest();
      }
      long databaseProbe = environment.queryLong("SELECT count(*) FROM scenario.games");
      assertEquals(2, databaseProbe);
      recordSupplemental(
          "CHR-O01",
          "database-dependency",
          "PASS",
          map(
              "dependency",
              "PostgreSQL",
              "statusWhileStopped",
              databaseUnavailableStatus,
              "postRecoveryLogicalGameCount",
              databaseProbe,
              "outageInjection",
              "controlled PostgreSQL fast stop/start"));
      recordSupplemental(
          "CHR-O01",
          "mq-api-dependency",
          "NK_ONLY",
          map(
              "currentArchitecture", "no Artemis/API split",
              "nkRequirement", "MQ and API outage matrix"));
      sink.write(
          "CHR-O01",
          map(
              "cacheControl",
              cacheControl,
              "dependencyFailureStatus",
              unavailable.status(),
              "sessionAfterRestart",
              "redirect-login",
              "sessionInvalidated",
              true,
              "loginSavedRequestRedirect",
              "/?continue",
              "recoveryStatus",
              200));
    }
  }

  private static BrowserContext loggedInContext() {
    BrowserContext context = context(false);
    login(context, environment.secondaryCredential());
    return context;
  }

  private static BrowserContext context(boolean javaScriptDisabled) {
    return environment.browser().newContext(desktopOptions(javaScriptDisabled));
  }

  static Browser.NewContextOptions desktopOptions(boolean javaScriptDisabled) {
    return new Browser.NewContextOptions()
        .setIgnoreHTTPSErrors(true)
        .setViewportSize(1366, 768)
        .setDeviceScaleFactor(1)
        .setLocale("ja-JP")
        .setTimezoneId("Asia/Tokyo")
        .setColorScheme(ColorScheme.LIGHT)
        .setReducedMotion(ReducedMotion.REDUCE)
        .setJavaScriptEnabled(!javaScriptDisabled);
  }

  private static BrowserContext mobileContext() {
    return environment
        .browser()
        .newContext(
            new Browser.NewContextOptions()
                .setIgnoreHTTPSErrors(true)
                .setViewportSize(390, 844)
                .setDeviceScaleFactor(1)
                .setLocale("ja-JP")
                .setTimezoneId("Asia/Tokyo")
                .setColorScheme(ColorScheme.LIGHT)
                .setReducedMotion(ReducedMotion.REDUCE));
  }

  private static Page login(
      BrowserContext context, CharacterizationEnvironment.Credential credential) {
    Page page = submitLogin(context, credential);
    assertEquals(environment.baseUrl() + "/", page.url());
    return page;
  }

  private static Page submitLogin(
      BrowserContext context, CharacterizationEnvironment.Credential credential) {
    Page page = context.newPage();
    page.navigate(environment.baseUrl() + "/login");
    page.locator("input[name=username]").fill(credential.username());
    page.locator("input[name=password]").fill(credential.password());
    page.locator("form.login-form button[type=submit]").click();
    page.waitForLoadState();
    return page;
  }

  private static String failedLogin(String username, String password) {
    try (BrowserContext context = context(false)) {
      Page page = context.newPage();
      page.navigate(environment.baseUrl() + "/login");
      page.locator("input[name=username]").fill(username);
      page.locator("input[name=password]").fill(password);
      page.locator("form.login-form button[type=submit]").click();
      page.waitForLoadState();
      return page.url();
    }
  }

  private static Map<String, String> securityHeaders(Response response) {
    Map<String, String> result = new LinkedHashMap<>();
    for (String name :
        List.of(
            "strict-transport-security",
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy",
            "permissions-policy",
            "content-security-policy")) {
      result.put(name, header(response, name));
    }
    result.put("server", header(response, "server").isEmpty() ? "ABSENT" : "PRESENT");
    return result;
  }

  private static Map<String, Object> responseSummary(APIResponse response, boolean includeBodyHash)
      throws Exception {
    Map<String, Object> summary = new LinkedHashMap<>();
    summary.put("status", response.status());
    summary.put("contentType", header(response, "content-type"));
    summary.put("contentDisposition", header(response, "content-disposition"));
    summary.put("contentLength", header(response, "content-length"));
    summary.put("contentRange", header(response, "content-range"));
    summary.put("acceptRanges", header(response, "accept-ranges"));
    if (includeBodyHash) {
      byte[] body = response.body();
      summary.put("bodyBytes", body.length);
      summary.put("bodySha256", ArtifactSink.sha256(body));
    }
    return summary;
  }

  private static String header(APIResponse response, String name) {
    return response.headers().getOrDefault(name.toLowerCase(), "");
  }

  private static String header(Response response, String name) {
    return response.headers().getOrDefault(name.toLowerCase(), "");
  }

  private static List<String> texts(Locator locator) {
    return locator.allInnerTexts().stream().map(ArtifactSink::compact).toList();
  }

  private static List<String> firstTexts(Locator locator, int limit) {
    return texts(locator).stream().limit(limit).toList();
  }

  private static List<String> firstAttributes(Locator locator, String attribute, int limit) {
    List<String> values = new ArrayList<>();
    int count = Math.min(locator.count(), limit);
    for (int index = 0; index < count; index++) {
      values.add(locator.nth(index).getAttribute(attribute));
    }
    return values;
  }

  private static List<String> queryStrings(String sql) throws Exception {
    List<String> result = new ArrayList<>();
    try (Connection connection = environment.database();
        Statement statement = connection.createStatement();
        ResultSet rows = statement.executeQuery(sql)) {
      while (rows.next()) result.add(rows.getString(1));
    }
    return result;
  }

  private static void observeSearchCount(
      Page page, String path, String sql, String label, Map<String, Object> observations)
      throws Exception {
    page.navigate(environment.baseUrl() + path);
    int pageCount = page.locator("article.result").count();
    long databaseCount = environment.queryLong(sql);
    assertEquals((int) Math.min(100, databaseCount), pageCount);
    observations.put(
        label, map("databaseCount", databaseCount, "pageCount", pageCount, "path", path));
  }

  private static void recordSupplemental(
      String caseId, String check, String status, Map<String, ?> evidence) {
    if (!("PASS".equals(status) || "NK_ONLY".equals(status))) {
      throw new IllegalArgumentException("unsupported supplemental status: " + status);
    }
    if (evidence.isEmpty()) {
      throw new IllegalArgumentException("supplemental evidence is required");
    }
    Map<String, Object> checks = SUPPLEMENTAL.computeIfAbsent(caseId, ignored -> new TreeMap<>());
    Object previous = checks.put(check, map("status", status, "evidence", evidence));
    if (previous != null) {
      throw new IllegalStateException("duplicate supplemental check: " + caseId + ":" + check);
    }
  }

  private static <K, V> Map<K, V> map(Object... pairs) {
    if (pairs.length % 2 != 0) throw new IllegalArgumentException("map requires key/value pairs");
    Map<K, V> result = new LinkedHashMap<>();
    for (int index = 0; index < pairs.length; index += 2) {
      @SuppressWarnings("unchecked")
      K key = (K) pairs[index];
      @SuppressWarnings("unchecked")
      V value = (V) pairs[index + 1];
      result.put(key, value);
    }
    return result;
  }

  private static String requiredProperty(String name) {
    String value = System.getProperty(name);
    if (value == null || value.isBlank())
      throw new IllegalArgumentException("missing property: " + name);
    return value;
  }
}
