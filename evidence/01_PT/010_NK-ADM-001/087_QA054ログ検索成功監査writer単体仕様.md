# QA054 LOG_SEARCHED writer 単体仕様

Program NK-ADM-001 / LogQueryAuditWriter.write、Event、LogQueryApplicationService.persist（後者PG強化レビュー・動的PT HOLD）。RD FUN008/MON003/TST004、UI235/252/264、SS312/324/351/355、QA054/UIC011/SSC336、main f6df0102f。

|Test ID|class.method|事前fixture・入力と独立期待値|
|---|---|---|
|PT-ADM-SEARCHPORT001|LogSearchAuditPortTest.searchPort001AllClosedEventsUseIndependentSqlAndBindings|全5Event/ADMIN、固定Instant/UUID、literalSQL10bind・action/category/level/reason/outcome/step、sourcequery値なし|
|PT-ADM-SEARCHPORT002|LogSearchAuditPortTest.searchPort002AbsentActorUsesSqlNullForExistingDenialAndReplay|非成功4Event/actorなし、SQLNULL BIGINT/VARCHAR、actorRole欠落|
|PT-ADM-SEARCHPORT003|LogSearchAuditPortTest.searchPort003SuccessRequiresPresentAdminBeforeAnySql|success actorなし/USERは固定IllegalArgumentException、prepare0|
|PT-ADM-SEARCHPORT004|LogSearchAuditPortTest.searchPort004NfcAndDisplaySanitizationDoNotCopyQueryOrCredentials|結合e＋5制御separatorをé＋5space、固定6key以外なし|
|PT-ADM-SEARCHPORT005|LogSearchAuditPortTest.searchPort005ExactlyOneAffectedRowIsRequiredAndStatementClosed|row -1/0/2固定SQLException・own statement close、row1は001|
|PT-ADM-SEARCHPORT006|LogSearchAuditPortTest.searchPort006OwnedSqlFaultsAndUnknownRuntimeIdentityPropagate|prepare/bind/execute/closeのSQL/Runtime/Error同一instance、execute＋closeはprimary/suppressed同一、borrowed connection操作禁止|
|PT-ADM-SEARCHPORT007|LogSearchAuditPortTest.searchPort007AllNonNullBoundaryContractsFailBeforeSql|全5nonnull引数nullを即拒否、prepare0。NPEを正常化するproduction実装なし|
|PT-ADM-SEARCHPORT008|LogSearchAuditPortTest.searchPort008IndependentOwnedWorkersDoNotShareBindings|二ownedworker成功/REPLAYでbind混線0、join/close|
|PT-ADM-SEARCHPORT009（提案・未実行）|LogSearchAuditPortTest.searchPort009MissingStatementUsesFixedSqlFailureBeforeBinding|五eventでprepareがnull。固定SQLDataException／22004、原因・抑制なし、prepare一回・bind/execute/closeなし。SS332の必須DB値分類とSS351の監査失敗契約、JDBCの未取得資源規則から独立に確定。BUG-3417／YKT-2739。PG40860はcompile終了1。試験の差分は `5462_log_search_audit_statement_null_proposed.patch` へ保全。|

各入力は公開固定値だけ。contextは全0formatの合成値で発行・認証に使用せず出力しない。LogRequest.decode→protocolのみを呼び、canonical/キー/response snapshot/Inbox/APIサービスや実DB/JMS/Root/VM/nativeは実行しない。既LogVectors/LogApplicationFixtureはheld key経路を含むためcompile/selectしない。JDK JDBC Proxy以外のprovider0。expectedは承認設計/SQL仕様からliteralで記述しproduction関数で生成しない。

callerは初回Successかつ非REPLAYのみ、snapshot後/同connection finaltransaction内で保存するよう製造。query failure/denial/replayを成功にせず、保存失敗を既transaction rollbackへ伝播する。caller全経路はheld TemporaryInfrastructureException/ResponseSnapshotCodec/FingerprintKeyRingに依存するため動的PT未実行を維持し、静的レビューをPASS/coverageへ換算しない。

実行command/OS/JDK/対象source/run/全分岐・line/method/class/branch/例外/null/並行・静的/CRC/単exec/XML・エビデンスpath/hash/BUGは088結果とmanifestへ保存。着手時NOT_RUN。全source四100はwriter範囲で要求し、caller/全体451/CHR/native/正式受入は別未完。
