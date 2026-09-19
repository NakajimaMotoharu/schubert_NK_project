# 検索template単体テスト仕様書

NK-WEB-002/SCR003/search.html、fragments/pagination.html、schubert.css検索部、WebMvcConfiguration、FUN003/AUT/TST、UI222/223/234/264、SS313/352、PG202。正式PT-WEB-20260920-19で8PT成功、008結果/manifest参照。既存PG201scriptの実行PTはSCR025で重複計上しない。

| Test ID | method | fixture・入力・操作 | 独立期待 |
|---|---|---|---|
| PT-SCR-026 | search026CommonLayoutAndInputs | 両role、6入力/候補、実resolver render | Current/NK title/h1、候補順/選択、GET /search、共通操作、CSRFはLogout1個だけ |
| PT-SCR-027 | search027ResultsAndAudio | 2entry、chapter/speaker/代表audio有無 | literal metadata/body順・Scenario anchor/player/DL、なし時mediaなし |
| PT-SCR-028 | search028PaginationAndEmpty | 0/1/100/101/201件、先頭/中間/最終・条件特殊文字 | 空文言/上下pager、literal件数・範囲・前次URL、二重encodeなし |
| PT-SCR-029 | search029ValidationErrors | 全field違反/未知enum/構造違反/Unicode error | fixed field message・escaped入力再表示、結果/件数/pagerなし |
| PT-SCR-030 | search030EscapingAndCsp | username/filter/候補/本文へHTML文字 | 注入DOM/inline JS/event/styleなし、固定same-originscriptだけ、秘密contextなし |
| PT-SCR-031 | search031MaximumRowsAndCandidates | 100結果/500speaker/10game | 全件・両端・順序保持、silent truncateなし |
| PT-SCR-032 | search032CssResourcesAndViewBoundary | 独立Current CSS値、resource GET/HEAD/不存在、view allowlist | 全追加宣言/900pxを照合、JS実体配信、unknown view/JS拒否 |
| PT-SCR-033 | search033ConcurrentRendering | 64独立actor/filter/result/CSRF、共有resolver | cross-request混入なし、各DOM/入力/Logout CSRF一致 |

入力はpublic synthetic、期待はCurrent search.html/styles.cssとUI明示値を独立転記。Production mapper/URL methodをexpectedへ呼ばない。正常・境界・異常・nullはmodel/formのPG198～200と組み合わせ、templateの全条件/反復/escapeを確認。Java全4coverage100%/static、PG201JS coverage100%、既存Menu/Error/階層/本文回帰を維持。実Browser画像/HTTP業務controller/実NKgate/IT/STは未完了。008/manifestへcommand/時刻/commit/環境/exit/input/expected/actual/coverage/BUG/SSC/hashを保存する。
