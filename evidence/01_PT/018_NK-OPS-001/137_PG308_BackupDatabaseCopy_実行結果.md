# PG308 Production資格情報コピー：限定結果

NK-OPS-001/BAK/BKO/OPS009/UI251/SS3416.1/3436.6/SSC090・091、136仕様DBCP001～008。BackupDatabaseCopyは借用済みprivate tmpfs0700/専用UID・GID、新UUID.part0600、所有raw byteを消費する。file/root/name/inode/security/readbackを検査後heap全zero→固定dump callback→全terminal-positive return後zero write/force/close/readback/原本name再照合/unlink/sync。失敗は生成済み材料を保全し、不確定unlink後に再作成しない。

23:34:36：copy8＋archive8 PT failure/error/skip0/exit0、新クラス全6counter missed0、静的0。独立literal public pgpass/OSmode/latch/call count、各I/O失敗位置・読書progress・metadata null/wrong type・boundary・namespace置換・unknown/compound/並行を確認。初回消去negative fixtureは0を書き戻す既存corruption modeで期待zeroと区別できず1failed、Production期待値を変更せず非zero corruptionへ修正。collector準備canaryの新8 inventory/count3段階不一致は不合格として保全、owner/count修正後105PASS。

Native023：実VM専用UID992/GID977・systemd backup-pgpass・DB専用roleで、このProduction copy＋固定pg_dump/restore-listを実行、copy消去/readback/unlink/sync後runtime空、Unit inactive/dead Result=success exit0。取得実dumpはVM privateのみ、Git/hostへコピーしない。先行native compile試行のclasspath不足と未main起動失敗はPASSへ加算せず全private log hash保全。既存source credential/password/native022成果の上書きなし。

23:44:27全Batch452 failure/error/skipped0・exit0・全module6counter missed0（line5086/method865/class136/branch2633、各100%）・静的0、batch-regression.jsonへ全source/suite/log/coverage/static hash保存。wholebackup/manifest/DB両step/7世代/親総budget・M/A、全起動gate・業務main・実NK CHR未受入。正式source858713c0b/run24/1964PT/48.3%は不変更。

実行command: Java25.0.4、offline `./mvnw -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch test -Dtest=BackupDatabaseCopyTest,BackupArchiveProcessTest jacoco:report spotbugs:check`。branch dev-foundation/source基点55039eb3e後dirty、source/test/artifact/native log SHA-256はprovisional PG307-308 manifest。秘密値/rawsession/token/DBdumpなし。
