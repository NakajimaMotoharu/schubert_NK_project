# NK-CHR-001 baseline manifest項目 単体仕様

Program NK-CHR-001、GateContractValidator#validateBaselineMetadata と既validateBaseline前半、pureDefinitionsの2count guard。RD SCP001/004,MIG002/006,TST001～005/103、UI264/SS355、451/411、732/733、BUG2275/YKT2020。メモリ上JsonNodeの項目だけ。実baseline manifest/原report/Currentdata/FS/hashwalk/gateCommit/実Root等はアクセス/実行しない。

独立期待はSS355のcurrent/24case/2screenshot/16DIF/Java25.0.4/browser1187/ja-JP/AsiaTokyo、固定Sourcehash/59627/19240707190、public定義の23currentApplicable/27baselinefile。observed fixtureはTest内literal、productionをexpected生成に使用0。

|Test ID|class/method|
|---|---|
|PT-CHR-BMETA001|GateBaselineMetadataTest#acceptsIndependentManifestItemsWithoutMutatingInputsAndReturnsImmutableList|
|PT-CHR-BMETA002|GateBaselineMetadataTest#javaNullBoundariesFailWithFixedSignalAndJsonNullNeverCausesNpe|
|PT-CHR-BMETA003|GateBaselineMetadataTest#manifestCardinalitiesMustBeTypedExactIntegers|
|PT-CHR-BMETA004|GateBaselineMetadataTest#sourceAndDocumentHashesMustBeCanonicalMatchingText|
|PT-CHR-BMETA005|GateBaselineMetadataTest#masterCountsAndBytesRejectCoercionDefaultsAndOverflowOnBothSides|
|PT-CHR-BMETA006|GateBaselineMetadataTest#environmentAndTargetUseExactMarkersAndIntegerBrowserRevision|
|PT-CHR-BMETA007|GateBaselineMetadataTest#concurrentManifestFramesNeverShareMutationsOrFailures|
|PT-CHR-BMETA008|GateBaselineMetadataTest#contractCountsRejectCoercionAndKeepPinnedTwentyThreeAndTwentySeven|

正常/不変/JavaNull2とJSONnull2、3固定件数のtext/fraction/wrap/null/異整数、両側SHA不正、master2fieldの型/負/overflow/0LongMax境界、環境4fieldとtarget、own2thread隔離、2定義countのcoercion/欠落を試す。synthetic境界0/LongMaxは実dataset期待変更ではない。先に旧prefix同値733を新入口で原red、新scopeを元3176の成功と偽らず入力shaで固定。その後PG→build/static→source固定→新8＋関連47=55unique/9class・正常jar/単exec/全9physical/元XML/六resource/sourceCRCの独立post。旧exec合算/除外0、wholeGCV/CLI未達を残す。

実環境とcommand/JDK/tool/時刻/対象commit/原red/正常結果/coverage/BUG/証跡hashは011結果とmanifestで保存。独立pure段の成功を実baseline又は実業務の資格へ変換しない。型是正はYKT2020、物理IO/CLI残はOPEN。現在8Test未実行。
