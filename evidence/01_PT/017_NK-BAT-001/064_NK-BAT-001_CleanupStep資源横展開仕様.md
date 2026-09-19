# NK-BAT-001 CleanupStepRepository資源横展開仕様

PG181/SSC063/BUG195・206/YKT154・162、2026-09-20。DAT009/OPS009/UI251/SS331§3.14/332/341。対象CleanupStepRepository.execute/present/requireとowned Statement/ResultSet。Production変更前、未実装・未認定。

既存BAT168 interruptRuntimeAndResourceOwnershipへ独立JdbcResourceCasesの68複合を追加する。2scope×（SQL/IAE/IllegalState/NPE/Errorの25別組＋同一未知4＋body成功closeだけ5）。cleanup専用SQLを識別し、前後RunReference readに誤注入しない。最初にcleanup getter/provider IAE単独と同一unknown body/closeを再現する。公開JDBCのみをproxyで監視し、実closeを先に実行してからclose故障を注入する。

期待値は060の独立例外順位表を再利用し、Productionから計算しない。unknown primary同一物＋固定BatchRepositoryException secondary1件、known SQL primary＋unknown closeはclose同一物、SQL同士は固定message/causeなし/suppressed0。取得済資源各1回/未取得0/live0、借用Connectionのcommit/rollback/close/config変更0。fixtureのrun/step/質問2行を用い、caller rollback後に独立SQLで質問とstep countsが元に戻ることを検証する。

countsの3getter、累積2getter、complete/reasonの取得はprovider呼出でありIAE検査の外へ置く。CleanupCounts、Reason.valueOf、CleanupStepChunkの値構築だけをSQLDataExceptionへ固定する。元NULL Statement/ResultSetはpresentによる固定SQL不正であり、CleanupRepositoryのnonnull NPE契約と混同しない。nullable累積の両列同時NULL、7kindの対応、limit1～1000、UTC、前後run同一性、並行/保持/rollback、不正投影の既存8PTを全再実行する。

実行は既定JDK25.0.4/Maven3.9.12/offline M2。選択ResourceScopeTest,CleanupStepRepositoryTest,StepCleanupServiceTestをbatch -amでtest、JaCoCo report、SpotBugs check。実行command・時刻・OS・source・exit・各counter・ログhashは065実行結果と正式manifestへ記録する。全変更classのline/method/class/branch100%、静的解析未解決0、新除外/抑止なし、failed/error/skipped0。正式clean verifyと46負canary/38scope後に認定する。

新JUnit/部分成果加算0。BUG195/YKT154/SSC063とBUG206/YKT162の残BatchRun/BackupStep等は別段で継続。実parent/全cleanup/PGPT/IT/STの完了としない。
