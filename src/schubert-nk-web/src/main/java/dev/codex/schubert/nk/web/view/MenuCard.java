package dev.codex.schubert.nk.web.view;

/**
 * Fixed display catalog, never a client-selected URL. NK-WEB-001; FUN-002; UI223; SS313;
 * PG-D-115/PT-WEB-142..147.
 */
public enum MenuCard {
  SCENARIOS("シナリオ閲覧", "シナリオ一覧から本文を読む", "/scenarios"),
  SEARCH("検索", "本文、話者、章タイトル、音声有無で探す", "/search"),
  ANIMATION("アニメ視聴", "メインパート、OVA、オープニング映像を見る", "/animation"),
  MUSIC("音楽", "BGMや曲を一覧から再生する", "/music"),
  QUESTION_NEW("質問する", "質問を送信する", "/questions/new"),
  NOTIFICATIONS("通知", "自分への通知を確認する", "/notifications"),
  QUESTIONS("質問回答", "質問と回答を確認する", "/questions"),
  LOGS("ログ照会", "操作ログとリクエストログを検索する", "/logs"),
  USERS("User管理", "ユーザーを作成・管理する", "/admin/users");

  private final String title;
  private final String description;
  private final String href;

  MenuCard(String title, String description, String href) {
    this.title = title;
    this.description = description;
    this.href = href;
  }

  public String getTitle() {
    return title;
  }

  public String getDescription() {
    return description;
  }

  public String getHref() {
    return href;
  }
}
