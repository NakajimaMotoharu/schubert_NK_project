# NK-BAT-001 backup両step横展開・独立oracle

PG-D-168 / SSC-061 / BUG-191～194 / YKT-151～153。2026-09-13。
正式12/source2abb30ff、08:53:53～09:09:54 JST/exit0、全1391 PT・4coverage100%・Production static未解決0、38scope/38負canaryで再試験認定。全14所有者の回帰は成功、BUG191～194/YKT151～153完了。新2class/12method/115line/84branch、既存Step1class/5method/63line/46branchは全missed0。以下の探索反例・選択成功は履歴であり、それだけで全PGPT合格としたものではない。

## 1. 独立期待値と故障出現点

041/BAT210～217、043/BAT218～225。実PostgreSQL18/Flyway SQL20本、SCHEMA作成履歴1行は別分類。Productionからexpectedを生成しない。公開fixture run=12345678-9abc-def0-8123-456789abcdef、cutoff=2026-09-12T15:00:00Z、start=2026-09-13T02:00:00Z、contentFinished=02:00:02Z、end=02:00:03Z。2完全handle=90001/BACKUP_DB/attempt1と90002/BACKUP_CONFIG/attempt1（逆順も試験）。

14列はid/run_id/business_date/step/attempt/status/started_at/ended_at/target_count/success_count/failure_count/byte_count/error_code/error_summary。DB成功は1/1/0/26、CONFIG成功は2/2/0/67、共通UTC endとNULL診断、RUNNINGは0/0/0/0・end NULL。SQL後条件はUTCへ明示変換したµs6桁literal。BAT210でUTC/JST双方を同一期待値とtyped endで再確認する（BUG191）。schema履歴はsuccess/version非NULL/type SQL=20、type SCHEMA/version NULL=1を独立確認（BUG192）。旧migrationは変更しない。

JDBC inventoryはpublic Connection/Statement/ResultSetだけを観測。inspect=前後run参照16×2+pair query38=70、新complete=70+既存finish50×2+再inspect70=240、既存SUCCESS replay=70、全SQL fault=380出現点。serviceは入口3+setAutoCommit2+commit1を加え新246/既存76。246箇所のSQL失敗とinterruptを個別注入する。全14列・0/1/3行・status対・µs/time境界・null・行/所有lock・2connection並行を実施する。

Javac生成try-with-resourcesのclose/suppressed経路もpublic JDBC proxyから到達させる。coverage除外、反射によるProduction private呼出、Productionによるexpected算出は使用しない。trace5本は実DB SELECT/観測callから出力し、020は独立literal、019は全byte改変・欠落・余剰・不正testcaseで検証する。

## 2. 反例→修正→再試験

| BUG | 修正前起票commit | 実際の反例 | 修正と選択結果 |
|---|---|---|---|
| 191 | 8a6fbbc9 | explore1の7期待不一致、同じtimestamptzがJST textの+09で表示 | oracleをUTC/µsに固定。Production不変更。全16とUTC/JST再試験。 |
| 192 | 8a6fbbc9 | explore1でFlyway全履歴21をSQL migration20と混同 | SQL20/SCHEMA1を別々にassert。旧DDL不変更。 |
| 193 | f030f647 | 08:36:15の2試験で先行IllegalStateExceptionがrollbackのNPEへ置換 | Backup/Stepでunknown primary同一性、固定secondary、known/fatal優先順位をSS341§6.6と一致。Backup60+Step70=130複合と元2反例を既存BAT176/224内で再試験。SQL/Runtime/NPE/Error、同じthrowable再送、rollback/復元双方を含む。 |
| 194 | b1d56666 | 08:41:08 SpotBugs THROWS_METHOD_THROWS_RUNTIMEEXCEPTION 2件 | pattern Runtime別名でなく元multi-catch参照をthrow。意味/expected不変更、抑制不追加。08:43:19の選択Batch24+Storage8・SpotBugs0、exit0。 |

rawログはローカル/tmpのみ。秘密値を含めず結果を上表へ要約し、元ログhashを保存する（rawのGit格納なし）。

| local log | SHA256 |
|---|---|
| pgpt-backup-step-explore1.log | 64733dd579834a0e71f46914f11ee6b656e317d2808451291ec3554a43fc05c5 |
| pgpt-backup-step-explore2.log | 8ef2c87c3d68ea47c964c131d0a8fb70af27213dd683272f0e067e50e7e48716 |
| pgpt-bug193-red.log | 0176859f87d8a1ea473a54b8a77ab8dd54604ea66cad0ed7e6c8070b264d93b3 |
| pgpt-bug193-green.log | 5f00b8670fb971432a7ead9fc9ea0af12df55c8a7998b8eb00dd42c3223e6ea9 |
| pgpt-bug193-static.log | b7a49ceefba9b25054ec3e40c173e06bf5e015d89c4f2925fa14e94dd386c027 |
| pgpt-bug194-green-static.log | 754aef5d547d88127c28a3a3cfa40c93f01fd2ac24c56b4edbf3dfda382694b2 |

## 3. YKT152 全14 rollback所有者の契約別確認

検索条件：全Productionのrollback直後catch、transaction/Connection所有、outer catch、public失敗契約。名称だけの検索完了ではなく、直接修正2件と下記12件の非該当理由・再試験対象を確認する。非該当は「未知例外が起こらない」という意味ではない。全体を成功/正常応答へ変換しない既存契約を確認し、SSC061の借用connection/unknown primary同一性という追加契約を無関係な外部APIへ無断拡張しない。

| owner | 対応/非該当根拠 | 回帰試験 |
|---|---|---|
| BackupCommitService | 直接修正。借用connectionのrollback/restore両方、unknown primary同一性契約 | BAT218～225、特に224複合60 |
| StepCleanupService | 直接修正。同じborrowed restore/primary契約、CleanupStopped既知型も区別 | BAT170～177、特に176複合70 |
| LogCleanupService | SS341§3/7.2の既存DATABASE_FAILURE/停止契約。rollback失敗は固定DATABASE_FAILURE、unknown runtimeは非成功。primary同一性をこの既存契約へ追加しない。rollback未成功時autocommit復元なし、SessionLeaseのみrelease、caller接続破棄 | BAT025 rollbackAndUncertainCommit、026 restorationAndUnlockFailures、029 failuresLeaveNoFalseSuccess |
| LogQueryApplicationService | owned TWR Connection、outer SQL/Runtime→固定TemporaryInfrastructureException。元unknownのidentityを返すAPIではない | ADM069 database/crypto/resource rollback |
| UserQueryApplicationService | owned TWR、outer SQL/Runtime→固定Infrastructure。close含め失敗なら成功応答なし | ADM050 |
| UserMutationApplicationService | owned TWR、SQL/Runtime→固定Infrastructure、更新/監査/Inboxのatomic契約 | ADM035 |
| ScenarioApplicationService | owned TWR、auth/access/Inboxの確定業務拒否のみ分類、suppressed有ればTemporary。unknown rollback RuntimeもTemporary、成功/ACKへ戻らない | failuresAtEveryTransactionFileClockAndIdentityBoundaryNeverClaimSuccess |
| MediaApplicationService | owned TWR、Scenarioと同じ固定Temporary/承認拒否の分類。borrowed autoCommit復元なし | MED059 |
| EncryptedWebSessionRepository | owned TWR、SQL/security/Runtimeを固定SessionStoreException、失敗sessionを返さない | WEB041 |
| JdbcSyncRequestProcessor | owned TWR、PermanentProtocolはrollback/close確認済みのみ、その他SQL/RuntimeはTemporary。unknownもACK用正常結果へ変換しない | LoginInboxServiceTest.jdbcLifecycleFaultsRemainRetryableAndRedacted / permanentProtocolNeedsConfirmedRollbackAndClose |
| InboxCleanup | owned TWR、外側SQL/Runtime→固定InboxMaintenanceException。verifyTransaction後commitのみ、失敗は成果0推定しない | InboxInspectionProgressTest.checkpointFaultsRollbackDeletion / uncertainCommitReloadsDurableCounts / ownsLocksWithoutSavepoints |
| WebLogIngestService | owned TWR、SQLは固定LogProjectionDatabaseException、unknown Runtimeはthrow。public契約はinsert/duplicate返却前commit、失敗をACKしないことでありunknown primary identityではない | transactionFailuresNeverReportSuccessAndAlwaysReleaseConnection（SQL/Runtime×rollbackSQL、close/rollback回数、実DB件数）、databaseCommitSurvivesAckFailureAndBrokerCacheMiss |
| WebLogDispatcher | claim/mark専有TWR、例外時dispatch reportを返さず、leaseで再送。unknown cleanupでも正常mark/reportなし。borrowed restoreなし | databaseFailuresRollbackAndCloseWithoutInventingSuccessfulMarks、confirmedSendThenMarkFailureRecoversAfterLeaseWithoutDuplicate |
| OutboxDispatcher | claim/markSent/markFailureの専有TWR、rollback helperとsetup close確認。失敗時reportを返さず、lease/send-mark再送が正本。borrowed restore/unknown identity契約なし | publicBoundariesRejectNullModesBoundsErrorsAndEveryWireIdentityMutation、dispatcherPersistsBothDestinationsAndArtemisSuppressesSendMarkCrashDuplicate |

YKT151は共通fixture全2class16PT、既存BatchRunRepositoryのtyped UTC/歴史境界、全JDBC UTC回帰を実行する。YKT153は直接2classの精密rethrowと既存BUG181の同形primary経路、全Production SpotBugsを再実行する。上表の全対象が正式全reactorで通るまでYKTを完了にしない。

## 4. 限界・追跡

fixture hashは公開合成文字列であり、PG168は任意BackupManifestを認証しない。root CREATE_NEW0600 MANIFEST書込・trusted reader、dump/list/tar/age検証、fsync/atomic、7世代、親OS lock継続・全朝batch・実NKCHR・IT/STは未認定。SQL pair success単独を削除gateにしない。正式認定後の日時/commit/command/4coverageは042・044とevidence/manifest.json、sourceFilesとfiles hashで追跡する。
