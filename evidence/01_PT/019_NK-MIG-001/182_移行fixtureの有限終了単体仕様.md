# 移行fixtureの終了契約

SS354、NK-MIG-001、YKT-2997、WBS-G03.05。対象は試験専用 `MigrationFixtureWorkers.close`。手製のJDK代理は呼出名・順序・期限だけを記録し、業務・DB・COPYを呼ばない。既135件のfixture本文と製品Coreは維持する。

| Test ID | 代理の結果 | 独立した期待値 |
| --- | --- | --- |
| PT-BOOT-MIG-WORKER001 | 終了済み | cancel、7秒の待機を各1回。正常終了 |
| PT-BOOT-MIG-WORKER002 | 未終端 | cancelと一度だけ待機、固定の終了未成立診断 |
| PT-BOOT-MIG-WORKER003 | 固定のInterruptedException | 同じ原因、元割込み状態falseからtrue、固定診断、各1回 |

試験終了時に試験スレッドで立てた割込みを解除する。域外のJVMや実環境の終了判定に用いない。
