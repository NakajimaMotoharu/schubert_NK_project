# NK-WEB-002 Scenario階層画面単体テスト仕様書

Program共通追補（2026-10-22、Scenario画面本体の仕様変更なし）：ReceiptReferenceRepositoryのPT-WEB-RECEIPT-GRAPH329001～003は[018/1448](../018_NK-OPS-001/1448_Web_SQLcatalog・REQUEST投影graph単体テスト仕様.md)へ一意に追跡する。SS312/3319.4/332/354・QA048/BUG1592、独立SQL/unknown優先/閉資源counter・固定catalog・例外graphの仕様であり、表示/認可/technical locatorの業務契約は不変更。旧不適格赤/fixture是正は1449、当原資格・coverage未確定分を正式画面PTへ加算しない。

対象: ScenarioController.games/routes/filesと内部認証/交換/終端helper、ScenarioMvcConfiguration、WebMvcConfiguration view allowlist追補、templates/scenarios.html・scenario-routes.html・scenario-files.html・fragments/layout.htmlの共有user操作。FUN004/AUT001～003/SYS006/TST001～005、UI221～223/234/264、SS311/313/314/323/352、SSC071/PG194。他画面や本番bootstrapは対象外。

| Test ID | method | 事前条件/入力/操作 | 独立期待 |
|---|---|---|---|
| PT-SCR-001 | screens001GamesSuccess | USER/ADMIN、0000/0200、GAM0/2/10 | 1回要求、固定空DATA、閉model、title/code/順/URL一致 |
| PT-SCR-002 | screens002RoutesSuccess | 両game、RTE1/50、prefix00/99 | 要求game literal、response順・route名・件数を保持 |
| PT-SCR-003 | screens003FilesSuccess | 両game/prefix01/99、SCF1/500 | game/prefix binding一致、routeName/title/path/entries/URL保持 |
| PT-SCR-004 | screens004EmptyHierarchy | GAM/RTE/SCF0件成功応答 | GAM200空結果、Route/FileはCurrent同様404、成功modelなし |
| PT-SCR-005 | screens005AllResultCodes | 12result code、error profile固定vector | 独立HTTP表、0102は別専用終端、modelなし、追加送信なし |
| PT-SCR-006 | screens006InvalidSessionTerminal | 実暗号session/現在context、API0102 | local破棄、nav302 login?session-expired/非nav401、後続renderなし |
| PT-SCR-007 | screens007WireAndBindingFailure | 不正header/SCF game・prefix不一致/transport | 503・modelなし、retryなし、raw/cause非表示 |
| PT-SCR-008 | screens008NullAndForeignPrincipal | constructor/handlerのnull、他Principal | 境界拒否、MQ0、偽principal値を読まない |
| PT-SCR-009 | screens009ClosedRoutesAndRequests | 正規game/ASCII2桁、未知/数値/detail path、method | 3正規routeだけdispatch、衝突なし・未知は404/405、query偽role/context非使用 |
| PT-SCR-010 | screens010RealTemplatesAndNavigation | 3実template＋CSRF/Topbar | Current見出し/nav/カード列・文字列、POST logoutとCSRF、USER/ADMIN表示 |
| PT-SCR-011 | screens011HtmlEscaping | API title/route/pathとusernameにHTML文字 | text保持、script/event nodeなし、raw context非露出 |
| PT-SCR-012 | screens012CompatibilityObservations | Current/UI固定表示literalとDOM抽出 | CHR-S05/S06に対応する公開合成fixtureの順序/文字列/URL比較。実NK全体gateとは別 |
| PT-SCR-013 | screens013ConcurrentQueries | 100独立context/correlation | 応答取違え/共有Modelなし、pending0 |
| PT-SCR-014 | screens014FailurePropagation | model追加/response IO/未知runtime/0102失敗 | 元失敗を成功扱いしない、追加送信/正常画面なし |
| PT-SCR-015 | screens015MvcConfiguration | bean依存/allowlist/null/unknown view | 明示登録3画面、未知/外部redirect/forward不可、既存Menu/Error維持 |
| PT-SCR-016 | screens016RealHttpSecurityAndTerminal | 実Tomcat＋既存security/session＋合成API sender | 未認証Login遷移、USER/ADMIN、no-store/header/CSRF、API0102後session終端 |

golden電文はUI232/234 byte offsetから独立構築し、expectedにProduction codecを使わない。HTTP/DOM期待はCurrent templateとUIのliteral。fixtureは公開合成値で、master実体/credential/session/cookie/tokenは証跡に保存しない。正常/boundary/null/exception/並行・0/最大、追加Retryなしを網羅。既存Menu/error/session/APIinvalid PTも回帰する。

Java4coverage100%/NullAway/staticを要求。templateの各if/each分岐は空・単・最大・escape/role/CSRFで照合する。失敗/flaky/skipped/not-runを成功に含めない。実行command/環境/対象commit/終了/結果/coverage/BUG/SSC/hashは002とevidence/manifest.jsonへ成功後固定する。正式PT-WEB-20260920-12で16PTと全reactor成功、002/manifest参照。実Artemis/全layout登録/本番logger/実NK全CHR/IT/STの完成証跡ではない。


P01504再送記録の原16＋graph4＋新fatal5全25仕様は[4121](../015_NK-WEB-001/4121_P01504再送記録原十六・新五全二五件単体仕様.md)。元19328成功は原source維持、未実行をPASSへ加算しない、費用主担当P01504一度だけ。

[4121 再送記録通常25](../015_NK-WEB-001/4121_P01504再送記録原十六・新五全二五件単体仕様.md): PG27508-REVOCATION25固定全25成功、原赤3失敗別記/target2四100・全scopepartial・原WBS未受入。

[4123 失効暗号通常16](../015_NK-WEB-001/4123_P01505失効暗号原七・新五全十六件単体仕様.md): PG27548-REVOCATION-CRYPTO16固定全16成功、原赤3失敗別記/target2四100・全scopepartial・原WBS未受入。


WBS-P016-01公開source契約/独立期待値/TestIDは[4126_P01601Login画面原二artifact契約対応.md](4126_P01601Login画面原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-02公開source契約/独立期待値/TestIDは[4127_P01602Menu画面原四artifact契約対応.md](4127_P01602Menu画面原四artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。

[4128 共有TraceMenu通常24](../006_NK-MSG-002/4128_P00603共有Trace原十五・新五全二四件単体仕様.md): PG27610-TRACE-MENU24固定全24成功、原赤3失敗別記/実target全四100・全scopepartial・原WBS未受入。

[4129 CaddyContext通常24](../015_NK-WEB-001/4129_P01502CaddyContext原十五・新五全二四件単体仕様.md): PG27630-CADDY-CONTEXT24固定全24成功、原赤5失敗別記/実target全四100・全scopepartial・原WBS未受入。


WBS-P016-03公開source契約/独立期待値/TestIDは[4130_P01603SCR003検索入力結果原四artifact契約対応.md](4130_P01603SCR003検索入力結果原四artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-04公開source契約/独立期待値/TestIDは[4131_P01604SCR004Game一覧原二artifact契約対応.md](4131_P01604SCR004Game一覧原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-05公開source契約/独立期待値/TestIDは[4132_P01605SCR005Route一覧原二artifact契約対応.md](4132_P01605SCR005Route一覧原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-06公開source契約/独立期待値/TestIDは[4133_P01606SCR006File一覧原二artifact契約対応.md](4133_P01606SCR006File一覧原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-07公開source契約/独立期待値/TestIDは[4134_P01607SCR007本文通信組立原九artifact契約対応.md](4134_P01607SCR007本文通信組立原九artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01608/09の個別契約と/2不足は[4137_P0160809Animationメニュー一覧個別契約対応.md](4137_P0160809Animationメニュー一覧個別契約対応.md)。metadata準備のみ、原16/DOM43は元source参照・新PT0。


WBS-P016-10公開source契約/独立期待値/TestIDは[4138_P01610Animation視聴原五artifact契約対応.md](4138_P01610Animation視聴原五artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01610公開表示モデルの新4通常Unitは[4139_P01610視聴public四単体テスト仕様・結果.md](4139_P01610視聴public四単体テスト仕様・結果.md)。Watch target100/全181partial、実ControllerのHOLD/原190未受入は維持。


P01611/12の個別契約と/2不足は[4140_P0161112Music分類区分個別契約対応.md](4140_P0161112Music分類区分個別契約対応.md)。metadata準備のみ、原16/DOM43は元source参照・新PT0。


P01611/12の既全14通常PTは[仕様](4141_P0161112原Music十四単体テスト仕様.md)と[結果](4142_P0161112原Music十四単体結果.md)。新定義0/同execVM2 target100/full211partial、実業務/CHR/原190の/2未受入。


WBS-P016-13公開source契約/独立期待値/TestIDは[4143_P01613Music曲一覧原五artifact契約対応.md](4143_P01613Music曲一覧原五artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01613の公開モデル6新規Unitは[仕様](4144_P01613MusicTrack公開六単体仕様.md)/[結果](4145_P01613MusicTrack公開六単体結果.md)。target100/全180partial、原/2や実ControllerのHOLDは維持。


WBS-P016-14公開source契約/独立期待値/TestIDは[4146_P01614Log原七artifact契約対応.md](4146_P01614Log原七artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01614と共通Pageの原全40は[仕様](4147_P01614原Log四十単体仕様.md)/[結果](4148_P01614原Log四十単体結果.md)。target4 outer四100/全220partial、実業務/監査DB/CHR/原190終了は未受入。


WBS-P016-15公開source契約/独立期待値/TestIDは[4151_P01615User一覧原三artifact契約対応.md](4151_P01615User一覧原三artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-16公開source契約/独立期待値/TestIDは[4152_P01616User追加原三artifact契約対応.md](4152_P01616User追加原三artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-17公開source契約/独立期待値/TestIDは[4153_P01617User詳細更新原十二artifact契約対応.md](4153_P01617User詳細更新原十二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01615/16/17原pureUser32は[仕様](4155_P016151617原User三二件通常単体仕様.md)/[結果](4156_P016151617原User三二件通常単体結果.md)、8source9Code同exec四100/全191partial、actual認証・更新DB/HTTP/token/CHR/451終了は未受入。


P01615新User検索入力8は[仕様](4157_P01615User検索入力八単体仕様.md)/[結果](4158_P01615User検索入力八単体結果.md)、Form全source四100/全177partial、actualHTTP/認可/DB/CHR/451は別未受入。


WBS-P016-18公開source契約/独立期待値/TestIDは[4161_P01618質問受付原六artifact契約対応.md](4161_P01618質問受付原六artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01618/19と要求表示共有の原18は[仕様](4163_P0161819質問入力表示原十八単体仕様.md)/[結果](4164_P0161819質問入力表示原十八単体結果.md)、5source同exec四100/全186partial、actualHTTP/認可/token/DB/CHR/451は別未受入。


WBS-P016-19公開source契約/独立期待値/TestIDは[4165_P01619受付完了原二artifact契約対応.md](4165_P01619受付完了原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-20公開source契約/独立期待値/TestIDは[4166_P01620通知一覧原三artifact契約対応.md](4166_P01620通知一覧原三artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01620/22原検索入力26は[仕様](4167_P0162022通知質問検索原二十六単体仕様.md)／[結果](4168_P0162022通知質問検索原二十六単体結果.md)、二Form全source四100/全178partial、actualNQview/ownerAPI/HTTPDB/CHR/451別HOLD未受入。


WBS-P016-21公開source契約/独立期待値/TestIDは[4169_P01621通知明細原七artifact契約対応.md](4169_P01621通知明細原七artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01621/23原取消削除8は[仕様](4171_P0162123取消削除原八単体仕様.md)／[結果](4172_P0162123取消削除原八単体結果.md)、三完全source component四100/全179partial、実TokenDB/ownerAPI/HTTP/CHR/451別HOLD未受入。


WBS-P016-22公開source契約/独立期待値/TestIDは[4173_P01622質問一覧原三artifact契約対応.md](4173_P01622質問一覧原三artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-23公開source契約/独立期待値/TestIDは[4174_P01623質問明細原三artifact契約対応.md](4174_P01623質問明細原三artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。
