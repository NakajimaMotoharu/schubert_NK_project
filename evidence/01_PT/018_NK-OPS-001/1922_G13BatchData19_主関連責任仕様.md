# G13.07 Batch結果値・repository・MQ境界19 sourceの主関連責任

2026-10-25 15:22 JST、G13_BATCH_DATA19_SOURCE_V1、Production64446不変更。開始見積.5/2/6pp・一群上限10pp。開始fresh使用0/残100/reset1793513544（06:12:24UTC照会値のmarker、正確照会時刻は未保存）。以前の窓消費を現在残から差し引かず、fresh残10以下/取得不能で保全。markerが変わった区間の費用はnullとし、reset操作/追加課金を行わない。

限定source rootは`src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/`。実Main責任は原485/941を維持する。BackupManifest/VersionsはP01705、BackupStepRepositoryはP01706、MorningDatabaseSessionはP01701、CleanupStep familyはP01707、ExpiryAuditRepositoryはP01711、ArtemisManagementReadinessClientはP01710。fixtureの複数参照担当を消さず、Test名・配置・変更群の担当だけで主担当を決めない。

|source|primary/cost|実Main又はliteral source根拠|
|---|---|---|
|backup/BackupManifestFixture.java|WBS-P017-05|独立manifest fixture、BAT178..193、BackupManifest/Versions、digest03関連保持|
|backup/BackupManifestValuesTest.java|WBS-P017-05|manifest値/時刻/不変性、UI251/SS341343、BAT178..185|
|repository/BackupStepFixture.java|WBS-P017-05|manifest()が直接生成するBackupManifest/Versionsがprimary。利用先Repository06と区別、PG168/BAT210..225のSQL oracle関連を保持|
|repository/BackupTerminalObservationTest.java|WBS-P017-01|MorningDatabaseSession.BackupObservationのterminal組/保持/欠落、SSC134/ISSCOMP001..003|
|repository/BatchStepValuesTest.java|WBS-P017-02|BatchRun/Step/Result値を中心とするcatalog、BAT130..137、attempt12関連保持|
|repository/CleanupStepFixture.java|WBS-P017-07|CleanupStepRepository独立fixture、SS3313.14/BAT162..177|
|repository/CleanupStepValuesTest.java|WBS-P017-07|CleanupStepChunk/Kind/Counts/Reason、SS331332341/BAT154..161|
|repository/EnumValueCatalogCompatibilityTest.java|WBS-P017-02|root BatchStep catalogと結果列挙、cleanup07/attempt12関連保持、BUG1478|
|repository/ExpiryAuditResourceFailureTest.java|WBS-P017-11|ExpiryAuditRepository資源/例外の独立JDBC proxy、EXP310001/BUG1530|
|repository/ExpirySuccessfulScopeTest.java|WBS-P017-11|ExpiryAuditRepository成功境界とTWR独立oracle、EXP4956001..024|
|repository/MorningDatabaseAccessContractTest.java|WBS-P017-01|MorningDatabaseSession.Accessのdefault/不許可/null、MAccess585..587|
|repository/MorningExpiryObservationInvariantTest.java|WBS-P017-01|MorningDatabaseSession expiry observationのliteral整合、EXP1749|
|repository/MorningExpirySessionTest.java|WBS-P017-01|同sessionのDB admission/readback/handoff、MDB2604..2614、実DB再演しない|
|repository/MorningSuccessfulBackupProjectionTest.java|WBS-P017-01|同sessionのSQL projection、MDB-PROJ1737001..007|
|repository/WebReceiptCleanupTest.java|WBS-P017-07|CleanupRepositoryのreceipt orphan削除、QA048/SSC175/RCPT004、実DB再演しない|
|file/CurrentObservationValueTest.java|WBS-P018-03|StartupPermitRecords.Epoch/CurrentObservationのsynthetic data保持、DATA511001、実permit操作なし|
|mq/ArtemisManagementEncoderBoundaryTest.java|WBS-P017-10|ArtemisManagementReadinessClient encoder引数と借用境界、ENC001..003|
|mq/ArtemisParentDeadlineTest.java|WBS-P017-10|同clientの親remaining/timeout切捨て、EXPARENT005|
|mq/ArtemisUnknownBoundaryTest.java|WBS-P017-10|同clientのquery/encoder UNKNOWN identity、MQUNKNOWN001..004、expiry11関連保持|

既PG9386v3 graph・正常build9246のSourceFile/constant-pool・現source hash・原Main担当へ静的照合する。上表は別parserで独立expectedとして読み、5完全path選択vector/9catalog反例/8mapper反例/19近傍/旧807全canonical・関連・不確定・artifact witness保持を検証する。Batch→別module反例は明示mutationで行う。未実行PTのPASS化、元oracle/Currentbaseline変更、実測coverage補完をしない。

着手許可はpublic repo/保存classfile/JDK javapのbyte読取と工具自身の限定metadata vectorのみ。ターゲットclass load/init/compile/JUnit、実VM/DB/broker/Backup/鍵/Root/cohort/intent/permit/配備/Service操作・遠隔接続なし。名称上のsecurity機能を一括拒否PTと認定するものではなく、今回作業は実行PTの代替ではない。実操作のHOLDは維持する。

見込source責任1632→1651/1789、Test667→686/824、残157→138、限定807→826。独立検証後だけ計上。費用はG13.07一回、元見積/受入/941943/歴史sourceと成功失敗証拠は不変。正式1964PT/53scope・既17/190・工数null・QA051final・BUG1746全current WBS監査HOLD維持。終了条件は19literalと当source/hash/元担当/関連保持を確認し485486を同期する限定成果であり、全G13/451受入ではない。終了後も独立PG/PTへ継続する。
