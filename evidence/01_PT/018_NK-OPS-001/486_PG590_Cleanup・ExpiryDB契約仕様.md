# PG590 failedBackup→Cleanup→Expiryの実host DB契約

NK-BAT-001/MorningDatabaseSession.Session.beginExpiry/handoffExpiry/observeExpiry/observeCleanupBackupUnavailable/cleanupReferences、RD OPS009/DAT009/UI251/SS331341343/SSC124199200。主担当485はP017-01の共有Sessionであるため、初回event0090のP017-07.02分類を訂正し既P017-01.03群0.66/1.66/3.66ppへ継承する。新群予算を二重加算しない。SQL fixtureは当Session契約の独立oracleで、P017-07側の業務consumer費を計上しない。native Unit/Root権限の受入ではない。

PT-OPS-MDB590001: JST09-20～25独立六日付/run、Backup FAILED二行の正規完了・sole handoff後、子SQL独立fixture六SKIPPED/BACKUP_UNAVAILABLE・Transfer SUCCESS/0件を17列SSliteralで作成。七step順序/id/status/count/reason/time及び原本参照七emptyを独立期待値で照合。Cleanup前Expiry禁止/未handoff観測禁止/null/誤targetを確認。Expiry beginはRUNNING/非SKIP・sole child後に独立SQLでSUCCESS/0、WARNING/10、FAILED/30のaudit cutoff−7日/before1/after0又は1/target1/byte25を作成し、三正常一致と三receipt不一致拒否を確認。readback前後全column不変、終了Connection閉鎖・同DBadvisory解放。fixtureのreceiptはbus/kernel literal sequencingでnative authorityでない。expectedをProduction methodで生成0。

コマンド `bash tools/quality/vm/050_s1/pg590_cleanup_expiry_db_v1.sh <固定HEAD>`。MACCESS9/MDB既25＋新1=35PT予定、未実施を合格にしない。新onlyprivatepg590、前selectedexecSHA/sixmain1600classbyteをPG585-current-m2へ事前照合、failed/旧nativeをappend0。環境JDK25.0.4/Maven3.9.12/PG18/Flyway28/NullAwayWerror/Spotless/Spotbugs/JaCoCo0.8.15。actual exit/source/時刻/XML/counter/hash・障害があれば915916へ先行記録し実後追記。全global四100/正式source回帰/CHR/ITST合格は別条件。
