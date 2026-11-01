package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.controller.MenuController;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.security.Principal;
import java.time.Instant;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

final class MenuProjectionContractTest {
  private static final List<String> TITLES =
      List.of("シナリオ閲覧", "検索", "アニメ視聴", "音楽", "質問する", "通知", "質問回答", "ログ照会", "User管理");
  private static final List<String> PATHS =
      List.of("/scenarios", "/search", "/animation", "/music", "/questions/new",
          "/notifications", "/questions", "/logs", "/admin/users");

  private static SessionPrincipal principal(UserRole role) {
    return new SessionPrincipal("PUBLIC_DISPLAY", role,
        AuthenticationContext.of("a".repeat(64)), Instant.parse("2026-11-01T00:00:00Z"));
  }

  @Test
  void menuProjection001FixedCatalogMatchesCurrentLegacyValuesAndApprovedMenuPurpose() {
    MenuCard[] cards = MenuCard.values();
    assertEquals(9, cards.length);
    for (int i = 0; i < cards.length; i++) {
      assertEquals(TITLES.get(i), cards[i].getTitle());
      assertEquals(PATHS.get(i), cards[i].getHref());
      assertFalse(cards[i].getDescription().isBlank());
      assertFalse(cards[i].getDescription().contains("\n"));
      assertFalse(cards[i].getDescription().contains("\r"));
    }
    String[] legacyDescriptions = {"シナリオ一覧から本文を読む",
        "本文、話者、章タイトル、音声有無で探す",
        "メインパート、OVA、オープニング映像を見る", "BGMや曲を一覧から再生する"};
    for (int i = 0; i < legacyDescriptions.length; i++)
      assertEquals(legacyDescriptions[i], cards[i].getDescription());
    assertEquals("操作ログとリクエストログを検索する", cards[7].getDescription());
    assertTrue(cards[4].getDescription().contains("質問"));
    assertTrue(cards[5].getDescription().contains("通知"));
    assertTrue(cards[6].getDescription().contains("回答"));
    assertTrue(cards[8].getDescription().contains("ユーザー"));
  }

  @Test
  void menuProjection002UserHasExactlySevenImmutableCardsAndOnlyDisplayTopBar() {
    var value = MenuViewModel.from(principal(UserRole.USER));
    assertEquals(TITLES.subList(0, 7), value.getCards().stream().map(MenuCard::getTitle).toList());
    assertEquals(PATHS.subList(0, 7), value.getCards().stream().map(MenuCard::getHref).toList());
    assertEquals("schubert NK", value.getTopBar().getBrand());
    assertEquals("PUBLIC_DISPLAY", value.getTopBar().getUsername());
    assertEquals("USER", value.getTopBar().getRole());
    assertEquals("MenuViewModel[REDACTED]", value.toString());
    assertThrows(UnsupportedOperationException.class, () -> value.getCards().add(MenuCard.LOGS));
    assertEquals(7, value.getCards().size());
  }

  @Test
  void menuProjection003AdminAddsOnlyTheTwoApprovedCardsInOrder() {
    var value = MenuViewModel.from(principal(UserRole.ADMIN));
    assertEquals(TITLES, value.getCards().stream().map(MenuCard::getTitle).toList());
    assertEquals(PATHS, value.getCards().stream().map(MenuCard::getHref).toList());
    assertEquals("schubert NK", value.getTopBar().getBrand());
    assertEquals("PUBLIC_DISPLAY", value.getTopBar().getUsername());
    assertEquals("ADMIN", value.getTopBar().getRole());
    assertThrows(UnsupportedOperationException.class, () -> value.getCards().remove(0));
    assertEquals(9, value.getCards().size());
  }

  @Test
  void menuProjection004EveryRequiredPrincipalAndModelBoundaryRejectsNull() {
    var controller = new MenuController();
    var model = new ExtendedModelMap();
    assertThrows(NullPointerException.class, () -> MenuViewModel.from(null));
    assertThrows(NullPointerException.class, () -> controller.show(null, model));
    assertTrue(model.isEmpty());
    assertThrows(NullPointerException.class, () -> controller.show(principal(UserRole.USER), null));
  }

  @Test
  void menuProjection005DirectControllerPublishesOnlyPageAndPreservesCallerModel()
      throws Exception {
    var mapping = MenuController.class.getMethod("show", Principal.class, Model.class)
        .getAnnotation(GetMapping.class);
    assertArrayEquals(new String[] {"/"}, mapping.value());
    for (UserRole role : List.of(UserRole.USER, UserRole.ADMIN)) {
      var controller = new MenuController();
      var model = new ExtendedModelMap();
      var marker = new Object();
      model.addAttribute("retained", marker);
      assertEquals("menu", controller.show(principal(role), model));
      assertEquals(Set.of("retained", "page"), model.keySet());
      assertSame(marker, model.get("retained"));
      var page = (MenuViewModel) model.get("page");
      assertEquals(role == UserRole.ADMIN ? 9 : 7, page.getCards().size());
      assertEquals("PUBLIC_DISPLAY", page.getTopBar().getUsername());
      assertFalse(model.toString().contains("a".repeat(64)));
      assertFalse(model.toString().contains("SessionPrincipal"));
    }
  }

  @Test
  void menuProjection006ForeignPrincipalIsRejectedBeforeAnyModelPublication() {
    Principal foreign = () -> "PUBLIC_DISPLAY";
    var model = new ExtendedModelMap();
    var failure = assertThrows(SessionStoreException.class,
        () -> new MenuController().show(foreign, model));
    assertEquals("session storage is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertTrue(model.isEmpty());
  }
}
