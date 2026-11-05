# Inbox検査summary 単体テスト仕様書

NK-BAT-001 / InspectionSummaryRepository全Source / WBS-P004-02 / OPS009・DAT009/UI251/SS311・331§3.13・332・341§7.3/SSC049056063/BAT114～121/451/815。Main b093不変更、PGレビューとPTを並行する。InspectionSummaryPortTest全8、INSPPORT001～008。旧TestはDB BeforeAll/TempDirを持つためcompile/選択しない。

literal4列/UUID+UTCµs2bind/timeout5、autoCommittrue・readonlyfalse・RC（通常借用TXと逆の前提）、missingOptionalと0count DTO、countbalance/negative/null/unknown/2row、SQL-RTE-Error/両close優先・全ownedclose、前後interruptを独立vectorで検証。source/expectedをproduction mapper/SQL/predicateで生成しない。

fixtureは固定UUID(0,1)/UTC2026-11-05T00:00:00.123456Z・手組map/JDKProxy、実DB/SQL/Inspectorchild/Root/原本/Backup/鍵/native/VM/network0。interruptは自所有workerへだけ、有限future.get/flagfinallyclear/parentflag不変、sleepなし。readが返したDB観測を新鮮なchild終了やOS/DB排他の資格へ読み替えない。borrowedconn取得/commit/rollback/close/config0。

実commandは既qualifier prepare/static/run/post inspection_summary。全8sourcefreeze/push→単exec/session→全physical1正常CRC/全@Test/四100・HELD四0・原XML/環境/argv/真正OS終端/static適用0/同六Main/NullAway/SBを独立postし、708/816以降へ各method/期待・coverage・BUG・pathhashと結果を記録。failed/skip/notrun算入0、安易除外/到達不能偽装0。原見積.75/2/5 cap10普通PGPT、S/V付替え0。新WBS個別受入/正式1964-53/工数null/第一V/実環境/451全体は別。

|Test ID|class.method|独立期待・検査|
|---|---|---|
|INSPPORT001|InspectionSummaryPortTest.literalSqlTimeoutAndUuidUtcBindingsReturnAllFourColumnsWithoutOwnershipMutation|literal4列/timeout5/UUIDUTCµs2bindと16操作順、3/2/1・completefalse|
|INSPPORT002|InspectionSummaryPortTest.trueAbsenceIsDifferentFromZeroKnownCountsAndBothCompleteValuesArePreserved|absenceOptionalと既知0を区別、completefalse/true・MAX/Max-1/1|
|INSPPORT003|InspectionSummaryPortTest.requiredNullCountBalanceAndDuplicateRowsCannotFabricateAValidSummary|必須4null/negative3/不整合balance/2rowは固定例外|
|INSPPORT004|InspectionSummaryPortTest.nullAndExplicitAutocommitWritableReadCommittedPrerequisitesRejectBeforeOwnedSql|nullconstructor/run/autoCommitfalse/readonlytrue/非RCはSQL取得0|
|INSPPORT005|InspectionSummaryPortTest.nullStatementOrResultSetIsCataloguedAndEveryAcquiredResourceStillCloses|nullstmt/rowは固定例外・取得したstmtだけclose|
|INSPPORT006|InspectionSummaryPortTest.everyProviderFaultPointIsReachedAndOnlySqlLosesPrivateDiagnostics|全16point×SQL-RTE-Error、実hit/原unknown同一性・SQLdiagnostic固定|
|INSPPORT007|InspectionSummaryPortTest.primaryAndBothCloseScopesHaveIndependentPriorityAndExactSafeSecondaryCounts|body×rowclose/stmtclose18組、safe secondaryの正確な個数/型/固定message|
|INSPPORT008|InspectionSummaryPortTest.beforeAndAfterInterruptRejectOnAnOwnedWorkerAndNeverChangeTheParentFlag|ownedworker内だけ前後割込み、post失敗でも両close、finallyflag消去/親flag不変|

PG19140compile0/PG19142 raw28全個別非適用・適用0/CS0/parser0、816。thread関連ルールはstandalone batchのflag読取/自所有JUnit workerだけでJ2EEではない根拠を各位置に記録。scopeのActualRole/DB/child/OS資格を模擬値で認定しない。source固定/push後に新専用PG19148で全8を一回、独立postへ。新BUG0。
