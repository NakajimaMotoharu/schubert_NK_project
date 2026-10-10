package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.Map;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.thymeleaf.context.WebContext;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.FileTemplateResolver;
import org.thymeleaf.web.servlet.JakartaServletWebApplication;

/** UI222 sections 2/9, UI223 section 6: closed public display fixture only. */
class AnimationWatchDisplayContractTest {
  @Test
  void watchMediaAttributesEscapingAndNamedNavigation() {
    var resolver = new FileTemplateResolver();
    resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");
    resolver.setSuffix(".html");
    resolver.setCharacterEncoding("UTF-8");
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    var servlet = new MockServletContext();
    var request = new MockHttpServletRequest(servlet);
    request.setRequestURI("/animation/opening");
    var exchange =
        JakartaServletWebApplication.buildApplication(servlet)
            .buildExchange(request, new MockHttpServletResponse());
    var values =
        Map.of(
            "topBar",
            Map.of("brand", "schubert NK", "username", "fixture", "role", "USER"),
            "title",
            "映像<script>",
            "category",
            "オープニング",
            "displayPath",
            "公開/op.mp4",
            "backHref",
            "/animation",
            "backLabel",
            "アニメ視聴",
            "mediaHref",
            "/animation/media/opening");
    var dom =
        Jsoup.parse(
            engine.process(
                "animation-watch",
                new WebContext(
                    exchange,
                    Locale.JAPAN,
                    Map.of(
                        "page",
                        Map.of("values", values),
                        "_csrf",
                        Map.of("parameterName", "_csrf", "token", "synthetic-csrf")))));
    assertEquals("映像<script>", dom.select("h1").text());
    assertEquals(0, dom.select("script,[autoplay]").size());
    assertEquals(
        1,
        dom.select(
                "main.video-page .video-shell"
                    + " video[controls][playsinline][preload=metadata][src='/animation/media/opening']")
            .size());
    for (var nav : dom.select("nav")) assertFalse(nav.attr("aria-label").isBlank());
    assertEquals(2, dom.select("a[href='/animation']").size());
  }

  @Test
  void watchWidthAndSixteenNineDeclarationsFollowDesign() throws Exception {
    var css =
        Files.readString(Path.of("src/schubert-nk-web/src/main/resources/static/css/schubert.css"));
    assertTrue(css.matches("(?s).*\\.page\\.video-page\\s*\\{[^}]*max-width:\\s*1280px;[^}]*}.*"));
    assertTrue(
        css.matches(
            "(?s).*\\.video-shell video\\s*\\{[^}]*width:\\s*100%;[^}]*aspect-ratio:\\s*16 /"
                + " 9;[^}]*}.*"));
  }
}
