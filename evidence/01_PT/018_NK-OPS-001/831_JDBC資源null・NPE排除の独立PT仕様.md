# JDBC資源null・NPE排除の独立PT仕様

PT-MDB-2792-001、NK-BAT-001、Session.successfulBackup、MorningDatabaseSessionTest.mdb2792001SuccessfulBackupRejectsNullJdbcResourcesWithoutNpe。主担当WBS-P017-01.03、RD OPS009/DAT009、UI251/253、SS332/341/343/SSC063/451。2788の独立時刻pair試験は既網羅条件のoracle強化で追加coverage0、実gap927/928はjavapでTWRのnull close guardと確認。正本を変えず、null resourceを既SQL unavailableとして拒否する契約を現Mainで先に再現する。開始.5/1.5/4ppはevent0740。

隔離実PG/DDLs、STATEMENT/ROWS二入力。固定run27920001/2052-01-09T15Z＋日差、原二SUCCESS/target-success1/2・26/67bytes・終了+3秒を独立SQLでseed。対象successfulBackup queryだけ、実生成したstatement又はresultをfixtureが閉じた上でnullへ置換する。他Role/lock/schema queryは実値。期待はIOException/固定redacted文言/cause-suppressed0、null注入1、親connection/client/advisory解放、原二SUCCESS全列不変。NPEをcatchして正常化しない。初回は期待との差を実証し、実装済み違反ならBUG/YKTを修正前起票する。

Source042/PG2654/full2770/当native2774に対する修正前限定command `python3 -B tools/quality/pg2792_null_jdbc_resource_selected.py`（構築済PYTHONPATH）。初期未実行、未実行mode・非合格・oldSourceの結果を将来修正Mainへ流用しない。Production変更時は必要なfresh全体/静的/新Main byte・新Source native資格が別必要で、旧nativeを移植して合格にしない。Root/Backup/ADMIN/VM/stop/配備/reloadの無根拠再演0。
