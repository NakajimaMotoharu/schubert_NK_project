# PG484 CleanupDB境界・借用資源仕様

NK-OPS-001/NK-BAT-001、CleanupTerminalRepository.read/references/readRejected/entry/check、RD DAT009/OPS009/MON004、UI251、SS331332341343/SSC063119120126、PG-D390。production入口のみ、実PG18 fixtureと公開JDBC probe、private reflection0。

|Test ID|入力/操作・独立期待値|
|---|---|
|PT-OPS-CTERM006|正常七行に対し十四列null/foreign/未知enum/負counter/誤summary/将来時刻、nullstatement/nullrows/八行目/duplicateを注入。固定BatchRepositoryExceptionで拒否、全ownedstatement/rows解放、借用Connection/transaction変更0、独立SQL全行保全|
|PT-OPS-CTERM007|readRejectedのRUNNING/terminal別条件と接続autoCommit/readOnly/isolation/元run整合を一つずつ破壊。欠落slotを成功へ補完0、RUNNINGは全zero/ended空/code-summary空を要求。guard故障は既固定SQL、未知/fatalは同一性で上位へ返す|
|PT-OPS-CTERM008|read/readRejected/references各owned row/statement scopeでSQL primary＋未知close・未知primary＋各close・body正常close故障・同Throwable再送。独立SSC063分類表：SQL+SQL固定、未知primary同一性＋redacted secondary、SQL+未知cleanupはcleanup同一性、body正常でもclose正常まで返さない。借用Connectionのcommit/rollback/config/close0|
|PT-OPS-CTERM009|六BACKUP_UNAVAILABLE/SKIPPED/zero・同時刻＋Transfer SUCCESSの独立SQL正常形、正常profileへの混入/誤reason/時刻差/nonzero/Transfer混入を拒否。referencesの独立current SKIPとprior SUCCESSにnullscope/欠落/複数/別step/同id/非priorattempt/WARNING及びpublic current不整合を投入し、固定拒否と全FD/元全列不変を確認|

負値入力はspec literal/実JDBCインターフェースだけ、source/read/private診断を成功oracleに使わない。期待時刻は手書きUTC、期待fieldはDDLと十四列SQL、各projection拒否後原行をSQL後条件へ照合。並行/native・再送は既同owner/regressionへ分離、coverage除外0、未実行・中断・別source・global100未達の合格加算0。command/source/XML/static/counter/BUG・hashは393へ。秘密/rawsession/DB dump/私有logはGit外。
