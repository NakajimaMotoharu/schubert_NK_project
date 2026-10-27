# Main残Map八件・source-only PGレビュー結果

source442441c83f73935eb2bd33cd40a7b9884eb7dfe3、2323/PG-D737/event2688、全Main/Test/source不変更。MaintenanceRunFiles1426行/InspectorUnitSnapshot416行、BatchRun/MaintenanceActivation/MaintenanceCompletion三record全文を確認し、当八builderは呼出し内local→private immutable copyであって共有可変Mapではないと判断した。ConcurrentHashMapへの機械置換・抑制0。原raw八は保持し、全体の適用性判定待ちとする。

|原ID|method/変数|copyと非escape根拠|元owner/cost|
|---|---|---|---|
|02847/02848/02849/02850|retirementScan/runs,begins,done,plans|各呼出しで四new HashMap、IO/decoderへMap引渡し無し、private Inventory compact constructorで四Map.copyOf|P00403|
|02853/02854/02855|scan/runs,begins,done|各呼出し三new HashMap、同期private graph検証→Map.copyOf三→private Graph、可変builderを共有field/外部callbackへ渡さない|P00403|
|03093|InspectorUnitSnapshot.parse/fields|fresh fields→private constructor final values=Map.copyOf、String/UUID/数値等の観測だけで可変aliasなし、入力clone/wipe|P00404|

三Map値はUUID/Instant/enumと不変recordの組合せで、Map.copyOfだけを深いcopyと誤認していない。Session.performのstateLock/executeのscopeLockは補助根拠で、外部OS/DB排他の成立証拠ではない。Root/Inspector/Unit/原本/退役/実ファイル/Backup/DB/VM/native/permit/鍵の操作0、Main method/parse自体も実行0。既関連Testの部分抽出や別fixtureで代用せず、新PT/coverage/動的資格0。呼出し・copy/value/alias構造が変われば再評価する。

|証拠（evidence/provisional配下）|実結果・SHA256|
|---|---|
|PG12334-remaining-main-maps-context-v1|0/八理由/二Main＋三値定義・4227b10cee4cf12fdb0bf19af53bd3f75236625d4470680294fa8d80cb91a17e|
|PG12336-remaining-main-maps-post-v1|0/28異常metadata（row19＋件数6＋owner3）・e180597ce36baed2150998a199c08d182ca79f147fd08f8b1ef36abf36b02db0|
|PG12338-current-remaining-main-maps-delta-v1|0/八raw保持・ac6daf60dbf666a1ed0af9b17a49c1ad651e963e7bc54a555ab7c7733521fdde|
|PG12340-current-remaining-main-maps-delta-post-v1|0/独立集合八異常・ef0537f204a8fcfad0e50918464abe66e8bff61322453dbb6b51bc0d482f3949|
|PG12342-remaining-main-maps-trace-v1|0/追加参照だけ・150645180bbcd889b331c6ff5addc0d73d1aae7427cfeec4c67240917b95887b|
|PG12344-remaining-main-maps-trace-post-v1|0/原意味不変・cf94b806a2de96aab29234fb37f800033a2272a24b9af21cde1fc5c83bbe30fe|

commandは各checked entry `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg<番号>_<対象>.py`、全lint/body0。writer/独立側は原10690の完全path＋属性/ID、raw byte spanと別enclosing-method解析、全source/normal12312 input SHA、copy制御、原artifact owner/costとtrace_owner_joinを検証。sourceContexts/rawRetainedは一意選択ID八から算出、wholeStaticScopeRawは未測定null。trace manifestのsourceContextsはdescriptor配列八でcontext manifestの整数八とschemaを区別する。

current raw8583/累計834/Main1512-Test7071/追加8は不変、理由参照3114→3122/pending662→670/未参照5461。理由参照の増加を新raw是正八や新受入八にしない。過去Main Map十一理由は元source別の歴史証拠として保持し、当source実PTへ合算しない。485二section追加参照/486inventorySHAのみ、983行/原artifact/requirements/owner-cost/予算/受入は不変、全監査前後同HOLD1。

当群新工具失敗0、draft AST参照検査・初回checked lintを適用、元成功再演0。原0.5/2/4pp cap10/fresh60→60/reset1793599188、usage e94fdd599143105d9b6f493822ed2ad556c167561d07c203ab8f6422f850222f/N-T専有費null、丸め共有0≠専有0。正式1964/53・17/190・工数null/QA051final/全F03-451/HOLD・元予測不変更。保存commit/公開scan/具体的次commandは456/460へ。通常小群/commit/PMO待ちで停止しない。
