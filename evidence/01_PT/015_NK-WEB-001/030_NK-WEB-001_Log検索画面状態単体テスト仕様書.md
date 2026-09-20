# Log検索画面状態単体テスト仕様書

NK-WEB-001/SCR014、LogSearchViewModel.success/invalid/pageLink・Filters/FieldError、FUN008/AUT002/MON003/UI222/225/235/SS313/352/PG-D-215。仕様先行・未実装/未実行。LogSearchViewModelTestの8methodへ対応。

| Test ID | method | 入力・操作 | 独立期待値 |
|---|---|---|---|
| PT-WEB-286 | web286SuccessfulSnapshot | 全7条件/ADMIN/新着順2row | 全filter/TopBar/閉結果をliteral照合、errorなし |
| PT-WEB-287 | web287Pagination | 0/1/100/101/201件・先頭/中間/末尾/過大page | 固定URIのprev/next、空なし、過大は最終補正 |
| PT-WEB-288 | web288QueryEncoding | 日本語/補助文字/空白/plus/&/=/#/%/日時 | 独立percent literal、全7条件順・JST入力維持 |
| PT-WEB-289 | web289ResponseBinding | 要求/応答page不一致・invalid form・件数不整合 | 拒否、勝手なresort/補正なし |
| PT-WEB-290 | web290InvalidFields | 全field/未知名・control・length・value・31日 | 固定順errorと固定文言、非安全文字消去、結果/リンクなし |
| PT-WEB-291 | web291NullRoleOwnership | null境界/USER両factory/元list変更 | 契約拒否・snapshot不変・返却list不変 |
| PT-WEB-292 | web292ClosedBeanAndEscaping | bean properties/診断/HTML記号 | allowlistのみ・raw contextなし・Spring Thymeleafでtext escape |
| PT-WEB-293 | web293ConcurrentViews | 64条件/8worker | actor/filter/result独立・元fixture不変 |

期待値はUI225/Currentのfield表示とUI222の100件page算術・固定URI文字列から独立作成し、Production encode/page methodをexpected生成に使わない。正常/境界/異常/例外/null/並行を含み、再送は副作用なし投影なので非該当。Java25/Maven3.9.12、selected新8＋既存Log結果/form・Scenario状態後clean verify、4coverage100%/NullAway/SpotBugs等0を必要とする。

031結果/manifestへ実行日時/OS・JDK・tool/branch・commit/command・exit/input/expected/actual/coverage/関連BUG・SSC/path・hashを保存する。failed/flaky/skipped/not-runは非合格。HTTP認可・template・実broker・実NKgate・PGPT/IT/ST未完了。
