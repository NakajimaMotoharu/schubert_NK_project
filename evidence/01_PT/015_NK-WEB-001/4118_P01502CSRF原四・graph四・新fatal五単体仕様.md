# P01502 CSRF原4・graph4・新fatal5 通常13件仕様

Program NK-WEB-001/SS314/352/BUG2707・YKT2359。元WEB032..035（生成独立hex/全長64..128/先中末差分/欠落異常/null/NFC外字/redaction/100並行）、既SessionFailureGraph1＋SessionJdbcGraph328三を保持し、新WEB-CSRF-FATAL001..005を全4class13件の単execで検証する。元TokenTest4は既invokeAll20/Future20/finallyshutdownNow-await10で有限、修正/新規として計上しない。

|Test ID|新method|独立期待値|
|---|---|---|
|WEB-CSRF-FATAL001|fatal001ProviderCauseRetainsIdentityAndWipesThirtyTwoBytes|ProviderException.cause内Errorを元identityで伝播/出力一時32byte全0|
|WEB-CSRF-FATAL002|fatal002SuppressedSqlNextRetainsIdentityAndOriginalGraph|suppressed→SQLnext→cause到達Error同一/元graph不変/32byte消去|
|WEB-CSRF-FATAL003|fatal003NonfatalCyclesReturnOnlyFixedCatalogAndWipeBuffer|非fatal循環有限帰還/固定IllegalStateException文字列・cause/suppressed空/消去|
|WEB-CSRF-FATAL004|fatal004DirectErrorPropagatesAndCleanupStillRuns|直接Error非変換・finally32byte全0|
|WEB-CSRF-FATAL005|fatal005NextGenerationAfterFatalHasNoRetainedFailureOrBufferState|fatal保持・消去後に同caller CSPRNGが回復し次生成は独立literal29×32/一致/固定redaction/消去|

Error期待はfixture保持object、text/0配列/次回hexは手書き固定値、productionでexpectedを算出しない。public synthetic CSPRNGだけ、配備key/token/cookie/認証情報・DB・HTTP・OS権限・VM/Root・privateSnapshot・actual4のIOなし。CSRF tokenを認証grant/operation tokenへ代替しない。新@Testは5秒SEPARATE_THREAD、元workerの有限契約保持、NPE catch正常化なし。

PG27448はMainToken/SessionStore/InvalidRowとpackage-info二つの全5source/5physicalのみを変更なしroot Maven compiler（release25/ErrorProne2.50/NullAway0.14.1/JSpecify/Werror）で新compile。SB0、新TokenMain＋Test4 PMD raw5は元StandaloneJUnit有限worker文脈で個別非該当、CS/configuredGJF0・抑制0。JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15/JSpecify1.0.1だけ。Proto/Gson/Spring/API/Web project jarをCPへ入れず、class/source/hash/command/exitをmanifestへ結合。全5には自然branch0/未使用InvalidRowも含めて未網羅を残す。targetToken/helper四100は成立後に実測記録し、全5を強制100にしない。

開始費.15/.45/.9pp cap2（新5/元source red対照.075/.225/.45＋safeMain compile/static/必要13資格.075/.225/.45）。Main固定1e442e0e、Test sourceは実行時記録。PG27452は新5のみを元fa9b相当のnormal実classへ実行し想定3失敗を製品FAILで保存する。PG27460は修正後全13を一度、PG27462で真正terminal/XML/allTest/CRC/単session/全5scope/init/四counterを独立照合。旧成功/別source/別execを合算せず、他Crypto29/Json12/Proto130の確認再演なし。

実行 `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1643_csrf_fatal_original_red_control.py <固定Test source>`、次に`1641_csrf13_qualifier.py run <同source>`。全13未実行をPASSへ加算しない。BUG2707他projection六sourceと全53site runtime/実session認証/DB・chain・451/元190は未受入、正式1964/53/工数null、IT/ST宣言なし。
