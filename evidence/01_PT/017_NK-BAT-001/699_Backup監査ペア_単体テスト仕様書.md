# Backup監査ペア 単体テスト仕様書

NK-BAT-001 / BackupStepRepository全Source・Terminal / BAK-BKO-OPS009 / UI251 / SS331§8.3・341§6.6・343 / SSC061・063・134 / 451・802。Mainはb093不変更、PGレビューとPTを並行する。

旧BackupTerminalObservationTest全3（ISSCOMP001～003）の手書14列・SUCCESS/FAILED/SKIPPED・全requirednull・identity差・unknown JDBC保持・Terminal/純粋BackupObservation不変条件をそのまま含む。実DBの既存BackupStepRepositoryTestは含めない。

新BKPPORT001～010（BackupPairPortTest全10method）: 正常RUNNING/成功ペアとliteral SQL・timeout5・bind2、completeの1/2files・3/12bytesの独立UPDATE14bindと再送無更新、row0/1/3/重複/未知id/混在、不正14列とnull、ended境界・µs・両error列、SQL/RTE/Error各取得/操作/close・SSC063優先・null資源、parentidentity事前事後、完成後未反映拒否、null/time境界、Terminal構造・constructor契約。fixtureは手組行とJDKProxyのみ。

input claim: UUID(0,1)、UTC2026-11-05T00Z、db/config id7/8・start+1/+2秒、content+3/+4秒、observed+5秒、bytes3/5/7、synthetic64zerohex。versionsはfixture/001。BackupManifest ctorは入力carrierのみ。期待値はSQL/SS後条件/手書literalから独立作成しproductionで生成しない。実file/archive/key/DB/ownerの真正性を主張しない。

JDBC借用connへcommit/rollback/close/config/NewConnectionは禁止し、不明methodはAssertionError。各資源のclose回数、原unknown同一性、SQL固定diagnostic、secondaryredaction、UPDATE後readback拒否を検証する。並行同connを許可しないsingleowner事前契約、再送は既成功時刻保持/二重UPDATE0。

実commandは既qualifier prepare/static/run/post backup、最終source・環境・真正OS終端・全13XML・単exec/session・normalBatch全physical2 CRC・四100・HELD四0・class-init原hash・障害・hashは700結果。未達/失敗/skip/未実行は合格算入しない。旧成果合算/任意除外/coverage抑制0。PG/PT実環境/原本/Root/native/第一V/正式1964-53/工数nullは別条件。

|Test ID|class.method|独立期待・検査条件|
|---|---|---|
|BKPPORT001|BackupPairPortTest.runningAndSuccessReadExactPairSqlBindingsAndCloseBeforeReturning|RUNNINGペアempty、SUCCESS同END、literal SQL/order/timeout5/id7-8・closed2|
|BKPPORT002|BackupPairPortTest.completeWritesIndependentFourteenBindingsAndReplayRetainsOriginalTimeWithoutUpdate|db/config14bindは1-2filesと3-12bytes、全setter型、既成功END維持/UPDATE0|
|BKPPORT003|BackupPairPortTest.missingDuplicateExtraUnknownAndMixedPairsNeverBecomeComplete|row0/1/3・重複/未知id・RUNNING-SUCCESS混在/時刻差は固定例外|
|BKPPORT004|BackupPairPortTest.everyRequiredColumnAndRunningCounterOrIdentityDifferenceRejectsIndependently|必須11nullとidentity5差/ended混入/zero4差/error2差を一fieldずつ拒否|
|BKPPORT005|BackupPairPortTest.successRequiresExactFilesBytesErrorsAndMicrosecondContentObservationWindow|SUCCESSの件数bytes/失敗・error差、content前/未来/subµs拒否、contentfinish等号許可|
|BKPPORT006|BackupPairPortTest.eachJdbcFailurePreservesUnknownIdentityCatalogsSqlAndClosesOwnedScopes|全22JDBC箇所SQL固定・RTE/Error原値、nullstmt/row拒否と全close|
|BKPPORT007|BackupPairPortTest.bodyAndBothCloseFailuresFollowIndependentDeclaredPrecedenceAndRedactSecondary|body/rowclose/stmtclose18複合のSSC063優先と固定secondaryだけ|
|BKPPORT008|BackupPairPortTest.parentIdentityMustSurviveBeforeAfterAndCompletionReadbackCannotBeManufactured|identity第1/第2read喪失拒否、UPDATE後RUNNING/違う終端は失敗|
|BKPPORT009|BackupPairPortTest.nullAndObservationBoundsRejectBeforeBorrowingResourcesIncludingMaximumAcceptedTime|null/不正時刻はSQL0、+10000/past/subµs拒否、9999最終µs受理|
|BKPPORT010|BackupPairPortTest.terminalFalseSkipBranchAndTypedColumnFailuresDoNotCreateCapabilities|skip-expected不一致拒否、静的borrowedrow getterSQL/RTE/Errorは同一参照|

BUG2289/YKT2034は実行前レビューで起票し、yearliteral/無意味assert/適用style19箇所を是正。原draft compile/staticと全文横展開非該当根拠は803へ保全。最終PG19048compile0・PG19050 raw21個別非適用/適用0/CS0/parser0。旧3のhash不変。実行13はPG19052、sourceをcommit/push後に一回だけ開始する。
