# NK-CHR-001 metadata JSON 単体仕様

Program NK-CHR-001 / class GateContractValidator#validateEvidenceDocuments、既comparison/source/preflight/review下位段。RD SCP-001/SCP-004/MIG-002/MIG-006/TST001～005/TST103、UI264/SS355、451/411、728/729、BUG2275/YKT2020。metadata整合性の単体であり、fixtureのPASS/APPROVED/0600/freeBytes等を実検査・実承認・権限認定に使わない。

入力はTest内独立literalと六publicresourceのSS既定表、source59/doc18/master59627/19240707190、inventory262/99661/37256/35201/20/129、固定hash、28file比較、0600/loopback列/20GiB、unit-onlyreview6bool。expectedをproductionから算出0、実baseline/元report/原本DB/credentials/Root/VM/Browser/CLIへの読取実行0。

|Test ID|class/method|
|---|---|
|PT-CHR-META001|GateEvidenceDocumentsTest#acceptsIndependentLiteralMetadataAndKeepsInputsAndResultsImmutable|
|PT-CHR-META002|GateEvidenceDocumentsTest#rejectsEveryJavaNullBoundaryAndReportsJsonNullWithoutNpe|
|PT-CHR-META003|GateEvidenceDocumentsTest#comparisonCountsAndEmptyDifferenceCollectionsMustBeStrict|
|PT-CHR-META004|GateEvidenceDocumentsTest#sourceAndInventoryCountsRejectCoercionDefaultsOverflowAndNegativeValues|
|PT-CHR-META005|GateEvidenceDocumentsTest#sourceHashesRequireCanonicalTextOnBothSides|
|PT-CHR-META006|GateEvidenceDocumentsTest#preflightMetadataUsesTypedCapacityAndExactStaticMarkers|
|PT-CHR-META007|GateEvidenceDocumentsTest#reviewMetadataRequiresBooleanChecksAndTypedRoleWithoutGrantingApproval|
|PT-CHR-META008|GateEvidenceDocumentsTest#statusMarkersAndRepeatInventoryCannotSubstituteDifferentEvidence|
|PT-CHR-META009|GateEvidenceDocumentsTest#concurrentFrozenFramesKeepTheirDiagnosticsIndependent|

正常/不変/JavaNull全7Node＋String1/JSONnull、比較2count stricttype/emptydiff3配列、source4とinventory6全型・負・Long境界・bothdefault/observedonly不正、SHA canonical text、capacity20GiB±1/LongMax/型、review bool6とrole/evidence、全status拒否/全inventory差、own有限2thread並行を検証する。各negativeは固定診断codeをassertAllし、別の失敗だけで対象契約を満たしたとしない。count0/LongMaxは型境界のsynthetic期待で、Current実datasetの期待値を変更しない。

まず旧helper本体を729同値で純粋入口から呼ぶrefactor版に新9全methodを実行し、型仕様の原redを保存する。未実装pure入口の初期PGを、元5669 sourceの成功と偽らない。次に型guard PG→build/static→新source固定→正常artifactの新9＋必要旧38=47unique/8class、単exec/session/全9physical/全publicresource/source/元XML/CRCを独立照合。保留PTをsubset実行・代替PASSするものではない。実run/baseline後段/CLI3/親P02001/451/正式認定は未更新。

環境は既JDK25.0.4/Maven3.9.12/JUnit1.13.4/JaCoCo0.8.15、実command/日時/対象commit/原red/正常XML/coverage・関連BUG/証跡hashは009結果とmanifestに保存する。wholeGateContractValidator未達を含めて報告し、除外やexec合算0。metadata段に送信/再送/transactionなし、実経路再送は別の承認済み残依存。
