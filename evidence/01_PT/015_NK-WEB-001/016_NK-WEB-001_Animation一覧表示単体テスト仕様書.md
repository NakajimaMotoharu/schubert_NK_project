# Animationメニュー・一覧表示単体テスト仕様書

## 2026-11-21 当候補の既存8件再資格

SCR008/009、UI223/235、SS313/323、PT-WEB230～237。既存の固定入力、表示順、件数0/50/51と不整合、親子関係、ロール、HTML escape、有限並行、戻り値と秘匿の独立期待をそのまま実行した。元PG24476とは物理が相違するため現PG41454で一回実行。新しい試験定義は0。

現Core `2611e1acbd`／Test `2c13de0628`。JDK25、現Protocol JARと固定SDK、Webの表示4 Main・元1 Testだけ。実行 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5684_scr009_current_original_eight.py`。8/8成功・失敗/エラー/skip/未実行0。一つの元execに対してSCR009の3物理は生72行・20method・3class・48branch・341命令、SCR008の1物理は19行・8method・1class・4branch・74命令で未達各0。共用二型の未達は別欄に保持。過大件数のPG41182とは3物理が同一で、元テスト再演やexec合算はしていない。実HTTP・本番画面組立・認証・実CHRと全451は未受入。

- 実施結果・独立結果: evidence/01_PT/018_NK-OPS-001/evidence/PG41454-scr009-current-original-eight-v1/independent.json SHA-256 `d50def5f84d766a6845d413ff8be953c199bffe9f028cb371223b55a2bd51c3a`

NK-WEB-001/SCR008/009、AnimationMenuViewModel/AnimationListViewModel・nested Video/Row。FUN006/AUT/TST、UI223§6/235§4～5/264、SS313/323/352、PG204。正式21で8PT合格、実行詳細は017とmanifest参照。AnimationViewModelTestの以下8methodを一意対応。

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
