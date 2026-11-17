package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.web.form.LogSearchForm;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm;
import dev.codex.schubert.nk.web.logging.WebHttpLogKind;
import dev.codex.schubert.nk.web.revocation.RevocationFailureCode;
import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** Fixed public vectors: UI222/223/225/235, SS313/314/351/352, QA054, YKT2645. */
class WebPublicEnumContractTest {
  @Test
  void scenarioFieldsRetainTheClosedBindingDictionary() {
    dictionary(
        new String[] {"FORM", "Q", "GAME", "SPEAKER", "CHAPTER", "ENTRY_TYPE", "VOICE", "PAGE"},
        ScenarioSearchForm.Field::values,
        ScenarioSearchForm.Field::valueOf);
  }

  @Test
  void scenarioIssuesRetainTheClosedValidationDictionary() {
    dictionary(
        new String[] {"BINDING", "CHARACTERS", "LENGTH", "VALUE"},
        ScenarioSearchForm.Code::values,
        ScenarioSearchForm.Code::valueOf);
  }

  @Test
  void logFieldsRetainTheClosedBindingDictionary() {
    dictionary(
        new String[] {"FORM", "Q", "LOG_TYPE", "ACTION", "PATH", "LEVEL", "FROM", "TO", "PAGE"},
        LogSearchForm.Field::values,
        LogSearchForm.Field::valueOf);
  }

  @Test
  void logIssuesRetainTheClosedValidationDictionary() {
    dictionary(
        new String[] {"BINDING", "CHARACTERS", "LENGTH", "VALUE", "RANGE"},
        LogSearchForm.Code::values,
        LogSearchForm.Code::valueOf);
  }

  @Test
  void persistedRevocationWarningsExposeOnlyNonSensitiveCodes() {
    dictionary(
        new String[] {
          "SESSION_INVALID",
          "API_REJECTED",
          "INVALID_RESPONSE",
          "UNAVAILABLE",
          "KEY_UNAVAILABLE",
          "PAYLOAD_INVALID",
          "CRYPTO_UNAVAILABLE"
        },
        RevocationFailureCode::values,
        RevocationFailureCode::valueOf);
  }

  @Test
  void httpLogProjectionUsesTheApprovedKindsAndOneEligibleTruthRow() {
    dictionary(
        new String[] {"REQUEST", "MENU_VIEWED"}, WebHttpLogKind::values, WebHttpLogKind::valueOf);
    assertEquals(LogType.REQUEST, WebHttpLogKind.REQUEST.category());
    assertEquals("HTTP_REQUEST_COMPLETED", WebHttpLogKind.REQUEST.action());
    assertEquals("HTTP request completed", WebHttpLogKind.REQUEST.message());
    assertEquals(LogType.ACTION, WebHttpLogKind.MENU_VIEWED.category());
    assertEquals("MENU_VIEWED", WebHttpLogKind.MENU_VIEWED.action());
    assertEquals("Menu viewed", WebHttpLogKind.MENU_VIEWED.message());
    // Independent 32-row truth table: five input bits must all be set. No production oracle call.
    for (WebHttpLogKind kind : WebHttpLogKind.values()) {
      for (int mask = 0; mask < 32; mask++) {
        assertEquals(
            kind == WebHttpLogKind.MENU_VIEWED && mask == 31,
            kind.eligible(
                (mask & 1) != 0,
                (mask & 2) != 0 ? "GET" : "POST",
                (mask & 4) != 0 ? 200 : 201,
                (mask & 8) != 0 ? "/" : "/search",
                (mask & 16) != 0));
      }
      assertThrows(NullPointerException.class, () -> kind.eligible(false, null, 200, "/", false));
      assertThrows(NullPointerException.class, () -> kind.eligible(false, "GET", 200, null, false));
    }
  }

  @Test
  void menuCatalogRetainsAllNineFixedDisplayAndDestinationVectors() {
    dictionary(
        new String[] {
          "SCENARIOS",
          "SEARCH",
          "ANIMATION",
          "MUSIC",
          "QUESTION_NEW",
          "NOTIFICATIONS",
          "QUESTIONS",
          "LOGS",
          "USERS"
        },
        MenuCard::values,
        MenuCard::valueOf);
    String[][] vectors = {
      {"シナリオ閲覧", "シナリオ一覧から本文を読む", "/scenarios"},
      {"検索", "本文、話者、章タイトル、音声有無で探す", "/search"},
      {"アニメ視聴", "メインパート、OVA、オープニング映像を見る", "/animation"},
      {"音楽", "BGMや曲を一覧から再生する", "/music"},
      {"質問する", "質問を送信する", "/questions/new"},
      {"通知", "自分への通知を確認する", "/notifications"},
      {"質問回答", "質問と回答を確認する", "/questions"},
      {"ログ照会", "操作ログとリクエストログを検索する", "/logs"},
      {"User管理", "ユーザーを作成・管理する", "/admin/users"}
    };
    MenuCard[] cards = MenuCard.values();
    for (int i = 0; i < vectors.length; i++) {
      assertEquals(vectors[i][0], cards[i].getTitle());
      assertEquals(vectors[i][1], cards[i].getDescription());
      assertEquals(vectors[i][2], cards[i].getHref());
    }
  }

  @Test
  void errorStatusesRetainHttpAndDisplayVectorsWithoutRetainingAnException() {
    dictionary(
        new String[] {
          "BAD_REQUEST",
          "UNAUTHENTICATED",
          "FORBIDDEN",
          "NOT_FOUND",
          "METHOD_NOT_ALLOWED",
          "CONFLICT",
          "RANGE_INVALID",
          "RATE_LIMITED",
          "UNAVAILABLE"
        },
        ErrorViewModel.Status::values,
        ErrorViewModel.Status::valueOf);
    int[] codes = {400, 401, 403, 404, 405, 409, 416, 429, 503};
    String[] messages = {
      "入力内容を確認してください。",
      "再度ログインしてください。",
      "この操作を実行する権限がありません。",
      "対象が見つかりません。",
      "この操作方法は利用できません。",
      "状態が更新されたため操作できません。再表示してください。",
      "指定された範囲を取得できません。",
      "しばらく待ってから再操作してください。",
      "現在処理できません。しばらくしてから再操作してください。"
    };
    UUID id = UUID.fromString("10000000-0000-0000-0000-000000000001");
    ErrorViewModel.Status[] statuses = ErrorViewModel.Status.values();
    for (int i = 0; i < codes.length; i++) {
      ErrorViewModel model = ErrorViewModel.of(statuses[i], id, Optional.empty());
      assertEquals(codes[i], model.getStatus());
      assertEquals(messages[i], model.getMessage());
      assertEquals("10000000-0000-0000-0000-000000000001", model.getRequestId());
      assertEquals(Optional.empty(), model.getTopBar());
      assertEquals("ErrorViewModel[REDACTED]", model.toString());
    }
    assertThrows(NullPointerException.class, () -> ErrorViewModel.of(null, id, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> ErrorViewModel.of(ErrorViewModel.Status.NOT_FOUND, null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> ErrorViewModel.of(ErrorViewModel.Status.NOT_FOUND, id, null));
  }

  private static <E extends Enum<E>> void dictionary(
      String[] names, Supplier<E[]> values, Function<String, E> parse) {
    E[] first = values.get();
    assertArrayEquals(names, Arrays.stream(first).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < names.length; i++) {
      assertEquals(i, first[i].ordinal());
      assertSame(first[i], parse.apply(names[i]));
    }
    E[] second = values.get();
    E retained = first[0];
    assertNotSame(first, second);
    first[0] = null; // Poison a caller-owned array to prove enum storage remains unmodified.
    assertSame(retained, second[0]);
    assertSame(retained, values.get()[0]);
    assertThrows(IllegalArgumentException.class, () -> parse.apply("NOT_AN_APPROVED_CODE"));
    assertThrows(NullPointerException.class, () -> parse.apply(null));
  }
}
