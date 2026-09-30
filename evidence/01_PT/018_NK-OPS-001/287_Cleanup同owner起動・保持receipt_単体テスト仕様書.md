# 287 Cleanup同owner起動・保持receipt（実装前）

NK-OPS/BAT、MorningBackupUnitCycle/BackupUnitStartClient/BackupStartIntentFiles/BackupUnitReceiptGate/BackupUnitTermination/MorningDatabaseSession、RD OPS009/BAK001、UI251、SS341§7・343、SSC117/BUG354。

PT-OPS-CCYCLE001..006：閉鎖BACKUP/CLEANUP targetのliteral Unit/namespace/cgroup、跨target receipt/baseline/marker拒否。Cleanup開始前inactive/dead、実fresh0/10＋active/exited＋全nested process空、typed非forge receipt（Invocation/開始終了monotonic/実exit）を保持。client0だけ/旧Invocation/残process/signal/timeoutは不成立。

独立port順序：baseline→親advisory handoff解除→start/reap/fresh receipt/全終端→親再取得→DB readback→request退役→intent退役。Cleanup stop呼出0回、Backupは従来1回。UNKNOWN中はhandoff callbackが通常returnしない、M/A/原本/同親budget/marker保全。再取得/DB/retire不明も保全。begin commitだけのhandoffは0callbackで拒否、実FAILED両結果/readback後の一度handoffは実PostgreSQL子/親lockで検証。

Native：真正Cleanupを一度起動し、そのまま真正Artemisを起動してCleanup Invocation/開始/DB件数が不変・第二PID/attempt0を採取。現時点NOT-RUN、helper/mock成功をnativeや正式100%へ算入しない。
