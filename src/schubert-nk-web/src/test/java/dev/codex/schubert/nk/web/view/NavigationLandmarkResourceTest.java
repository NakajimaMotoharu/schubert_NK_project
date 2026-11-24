package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.io.IOException;
import java.util.List;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;

/** UI222 §9, UI223/224/225, SS313, PT-WEB-NAVL001..003. */
final class NavigationLandmarkResourceTest {
  @Test
  void mediaNavigationNamesTheScreenWithoutChangingDestinations() {
    assertAll(
        () ->
            assertNavigation(
                "animation-watch",
                "アニメ視聴画面のナビゲーション",
                List.of("@{/animation}", "${page.values.backHref}")),
        () ->
            assertNavigation(
                "music-list",
                "曲一覧のナビゲーション",
                List.of("@{/music}", "${page.values.categoryHref}", "@{/search}")));
  }

  @Test
  void userManagementNavigationsHaveDistinctNames() {
    assertAll(
        () ->
            assertNavigation(
                "admin/user-list", "利用者一覧のナビゲーション", List.of("@{/admin/users/new}")),
        () ->
            assertNavigation(
                "admin/user-new", "利用者追加のナビゲーション", List.of("@{/admin/users}")),
        () ->
            assertNavigation(
                "admin/user-detail", "利用者詳細のナビゲーション", List.of("@{/admin/users}")));
  }

  @Test
  void questionReceiptNavigationHasANameAndKeepsTheThreeActionsInOrder() throws IOException {
    assertNavigation(
        "questions/accepted",
        "質問受付完了のナビゲーション",
        List.of("/notifications", "/questions/new", "@{/}"));
  }

  private static void assertNavigation(String name, String label, List<String> destinations)
      throws IOException {
    try (var input =
        NavigationLandmarkResourceTest.class.getResourceAsStream("/templates/" + name + ".html")) {
      assertNotNull(input, name);
      var landmarks =
          Jsoup.parse(input, "UTF-8", "").select("nav").stream()
              .filter(nav -> !nav.hasAttr("th:replace"))
              .toList();
      assertEquals(1, landmarks.size(), name);
      var landmark = landmarks.getFirst();
      assertEquals(label, landmark.attr("aria-label"), name);
      assertEquals(
          destinations,
          landmark.select("a").stream()
              .map(link -> link.hasAttr("th:href") ? link.attr("th:href") : link.attr("href"))
              .toList(),
          name);
    }
  }
}
