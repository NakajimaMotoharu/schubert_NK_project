# Morning ownership four Main: three canonical preparatory scopes and independent expected lifetime/exception contracts

NK-BAT-001。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG29724](../018_NK-OPS-001/evidence/PG29730-p01701-test-id-corrected-contract-v1/manifest.json)。

- P01701-PREP-001 / execute native/injected / PT-OPS-MROOT001-006: root→M→policy→trusted→postroot, all eight deployable policies before any stop; M retained through callback; missing owner empty refuses callback; no A/DB/Backup/permit authority

- P01701-PREP-002 / executeVerifiedEpoch/executeCompletedEpoch / PT-OPS-MCTRL001-019: same M→clear all intent/residue→same dedicated DB/original→stop8→A→fresh8→durable INVALID exact activation→trustedwork; budget/root/original/DB rechecks before publication, completion inside original lifetime

- P01701-PREP-003 / protectGraph/protectPublication / PT-OPS-MCTRL001-019: failure invokes existing graph observation and publication abort before outer M release, no success on uncertain stop; outer completed owner retained only when actual captured graph exists; no inferred native proof

- P01701-PREP-004 / executeOwned/executeOwnedEpoch/executeResumeOwned/executeResumeOwnedEpoch / PT-OPS-MCTRL001-019: explicit resume UUID NN, null cannot select new run; callbacks no connection/original/borrowed A fd export; INVALID epoch exact identity and absent permitdigest; gate before/after each owned boundary

- P01701-PREP-005 / requireNoExpiryRequest/withClearIntent/executeStopAndStartup/afterOriginal / PT-OPS-MCTRL001-019: no start intent/residue under M before original/DB/stop; stop before A, terminals after A, borrowed FD not exported, empty M/A no trustedwork, all results NN; synthetic gate overload is not production entry

- P01701-PREP-006 / constructors/rootGate/releaseGate / PT-OPS-MDB001-008: only MORNING snapshot and exact loopback jdbc:postgresql://127.0.0.1:<1..65535>/schubert_nk; no URL extension, pool/fallback or SQL export; legacy schema callback cannot mint issuer inspection

- P01701-PREP-007 / execute/admitObservation/scalar / PT-OPS-MDB001-008: consume owned credential even preconnect refusal; password copy zeroed and Properties cleared on all exits; fixed schubert_batch login/effective/database/RW/readcommitted/notrecovery, one advisory71419602 before callback; callback sync NN result; Session invalid after callback and one owned connection close before return

- P01701-PREP-008 / Session.guard/Access defaults/currentRunReference / PT-OPS-MDB001-008: active same-thread/no handoff/interruption/root guard before JDBC; capability expires after callback, defaults refuse and data-only records not authority; same-run lookup rejects otherUUID but is not retained-original proof

- P01701-PREP-009 / DatabaseObservation/BackupBegins/BackupObservation/ExpiryBegins/ExpiryObservation / PT-OPS-MDB001-008: constructors establish NN, exactly2 ordered backup rows same run/start/end/status distinctID, prior pair only skipped/ALREADY_SUCCESSFUL/earlier attempts; expiry skipped zero/current-start/prior-audit/receipt0 vs actual terminal count/time/status; toString redacted

- P01701-PREP-010 / beginBackup/beginResumeBackup/successfulBackup/completionGuard / PT-OPS-MDB001-008: release/schema before both begins; atomic pair commit confirmed before autocommit/handoff/handle export; success lookup exactlytwo genuine matching rows all14columns/N12/microseconds/original businessdate; resume checks old manifest and genuine pair, new both skipped; no fabricated bundle

- P01701-PREP-011 / completeReusedBackup/completeBackup/failBackup/observeBackup/retainedBackupSuccessful / PT-OPS-MDB001-008: exact expected current pair, dedicated active owner+advisory, confirmed complete before finished; failed pair commit/readback and matching commandfailure timestamp; observe read-only rollback/restore, prior values separate from current, no missing row interpreted successful

- P01701-PREP-012 / recheckConsistent/requireAbandonedRequest / PT-OPS-MDB001-008: postbegin same run/cutoff/advisory, server READ ONLY actual TX, source readonly flags honest; old same-run request must predate current pair and match2 FAILED/ABANDONED lower attempts+JSTdate/time, not delete/repair or infer original from DB

- P01701-PREP-013 / handoffCleanup/handoffExpiry/beginExpiry / PT-OPS-MDB001-008: one synchronous InspectorLockHandoff, no DB operation while inHandoff and guard afterward; cleanup verification before expirybegin, existing backup/run binding, confirmed commit then independent readback and exact prior/initial audit; no retry minting

- P01701-PREP-014 / failedBackupSnapshot/observeExpiry/observeCleanup/observeCleanupRejected/cleanupReferences / PT-OPS-MDB001-008: whole actual fourteen-column audit/receipt0-10 or narrow30 profile, former original lookups separately bound, borrowed guard/deadline before/after and readback rollback; rejected partial30 is not completion, unknown/null/foreign rows refuse

- P01701-PREP-015 / query/present/require/closeReplace/known-catalog catches / PT-OPS-MDB001-008: nonnull provider Statement/ResultSet, querytimeout5 and boundSQL, reverse direct close1, SQL vs unknown primary precedence and no self-suppression; wrapped Error before known catalog discard remains open BUG2852, no assumption of actualDB post success

- P01701-PREP-016 / replace / JDBC2757001..008: pure priority only, no close/TX: null primary or SQL primary+nonSQL cleanup replaces; unknown primary identity plus fresh fixed secondary, SQL pair finite graph before discard; actual oldwhole8 original currentbytes and ownCRC proof only, no caller/DB/global transfer

P01701三子の原/1として全4Main2457行を公開source review、originmainSS341343332333352と16独立contract群に対応。M/root/policy→原本/DB→stop8→A→fresh8→同activationINVALID→publication/completionのscope、dedicated DBURL/role/advisory/thread/expiredcapability/TX/14列/backupとcleanup/Expiry readback/typedclose/null/refusalを分離。whole候補3は19+6+65=90定義、Root/DB/原本/permit/native実経路依存でHOLD未実行、抽出0。pure JdbcResourceFailures旧whole8 PG28380は旧sourcef5d3の全8inputhashが現byte同一で限定参照、再演0/別caller・globalへの転用0。Morning既SQL catalog変換20siteと独自connectioncloseのfatal graph残をBUG2852/YKT2359へ修正前起票PG29726、typedIO/未知を一括変更せず詳細適用確認・source/独立PTは未完。新PT/Main/Test変更0、旧SQL/実DB/Root/VM/native操作0。原3/1 .315/.786/1.575のみ、3/2/F02F03/451/元190新0/正式1964-53/工数NULL。 BUG2853説明ID誤記は原PG29724を保持してPG29730で元TestsourceのJDBC2757001..008へ追記訂正、他field/実結果不変。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1941b_original_subdivided_artifact_contract_stage.py audit evidence/01_PT/018_NK-OPS-001/input/2387_p01701_audit_contract.json` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。
