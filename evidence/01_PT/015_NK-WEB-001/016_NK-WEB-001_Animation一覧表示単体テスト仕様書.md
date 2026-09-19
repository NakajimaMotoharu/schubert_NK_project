# Animationメニュー・一覧表示単体テスト仕様書

NK-WEB-001/SCR008/009、AnimationMenuViewModel/AnimationListViewModel・nested Video/Row。FUN006/AUT/TST、UI223§6/235§4～5/264、SS313/323/352、PG204。仕様先行、未実装/未実行。AnimationViewModelTestの以下8methodを一意対応。

| Test ID | method | 入力・操作・fixture | 独立期待値・根拠 |
|---|---|---|---|
| PT-WEB-230 | web230AnimationMenuCounts | ANM15/4/true/20、0/0/false/0、999境界、不整合 | UI235整数相互整合、両role/username、opening値保持 |
| PT-WEB-231 | web231MainGrouping | 3main/2sub、subがparentより前、欠落sub | API main出現順、parent対応、件数5/rows3、メインパート一覧/section main、placeholder用Optional |
| PT-WEB-232 | web232OvaAndBounds | OVA4/0/50、MAIN0/50、51/件数不一致 | OVA順・title/byte/path/固定URL、上限50、0の不変空list |
| PT-WEB-233 | web233RejectInconsistentGroups | category混入、親欠落/不要親/orphan/重複parent/id/zero size/空dotID | IAE拒否、黙殺/重複表示/補正しない、固定message |
| PT-WEB-234 | web234NullAndOwnership | actor/data/category/list/要素null、可変list変更 | 明示境界拒否、返却list変更不可、入力変更非波及 |
| PT-WEB-235 | web235ClosedBeansAndRedaction | bean graph、全getter、toString、特殊ID URL | protocol/session/request/descriptor非保持、独立percent literal、fixed redact |
| PT-WEB-236 | web236SyntheticHtmlEscaping | title/path/username特殊文字、合成Thymeleaf template | text/属性escape、注入要素なし、文字列表示でfile解決なし |
| PT-WEB-237 | web237ConcurrentProjection | 64actor独立count/list、共有factory | 値・順序・TopBar混入なし、immutable結果 |

期待値はUI/Current AnimeController/AnimeService/animation-list.htmlの固定文字列・配列・countから作り、Production projection/URL生成をexpectedへ呼ばない。正常/境界/異常/null/例外/並行を網羅。再送は純粋factoryの同入力同投影で副作用なし、MQ再送責務は別。Java line/method/class/branch100%、NullAway/SpotBugs/Spotless、独立inventory canaryを要求する。

実行command/環境/対象commit/日時/exit/coverage/関連BUG/SSC/証跡path・hashを017結果・manifestへ記録する。raw context/token/path秘密を保存しない。これは表示部品であり、実template/HTTP/stream/MQ/実NK Characterization・PGPT/IT/STの完了ではない。
