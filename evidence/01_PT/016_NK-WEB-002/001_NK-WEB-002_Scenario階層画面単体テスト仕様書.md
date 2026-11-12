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
