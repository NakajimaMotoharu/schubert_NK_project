# Backup観測・handoff所有境界の独立PT仕様

NK-BAT-001/MorningDatabaseSession.Session.observeBackup、MorningDatabaseSessionTest.mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair。Test ID PT-MDB-2750-001、主担当WBS-P017-01、RD BAK/OPS/AVL、UI251/253、SS341§3～7・343/SSC134/451。実2748 gapの669 inHandoff trueを着手前照合。逆順IDは既mdb2490001で網羅済みのため重複製造しない。equal-ID防御条件は別invariant/driver-boundary分析を残し、到達不能・除外扱いしない。

fixtureは隔離実PostgreSQL＋既BatchDatabaseFixture/DDLs・公開credential、固定run27500001/開始2050-01-10T02:00Z/終了+3秒。beginBackup→COMMAND_FAILUREで実FAILED二行へcommit→正常observeでDB/設定二FAILED・prior空を確認。実advisory handoff callback中に同session/同pairをobserveするとIOExceptionでJDBC prepare前に拒否し、prepare回数が増えない。handoff自体は正常復帰するが、新Cleanup/Root/Backup/VM処理を発行した証拠ではない。

後条件：connection閉鎖、advisory/client解放、独立SQLのDB/CONFIG各行FAILED/target1-success0-failure1-byte0/固定終了日時が不変。before/expectedは独立literal、Productionからexpected生成なし。正常・境界・資源所有の一JUnit、既null/unknown/DB異常/並行契約試験は保持。

実command `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<構築済pyflakes runtime> python3 -B tools/quality/pg2750_db_backup_handoff_selected.py`。Source042/PG2654/保持PG2746-native-v2九stream/Full2744は不変更、変更はTestだけ。工具は全namespace/import/役割/JDBC/Flyway/固定Source/Jar/stream hashを実行前に確認し、未実行/skipを合格へ加点しない。初期状態未実行、Test対象commit・XML/coverage/hash/実静的・結果・関連BUGは実行後追補。VM再採取/Root/Backup/ADMIN/stop/配置/reload0。
