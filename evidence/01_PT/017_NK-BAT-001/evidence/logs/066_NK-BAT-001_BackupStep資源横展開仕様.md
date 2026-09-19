# NK-BAT-001 BackupStepRepository資源横展開仕様

PG182/SSC063/BUG195/YKT154・162、2026-09-20。BAK/BKO/OPS009/UI251/SS331§8.3/332/341§6.6/343。対象BackupStepRepository.inspectのpair Statement/ResultSet。未実装・未認定。

既存BAT216 nullAndUnknownFailuresへ2scope×34＝68複合を追加する。060の独立JdbcResourceCases表（SQL/IAE/IllegalState/NPE/Error別25、同一未知4、closeだけ5）をpair.* keyへ対応させる。最初は同一IllegalState row.next/row.closeの反例。既存Probeの実close後注入、prefix識別、first occurrenceでexact1を確認。前後guardやcompleteの別updateを対象試験へ誤計上しない。

unknown primary同一性と固定secondary、SQL primary＋unknown close優先、SQL-only固定診断、未取得close0/取得済各1/live0、Connection commit/rollback/close/config変更0を期待する。公開固定manifestと2 RUNNING行を使い、caller rollback後に独立state SQLでRUNNING/0 counts不変。NULL projection/resourceは元の固定SQL失敗、14列/fullhandle/2同値状態/時刻/排他/再送は元期待を維持する。provider IAEを広く捕捉していないためYKT162直接原因は非該当、5型確認で根拠を残す。BatchRun.finish呼出先は別段で未完了。

既定Ubuntu26.04.1/JDK25.0.4/Maven3.9.12/PG18.6。選択ResourceScopeTest,BackupStepRepositoryTest,BackupCommitServiceTestをbatch -amでtest/JaCoCo report/SpotBugs check。既存8＋8PT、変更class全line/method/class/branch100%、NullAway/Enforcer/Spotless/SpotBugs成功、新抑止/除外なし。実行command・source・時刻・exit・入力/期待/実際・hash・BUG番号は067と正式manifestへ記録する。全reactor/38scope/46負canary後に認定、新JUnit/部品加算0。親backup/生成/7世代/PGPT/IT/STの完了ではない。
