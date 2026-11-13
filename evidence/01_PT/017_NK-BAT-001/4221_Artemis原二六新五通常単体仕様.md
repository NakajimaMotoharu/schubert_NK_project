# Artemis原26・新5の通常単体仕様

NK-BAT-001/NK-OPS-001、WBS-P017-10/F03、MQ001002009010/SYS004/UI231251253/SS312321341342343352。source a81ffb6bcb3850f109021e743df40d915fdd7c4b。BUG2766/2767、YKT2359/2387。

原whole6Test全26の独立literal/全assertionを保持、親workerだけ10秒join→finallyinterrupt・10秒join→alivefalse、daemonは未終端時にtestを成功へせずprocess無期限保持を防ぐ。全26体の原source逆変換証明PG28526。新whole5は必要fatalcatalogの回帰であり拒否PTの抽出や代替fixtureではない。

Main10/全physical26（Guard1含む）を報告しhelper未網羅を除外しない。Acceptor/Startup全source＋Evidence/Managementを対象に四counter実測値を示し、不足は不足のまま残す。独自除外/旧exec合算なし。全190/正式1964-53/実Broker/Root/native/DB/coverage全体の受入は別、通過件数を全体認定へ足さない。

| Test ID | 独立期待値・根拠 |
|---|---|
|MQCAT001|OriginalError sameidentity forlegacy/detailed topology adapters fromcause/suppressed/cyclic graphs, legacyfirst1/later0/detailedaddressQuery1/no borrowedclose|
|MQCAT002|OriginalError identityfromknownActiveMQcause/suppressed/cyclic beforefixedtopology; nonfatalstillfixedARE/no cause-suppression; addressQueryexact1/close0|
|MQCAT003|JsonException/ClassCast/IllegalState ×cause/suppressed/cycle preserveOriginalError; parserexact1/started0/sessioncalls0|
|MQCAT004|CheckedSDKencoderoriginalError for3graphs; SS333existingIOException witherrorcause remainsfixedARME withoutcause-suppression; IRQfalse|
|MQCAT005|InterruptedExchange3graphs setsIRQbeforethrowOriginalError/queryexact1/existingattributeidentity; testrestorespriorIRQflag|

原26個別canonical TestID/fixture/hashは[PG28527](../018_NK-OPS-001/evidence/PG28527-mq31-current-source-independent-oracle-closure-v1/manifest.json)。PG28512で6SDKの公式既SHA1/POM/remote出自を先行確認。SDK依存はclient2/非nativeNetty3/SLF4J1だけ、接続factory/requestor/eventloopの実initはpostで拒否、同classの引用が権限を与えない。各proxyは固定callback/JSON又はstart/addressQueryで意図した独立例外を返し、実Socket/DB/Root/Unit/credential/permit操作0。

実行はtools/quality/pgpt_closed_host_profile.py prestyle→prepare→static→preflight→run <fixedsource>、独立pgpt_closed_host_post.py <profile> <samefixedsource>。RootJava25/NullAway/全PMD・CS・SB・GJF、正常/境界/null/unknown/再送読取・独立threadlocal/IRQ、F/E/Sabort0と全CRC/init/countersを照合。終了commit/manifestと実測coverageは結果書へ追記、未実行をPASSにしない。
