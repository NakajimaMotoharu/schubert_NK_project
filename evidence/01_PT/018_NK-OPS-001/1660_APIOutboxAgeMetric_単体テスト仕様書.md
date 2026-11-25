# 1660 API Outbox滞留時間metric 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS331351/PG-D546/group1883。対象OutboxAgeMetricRecorder/constructor/record/missing/snapshot/detailedMetricsRequested/seconds・Ages/constructor/value/生成equals/hash/text/accessor三。未実装の承認済みSS351供給値記録をPG/PT並行追加、TDD未実装は障害へ起票しない。

API store/既OutboxRows.StatusのPENDING/SENT/ERROR閉集合だけ、供給非負Duration三つの完全immutable snapshot→`nk_outbox_oldest_seconds{store=API,status}`三gauge。UNKNOWNはNaN/真zeroとは別、STD詳細登録保持0。DB/時計/最古row算出・空集合の意味はここで推測せずcaller未受入、Web store・dispatch・再送・制御・実VM等操作0。

| Test ID / method outboxAge対応 | 目的・入力・独立期待値 |
|---|---|
| OUTBOXAGE001 / 001CanonicalUnknownSeriesDoNotClaimObservedZero | DEBUG初期3gauge/固定名・型・二key・API/三status・NaN/借用registry close0 |
| OUTBOXAGE002 / 002ExactFractionalSecondsAndSuppliedSnapshotAreIndependent | supplied1.5s/1ns/300s→実SDK1.5/0.000000001/300、三typed値/同snapshot保持 |
| OUTBOXAGE003 / 003ZeroMissingRecoveryAndMaximumDurationNeverOverflow | 0→missingNaN→max秒+nano復旧、Duration秒Long.MAX_VALUE+nano999999999はbinary64固定0x1.0p63、原Duration/旧zero不変 |
| OUTBOXAGE004 / 004StandardRegistersAndRetainsNothingButChecksNull | STD登録保持0、明示null拒否 |
| OUTBOXAGE005 / 005NullNegativeAndUnknownModesCannotChangeExistingObservation | 三各null・-1ns/負秒/Long.MIN_VALUE、status/null/record/null/mode null未知拒否、原snapshot不変/固定errorで入力非echo |
| OUTBOXAGE006 / 006OneOwnerPublishesWholeImmutableSnapshotsConcurrently | 64並行2fixture snapshot whole identity/旧値immutable・系列増殖0、別gauge scrape跨同時性を主張しない |
| OUTBOXAGE007 / 007PartialProviderFailureKeepsCallerResourcesAndFailureIdentity | 二回目登録でRuntime/Error元同一throw・一既登録をcaller保持/SDK再試行0/closeはcaller一回 |
| OUTBOXAGE008 / 008SeparateOwnersAndGeneratedValueContractsAreExact | 別owner/1000更新欠測後999と7分離/3series、生成recordのself/同値/null/他型/三field一差・全accessor・hash3045/text固定 |

独立oracleは固定秒値/JDK Duration hash（秒3,5,7/nano0は各3,5,7）と31fold=3045/固定全fieldtext、expected生成に本methodを使わない。生成record六methodは直接契約/生成元byteを別記しcoverage分子へ合成0、標準filter以外除外追加0。constructor/factory invariant/NullAway/negative/全分岐・例外・境界を通常実行。既API72を必要回帰し当80PT10suite、全20Java/実17＋metadata1予定。元72/API/他roleの成功を算術加算せず新source当全実行、元4222/common44確認再演0。

原runPG7448/独立7450/六compile7452/全Jar7454/trace7456/review7458を予定。環境/command/日時/branch/source/exit/XML/coverage/static/input/output/hash/BUGは原manifest・1661以降へ。開始見積2/4/8pp上限10/原-v4-v5不変更、元製造新8と既72再資格/tool費を分離、正式1964/53・原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/native不変更。

BUG-3880／YKT-2997。OUTBOXAGE006の合成SDK registry、固定二cohort、8 worker／64件／10秒を維持。有限workerの終了失敗は元例外の抑制として保持し、registryは後に閉じる。局所二件と独立補助一件、F/E/skip各0。 [PG45488](evidence/PG45488-current-outbox-metric-shared-workers/manifest.json)
