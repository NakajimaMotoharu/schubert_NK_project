# NK-BAT-001 Inspectorロック引渡し実行結果

005/PT-BAT-030～037、PG-D-150。正式PT-WEB-20260909-47/source3cac4ede9bffd328adada4078f7207494c0b7e8f、2026-09-09 21:30:23～21:37:30 JST、全1111件・6 Java moduleのline/method/class/branch100%・Production5 module静的解析PASS。12collector/35scopeの同run/source/branch/hash検証と17負canary成功。環境・実行command・終了code・coverage・各Test結果/独立oracle・source hashはevidence/manifest.jsonを正とする。

親→子transaction→親の実ロック、再入/別namespace/競合、全JDBC位置/null資源/結果破損/close・割込・親状態の新8件を確定。BUG146/YKT114は先行702b64ac→修正3cac4ede→正式47再試験で完了。全対象根拠はevidence/logs/BUG-146-YKT-114.md。探索1の静的指摘1件は不合格のまま保持し、正式46以前へ新8件を遡及算入しない。親OS lockの全体保持/実子起動/backup/固定run原本/設定publishは本部品では完了にしない。
