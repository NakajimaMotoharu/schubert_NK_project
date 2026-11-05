# NK-CHR-001 metric・件数predicate単体仕様

GateContractValidator#gateMetrics/#matchesBaselineFileCount、RD SCP001/004,MIG002/006,TST001～005/103、UI264/SS355、411/451、741/742、BUG2275/YKT2020。JsonNodeと提供されたintだけ、実FS/Root/Fullgateなし。

独立SS値24/23/16/27/0、宣言不正はunknownとしてkey省略（0やnullへ置換しない）、Map不変、JavaNull2と非負数3、caseOrder/differences配列有無、type/fraction/wrap/欠落、件数0/27/MAX境界、own2threadを検証。実際のcount観測はcallerの既存計算/列挙のままでありunitfixtureの数値を実結果に使わない。

|Test ID|class/method|
|---|---|
|PT-CHR-METRIC001|GateMetricsCountTest#validSnapshotUsesExactProvidedCountsAndIsImmutable|
|PT-CHR-METRIC002|GateMetricsCountTest#javaNullAndNegativeProvidedCountsFailWithoutNpe|
|PT-CHR-METRIC003|GateMetricsCountTest#invalidOrMissingCurrentCountIsUnknownAndNeverAZeroOrCoercedValue|
|PT-CHR-METRIC004|GateMetricsCountTest#unavailableDeclarationArraysAreOmittedInsteadOfReportedAsZero|
|PT-CHR-METRIC005|GateMetricsCountTest#baselineCountComparisonRejectsCoercionAndRespectsExactIntegerBoundary|
|PT-CHR-METRIC006|GateMetricsCountTest#concurrentIndependentSnapshotsNeverShareUnknownValues|

先に旧map/predicateを742同値抽出したAPIに新6全methodをoriginalred、then不正宣言省略/typedpredicateをPG。後続はbuild/static/sourcefreeze→新6＋関連60=66unique/11class、正常Main10physical/source/単exec/session/XML/resource/CRCを独立post。旧sourceの60と合算0。wholeGCV/CLI/physicalcallerの未達を分母除外せず、actualsource/runtime許可・後条件を単体PASSに変換0。環境/tool/command/commit/日時/原red/結果/coverage/BUGと証跡hashは015結果・manifestに保存。
