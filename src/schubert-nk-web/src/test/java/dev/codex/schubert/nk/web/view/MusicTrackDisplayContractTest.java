package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.*;
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

/** UI222 section 9, UI223 section 7: literal closed media display fixture. */
class MusicTrackDisplayContractTest {
 @Test
 void namedNavigationEscapedTracksAndMissingPairSides() {
  var resolver = new FileTemplateResolver();
  resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/"); resolver.setSuffix(".html"); resolver.setCharacterEncoding("UTF-8");
  var engine = new SpringTemplateEngine(); engine.setTemplateResolver(resolver);
  var servlet = new MockServletContext(); var request = new MockHttpServletRequest(servlet); request.setRequestURI("/music/BGM/ゲーム");
  var exchange = JakartaServletWebApplication.buildApplication(servlet).buildExchange(request, new MockHttpServletResponse());
  var track = Map.of("title", "曲<img>", "displayPath", "公開/a.ogg", "byteSize", 1048576, "mediaHref", "/music/media/fixture", "downloadHref", "/music/download/fixture");
  for(boolean songs : java.util.List.of(false,true)) {
   var values = new java.util.HashMap<String,Object>();
   values.put("topBar",Map.of("brand","schubert NK","username","fixture","role","USER")); values.put("title", "BGM / ゲーム"); values.put("trackCount",1); values.put("category","BGM"); values.put("categoryHref","/music/BGM"); values.put("songs",songs); values.put("tracks",java.util.List.of(track));
   values.put("pairs",java.util.List.of(Map.of("title","曲<img>","main",java.util.Optional.of(track),"instrumental",java.util.Optional.empty())));
   var dom=Jsoup.parse(engine.process("music-list",new WebContext(exchange,Locale.JAPAN,Map.of("page",Map.of("values",values),"_csrf",Map.of("parameterName","_csrf","token","synthetic-csrf")))));
   assertEquals("曲<img>",dom.select(".music-info strong").text()); assertEquals(0,dom.select("img,script,[autoplay]").size());
   assertEquals(1,dom.select("audio[controls][preload=none][src='/music/media/fixture']").size()); assertEquals("/music/download/fixture",dom.select(".download").attr("href"));
   assertEquals(songs?0:1,dom.select(".scenario-meta").size()); assertEquals(songs?"インストなし":"",dom.select(".song-player-placeholder").text());
   for(var nav:dom.select("nav")) assertFalse(nav.attr("aria-label").isBlank());
  }
 }
}
