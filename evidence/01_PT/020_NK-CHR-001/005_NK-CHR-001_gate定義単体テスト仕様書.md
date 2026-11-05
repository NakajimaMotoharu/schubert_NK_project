# NK-CHR-001 gate定義JSON 独立単体仕様

Program NK-CHR-001、class GateContractValidator#validateDefinitions と既存full validateの定義段。RD SCP-001/SCP-004/MIG-002/MIG-006/TST-001～005/TST-103、UI264、SS355、品質451/コーディング411。着手720/同値721。独立TestはGateDefinitionDocumentsTest、Current baseline/実run/preflight/レビュー/秘密原本へアクセスしない。

前提fixtureは公開版 six JSONをimmutable snapshot/normalJarへcopy、全input hashをcompile manifestで固定。期待はSS355/UI264の24case/16DIF・狭いselector等と固定失敗code、production methodからexpected値を算出しない。各negativeはown deep-copyへ明示mutationして診断を確認し、単なるcounter目的のassertionを置かない。

|Test ID|class/method|目的・入力・独立期待|
|---|---|---|
|PT-CHR-DEF-001|GateDefinitionDocumentsTest#acceptsPinnedPublicDefinitionsWithoutMutationAndReturnsImmutableDiagnostics|公開6定義の24case/16DIF/Log groupを固定値で確認し診断0・不変list・入力不変|
|PT-CHR-DEF-002|GateDefinitionDocumentsTest#rejectsEveryJavaNullDocumentWithFixedSignal|6位置のJava null全てを固定IArgで拒否、NPE正常化なし|
|PT-CHR-DEF-003|GateDefinitionDocumentsTest#malformedJsonShapesProduceFailuresRatherThanNpe|JSON null/array/textを各6位置で診断非空、NPEなし|
|PT-CHR-DEF-004|GateDefinitionDocumentsTest#allFourVersionCallersRejectCoercionOverflowMissingAndNull|4guard×null/text1/floating1/BigInteger overflow/0/2/missingを拒否、BigInteger1だけ許容|
|PT-CHR-DEF-005|GateDefinitionDocumentsTest#contractCountsOrderIdentifiersAndHashesUseIndependentConstraints|gates/case件数・重複/DIF件数/commit/hashの独立固定診断|
|PT-CHR-DEF-006|GateDefinitionDocumentsTest#schemaDraftShapeAndItemConstraintsCannotBeWeakened|schema draft/type/required/min-max/itemsの緩和を拒否|
|PT-CHR-DEF-007|GateDefinitionDocumentsTest#catalogRejectsDuplicateMalformedUnknownAndShortIdsAndWrongModes|全normal8groupとshort/未知group/重複ID/未知mode/非arrayを検査|
|PT-CHR-DEF-008|GateDefinitionDocumentsTest#everyBrowserConstraintHasAnIndependentWrongValueIncludingSecondaryDimensions|15browser属性を各々単独に誤値へ変更し対応codeを要求|
|PT-CHR-DEF-009|GateDefinitionDocumentsTest#differencesRejectUnknownModesCasesBroadSelectorsDuplicatesAndEmptyValues|未知mode/selectorType/field重複/empty/未知case/重複selector/4broad構文/DIF015欠落を拒否|
|PT-CHR-DEF-010|GateDefinitionDocumentsTest#requirementsRejectMissingCoreKeysDuplicatesUnknownAndUnboundSupplementals|core両key/重複/漏れ/order/未登録補助/empty/unknown nkOnlyを拒否|
|PT-CHR-DEF-011|GateDefinitionDocumentsTest#concurrentValidAndInvalidDefinitionsRemainIndependent|own有限2threadで正常0/異常versionと不変・独立を確認してjoin/close|

PGはfull validate既存six段と後段の同値（721）を保存し、新pure入口のnull/IArgとimmutable戻りだけを明示。classloadはJSON/JDK/own finite executorだけ、FS読取は六public classpath resourceのみ、実Root/DB/VM/Browser/permit/intent/権限/Current baseline操作0。既存wholeCLI/ContractTestの前提を別名で実行するものではなく、新しいpure段を本full gateも呼び、実gateの後段は保留のまま。

正常24は変更frameworkの必要関連回帰、当sourceに新11を加えた35unique/6class全methodで実行前固定。失敗/エラー/skipped/abortedは成功へ含めない。実commandはjava25/JUnit1.13.4 exact --select-class6、通常artifactはPG18704、JaCoCo0.8.15 appendfalse・fresh単session、全9Mainphysicalを分母から除外せず報告。新validateDefinitionsの全条件/nullと既存定義下位branchを確認するが、IO/実gate後段を行わずwholeGateContractValidator100%と予告しない。旧24等とのexec合算0。

実行日時/対象commit/OS/JDK/tool/Input/command/終了code/XML/coverage/CRC/原失敗・hashは後続006結果とmanifestへ固定。現時点PG18704 compile0、11試験は未実行。再送はこのpure定義段に副作用/送信がないため非該当、実再送契約はP02001/他program/CHRの残依存。関連BUG2269/YKT2014の残四versioncallerを本scopeで検証し、realgate受入に変換しない。
