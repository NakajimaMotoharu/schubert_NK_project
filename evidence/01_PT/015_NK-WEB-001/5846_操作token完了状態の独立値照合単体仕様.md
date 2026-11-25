# 操作token完了状態の独立値照合

NK-WEB-001、QA049、UI226/236、SS314 §7.2.1、WBS-P015-03/2。公開のSessionOperationToken値だけを扱う。等しいpending値を再構築したとき、値比較とhashを使用する集合が同じ値として取得できることを確認する。同じ目的、固定UUIDと発行時刻でも完了状態の有無を区別する。

| Test ID | 独立した期待値 |
| --- | --- |
| PT-WEB-TOKVAL001 | pendingの固定集合に同値のpendingが存在し、completedは存在しない。completedの固定集合に同値のcompletedが存在する。8文字でも非許可purposeは拒否する。 |
| TOKV201 | 元の固定時刻、完了前時刻／null境界、各accessor、伏字診断を維持する。 |

JDK25の固定ctorを通常JUnitで確認する。候補tokenから期待hashを算出せず、固定の集合所属の真偽をoracleとする。実session・token発行・HMAC・DBに触れない。単一execの対象1class、生四指標、厳格compile、局所書式・静的・実XMLを5847とmanifestに記録。
