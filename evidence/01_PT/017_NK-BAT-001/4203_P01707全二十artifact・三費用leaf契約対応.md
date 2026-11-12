# P01707 business-technical削除の全二十artifact・三canonical費用leaf対応

NK-BAT-001。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG28310](../018_NK-OPS-001/evidence/PG28312-p01707-all-twenty-contract-v1/manifest.json)。

- P01707-ORACLE01 / CleanupStopReason.values/valueOf / BAT021..029: 固定LOCK_BUSY/BACKUP_GATE/TIME_LIMIT/INTERRUPTED/DATABASE_FAILURE。停止理由を成功完了や別runへ補完しない。

- P01707-ORACLE02 / CleanupStoppedException.constructor/reason / BAT021..029: 非null固定reason/固定message・raw JDBC cause値を保持しない。未知NPEをcatch正常扱いしない。

- P01707-ORACLE03 / LogCleanupService.constructors/withOwner/execute/check/transaction/owned/replace/known/SessionLease.acquire-close / BAT018..029,LOGTX337001..019: SS3417.2/SSC337: 借用親autoCommittrue/固定runと既owner、advisory71419602/0..10000chunk→永続progress ENDまでcommit・復元・leaseclose後だけsummary。chunk前後30分(負elapsed/1.8e12境界)/割込保持、同run継続は累積delta・commit済unknownをrollbackと偽らずdiscard。未知primary優先・knownprimary+unknowncleanup優先・selfsuppression禁止、rollback失敗復元0/connectionclose0。BUG2751既知五catalog未分類、元実DB wholeTestHOLD、旧純JDBCport19はfullclosure前で転用0。

- P01707-ORACLE04 / LogCleanupSummary.constructor/attemptCounts/exitCode/toString / CLEANVALUE003..006,BAT018..020: 同run/END必須/各累積非減少、試行はafter-before。独立固定before3/1/2→after10/5/5は7/4/3、同END再送delta0でも累積skipありexit10、保護0だけ0。MAX境界/全null不正・counts自体の不変条件により減算overflow無し。

- P01707-ORACLE05 / StepCleanupService.constructors/withOwner/execute/transaction/check / BAT170..177: SS3313.14/332/341: mapping/parentRW-RC-autoCommittrue、元budget/owner前後・1000ずつ同DELETEと累積atomiccommit。chunk0と実候補0だけ完了、QUESTIONS FKdeferredは非完了warning、savedbefore一致/未知commitは未完了でdispose。mutation入口拒否はrollback0、rollback失敗復元0、unknown primary/cleanup型優先保持。BUG2751既知三catalog未分類、実DB wholeHOLD。

- P01707-ORACLE06 / StepCleanupSummary.constructor/callCounts/complete/toString / BAT154..161,BAT170..177: mapping/LOGS除外、before/after skipped0、非減少target、deferredはQUESTIONSだけ。delta2=5-3、MAX-0/同MAX=0、deferred≠END。全null/不正値/固定redaction、purewholeStep8候補の独立literalを参照し実DB結果を捏造しない。

- P01707-ORACLE07 / CleanupWorkerRequestFiles.allconstructors/forStartup-prepareStartup-readStartup/forFailure-prepareFailure-readFailure-retireFailure/forOwner-prepareOwner-readOwner-retireOwner/requireOwnerProfile/forExpiry/requireClear/requireOwnedCycle/requireExpiryOwnedCycle/requireOwnedNames/prepare-prepareExpiry-prepareBytes/read-readExpiry-readBytes/retire-retireExpiry-retireBytes/directory/file/guard/write/verify/read / PT-OPS-CREQFILE001..008: SS343固定root0700/root600/同dev-inode-全snapshot/ACL/NOFOLLOW/CREATE_NEW/force-close-readback/no-replace。closedprofile namesからのみ選択しowner2/startup3/expiry/failedを混同せず、不明name/part/Inspector残留は拒否。publish前後namespace/長さ進捗EOF/全ownedwipe、借用root非close、全Unit終端/同owner原本確認なしretire不可。DII二fixed変換BUG2754、actualRoot-native-request-intent全HOLD。

- P01707-ORACLE08 / MorningCleanupExecution.Completion/execute/executeFailed/executeprivate/requireInspectorEnvironmentClear/digest / CEXEC001..004,CFLOW001: SS3417.3: 同parentbudget/M-A/INVALID/boot/run/activation/cutoffと原本、真正Backup結果に一致する固定dataだけ新規公開、親advisoryhandOff一回、実freshchild0/10又は正常拒否30全終端→reacquire→全7step現readback→原本request-owner最後intent退役。拒否30はBroker等0、不存在/RUNNINGをFAILEDで補完0。Root失敗cohortの実回収調査/操作でなく通常設計source対応のみ、native/Root/実owner能力発行HOLD。

- P01707-ORACLE09 / CleanupProfile.consume/encode/run/activation/cutoff / CFREQ001..006,CREQ001..007: sealed二data型のみ/headerdispatch/1..1024/owned全終了wipe、権限ではない。unknownheader/長さ/nullを拒否し勝手な第三型/修復をしない。

- P01707-ORACLE10 / CleanupWorkerRequest.constructor/encode/consume/toString/Expiry-PriorExpiry-constructors-handle-original-priorHandle-encode-consume-toString / PT-OPS-CREQ001..007,EXREQ001..008: NKCLEAN1固定5行+LF/256・nil/同runactivation拒否/µs/year1-9999/小文字hash64・再encode完全一致/全bytewipe。ExpiryはNKEXPIRY1又はNKEXPIRYSKIP2固定12/18行・1024、boot/epoch/broker32nonzero/fullstep id-attempt-start、skipとprior有無一致/別id小attempt/同JSTday/end<=newstart。claimだけでDB/native権限を作らない。

- P01707-ORACLE11 / CleanupChunk.constructor/counts/reason / BAT004/006/010,CLEANVALUE006: non-null counts/reason、拒否reasonではtarget0→counts不変条件で全0、OKは任意整合counts。未commit観測をOS/backup証明へ使わない。

- P01707-ORACLE12 / CleanupCounts.constructor/target/deleted/skipped / CLEANVALUE001,BAT002/010/011: 全非負、deleted<=target、skipped==target-deleted。独立0/1/MAX/MIN/±1と三component不整合、差分は非負MAX以下でoverflow0。

- P01707-ORACLE13 / CleanupDatabaseSession.allconstructors/rootGate-rootGateFor/forExpiry/cleanupSchema-CleanupSchema.verify/execute/check/queryTimeout/admit/scalar/query/present/require/closeReplace / PT-OPS-CDB001..008: 固定loopbackport1..65535/schubert_nkと専用schubert_batch current/session role・非recovery/RW-RC、schema後だけ自己advisory/同namespace自己lock readback、callback同期一回・戻前自己lock保持。credential所有byteとproperties消去/borrowedconnection全close、query5又は元ownerdeadline秒floor、失敗は非成功/未知identity。BUG2752 SQLfatalとfinally実primary bookkeepingは別内部audit待ち、credential/DB/Root実操作HOLD。

- P01707-ORACLE14 / CleanupKind.constructor/function/maximumRows/step / CLEANVALUE002,BAT003/005/009/154: 固定9kindとDDL関数suffixを独立literal配列へ対応、LOGSだけ10000・他1000、固定Step mapping/技術4kind同CLEAN_BATCH_RUN。任意SQLidentifierを受け付けずこのmetadata照合ではSQLを実行しない。

- P01707-ORACLE15 / CleanupReason.values/valueOf / CLEANVALUE006,BAT004/008/010: OK/LOCK_BUSY/BACKUP_GATE三固定、拒否を完了にしない。

- P01707-ORACLE16 / CleanupRepository.constructor/execute/readLogProgress/prepare/requireTransaction/bind/counts/required / BAT005..016,CQUERY001..008: 借用親transaction中だけfixed9SQL・run UUID/UTCcutoff+limitbind、1row全non-null型counts/limitとreason整合・余分row拒否、logprogress END累積の独立読み、全ownedRS/statementclose/connection非操作。DDL/SS332正: 完了-error state_changed<=cutoff-24h、cancelled<cutoff、QST論理削除+通知不存在/FK保護、hold/未完/lease保全。SQLknown二catalogBUG2751。

- P01707-ORACLE17 / CleanupStepChunk.constructor/requireMapping/beforeCounts/toString/Reason / BAT154..161: mapping/LOGSとskipped除外、countskip0、known=OK/FKだけoptional総数あり、拒否count0/END iffOK+count0、FKQUESTIONSのみ、total>=delta。独立delta2/total5→before3・MAX境界・null/unknown/等価性。

- P01707-ORACLE18 / CleanupStepRepository.constructor/execute/counts/present/require / BAT162..169,CSTEP001..008: V020 fixed7parameter/fullhandle+kind+limit1..1000、DBidentity前後、1row/non-null各count・optional累積二項同時存在/complete/reason/余分row0。DELETE+step累積はcaller同transactionでcommit、repositoryはcommit/rollback/borrowedclose0。SQLknown一catalogBUG2751、pure値parseIAEだけSQLDataException。

- P01707-ORACLE19 / CleanupTerminalRepository.Entry/Snapshot/RejectedEntry/RejectedSnapshot/constructor/read/readBackupUnavailable/references/progressSeal/projection/entry/terminal/snapshot/readRejected/rejected/rejectedSnapshot/check/seconds/present/require / CTERM006..009,CEXEC001,ISSSTEP003,REF200001: SS331/341/343: 実receipt後再取得親RW-RC/owner/runidentity、最新7step全14列・順序一意id/run/day/µs時刻/終了reason-summary/count一致。backup失敗は6実SKIP BACKUP_UNAVAILABLEとTransfer独立、旧成功参照は別anchor/同JSTday/小attempt/fullSUCCESS・LogInboxprogress seal、現在SKIPを旧SUCCESSへ改変0。不在/部分/RUNNINGは7optional slotsのまま保持/実query外pureprojectionだけIAE分類。SQL三catalogBUG2751、checkedIOの型規則は別/不変更。全actualDB-Root-HOLD。

- P01707-ORACLE20 / LogCleanupProgress.constructor/run/counts/complete / CLEANVALUE005,BAT004/006/007/011: 非nullrun/countsの未commitprogress値、completefalseをENDに補完しない。同run再送累積固定と試行差分はserviceの責任。

P01707全二十Main3147行を承認RD122NTF006007011/RD123QST009・UI251/SS33211/3417/343へ20oracle対応。485全20owner/costOwner一致/歴史hash差7・候補8Test93canonical method-IDの宣言metadataだけ保持しassertion資格へ転用0。実原票は.01SQL-FK/保持計数・.02資源例外・.03traceの三leaf各/1と/2であり架空parent/1を作らず、初回single-parent helperのrowguard前停止はPG28309に保全・価格/成果加算0、既多leafhelperで正規開始した。全fixedcutoff・通知24h inclusive/取消<cutoff・論理削除+通知不存在/FKdeferred・固定chunk1000/Log10000・durable END/差分と累積・元30分/borrowedclose/unknown複合優先を独立期待へ明示。SS341要約表誤語はSSC339へ修正前起票し設計only二fileをba94f093a03f439423f2a8e4c94716c0358ee7d9でmain通常push/remote確認、RD/UI/SQL/Test oracle不変更・新QA不要。BUG2751known14catalog/BUG2752SQL-primary-finally内部依存/BUG2753virtualworker/BUG2754DII2を修正前起票。pure2+8+4全三TestとJDKMain11は全source確認、元DB/Root/native全HOLD/部分抽出・代替fixture0、currentLogTxは先頭60行だけで閉包・キャッシュbyte資格は未確定。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1941b_original_subdivided_artifact_contract_stage.py audit evidence/01_PT/018_NK-OPS-001/input/2080b_p01707_canonical_split_contract_config.json` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。
