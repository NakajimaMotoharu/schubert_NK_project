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

/** UI224 section 3 and UI222 input/accessibility: synthetic GET display only. */
class QuestionAcceptedDisplayContractTest {
 @Test
 void publicReceiptEscapedFullQuestionAndNamedGetNavigation() throws Exception {
  var resolver=new FileTemplateResolver(); resolver.setPrefix("src/schubert-nk-web/src/main/resources/templates/");resolver.setSuffix(".html");resolver.setCharacterEncoding("UTF-8");
  var engine=new SpringTemplateEngine();engine.setTemplateResolver(resolver);
  var servlet=new MockServletContext();var request=new MockHttpServletRequest(servlet);request.setRequestURI("/questions/accepted/01ARZ3NDEKTSV4RRFFQ69G5FAV");
  var exchange=JakartaServletWebApplication.buildApplication(servlet).buildExchange(request,new MockHttpServletResponse());
  var page=Map.of("topBar",Map.of("brand","schubert NK","username","fixture","role","USER"),"values",Map.of("receiptId","01ARZ3NDEKTSV4RRFFQ69G5FAV","submittedAt","2026-10-11 09:00:00","question"," 質問<script> & 本文"));
  var dom=Jsoup.parse(engine.process("questions/accepted",new WebContext(exchange,Locale.JAPAN,Map.of("page",page,"_csrf",Map.of("parameterName","_csrf","token","synthetic-csrf")))));
  assertEquals("質問を受け付けました。",dom.select(".accepted-message").text());assertEquals("01ARZ3NDEKTSV4RRFFQ69G5FAV",dom.select(".receipt").text());assertEquals(26,dom.select(".receipt").text().length());
  assertEquals("2026-10-11 09:00:00",dom.select(".submitted-at").text());assertEquals(" 質問<script> & 本文",dom.select(".question-body").getFirst().wholeText());
  assertEquals(0,dom.select("script,img,.question-accepted-page > form").size());
  assertEquals(java.util.List.of("/notifications","/questions/new","/menu"),dom.select(".question-accepted-page > nav a").eachAttr("href"));
  assertFalse(dom.select(".question-accepted-page > nav").attr("aria-label").isBlank());
  var css=Files.readString(Path.of("src/schubert-nk-web/src/main/resources/static/css/schubert.css"));assertTrue(css.matches("(?s).*\\.question-accepted-page \\.question-body\\s*\\{[^}]*white-space:\\s*pre-wrap;[^}]*}.*"));
 }
}
