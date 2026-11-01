# ScenarioAuditWriter 原whole5 単体テスト仕様

2026-11-01 / PG-D1081 / PG17270-SCENARIO-AUDIT-ORIGINAL5、source6b53/開始HEAD85e23d810487ac99c79e8fc3b7f1e705a60cd833・dev-foundation。事前1.5/4/8共有pp cap10、主F03/元ownerはcanonical保持、共有used73/rem27。indexScenarioAuditWriter→1247/358を照合、旧sourceの監査成功を現sourceへ転用しない。現2650 registryに対象Mainとwhole Test5は未登録。

Main全81行（宣言/空行を含む実行対象はmanifestにhash固定）・原Test全文と全private Jdbc/Search/assertBinding helper・元ScenarioRequestFixture全文を読了。Main.writeは借用ConnectionのprepareStatementだけ、固定insert・八bind・一行影響判定・owned Statement close、request.response値とNFC/replacement/closed JSONだけ。TestはJDK Connection/PreparedStatement proxy、他Connection操作はAssertionErrorで拒否する。元wire fixtureは空白byte/固定offset/UTF8/独立CommonHeader/UUID.randomUUID、Test専用public synthetic UUIDを生成するが値は保存せず、runtime鍵やAuth sessionを発行しない。

ScenarioRequest.decode/headerの全current sourceと実呼出分岐を読了、LayoutRegistry/PayloadCodec/PayloadTypeCatalogの既current Source資格を補助根拠として再利用する。canonical/HMAC/query/Repositoryの分岐は呼ばない。API/DB/Root/VM/JMS/鍵file/native/権限/permit/intent/Graph操作0、実SQLbackend0、fake prepare/bind/execute/closeは真に呼ぶ。元helperを改変/抽出せずfresh javac、旧Test CP0・closed Mapで原5すべてを実行するPT_DEFAULT。

Test IDは一意なJUnit identity dev.codex.schubert.nk.api.application.scenario.ScenarioAuditWriterTest#methodを使用する。元Javadoc PT-SCN-AUD469003..006（四番号）を五methodへ暗黙zipせず、関連旧監査範囲として保持、新JUnit case/Test ID製造0。

|method（上記Test ID末尾）|独立input/期待|
|---|---|
|searchCountAndSensitiveConditionsNeverLeak|手書search DATA/件数0・2・99999900→SCENARIO_SEARCHED、八bind、actor101/é＋空白5、JSON key layout/resultCountだけ、機密条件非包含|
|inlineAndFileUseTheirIndependentRecordCounts|独立inline record1/file descriptor201→SCENARIO_VIEWEDの件数1/201、本文/title/pathをJSONへ入れない|
|nonCatalogListQueriesDoNotTouchDatabase|GAM/SPK/RTE/SCF原要求→prepare/close0、未承認audit actionを作らない|
|sqlFailuresArePropagatedWithStatementOwnership|prepare/bind/execute/close各単一SQL故障は同一instance、prepare前close0/取得後close1、影響件数0/2はSQL非成功|
|nullBoundaryFailsBeforeDatabaseEffects|五API引数null→NPE契約拒否/prepare0、NPEを正常扱いしない|

期待は固定SQL literal、列順/八bind、固定actor/日時/count/JSON keyset、故障instance/閉鎖回数。request.headerのUUIDは入力値の同一性確認であってwriterからexpectedを生成しない。Testのtuple/object getterを実DB結果の証明へ変換0。多重故障/実TX rollback・Inbox再送/実並行後条件は当単純writer scopeだけで閉鎖せず上位programに残す。

RD FUN003～005/MON003004、UI234237、SS323324332351352。原contextのold469001～008・BUG742/YKT523/BUG1516は関連歴史を保持し今回新解決に再加算しない。17269 plan→17270 rawでOS/JDK/env/argv/時刻/source/run/終了/XML/FES/abort/exec/hash、postでMain一Sourceの全physical/四counter/CRC/session/四held六native等を照合。実測前に100%や正式受入を予定値で認定しない。Main/Test/source/SS・現baselineは不変更、正式1964PT53scope/17of190/工数null/QA051final/全HOLD/原予測不変。通常小群/PMO待ち停止0。
