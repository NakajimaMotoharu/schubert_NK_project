# PG381 Expiry genuine child接続（実施中・未認定）

Program NK-OPS-001/NK-BAT-001。RD MQ-009/OPS-009/DAT-009、UI251/253、SS341§9/342/343、SSC111/SSC109、BUG333/YKT264。CleanupProcessMain literal `--expiry`、CleanupWorkerRequest.Expiry、同request file/private reader、CleanupDatabaseSession.forExpiry、既存ExpiryAuditRepository/ArtemisExpiryPurgeClientを対応付ける。

| Test ID | fixture/操作 | 独立期待・根拠 | 状態 |
|---|---|---|---|
| PT-OPS-EREQ001～004 | ExpiryWorkerRequestTest literalNKEXPIRY1/fullhandle/byte変造/null | 12line ASCII LF・全固定field、CLEAN_EXPIRY42/attempt1、入力全消去、NKCLEAN1相互拒否 | 実行中 |
| PT-OPS-EREQFILE001～004 | CleanupWorkerRequestFilesTest expiryFixedProfileNewOnlyReadRetireAndAllResidueIsolation | literalfile byte一致→保持再読→真正caller条件下のretire、part/unknown/oldrequest時はmutation0で次Morning拒否。別profile受理禁止 | 実行中 |
| PT-OPS-EMAIN001～004 | CleanupProcessMainTest expiryLiteralEntryAcceptsOnlyRealOutcomeAndUnknownIsNotNormalized | literal--expiryのみ、実work結果0/10/30、knownIO30、未知NPE/Error同一性、他引数work0回 | 実行中 |
| PT-OPS-EVM001 | 隔離VM外部genuine child、literal old/new Expiry message | stagecommitがpurge前に独立SQLから見える、固定cutoff旧だけ除去/new保持、count/bytes/after・terminalcommit全再読、同Invocation/原本/current不変、全child終端 | 未実行 |
| PT-OPS-EVM002～006 | VM実purge失敗/health/critical/DB再読不明/ALREADY_SUCCESSFUL/残留request | 非critical+freshhealthのみWARNING10、critical/health不明30、unknown afterはNULL、未実行ゼロ捏造なし、既存成功audit+fresh対象0のみresume受理 | 未実行 |
| PT-OPS-EHANDOFF001～004 | 親の同advisory handoff/再取得/全Unit終端・freshreceipt/再読 | M/A保持、二回handoff拒否・UNKNOWN保持・全子終端後のDB監査再読/request最後の退役 | 親結線未実装 |

Child nativeは保持host原本をreadonlyで観測し、private maintenance領域へ広域RWを付与しない。8Unit配置時点はS1の停止対象準備で、Expiryの実成功・正式受入ではない。Native external coverageは同sourceのJaCoCo agent→独立command/source/classbyte照合でhost dataへ統合予定。native code/Unit配置・実purge未実行をhost EMAIN mock結果で合格へ置換しない。実command/source/環境/日時/hash・coverage結果は後続結果/manifestへ固定する。
