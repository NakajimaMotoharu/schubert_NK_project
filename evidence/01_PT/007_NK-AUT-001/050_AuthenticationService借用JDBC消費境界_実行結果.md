# AuthenticationService借用JDBC consumer 実行結果

固定試験source `1349b86209a707abde09ed7b32dbf3b8c462a9a2`、Production CoreMain `7aed8eace7c844c2f79f2e39db766faf914890d5`。初回PG23800の16件、failure/error/skipped/aborted各0、真正終了0。再実行0。独立PG23816終了0。正式1964PT/53scope、新規leaf0、工数完成率nullは不変。

対象全written CodeはAuthenticationService一physical、constructor二・authenticate/retry/clinitの5method。L54/M5/C1/B24すべてmiss0。normal22084の全SourceFile/physical SHA・独立CRC64・単一exec/session・固定source入力の全一致。旧exec合成/手動除外0、helper全体資格0。

実行command：`PYTHONPATH=tools/quality python3 -B evidence/01_PT/007_NK-AUT-001/input/018_authentication_memory_port_qualifier.py run 1349b86209a707abde09ed7b32dbf3b8c462a9a2`。独立command：同020。JDK25.0.4、JUnit1.13.4、JaCoCo0.8.15、OS/JDK実値・全stage command/exit/hashはmanifestと公開originalログ/XMLへ保存。

独立manifest：`evidence/01_PT/007_NK-AUT-001/evidence/PG23816-authentication-memory-port-independent-v1/manifest.json` SHA256 `16d8ffd9c4e0be2e2afe54608b0a4a7b7c1844739982baea5643f952190fea1b`。共通OPS支援preflight `evidence/01_PT/018_NK-OPS-001/evidence/PG23798-authentication-memory-port-preflight-v1/manifest.json` SHA256 `c44fdb4abb1a6a131f8b6319afa212cfd47be3e4a690080e8d2a83ed72eec584`。原run/begin・正常compile/静的・全artifact SHAは両manifestへ結合。

期待値は049とorigin/main42450 SS314/332の固定counter/time/identity/SQL後条件・明示JSONを独立記述。Productionをexpected生成に使わない。8つのoracle変異（retry/ceil/counter/消去/close/audit display/oldest/別actor）をsource否定として拒否。

| Test ID | 実method | 秒 | 結果 |
|---|---|---:|---|
| PT-AUT-MEMPORT001 | memory001ConstructorsRejectMissingDependenciesAndDefaultCheckerIsConstructionOnly() | 0.01 | PASS |
| PT-AUT-MEMPORT002 | memory002UserSuccessPreservesNormalizedDisplayAndBorrowedTransaction() | 0.003 | PASS |
| PT-AUT-MEMPORT003 | memory003AdminIdentityComesFromTheOwnedRow() | 0.002 | PASS |
| PT-AUT-MEMPORT004 | memory004AbsentAndDisabledAccountsUseDummyWorkAndOneCommonFailure() | 0.002 | PASS |
| PT-AUT-MEMPORT005 | memory005WrongActivePasswordUpdatesBothCountersWithoutIssuance() | 0.001 | PASS |
| PT-AUT-MEMPORT006 | memory006UserFiveAndIpTenLockOnThisAttempt() | 0.002 | PASS |
| PT-AUT-MEMPORT007 | memory007ExistingLocksUseMaximumWithoutCheckerOrMutation() | 0.002 | PASS |
| PT-AUT-MEMPORT008 | memory008FractionalRetryCeilsAndCapsAtNineHundred() | 0.001 | PASS |
| PT-AUT-MEMPORT009 | memory009ExpiryEqualityPermitsCheckWhileWindowEqualityStillAccumulates() | 0.002 | PASS |
| PT-AUT-MEMPORT010 | memory010NullAndInvalidInputsNeverSkipPasswordConsumption() | 0.003 | PASS |
| PT-AUT-MEMPORT011 | memory011CheckerFailuresMapOnlyDeclaredCatalogAndPreserveDirectFatalIdentity() | 0.003 | PASS |
| PT-AUT-MEMPORT012 | memory012JdbcReadUpdateAndResourceFaultsFailClosedWithoutOwningTheConnection() | 0.125 | PASS |
| PT-AUT-MEMPORT013 | memory013CriticalAuditFaultAndNestedFatalNeverReturnSuccess() | 0.003 | PASS |
| PT-AUT-MEMPORT014 | memory014ThirdSessionDelegatesOldestRevocationWithSeparateSafeAudit() | 0.028 | PASS |
| PT-AUT-MEMPORT015 | memory015RepeatedConsumerCallsKeepCallerRowsAndPasswordsIndependent() | 0.002 | PASS |
| PT-AUT-MEMPORT016 | memory016TwoOwnedFiniteTasksUseSeparateBorrowedConnectionsAndConsumeEachArray() | 0.007 | PASS |

User5/IP10、窓終了一致/strict超過、lock終了一致、ceil/cap、存在/disabled/unknown/null、成功と失敗/監査、password全exit消去、借用Connection lifecycle禁止、返却PS/RS各一close、DIF016 delegate最古一件、別caller独立と二owned有限taskを確認。実DBのtransaction commit・locking競合・realSession/Login性能/IT-STは未実証。

六module Main静的22086とMain compile22084はsource不変を結合して再利用。Test compile23806 lint-Werror0、rawPMD8は記録を抑制せず個別適用性を23798へ保存：standalone有限task3、crossworker synthetic observation volatile1、callerごとNULL許容map3、標準JDBC Proxyのdefiningloader1。適用指摘0、CS0、未分類0。

BUG2499/YKT2237：初23796raw11の三duplicate群は23802へbefore保存後、DENIED/reason/resultCode全箇所を同値定数化。他token完全逆一致、初16と8否定で有限CLOSED。BUG2500/YKT2238：preflightのcleanup呼出数19推定は実22と不一致で起動前guard1、23814へbefore保全。実22・二caller追加各一・16Test/28Main/31physical/PMD8件内訳3-1-3-1を観測して訂正、独立post再確認。いずれもfix commit1349b86209a707abde09ed7b32dbf3b8c462a9a2。

実DB/driver/backend/HTTP/Login/Root/VM/FFM/cohort/intent/permit/keys file/held4初期化は0。全key/password/contextはown synthetic・未発行、raw値を証跡へ保存しない。元DBTest/fixture805行はcompile-run抽出0でwhole HOLD。既Caddy18844/Audit20448再演0。

群4372→4373：開始見積2/5/9pp cap10不変、共有観測1pp、配賦実費/実token N/Tは不明null、原計画/再認証/追加/手戻りを同一視しない。暫定追加unique501→517、Java397→413、候補113→114/pending11→12。正式認定・工数率へ転用0。通常自走を継続する。
