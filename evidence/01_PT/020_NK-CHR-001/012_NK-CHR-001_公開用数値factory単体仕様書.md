# NK-CHR-001 公開用数値factory 単体仕様

GateCli#baselineNumericMetadata とBaselineNumbers、RD SCP001/004,MIG002/006,TST001～005/103、UI264/SS355、411/451、736/737、BUG2277/YKT2022/YKT2020。factoryだけ通常PT、actualpromote/copy/FS後条件はHOLD。

独立literal59627/19240707190/1187、非負Long0/MAX・正int1/MAX、null/missing/type/fraction/wrap/negativeとconstructor不変・own2threadを検証。Source/BrowserはownJsonNodeのみ、productionでexpected生成0、実data/read/Path/CLI/publish操作0。

|Test ID|class/method|
|---|---|
|PT-CHR-NUM001|BaselineNumericMetadataTest#fixedAndBoundaryValuesStayExactAndInputsRemainFrozen|
|PT-CHR-NUM002|BaselineNumericMetadataTest#missingAndNullDocumentsOrFieldsNeverBecomeZeroDefaults|
|PT-CHR-NUM003|BaselineNumericMetadataTest#invalidScalarKindsFractionsOverflowAndNegativeNumbersAreRejected|
|PT-CHR-NUM004|BaselineNumericMetadataTest#primitiveRecordConstructorEstablishesRangeInvariants|
|PT-CHR-NUM005|BaselineNumericMetadataTest#concurrentIndependentValidAndInvalidInputsPreserveTheirOwnResults|

先に旧三coercionを737と同値抽出したfactoryへ新5全methodをoriginalred、then typedreader PG/record invariants/build/static/sourcefreeze→新5＋旧関連55=60unique/10class。newrecord追加で全Mainphysical10を分母に含める。Source/正常jar全classCRC/単exec/session/元XML/六publicresourcesを独立postし、旧exec合算/除外0。record compiler既定filterは変更しない。constructorは実domain不変を持ち、値/例外のassertはfactory出力契約でgetterだけのcoverage目的試験ではない。

実command/環境/JDK/tool/対象source/日時/coverage/原red/BUGとhashは013結果/manifestへ保存。順序はPG/REVIEW_STATICで全copy/writeの位置を明示するが、actualpublisherPASS又はatomicity保証に変えない。全Root/baseline/native/CHR/451/親受入は未更新。
