# WebLogOutbox全JDBC port 単体テスト仕様

Program NK-WEB-001/NK-MSG-002・WebLogOutboxRepository全method。canonical owner/costOwner WBS-P006-03、UI235/242、SS324§8.3/9・331§9.3/352、QA054承認後のREQUEST/MENU共有outbox。原開始見積1.5/4/8pp cap10、860参照。未実行を合格へ算入しない。

事前: normal six Main compile/NullAway・sixSB各真正0、source/Test/tool/CPを固定。新suiteのみ全@Testを選択し、元成功の再演なし。JDBC dynamic proxyがConnection.getAutoCommit/prepareStatementと明示されたStatement/ResultSetだけを許可し、commit/rollback/close/実driverはAssertionError。各worker専有、実排他の証明ではない。

固定入力: 2026-11-06T00:00:00.123456Z、UUID低位public整数、29個0byteの非実包絡とPUBLICラベル。鍵/署名/crypto/recovery/Root等を呼ばない。独立期待値は本Testの手書きSQL/列/型/引数/返却順/固定message・SQLState・範囲。SSのdelay1/5/30/60/300秒と±10%、attempt100飽和、claim1..100/lease10秒を入力表で算出。Production定数/getterを期待値の算出に用いず、実値getterはactualだけ。DateTimeException/SQL failure/unknown runtime/Errorは同一例外伝播とowned Statement/ResultSet逆順close、borrowedConnection非操作を確認。

|Test ID|class.method|独立期待値・観点|
|---|---|---|
|WLG-PORT-001|WebLogOutboxPortTest.port001SupplierNullIsRejected|constructor supplier null拒否|
|WLG-PORT-002|WebLogOutboxPortTest.port002EnqueueFirstWriteAndDuplicateUseExactSqlBindings|enqueue初回1/重複0・6bind型/固定SQL/合成cipher不変|
|WLG-PORT-003|WebLogOutboxPortTest.port003EnqueueRejectsEveryRequiredArgumentBeforeSql|enqueue三必須null→SQL未準備|
|WLG-PORT-004|WebLogOutboxPortTest.port004AllPublicOperationsRequireBorrowedExplicitTransaction|全4operation connection null/autocommit拒否|
|WLG-PORT-005|WebLogOutboxPortTest.port005ClaimEmptyAndLimitBoundsBindUtcAndTenSecondLease|claim空とlimit上下端・5bind/UTC/10秒|
|WLG-PORT-006|WebLogOutboxPortTest.port006ClaimSortsDueThenIdAndReturnsIndependentImmutableRows|claim due/id順・全field・immutable/clone|
|WLG-PORT-007|WebLogOutboxPortTest.port007ClaimRejectsInvalidWorkerLimitAndNullTime|worker/limit範囲/欠落時刻拒否|
|WLG-PORT-008|WebLogOutboxPortTest.port008SentUsesOwnerStatusCasAndReportsUnchangedRows|SENT CAS1/0・owner/status/3bind|
|WLG-PORT-009|WebLogOutboxPortTest.port009SentRejectsNullRowAndTime|SENT null row/time拒否|
|WLG-PORT-010|WebLogOutboxPortTest.port010FailureBackoffAndSaturatedAttemptUseIndependentVectors|failure全backoff/±10%/attempt100飽和と6bind/CAS0|
|WLG-PORT-011|WebLogOutboxPortTest.port011DefaultJitterStaysWithinIndependentTenPercentBounds|default supplier jitterの独立900..1100ms範囲|
|WLG-PORT-012|WebLogOutboxPortTest.port012FailureRejectsMissingOrUnboundedErrorCode|failure null/error字種/長0,64,65|
|WLG-PORT-013|WebLogOutboxPortTest.port013FailureRejectsOutOfRangeJitterBeforeSql|jitter範囲外のSQL準備0|
|WLG-PORT-014|WebLogOutboxPortTest.port014EveryMissingDatabaseFieldProducesFixedSqlDataFailure|DB全必須10field欠落→固定22004|
|WLG-PORT-015|WebLogOutboxPortTest.port015InvalidStoredLayoutOrVersionRejectsBeforeOtherFields|layout/version未知/空/null→固定22000|
|WLG-PORT-016|WebLogOutboxPortTest.port016StoredConstructorInvariantsAreNotNormalizedAsSuccessfulRows|保存rowのconstructor invariant不備は拒否|
|WLG-PORT-017|WebLogOutboxPortTest.port017TimeOverflowAndSupplierFailureKeepIdentityAndResourceOwnership|時刻overflow/同期supplier failure identity/close|
|WLG-PORT-018|WebLogOutboxPortTest.port018JdbcFailuresPropagateWithoutTransactionOrConnectionOwnership|全4操作SQL段階例外とResultSet例外/借用owner不変更|
|WLG-PORT-019|WebLogOutboxPortTest.port019BorrowedConnectionRemainsUntouchedOnSuppressedAndUnknownFailure|固定SQL primary/suppressedとunknown非正常化|
|WLG-PORT-020|WebLogOutboxPortTest.port020SharedRepositoryHasIndependentConcurrentJdbcState|二専有worker同repoのstate非共有|

command: archived input/007_owned_web_outbox_unit.py prepare/static/run/post (新unused slotsだけ)、post後に047結果とmanifestへOS/JDK/tool/source/argv/exit/XML/coverage/CRC/exec/hashを記録。全line/method/class/branch100、normal全physicalと単一exec/sessionで確認。安易除外/合成0。静的指摘は適用性を個別根拠付き分類、抑制せず適用不備は是正。

NPE排除: @NullMarked package/normal NullAway、constructor/境界null契約、collection row各欠落と正常fixture、NPEを製品で正常扱いcatchしない。並行=own2workerのstate分離、再送=MessageUK conflict/attempt/CASのSQL構造と戻値。実PostgreSQL SQL構文/row競合/commit、暗号真正性、broker/再送workerの実行、producer/ingest全体、Runtime/CHR/native/451全体/IT-STは本試験で受入しない。BUG/実績は結果へ追記。
