# Cleanup通常成功参照のJDBC責務移管

NK-BAT-001／DAT-009／OPS-009、UI251、SS331・332・341・343、SSC-461／200、BUG-3233、WBS-F02/SYS-005。対象は \`CleanupTerminalRepository.references(Snapshot, SuccessRunLookup)\` のうち、通常の成功履歴を取得するSQL例外の処理。

| Test ID | fixtureと操作 | 独立期待値 |
| --- | --- | --- |
| PT-F02-CTERM-REF-001 | 正常な7行の合成現在Snapshotの一つをALREADY_SUCCESSFULとし、参照SQLのprepareでnext例外のcauseに合成Errorを入れる | 元Errorの同一性。親参照の行・文を各一回解放。成功参照SQLのprepareは一度、借用Connectionにcommit・rollback・closeなし |
| PT-F02-CTERM-REF-002 | 同じ参照SQLに通常の合成SQLException | 固定診断、cause・suppressedなし。同じSQL、解放順、呼出回数と条件 |

承認済みSQLをオラクルに使い、期待値を製品から生成しない。同じ試験を移管前後の固定sourceで各一回。変更は成功参照の例外所有一箇所。実DB、失敗profile・拒否記録、実原本・保守処理を使用しない。全実行結果と局所coverageは対象manifestを参照。
