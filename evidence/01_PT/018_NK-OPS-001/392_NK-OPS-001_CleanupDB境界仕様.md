# PG484 CleanupDB境界・借用資源仕様

## PG486 CTERM010 公開value record境界（2026-10-06）

PG485 fresh実XMLで内record合計7branch/2line残を確認。Production変更/SQL変更/除外はせず、Entry/Snapshot/RejectedEntry/RejectedSnapshotの本来の公開invariantを独立literal fixtureで検証する。正常七slotはCLEAN_NOTIFICATION/QUESTION/SESSION/INBOX_OUTBOX/LOG/BATCH_RUN/TRANSFER、id1～7・run fixture・started2026-09-13T02:00:00Z・ended02:00:01Z・SUCCESS(1,1,0,0,NONE)。expectedはこの明示list/time/拒否契約でありrepository.readの戻り値から生成しない。

Test ID=PT-OPS-CTERM010：上限9999-12-31T23:59:59.999999Zは受理、その+1000ns及び正常ended+1nsを拒否。第二slotのforeign runとduplicate id、RejectedEntryのended<started/non-skipped+SKIPPED/skipped+RUNNING(empty)、null collection要素を拒否。正常全七slotの両Snapshot値をliteral入力と一致確認する。public record factoryは入力にのみ使用、独立拒否oracleをProduction検査methodで生成しない。実PG18 fixtureの通常scopeを既存BeforeEachで維持する。

command=`bash tools/quality/vm/050_s1/pg486_cleanup_terminal_selected_v1.sh`、source=3e6f1a304基点＋CTERM010 test-only dirty、private証跡WorkPG379/pg486-cleanup-terminal-selected-v1.*。当追記時点は試験実行中/結果未確定。Coverageはouter＋全4内record＋Projectionの四counter全miss0（分岐のないrecordはBRANCH無し）を実XMLで確認する。PG485全体成功を当新test/sourceの成功へ流用しない。

NK-OPS-001/NK-BAT-001、CleanupTerminalRepository.read/references/readRejected/entry/check、RD DAT009/OPS009/MON004、UI251、SS331332341343/SSC063119120126、PG-D390。production入口のみ、実PG18 fixtureと公開JDBC probe、private reflection0。

|Test ID|入力/操作・独立期待値|
|---|---|
|PT-OPS-CTERM006|正常七行に対し十四列null/foreign/未知enum/負counter/誤summary/将来時刻、nullstatement/nullrows/八行目/duplicateを注入。固定BatchRepositoryExceptionで拒否、全ownedstatement/rows解放、借用Connection/transaction変更0、独立SQL全行保全|
|PT-OPS-CTERM007|readRejectedのRUNNING/terminal別条件と接続autoCommit/readOnly/isolation/元run整合を一つずつ破壊。欠落slotを成功へ補完0、RUNNINGは全zero/ended空/code-summary空を要求。guard故障は既固定SQL、未知/fatalは同一性で上位へ返す|
|PT-OPS-CTERM008|read/readRejected/references各owned row/statement scopeでSQL primary＋未知close・未知primary＋各close・body正常close故障・同Throwable再送。独立SSC063分類表：SQL+SQL固定、未知primary同一性＋redacted secondary、SQL+未知cleanupはcleanup同一性、body正常でもclose正常まで返さない。借用Connectionのcommit/rollback/config/close0|
|PT-OPS-CTERM009|六BACKUP_UNAVAILABLE/SKIPPED/zero・同時刻＋Transfer SUCCESSの独立SQL正常形、正常profileへの混入/誤reason/時刻差/nonzero/Transfer混入を拒否。referencesの独立current SKIPとprior SUCCESSにnullscope/欠落/複数/別step/同id/非priorattempt/WARNING及びpublic current不整合を投入し、固定拒否と全FD/元全列不変を確認|

負値入力はspec literal/実JDBCインターフェースだけ、source/read/private診断を成功oracleに使わない。期待時刻は手書きUTC、期待fieldはDDLと十四列SQL、各projection拒否後原行をSQL後条件へ照合。並行/native・再送は既同owner/regressionへ分離、coverage除外0、未実行・中断・別source・global100未達の合格加算0。command/source/XML/static/counter/BUG・hashは393へ。秘密/rawsession/DB dump/私有logはGit外。

## SSC-461 Cleanup終端SQL分類の独立単体

PT-BAT-SSC461-CT001～004、PG43832、BUG-3233／YKT-2680。公開read／readRejectedに固定run・観測時刻・5秒の合成guardを供給し、借用Connection代理の最初のgetAutoCommitでSQLExceptionを発生させる。取引やprepared resourcesは未取得。固定BatchRepositoryException、空cause・suppressed、SQL nextの同一Error、普通causeの優先、代理呼出は各一回で他操作0を独立確認する。readBackupUnavailableの共有read本文、既SQL・close・提出済みintegration試験は変更しない。現sourceの局所静的・公開ABIとbefore/afterの選択結果を保持。実DBとは別。
