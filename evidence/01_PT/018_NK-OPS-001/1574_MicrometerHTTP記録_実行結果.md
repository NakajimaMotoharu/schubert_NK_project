# 1574 Micrometer HTTP記録 実行結果

2026-10-23、1573/PG-D527/group1830。固定source `ef6f9f22aaa8b16ffcfe39952bfc9a2196b0308a`。Production Mainはb0c43d737のrecorderから変更せず、試験fixture型/SDK aux分類を是正した。当候補は実Micrometer core1.17.1/commons-observation1.17.1/HdrHistogram2.2.2を正規依存として使用（SDK四Jarは前後hash一致、除外0）。既HTTP terminal/Root assembly・Prometheus公開・quantile/性能は未受入。

|原job|真正結果|manifest SHA-256|
|---|---|---|
|PG7106-micrometer-http-host-v1|sourceb0、format/Main compile0→Test compile1（SDK close型誤認）、PT0/未実行|38bb83d1a54e733de7d6c941151b3a3865587b674c34b5c9a7a036d94d5e94bd|
|PG7110-micrometer-http-host-v2|source693、真正15件/F4/E0/S0、SDK auxを未分類のoracle失敗。全体成功ではない|c835148ea08cad258607172400292d63bbbe6fbb5a891f44f250babf10a2bd26|
|PG7114-micrometer-sdk-oracle-v1|固定vendor bytecodeのSLO Gauge呼出/.histogram/le/秒変換を確認、35×9=315の独立補完、Production実行0|a7e11af5c05454cb5464d0c9f6b194b84c63dcdf6a4d527056d5daa33ef28292|
|PG7116-micrometer-http-host-v3|sourceef6、真正通常verify/六format0、15PT/2suite/F/E/S/rerun/flaky0|4f0124b47866ca41c13f05a626355c74e5726de6cf26ad0718e3ebfcb3e8a311|
|PG7118-micrometer-http-post-v3|原15XML/5Java source・SDK四Jar同byte、実7class＋metadata1/単一sessionCRC0、L154/M33/C7/B27全miss0|0aa4cee63e3f64d8b0439edd8b6da776f8a3bd9466e4dbc714f3c28ae7f7518b|
|PG7120-micrometer-http-six-compile-v1|当source六Main/Test compile/package0、PT実行0/UNRUN_NOT_PASS_COMPILE_ONLY、SDK四Jar pin前後一致|9846dbb42e894dd3feb2a2a945ee58f7284eaa4255a40abd27633d16dcbcc3a3|

公開pathは各 `evidence/provisional/<job名>/manifest.json`。原snapshot/source.tar/begin/process/終了/log/XML/exec/Jarは `work/pgpt-runs/PG379/pg7116-micrometer-http-host-v3` と `pg7120-micrometer-http-six-compile-v1`、旧失敗は元7106/7110へ保全。実command/時刻/OS/JDK25.0.4/Maven3.9.12/entrypoint-library-helper-loaded source hashとSDK pinsは原manifest。vendor bytecode本文は7114 workspaceだけに保全しGitへ格納0。

HTTPREC001～009/HTTPMETRIC001～006を1570/1573の独立literal/35行goldenとSDK primary根拠で実行。primary Counter1750/Timer35、Simple providerの内部Gauge315を分離して全2100のname/type/tag/le九値/route各9を確認。全1750 record行列・Timer各50秒、未知1万の固定series/件数、単一Long.MAX_VALUE/0境界、null/不正拒否、SDK Runtime/Error同一object/再試行0/部分計測を成功へ補正0、borrowed close0・owner close1、64並行actual count/時間を確認。実exporterの新catalog名を承認した結果ではない。

親Enforcer/Production-Test lint/Werror/NullAway/SpotBugs/Checkstyle0。PMD raw1/exit4は既HttpMetricContract INDEX/indexのprivate immutable組立に限定、1571と当同byteの個別CONTEXT_NOT_APPLICABLEを再照合、未分類0・抑制0。新Recorder指摘0。BUG1650/YKT1403のfixture bridge、BUG1651/YKT1404のSDK補助表現補完は新15件と静的で当範囲を確認、最終実Jar/横展開閉鎖は続報へ。

Source依存差分はWebに既管理core1.17.1をcompileへ正規追加した一件だけ、既business/ログ/codec/DB設定は変更0。旧Batch73/source71・原e7/4222・common3c/44を当sourceの測定へ転用せず、旧2失敗と新成功を合算0。全体451/全scope同source-run/native/CHR/正式1964-53・歴史17/source別新7・原190新受入0・工数null/QA051final/PTALT0/HOLDは維持する。
