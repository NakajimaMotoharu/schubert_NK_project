# Web失効codecの鍵単一確保 実行結果

NK-WEB-002、WBS-P018-10.03、BUG-3484／YKT-2779、PT-REV-KEYOWNER-001。旧PG41358で全事前検査後の二cloneと保護範囲なしを確認。新PG41360では一回確保・二つの固定32 byte領域のcopyを確認した。

同じ新sourceのRoot NullAway／Werror付き局所compileとRERUN003／OWN／FATALの13件が全成功。PG41362で元単一exec・CRCを照合。構築の全指標到達、classの行109・method 10・class 1・分岐40すべて100%。既closeの未到達命令6を保全。Checkstyle・SpotBugs・PMDの対象production指摘0。実OOM・実失効・DB／JMS・451／正式は区別する。

[元構築](evidence/PG41358-p01810-revoke-ownership-baseline-v1/manifest.json) · [通常13](evidence/PG41360-p01810-revoke-ownership-qualified-v1/manifest.json) · [元CRCと静的](evidence/PG41362-p01810-revoke-ownership-independent-v1/manifest.json)
