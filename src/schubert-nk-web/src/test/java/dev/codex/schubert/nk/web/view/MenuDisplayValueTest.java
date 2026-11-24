package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SCR002 display values from UI223 and SS313, without any controller or audit context. */
class MenuDisplayValueTest {
  private static final String READER = "fixture-reader";
  private static final List<Card> EXPECTED =
      List.of(
          new Card("シナリオ閲覧", "シナリオ一覧から本文を読む", "/scenarios"),
          new Card("検索", "本文、話者、章タイトル、音声有無で探す", "/search"),
          new Card("アニメ視聴", "メインパート、OVA、オープニング映像を見る", "/animation"),
          new Card("音楽", "BGMや曲を一覧から再生する", "/music"),
          new Card("質問する", "質問を送信する", "/questions/new"),
          new Card("通知", "自分への通知を確認する", "/notifications"),
          new Card("質問回答", "質問と回答を確認する", "/questions"),
          new Card("ログ照会", "操作ログとリクエストログを検索する", "/logs"),
          new Card("User管理", "ユーザーを作成・管理する", "/admin/users"));

  /** PT-WEB-SCR002-VM001. */
  @Test
  void display001UserSeesTheFirstSevenFixedCards() {
    var page = MenuViewModel.from(principal(UserRole.USER));
    assertEquals(EXPECTED.subList(0, 7), views(page));
    assertTopBar(page, "USER");
  }

  /** PT-WEB-SCR002-VM002. */
  @Test
  void display002AdminSeesTheSameSevenThenLogAndUserManagement() {
    var page = MenuViewModel.from(principal(UserRole.ADMIN));
    assertEquals(EXPECTED, views(page));
    assertTopBar(page, "ADMIN");
    assertThrows(UnsupportedOperationException.class, () -> page.getCards().removeFirst());
    assertEquals(EXPECTED, views(page));
  }

  /** PT-WEB-SCR002-VM003. */
  @Test
  void display003TheModelAndEnumDoNotRetainMutableResultsOrPrintIdentity() {
    assertThrows(NullPointerException.class, () -> MenuViewModel.from(null));
    var page = MenuViewModel.from(principal(UserRole.ADMIN));
    assertEquals("MenuViewModel[REDACTED]", page.toString());
    assertEquals("TopBarViewModel[REDACTED]", page.getTopBar().toString());
    var catalog = MenuCard.values();
    assertEquals(9, catalog.length);
    catalog[0] = MenuCard.USERS;
    assertEquals(MenuCard.SCENARIOS, MenuCard.values()[0]);
    assertEquals(MenuCard.NOTIFICATIONS, MenuCard.valueOf("NOTIFICATIONS"));
    assertThrows(IllegalArgumentException.class, () -> MenuCard.valueOf("UNKNOWN"));
  }

  private static void assertTopBar(MenuViewModel page, String role) {
    var top = page.getTopBar();
    assertEquals("schubert NK", top.getBrand());
    assertEquals(READER, top.getUsername());
    assertEquals(role, top.getRole());
  }

  private static List<Card> views(MenuViewModel page) {
    return page.getCards().stream()
        .map(card -> new Card(card.getTitle(), card.getDescription(), card.getHref()))
        .toList();
  }

  private static SessionPrincipal principal(UserRole role) {
    return new SessionPrincipal(
        READER, role, AuthenticationContext.of("0".repeat(64)), Instant.EPOCH);
  }

  private record Card(String title, String description, String href) {}
}
