# NK-OPS-001 親INVALID世代所有値受渡しPT仕様（PG378）

対象`MorningControlScope.executeOwnedEpoch`、旧`executeOwned`互換。RD OPS-009/BAK-001、UI251/253、SS341§5/343§6.15、SSC089/094/105/108、471 R1/D04/05。Production code変更前に作成。同じM→原本/DB→固定8 stop→A/fresh8→INVALID読戻し成功後、返った`Epoch`実体を同じ所有callbackへ借用させる。これはpermit発行権限ではなく、callback退出後に持続的能力として使わせない。既存二引数callbackと外部fail-closed mainは維持する。

| Test ID | fixture/入力・操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MCTRL015 | 固定run/activation/boot/epoch、M/A/原本/DBの合成保持、固定`INVALID` Epochを返すinvalidation、同値callback | M→原本→stop8→A→fresh8→INVALID→work→A/原本/M close順。work中は三所有値保持、state/DB/Epochが各fixtureと同一object。EpochはINVALID/同activation/digestなし。 |
| PT-OPS-MCTRL016 | invalidationがIOException又はnull | work0回、A/原本/Mは各1回close、例外の成功化なし。null値を後続へ流さない。 |
| PT-OPS-MCTRL017 | invalidationが別activationのINVALID又は同activationのISSUEDを返す | 借用work0回、非成功。既存原本と一致しない/発行済み世代を次段へ渡さない。 |
| PT-OPS-MCTRL018 | gate/lock/original/stop/A/terminal/invalidation/work null、work null返値 | 必須引数nullは資源取得前に拒否。work nullは帰還成功値にせず全所有scope close。旧二引数workの既存MCTRL012～014も回帰。 |

期待値の固定UUID/イベント列/状態は本仕様とSSの順序から作成し、Production `invalidate`の返値をexpected生成に使わない。JUnit/Maven/JDK/branch/commit/exit、coverage四指標/静的解析、入力・実際・関連障害、sanitized evidence/hashを267/manifestへ記録する。Production6 security/owner全回帰を同sourceで実施する。真正root M/A/DB/原本、Unit/issuer、root canonical digest、外部Web/APIとCHRは別未受入。
