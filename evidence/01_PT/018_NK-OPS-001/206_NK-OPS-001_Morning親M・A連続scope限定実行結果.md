# 206 NK-OPS-001 Morning親M・A連続scope・限定実行結果

2026-09-28 JST、`dev-foundation`、source commit `bae23ce20`、PG341。対象・Test ID・独立期待は205。RD OPS-009、UI251/253、SS341/343、SSC100～102/105、BUG315/YKT248。

`MorningControlScope`は同一親callbackでM取得→固定8 stop pass→A取得→A内で固定8 fresh whole-Unit/kernel観測→trusted workを順序化した。A取得前にstop失敗、M/A競合、A後fresh失敗、work例外/null、別thread未解決stopを手書きevent/latchで検証。追加MCTRL001～007の7件とMROOT6、MPASS9、MCLIENT12、MTERMS5、MPOL7を同一clean runで実行し、計46PT/6suite F/E/S0、Batch SpotBugs BugInstance0/Error0、Build成功。実systemd停止・実A取得をこのfixtureで証明したとは扱わない。

新class `MorningControlScope` JaCoCoはbranch missed0/covered4、line missed11/covered28、method missed4/covered4、class missed0/covered1。native factoryやconstructor等が未被覆であり、4指標100%未達。除外なし。原始logはGit外`/tmp/pg341-selected.log`のSHAのみ保全。sanitized JUnit6 XML＋coverage1＋static1＝8file全hash再照合、manifest SHA-256 `0fef441e731616eebc0de9088443da88488f0c1a01da592dbf325e25320a1de6`、path `evidence/provisional/PG341-morning-control/manifest.json`。manifestには実行時刻/OS/JDK/Maven/branch/commit/command/exit/input/期待/実際/coverage/BUG/SSC/source hashを含む。秘密・raw session/journalなし。

Production候補`MorningProcessMain`は依然read-only exit30で、このscopeは未結線。既存PG323の正規Morning検証用Unitも無変更。原本run/DB advisory、current INVALID、Artemis clean journal、同run backup/Cleanup、permit、全8実Unit、handleなしUNKNOWNのhard-timeout後保全は未達。R2/R3、正式`858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`/1964PT/53scope・中心48.3%は更新しない。
