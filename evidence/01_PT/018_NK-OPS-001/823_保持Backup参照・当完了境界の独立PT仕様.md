# 保持Backup参照・当完了境界の独立PT仕様

PT-MDB-2754-001、NK-BAT-001、MorningDatabaseSession.Session.retainedBackupSuccessful / MorningDatabaseSessionTest.mdb2754001RetainedBackupRequiresCurrentCompletionAndPreservesOriginalRows。主担当WBS-P017-01、RD BAK/OPS/AVL、UI251/253、SS341§3～7/343/SSC134/451。2748実method756 backupFinished=falseを着手前照合、開始予算.25/.75/2ppはevent0728で固定。

隔離実PostgreSQL/DDLs、固定run27540001・2050-02-09T15Z/開始翌02Z、逆順ID原本DB27540011/CONFIG27540010、独立literal SQLのSUCCESS二行・target1/2-success1/2-bytes26/67・終了+3秒、fixture manifest content終了+2秒。開始直後及びbeginResumeBackup後（当SKIPPED未完了）に参照してもIOException/JDBC prepare追加0。completeReusedBackup後だけtrue。各段階とsession閉鎖後、独立SQLが原SUCCESS二行・当SKIPPED二行の全列/件数を確認し、connection/client/advisory解放を確認。

期待値は固定literal/独立SQL、Productionの返却値をexpected生成へ使わない。現Main Source042/PG2654・full2744/保持当native2746v2を使用、Testだけ変更、Root/Backup/ADMIN/VM/stop/配置/reload0。実commandは構築済PYTHONPATHで `python3 -B tools/quality/pg2754_retained_backup_selected.py`。初期未実行、未実行/skip/global100/正式へ加点0。結果・対象commit・XML/coverage/hash・関連BUGは実終端と独立資格後に追補。
