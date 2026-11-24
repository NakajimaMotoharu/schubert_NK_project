package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.regex.Pattern;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.Test;

/** SYS-006 / UI222 §3 and §9, UI224/225, SS313, PT-WEB-TABLE-NARROW001..004. */
final class NarrowListTableResourceTest {
  private static final String CONDITIONAL = "th:if";

  @Test
  void userListKeepsAllEightColumnHeaders() throws IOException {
    assertTable(
        "admin/user-list",
        "利用者一覧の表",
        List.of("Username", "Role", "状態", "Lock終了日時", "最終Login日時", "作成日時", "更新日時", "詳細"));
  }

  @Test
  void notificationListKeepsAllSixColumnHeaders() throws IOException {
    assertTable(
        "notifications/list",
        "通知一覧の表",
        List.of("区分", "受付ID", "受付日時", "最終更新日時", "概要", "操作"));
  }

  @Test
  void questionListKeepsItsColumnsAndTheAdminOnlyOwnerColumn() throws IOException {
    var table =
        assertTable(
            "questions/list", "質問回答一覧の表", List.of("受付日時", "利用者", "質問", "回答状態", "回答日時", "操作"));
    var header = table.select("thead .owner-heading");
    assertEquals(1, header.size());
    assertEquals("${page.filters.admin}", header.attr(CONDITIONAL));
  }

  @Test
  void sharedStyleContainsHorizontalOverflowAtTheApprovedBreakpoint() throws IOException {
    try (var input =
        NarrowListTableResourceTest.class.getResourceAsStream("/static/css/schubert.css")) {
      assertNotNull(input);
      var css = new String(input.readAllBytes(), StandardCharsets.UTF_8);
      var rule =
          Pattern.compile("@media\\s*\\(max-width:\\s*900px\\)\\s*\\{\\s*\\.table-scroll\\s*\\{([^}]*)}")
              .matcher(css);
      assertTrue(rule.find());
      assertTrue(Pattern.compile("overflow-x\\s*:\\s*auto\\s*;").matcher(rule.group(1)).find());
      assertTrue(Pattern.compile("max-width\\s*:\\s*100%\\s*;").matcher(rule.group(1)).find());
    }
  }

  private static Document assertTable(String name, String label, List<String> headings)
      throws IOException {
    try (var input =
        NarrowListTableResourceTest.class.getResourceAsStream("/templates/" + name + ".html")) {
      assertNotNull(input, name);
      var document = Jsoup.parse(input, "UTF-8", "");
      var container = document.select(".table-scroll[role=region][tabindex=0]");
      assertEquals(1, container.size(), name);
      assertEquals(label, container.attr("aria-label"), name);
      assertEquals("${!page.rows.empty}", container.attr(CONDITIONAL), name);
      assertEquals(headings, container.select("table > thead th").eachText(), name);
      assertEquals("該当するデータはありません", document.select(".empty-results").text(), name);
      assertEquals(0, document.select(".table-scroll .empty-results").size(), name);
      return document;
    }
  }
}
