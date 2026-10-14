# 再利用Backup完了・JDBC障害後条件の独立PT仕様

PT-MDB-2758-001、NK-BAT-001、MorningDatabaseSession.Session.completeReusedBackup / MorningDatabaseSessionTest.mdb2758001ReusedBackupSqlCompletionFailuresPreserveOriginalAndSkippedRows。主担当WBS-P017-01、RD BAK/OPS/AVL、UI251/253、SS341§3～7/343/SSC134/451。2748実method1012/13 SQLException catchの未実行2lineを着手前照合、予算.25/.75/2ppはevent0730で固定。

隔離実PostgreSQL/DDLs、二入力ROLLBACK/AUTOCOMMIT。固定run27580001の二UUID/2050-03-09T15Z＋日差、逆順原本SUCCESS DB/CONFIG二行、26/67bytes・target/success1/2・終了+3秒。beginResumeBackupが当SKIPPED二行を実commitし、独立SQLで全四行を確認した後だけproxyの一回用armedを立てる。completeReusedBackup中のConnection.rollback又はsetAutoCommit(true)へ一回SQLExceptionを注入、IOExceptionの公開固定文言、注入回数1、後続成功経路未到達、接続閉鎖、独立SQL全四行不変、client/advisory解放を確認。private field/expected生成/DB本番/VM操作なし。

Main Source042/PG2654・full2744/保持当native2746v2不変更。Test only。実command構築済PYTHONPATHで `python3 -B tools/quality/pg2758_backup_completion_selected.py`、初期未実行。全体新Test統合/global100/正式への加点0、実結果・source・XML/coverage/hashは真正終端と独立資格後に追補。
