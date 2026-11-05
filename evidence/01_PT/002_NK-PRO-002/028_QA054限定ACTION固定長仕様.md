# QA054 WLGEVT01限定ACTION 単体テスト仕様

Program NK-PRO-002 / WebLogEventData, LayoutFieldCatalog, PayloadCodec, PayloadSemanticValidator。RD FUN-008/MON-003/MQ-025..029/TST-004、UI235/252/264、SS312/323/324/351/355、QA054/UIC011/SSC336/main f6df0102f。

PT-PRO-QA054-001..012はWebLogActionContractTestの@Test順ではなく、各method先頭commentで一意対応する。実行前fixtureはInstant 2026-11-05T00:00:00Z/固定公開UUID/loopback/USER、秘密・実session/keyなし。期待payloadはUI235のbyte offsetをliteralで配置した2080byteの独立vector。header256を含むlayout total2336、64layout集合と旧REQUEST golden hashを維持する。productionでexpectedを生成しない。

正常REQUEST旧constructor/省略action/明示action、限定ACTION MENU_VIEWED、全未知/他category・交差action・ACTION省略/blank・NFC/byte超過/型/null/metadata境界、typedrecord fieldroundtripと全constructor null、二ownedworker独立、redactionを検証する。codec汎用TEXTとnamed semantic責務を区別し、欠落・未知・不正を正常扱いしない。旧golden fileの期待hashは変更しない。

試験は既存許可済host JDK heapとowned fixture/一時出力のみ、実DB/JMS/VM/Root/鍵/拒否対象/held四classを実行しない。変更Mainはfresh normal六module compiler/NullAway、そのJARに対するselected protocol compile/JUnit/JaCoCo/CRC/同exec/counter/XML/終了codeを結合する。全source四counter不足は不足のまま報告し、追加test又は根拠ある是正を行い抑制しない。静的/coverage/manifestと対象commit/環境/command・TestID・hashは結果029へ保存する。現時点NOT_RUN、global451/CHR/native/正式受入未完。

|Test ID|class.method|主期待値|
|---|---|---|
|PT-PRO-QA054-001|WebLogActionContractTest.legacyRequestMatchesIndependentOriginalBytes|旧REQUEST独立2080byte/64layout/2336byte|
|PT-PRO-QA054-002|WebLogActionContractTest.menuActionMatchesIndependentOffsetsAndRoundTrips|MENU全offset独立vector|
|PT-PRO-QA054-003|WebLogActionContractTest.explicitRequestActionKeepsItsOwnClosedPair|明示REQUEST同byte|
|PT-PRO-QA054-004|WebLogActionContractTest.everyOtherCategoryIsRejectedByNamedBoundary|他category拒否|
|PT-PRO-QA054-005|WebLogActionContractTest.crossedAndUnknownActionsAreNeverNormalizedToSuccess|交差・未知action拒否|
|PT-PRO-QA054-006|WebLogActionContractTest.omittedActionIsAllowedForRequestOnly|REQUEST省略だけ可|
|PT-PRO-QA054-007|WebLogActionContractTest.missingBlankUnknownAndWrongCaseCategoryFail|category欠落/未知/大小文字拒否|
|PT-PRO-QA054-008|WebLogActionContractTest.nfcAndExactUtf8ByteBoundaryHaveIndependentExpectedBytes|NFCと512/513byte境界|
|PT-PRO-QA054-009|WebLogActionContractTest.everyCanonicalConstructorReferenceRejectsNull|14参照null契約|
|PT-PRO-QA054-010|WebLogActionContractTest.existingHttpMetadataAndReservedRulesRemainEnforced|HTTP必須・path・Reserved不正拒否|
|PT-PRO-QA054-011|WebLogActionContractTest.independentConcurrentCallersDoNotMixCategories|二ownworker混線0|
|PT-PRO-QA054-012|WebLogActionContractTest.recordFieldsAreCompleteImmutableAndRedacted|全field/immutable/redaction|
