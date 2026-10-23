# 1672 WebLog滞留警報 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS351§7/PG-D549/group1889。WebLogBacklogMonitor.observe/snapshot/constructorとEvaluation constructor/生成6method。既thresholdとWEB_LOG/WEB lifecycleのpure結線だけ、queue/outbox source/合成方法/owner/監視運用/業務制御・実broker/DB/VM/Root等操作0。

| Test ID / webLog method | 入力・操作・独立期待値 |
|---|---|---|
| WEBLOG001 / 001KnownNormalAndMissingRemainDifferentWithoutInventedEvents | 4999件/299.999999999秒の全既知normal、両unknown/件数だけ0/ageだけ0は個別present flagsを保持し新eventを捏造しない |
| WEBLOG002 / 002ExactCountAndAgeBoundariesRaiseWithEitherKnownAbnormalInput | 4999/5000/8999/9000/MAX件と299.999999999/300/1799.999999999/1800/MAX秒、独立固定severity。片側unknownでも既知側warn/criticalなら検出、固定Condition.WEB_LOG/Service.WEB/初回count1/UTC field |
| WEBLOG003 / 003UnknownAndPartialLowEvidenceBreakNormalRecoveryWithoutClosing | warning0→normal1→unknown180/片unknown181/182→normal200/499→500の全5分で初めてclose、旧event immutable/count1/first-last0 |
| WEBLOG004 / 004CriticalStaysStickyUntilTenNormalMinutesAndConfirmedCause | critical0→warning1でもcritical/count2、normal2→602の10分は原因未確認でopen、603確認済みでclose・first0/last1/count2保持 |
| WEBLOG005 / 005ExplicitGapCannotBridgeTheFiveMinuteNormalWindow | warning0/normal1・300のexplicit gapで正常窓を切断、599open/600close |
| WEBLOG006 / 006InvalidInputsAndReversedElapsedCannotMutatePriorEvent | null optionals/context・件数-1/age-1ns・elapsed逆行拒否、旧event同一、後正常6→306で5分復旧 |
| WEBLOG007 / 007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts | 64caller同elapsed0・5000/9000混在、最終critical/count64/first-last0、別ownerwarning/count1不変 |
| WEBLOG008 / 008GeneratedEvaluationContractsHaveIndependentFieldAndPlatformOracles | self/同値/null/他型/各bool・Optional field一差/accessor両boolean値、空hash1221152=31*(31*1231+1231)、非空はEventのJDK identity加算・固定全fieldtext、各null境界 |

期待値は承認閾値/明示時系列/固定severityと独立31fold/JDK Boolean/Object identityで作り、production threshold/lifecycle/record methodでexpectedを生成しない。Eventは既immutableメモリfixtureでObject equals/hash/text非overrideを確認済み、record oracleで本recordのhash/textを使用0。生成6methodは別明示しJaCoCo数値へ加算せず、既GENB7の生成60も当sourceで必要回帰する。

unknownへ内部lower-bound0を渡すのは既thresholdのOR超過だけを評価するためで、正常化ではない。正常復旧は両側presentの場合だけ、欠測/非連続はwindow切断、service key固定・DEBUG限定でないmode-neutral health kernel。実source/集計/時刻・原因flag真正性と通知/制御は未受入、供給scalarから実権限/業務成功を作らない。

新8/必要既Batch176→当184PT25suite/全51Java・実44＋metadata1予定。原run7490/独立7492/正常六compile7494/全Jar7496/trace7498/review7500を固定sourceで実施、環境/branch/source/command/time/actual exit/input/output/XML/four100/static/BUG/hashは原manifestと結果へ。旧176/他role成功の算術合算0/4222-common44確認再演0、原-v4-v5/群2-4-8pp上限10固定、元製造8/既176再資格/toolを分離。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/native/CHR/actualHOLD不変更。
