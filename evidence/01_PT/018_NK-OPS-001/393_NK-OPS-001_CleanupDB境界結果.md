# PG484 CleanupDB境界・複合故障限定結果

392/CTERM006～009、SS332341/SSC063199、PG-D390、BUG784785/YKT560561。host Linux/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/PostgreSQL18 fixture、dev-foundation、HEAD cced357e16fe01b00f58df8d6a1cc91cfacb2aab＋保存src差分。実VM currentは別bab/PG479のまま、新sourceのnative未受入。設計only cced357e1→isolated156b08374→PR31通常merge→origin/main07fae416b57153c947363f9d8e81cedbe02c70e0、SS332/341/914三文書だけ、未受入code/tools/evidence混入0。

|試行|実結果/区別|
|---|---|
|v1/session1751|wrapper1/Maven1、CTERM008でSQL next＋fatal ResultSet closeが固定BatchRepositoryExceptionへ隠れる反例。10PT/F1/E0/S0、BUG784修正前起票、旧XML/log保持|
|v2/session34428|CTERM204合成含む全選択PT成功、static六OBL指摘でwrapper1。BUG785起票、callback移譲による所有分断・取得後callback評価間隙をdirect lexical finallyへ是正。実OOM漏洩を観測実績にしない|
|v3/session54812|98PT10suite/FES0/static5zero/actual0。driver未知同一性・六scopeのdirect finally/borrowed Connection保全を確認。global100ではない|
|v4/session71305|失敗Backup profile/元成功参照/nullscope等CTERM009追加、fresh99PT10suite/FES0/static5zero/actual0。対象outer class四counter missed0、Projection全line/method/class missed0。inner record残branchは全回帰で確認、除外なし|

v4command `bash tools/quality/vm/050_s1/pg484_cleanup_terminal_selected_v4.sh`、19:27:58.360542593～19:30:23.310044330 JST。log SHA256 `84a07ffbe6596464540ee26652491e14c7b1f13f83a0f17ce9b37a7662c5c5a7`、WorkPG379 stem `pg484-cleanup-terminal-selected-v4`。初回red XML `pg484-cleanup-terminal-red-v1.private.xml`、static拒否XML `pg484-static-refused-v2.private.xml` と各log/diff/開始終了はGit外私有保持。

CTERM006：十四列null/foreign/未知/負counter/summary/未来、null statement/rows/8行目/duplicateを拒否、全owned FD解放・borrowed transaction不変更。CTERM007：autoCommit/readOnly/isolation/run参照不整合・RUNNING全zero/ended/code/summary各拒否。CTERM008：read/readRejected/referencesで68×3=204の独立SSC063分類表を適用、SQL+未知closeは未知同一性、未知primaryのsecondaryは固定redactedだけ、同Throwable再送安全、全SQL十四列原行不変。CTERM009：六BACKUP_UNAVAILABLE/zero/同時刻＋Transfer SUCCESSの正常SQL形、正常profileへの混入・時刻/理由/count/Transfer不正を拒否、priorのnull/欠落/複数/step/id/attempt/statusとcurrent public不整合を拒否。

providerの全十四getterはpure decoderのcatch外へ移動し、enum/record値不正だけSQLDataExceptionへ分類。Immutable BatchStepResultがBACKUP_UNAVAILABLE→SKIPPED/全zero及びSUCCESS→NONEをconstructorで保証するため、後段の同じguardを重複させず、実不正値拒否をindependent fixtureで維持する。scope取得の直後にdirect try/finally、未知非正常化・一度close・close正常まで返却0、借用Connectionのcommit/rollback/config/close0。JDBC SQL/bind/date/七step・外部業務・起動権限は変更0、annotation suppression/coverage除外追加0。

YKT560561対象六scopeすべて修正・再試験。既RunReference/InspectionSummary/Cleanup/BackupStep/BatchRun五Repositoryはdirect finallyを使う非該当根拠を確認し、既136/68等の複合試験をこの選択runへ含め、59関連PTもFES0。旧immutable工具/歴史UNKNOWNは別原因SSC174、正常化0。修正commitは本結果保存履歴、当host範囲完了日2026-10-06、実VM/global/formalは未受入。次はsource固定PG485 fresh全6→同source署名/保全配備/新実経路/native。正式run24/1964PT53scope/48.3%、QA051比較保留、IT/ST未完了を維持。
