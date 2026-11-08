# 型catalog十二method・P00102全20Sourceの参照結合

G13.07 ORIGINAL_PLAN原0.5/1.5/4cap5、P00102追加費0。Main7aed/Test64f3/normal24642元120実結果を保持。PG24730順0/3834c90f→24732独立逆0/92e415a1fc5c04e21a5c97ba636c399ee39acff1a0fdbf037c4de2a007e82ec4、7誤metadata反証。PayloadTypeCatalog一Source/三class、25raw=12公式測定+record生成12/空privatector1の標準filter13。実Test六case（独立directional wrapperを含む）/元helper Sourcehash/固定SS323 class表・296component独立期待・不正型/null/optionalをmethodへ結合。wrapperのassertはhelper内であり、当methodに直接assertがあると偽らない。

|class.method|descriptor|実Case参照|静的責務経路|
|---|---|---|---|
| PayloadTypeCatalog$Mapping.<init> | `(Ljava/lang/String;Ljava/lang/Class;Ljava/util/function/Function;Ljava/util/Optional;)V` | C1,C2,C3 | mapping factories -> new Mapping |
| PayloadTypeCatalog$RecordMapping.<init> | `(Ljava/lang/Class;Ljava/util/function/Function;)V` | C1,C2,C3 | repeatingmapping factory -> new RecordMapping |
| PayloadTypeCatalog.decode | `(Ldev/codex/schubert/nk/protocol/layout/PayloadValues;)Ldev/codex/schubert/nk/protocol/layout/TypedPayloadValues;` | C1,C3,C4,C5,C6 | Tests directdecode -> require/mapping dataDecoder/decodeRecords/PayloadSemanticValidator |
| PayloadTypeCatalog.encode | `(Ldev/codex/schubert/nk/protocol/layout/TypedPayloadValues;)Ldev/codex/schubert/nk/protocol/layout/PayloadValues;` | C1,C3,C4,C5,C6 | Tests directencode -> require/validateRecordTypes/PayloadSemanticValidator |
| PayloadTypeCatalog.dataType | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;)Ljava/lang/Class;` | C2,C5,C6 | C2 originalTSV expected -> dataType |
| PayloadTypeCatalog.recordType | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;)Ljava/util/Optional;` | C2,C3,C5,C6 | C2 originalTSV - orclassname -> recordType |
| PayloadTypeCatalog.decodeRecords | `(Ldev/codex/schubert/nk/protocol/layout/PayloadValues;Ljava/util/Optional;)Ljava/util/List;` | C1,C3,C5 | decode -> decodeRecords |
| PayloadTypeCatalog.validateRecordTypes | `(Ljava/util/List;Ljava/util/Optional;)V` | C1,C3,C5 | encode -> validateRecordTypes |
| PayloadTypeCatalog.require | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;)Ldev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog$Mapping;` | C2,C5,C6 | decode/encode/dataType/recordType -> require |
| PayloadTypeCatalog.mapping | `(Ljava/lang/String;Ljava/lang/Class;Ljava/util/function/Function;)Ldev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog$Mapping;` | C1,C2,C3 | STANDARD staticinitializer -> overloadedmapping -> Mapping/RecordMapping constructors |
| PayloadTypeCatalog.mapping | `(Ljava/lang/String;Ljava/lang/Class;Ljava/util/function/Function;Ljava/lang/Class;Ljava/util/function/Function;)Ldev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog$Mapping;` | C1,C2,C3 | STANDARD staticinitializer -> overloadedmapping -> Mapping/RecordMapping constructors |
| PayloadTypeCatalog.<clinit> | `()V` | C1,C2,C3 | STANDARD Map.ofEntries calls mapping factories; C2 independentlycompares64 |

実Caseと独立期待：

- C1：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#allNamedTypesHaveIndependentDirectionalFieldMeaning() / PT-PRO-001-T02,PT-PRO-002-P04。Existing IndependentNamedFieldOracle.verifyAll ownsassertions: independentexplicitgetter-field bindings andfixedscalar values/SS/UI296component table; decode/getter andencode/fields checked separately, notProduction-generated expected.
- C2：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#explicitCatalogMatchesIndependentSs323NamedTypeFixture() / PT-PRO-001-T01。SS323 independent64row named-types TSV expecteddata/record classnames; missingrecord indicatedliteral -, total64.
- C3：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes() / PT-PRO-001-T02,PT-PRO-002-P04。Generic minimuminput supplies64layouts,69distinctnamedtypes/14repeat; returneddata/record class andredaction; roundtrip consistency supplementedbyC1/C2 independentdirectional/table oracle.
- C4：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#optionalFieldsSupportUnsetAndPresentValuesWithoutLosingWireNames() / PT-PRO-001-T02,PT-PRO-002-P05。ExplicitGame code unset vsNUKITASHI1 preserved, typeddiagnostic excludesinput; separateC1 preventssole roundtrip oracle.
- C5：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes() / PT-PRO-001-T02,PT-PRO-002-P05。UnknownZZZREQ01 andwrongdata/recordtype, unexpectedrecordsinrecordlesslayout rejected bytypedexception.
- C6：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#typedModelsAndHelpersRejectNullMissingAndWrongKinds() / PT-PRO-001-T03,PT-PRO-002-P05。Explicitrequiredtext safe/numeric7/flagtrue/unset/optional contracts, nullvalues/catalog refs/typedmodel invariants rejected; sharedTypedFieldValues methods haveotherowner andnoacceptancecredit.

全行/hash/要件は[method-trace](../018_NK-OPS-001/evidence/PG24730-typecatalog-method12-trace-v1/method-trace.json)。L176M12C3B18/I844全miss0は元XML subset参照・新測定0。型別変換の意味はC1既独立getter/field期待とC2独立class表が補い、往復一致だけを正しさの根拠にしない。元主担当P00102/専有RD空/関連MQ016017不変更。

## P00102全20Sourceの参照結合

24732の[p00102-all20-reference-summary](../018_NK-OPS-001/evidence/PG24732-typecatalog-method12-trace-independent-v1/p00102-all20-reference-summary.json)は既24694/24706/24718と当型catalogを別runの実測unionなしで結合した参照表である。20/20元ownedArtifacts・29物理class・22測定class/84/84公式methodのJVM signatureを現XMLへ非重複照合。raw174=測定84+標準生成filter85+抽象5、annotation3/marker1/抽象interface1/compiler2を人工class100へ換算しない。元normal120の実Case参照は重複を除き16、旧Carrier6や旧sourceの合格を加算しない。参照counter L564M84C22B170/I3034全miss0は元単一normal120の部分集合で新coverage測定0。

WBS485/486へcurrentP00102MethodReferenceTrace20261109を同一観測として追記し、PG24734で旧全値不変更（486rootinventoryhashだけ現485へ整合）/既guard580/誤hash・型・重複4反証を確認。参照結合完成をSource登録/ownerの品質受入/全G13/451へ変換しない。個別case probe帰属null・全分岐独立oracleの個別完了は未主張。

新製品PT/PASS/Java/compile/Analyzer/coverage/leaf0・unique520/正式1964-53/工数null/全HOLD不変更。工具失敗0、元成功確認再演0。

BUG2552/YKT2276補足：現component期待数は296。旧295を含む1197だけ文字置換し、3902（旧数記載0）は必須補足のみ。元3901/781/24730 case説明は歴史byteのまま保持し、PG24744-current-component296-correction-v1/manifest.jsonとnamed-shapes.jsonを必須補足とする。製品・実120・84method/20Source参照・WBS受入/coverage/費用に変更なし。
