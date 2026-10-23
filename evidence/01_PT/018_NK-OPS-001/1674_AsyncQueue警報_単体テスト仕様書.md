# 1674 Async Queue警報 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS351§7/PG-D550/group1891。AsyncQueueMonitor.observe/snapshot/constructor・Evaluation constructor/生成6method。既asyncQueue BigInteger threshold→ASYNC_QUEUE/API lifecycleのpure結線のみ、実queue/capacity/source/owner/集計・9001制御/削除/通知/実JMS/DB/Root等操作0。

| Test ID / asyncQueue method | 独立入力・期待値 |
|---|---|---|
| ASYNCQUEUE001 / 001KnownNormalAndMissingRemainDifferentWithoutInventedEvents | 全既知4999/100000でnormal、両unknown/queuedのみ0/capacityのみ100000を個別present flags保持・新event0 |
| ASYNCQUEUE002 / 002ExactAbsoluteAndRatioBoundariesUseIndependentGoldenValues | 69/100 normal・70/100 warning・89/100 warning・90/100 critical、699/1000～900/1000/7-9/10/1-1、absolute4999/5000/8999/9000/MAX（高capacityでも絶対閾値）、全固定severity。queuedのみ4999/5000/9000/MAXはunknown-no-event/warn/crit/crit、capacityだけ1/100/MAXはunknown-no-event |
| ASYNCQUEUE003 / 003UnknownAndPartialLowEvidenceBreakNormalRecoveryWithoutClosing | warning0/normal1→unknown180/片unknown181・182→normal200/499→500で全5分後初close、旧event immutable/count1 |
| ASYNCQUEUE004 / 004CriticalStaysStickyUntilTenNormalMinutesAndConfirmedCause | critical0→warning1でもcritical/count2・normal2→602原因未確認open→603確認済close、first0/last1保持 |
| ASYNCQUEUE005 / 005ExplicitGapCannotBridgeTheFiveMinuteNormalWindow | warning0/normal1→300 explicit gap、599open/600close |
| ASYNCQUEUE006 / 006InvalidInputsAndReversedElapsedCannotMutatePriorEvent | null optionals/context・queued-1/capacity-1/0（queued未知でも0capacity拒否）/elapsed逆行、旧event同一・正常6→306で復旧 |
| ASYNCQUEUE007 / 007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts | 64同owner5000/9000・高capacity/同elapsed0、最終critical/count64、別ownerwarning/count1不変 |
| ASYNCQUEUE008 / 008GeneratedEvaluationContractsHaveIndependentFieldAndPlatformOracles | record各bool/Optional差・self/同値/null/他型・両bool値accessor、空hash1221152とEvent JDK identity加算・固定全fieldtext/nullOptional拒否 |

expectedは固定有理数/絶対閾値/明示時系列/JDK Boolean-Object identity31foldから独立作成し、production threshold/lifecycle/record methodをexpected生成に使わない。capacity未知のLong.MAX_VALUEはratioの保守的lower-boundでOR異常だけを認定するため、両側presentでなければ正常復旧0。既知容量は正、count非負、capacityを超えた既知countは既threshold通りcriticalで範囲外正常化0。mode-neutral health kernelとして詳細metricがないSTDでも使用できる。実source/正規組合せ/時計・原因flag真正性は未受入。

新8＋必要既Batch184→当192PT26suite/全53Java・実46＋metadata1予定、元184の成功や歴史API98/Web27のcounter合算0。run7504/独立7506/正常六compile7508/全Jar7510/trace7512/review7514、環境/branch/source/command/time/exit/input/output/XML/四100/static/BUG/hashは原manifestと結果へ結合。新生成6＋既66を当ordinary契約/実byteへ結合し分子へ加算0/除外追加0。初期draftのOptional型残りは実行前読取/静的整形時に是正、Production/期待値緩和0。原-v4-v5/群2-4-8pp上限10固定・元製造8/既184再資格/toolを分離、正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/native/CHR/actualHOLD不変更。
