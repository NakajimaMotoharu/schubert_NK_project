# SSC-461 BackupCommitServiceの借用JDBC例外伝播

NK-BAT-001、WBS-F02-a／P004-05／P017-06、BAK／BKO／OPS009、UI251、SS311／332／341 §6.6／343、BUG-3233／YKT-2680。対象はBackupCommitService.completeの三call。JDBC graphだけBootstrapへ移す。既[BackupPair原10](../017_NK-BAT-001/699_Backup監査ペア_単体テスト仕様書.md)のSQL・合成manifest・rowとoracleを保持し、外側の借用transactionに6件を追加する。実Backupファイル、原本、DB、所有者と既BeforeAll suiteは対象外。

| Test ID | 入力または操作 | 独立期待 |
| --- | --- | --- |
| BKPCOMMIT461001 | RUNNING→SUCCESS、既SUCCESSの再通知 | begin→commit→復元、2更新と0更新、固定元時刻、借用close0 |
| BKPCOMMIT461002 | null、autoCommit/readOnly/isolation不整合 | 開始・SQL・復元0、公開契約のnullまたは固定失敗 |
| BKPCOMMIT461003 | 入口／primary／rollbackのcause・suppressed・SQL next辺に固定Error | 元Error同一参照、順序、無変換 |
| BKPCOMMIT461004 | 参照前の既知SQL失敗 | rollback→復元、更新／commit0、固定・causeなし |
| BKPCOMMIT461005 | compound既知組、未知cleanup、同じ未知primaryの再throw | 既知だけ固定、元未知同一参照、固定二次だけ、借用close0 |
| BKPCOMMIT461006 | 確定commit後復元エラーと自身スレッドの割込み | 確定commitをrollbackと示さず、所有スレッドが試験後に割込み解除 |

当sourceのRoot符号・NullAway・静的・通常全16・独立XML/CRC、生coverageと公開ABIを確認する。未到達や全451の不足は未受入のまま保存する。試行ごとのsource／環境／command／hashは結果に記録する。
