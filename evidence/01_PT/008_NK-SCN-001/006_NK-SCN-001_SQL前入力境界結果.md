# Scenario/Media SQL前入力境界・実行結果

2026-10-26 13:28 JST、仕様SCN005/MED003/assessment2044、source f12718441140c670950760185b596ab5627377db/dev-foundation、Production Main21d不変。Scenario新九ID/九method、Media新13ID/13method、共同runの合計22/2suiteを一回だけ実行し全成功。F/E/S/aborted0、39単独null投入＋8幅超過の47入力条件を確認。Test method数22と入力47を混同しない。

実command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B tools/quality/pg10264_scenario_media_boundary_host.py`。Linux amd64 7.0.0-38-generic/JDK25.0.4+7-1-26.04-Ubuntu/Maven3.9.12/JUnit5.13.4・platform1.13.4/JaCoCo0.8.15・ASM9.10.1。実引数/dependency hash/時刻/各exitは共有manifest参照。実DB/VM/JMS/Root/network/credential/native操作0。

018_NK-OPS-001/evidence/provisional配下：

|manifest|SHA-256|結果|
|---|---|---|
|PG10258-scenario-media-boundary-static-v1|934b284ce3ac64b042732e1ef96ade160bd76a70919caf07f78105a0c7fac043|初稿Role import未訂正/raw4・1、保持|
|PG10259-scenario-media-boundary-static-v2|69a0439b36db85554ccf966c4d8904583aeacc8b60f46e02156490828b4311e4|Role既宣言に訂正後/raw4・1、保持|
|PG10260-scenario-media-six-compile-v1|a8a30b3ffb1c61b1330b2edb882eca3005226a826c981fe691e26a7896412b27|source34748/Test enum誤記二件でcompile1・三jar/PT0、後続未実行|
|PG10261-scenario-media-boundary-static-v3|1caa334d9d8cc396c5639395c4980ba3f78a972bd515a7eee4413ba781e84741|当正規enum/currentSHA、PMD4/CS0/処理0/raw1|
|PG10263-scenario-media-six-compile-v2|52622b296c357e6dabb76957c15978a1430b4d928887b0785f41d18ece977558|六jar/正常compile0/PT0/NullAway-Werror、own60626真正0|
|PG10262-scenario-media-boundary-preflight-v1|b754c6de3bf345c52acbc1788ee66bc05ae5deb6956a721b610968097f4faf72|閉22/2、四Test/four Main、元初稿hash一致の二txtも保存|
|PG10264-scenario-media-boundary-host-v1|7644b073f2e2678ff7ea8971a944473e0476a2c9fee6dc397578e782ef66a031|当22全成功/own19070真正0、一JUnitのみ|
|PG10266-scenario-media-boundary-post-v1|d0f678a7623728bf03bdcff2628ad69d6ad12797bc2a00df35b9bf38a98750ed|独立post0/own32950真正0、XML/CRC/一session/probe後条件|

四静的指摘は両fileのboundary内CloseResource各一件及びNoSql.portのUseProperClassLoader各一件。実Connection/resourceを開かない自己JDK Proxy、任意呼出し/closeを禁止しJDBC0をassertすること、JavaEEでないstandalone public Connection interfaceのclassloaderという個別file/line理由を10266へ保存。抑制0/適用違反0、元raw1をstatic0へ書換えない。

独立post：全XML22と一意ID/固定method集合/全成功、一exec/session・現CRC、NoSql handler二のcovered instruction0、try内専用DB helper命令0、保留Main二/他module等probe0。rows/queryの境界probeをSQL実行と混同しない。全Main1843同byte、旧Test1937同byte、新二source四Test physicalだけ追加。

|完整source-unit|LINE hit/total|METHOD hit/total|CLASS hit/total|BRANCH hit/total|
|---|---:|---:|---:|---:|
|ScenarioRepository|46/217|12/34|1/1|2/70|
|MediaRepository|32/132|13/31|1/1|0/40|
|Scenario/Media RowMapper二interface|各0/0|各0/0|各0/0|各0/0|

外class四100は未達、Codeなしinterfaceは測定PASSでない。旧実DB/別sourceのcoverage又は成功を合算せず、正常SQL/表示順/owner/transaction/実配信/並行/再送/Graph9等は別未完/HOLD。

BUG1809/YKT1560を修正前起票し、Test二参照だけGameCode.NUKITASHI_1へ是正（wireNUKITASHI1/Main不変更）、元34748 snapshot/compile1/log hashを保持。初稿security.Role誤記はcompile前にdomain.Roleへ訂正、元10258の二sourceを10262/initial-draftでhash一致復元し保全。失敗/未実行をPASSへ加算0。trace新二path/22IDは次群で原P00801/P00901へ登録するまでpending。正式1964-53/既17-190/工数null/全HOLD/QA051final不変。
