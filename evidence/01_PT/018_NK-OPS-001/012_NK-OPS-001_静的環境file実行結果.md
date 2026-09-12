# NK-OPS-001 静的Inspector環境file実行結果

011/PT-OPS-CFG-001～006、PG-D-151。正式PT-WEB-20260912-01/source d2d3a0809de9e9805c1907eeef74721e6b95e4bf（2026-09-12 21:00:14～21:07:39 JST）で全1117件成功、6 moduleのline/method/class/branch100%、Production5 moduleの静的解析成功。新CFGは1class/3method/15line/16branch、全missed0。render雛形もliteral expectedと完全一致、017の1件/019の16件canary、12collector/35scope同時点性・hash検証も成功。BUG147/YKT115は先行a98ac3cb→修正d2d3a080→正式回帰で完了。

環境/command/日時/branch/source・Test ID/実際結果/独立oracle・coverage/hashはevidence/manifest.json。本部品の合格に保持inode/属性・bounded read・atomic publish・親結線は含めない。PG152の8件は仕様のみ。以前の正式47へCFG6件を遡及算入しない。
