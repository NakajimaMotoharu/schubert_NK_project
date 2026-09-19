# NK-BAT-001 BatchRunRepository資源横展開仕様

PG183/SSC063/BUG195・206/YKT154・162、2026-09-20。OPS009/DAT009/UI251/SS331§8.3/332/341。対象begin/finish/history/abandon/insert/replayedと8 owned JDBC scope。未実装・未認定。

既存BAT151 interruptionAndRuntimeへ272複合を追加する。history/insert/replay各query68（row/statement各34）、abandon/finish各update34。独立060のSQL/IAE/IllegalState/NPE/Error25別組＋同一未知4＋closeだけ5。updateはstatement.executeQuery標本をexecuteUpdateへ対応しrow標本は対象外（row取得なし）。各SQL分類prefixで前後RunReferenceや別stageへの誤注入を防ぐ。注入数と各取得済close1/未取得0/live0、borrowed commit/rollback/close/config変更0を確認する。

最初はhistory同一IllegalState body/closeとprovider IAEを再現。旧BAT151末尾はprovider.executeQuery IAEを固定DB失敗と期待していたが、BUG206の広いcatchと同じ分類混同なので、先行SSC063/SS332に基づき未知provider同一性へ修正する。期待をProductionから生成せず、060の独立表を用いる。DB不正id/NULL/時刻/順序/件数/terminalの旧固定診断oracleは一切変更しない。insertはJDBC id取得をconstructor catch外へ置き、pure BatchStepAttempt生成の不正値だけSQLDataExceptionに変換する。public不正引数のIAEは従来どおり。

Fixture: 公開固定RUN/STEP/NOW/END、history/insertは空から、abandonは同run RUNNING1行をseed、finishは新規handle、replayは同値SUCCESSをcommitした状態。各標本の実行後caller rollbackを行い、独立snapshot SQLで試験前行と件数/状態が完全一致すること。未知例外を成功・空結果へ変換しない。既存全16 Repository PT、399 JDBC位置、24値を含む親step PT、関連CleanupStep/BackupStep/Serviceも回帰する。

既定Ubuntu26.04.1/JDK25.0.4/Maven3.9.12/PG18.6。選択ResourceScopeTest,BatchRunRepositoryTest,BatchStepValuesTest,BackupStepRepositoryTest,BackupCommitServiceTest,CleanupStepRepositoryTest,StepCleanupServiceTestをbatch -amでtest/JaCoCo report/SpotBugs check。class名は実ファイル名と照合して実行する。全変更classのline/method/class/branch100%、static未解決0、追加除外/抑止なし、failed/error/skipped0。command・source・時刻・exit・hashと各独立後条件は069と正式manifestへ記録する。全reactor/38scope/46負canary後に認定、新JUnit/部品加算0。広域YKT154は他所有契約の非該当根拠を揃えるまで閉じない。
