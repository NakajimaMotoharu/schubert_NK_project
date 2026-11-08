# 項目catalog七Source・33methodの要件/Test参照

G13.07 ORIGINAL_PLAN原0.5/2/5cap7・P00102追加費0。Main7aed/Test64f3/normal24642元120実結果を参照。PG24704順0/bb25c1f4→24706独立逆0/744f86cebafd04bdfa03e84abce393f467fc1a810dff4ade560fff5e20b1ca29、7型保持metadata否定。全七Source/十物理/八測定class、70raw=33測定+record19/enum16/switchmap2標準filter37。switchmap二classは24594の同classSHA/CRC実証を再利用しbyte再解析/Java初期化0。個別probe帰属null、全分岐独立oracle完成を主張しない。

|class.method|descriptor|実Case参照|静的責務経路|
|---|---|---|---|
| FieldArea.<clinit> | `()V` | F1,C1 | F1 enum.values().length; C1 fixed389field semantics |
| FieldDefinition.<init> | `(Ldev/codex/schubert/nk/protocol/layout/FieldArea;Ljava/lang/String;IILdev/codex/schubert/nk/protocol/layout/WireType;Ldev/codex/schubert/nk/protocol/layout/Presence;Ldev/codex/schubert/nk/protocol/layout/Padding;Ljava/lang/Class;Ljava/lang/String;)V` | F1,C1,C2,C3 | Test field helper/directFieldDefinition -> delegating/canonical constructors |
| FieldDefinition.<init> | `(Ldev/codex/schubert/nk/protocol/layout/FieldArea;Ljava/lang/String;IIILdev/codex/schubert/nk/protocol/layout/WireType;Ldev/codex/schubert/nk/protocol/layout/Presence;Ldev/codex/schubert/nk/protocol/layout/Padding;Ljava/lang/Class;Ljava/lang/String;)V` | F1,C1,C2,C3 | Test field helper/directFieldDefinition -> delegating/canonical constructors |
| FieldDefinition.checkedEnd | `(II)I` | F1 | Both FieldDefinition constructors -> checkedEnd |
| LayoutFieldCatalog$MutableFields.<init> | `()V` | C1,C2 | parse -> computeIfAbsent lambda andgetOrDefault -> new MutableFields |
| LayoutFieldCatalog.<init> | `(Ljava/util/List;)V` | C1 | parse -> new LayoutFieldCatalog(result) |
| LayoutFieldCatalog.standard | `()Ldev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog;` | C1 | C1 direct standard() |
| LayoutFieldCatalog.all | `()Ljava/util/List;` | C1 | C1 all().size/filter/clear |
| LayoutFieldCatalog.require | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;)Ldev/codex/schubert/nk/protocol/layout/LayoutFields;` | C1 | C1 directString/typed require; String delegates typed |
| LayoutFieldCatalog.require | `(Ljava/lang/String;)Ldev/codex/schubert/nk/protocol/layout/LayoutFields;` | C1 | C1 directString/typed require; String delegates typed |
| LayoutFieldCatalog.fieldCount | `()I` | C1 | C1 literal389 -> fieldCount |
| LayoutFieldCatalog.tsvRows | `()Ljava/util/List;` | C1 | C1 originalfixture expected -> tsvRows |
| LayoutFieldCatalog.parse | `(Ljava/lang/String;Ldev/codex/schubert/nk/protocol/layout/LayoutRegistry;)Ldev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog;` | C1,C2 | C1 independentfixture andC2 explicitinvalidrows -> parse |
| LayoutFieldCatalog.appendRows | `(Ljava/util/List;Ldev/codex/schubert/nk/protocol/layout/LayoutId;Ljava/util/List;)V` | C1 | tsvRows -> appendRows |
| LayoutFieldCatalog.parseArea | `(Ljava/lang/String;)Ldev/codex/schubert/nk/protocol/layout/FieldArea;` | C1,C2 | parse -> parseArea |
| LayoutFieldCatalog.parseWireType | `(Ljava/lang/String;)Ldev/codex/schubert/nk/protocol/layout/WireType;` | C1,C2 | parse -> parseWireType |
| LayoutFieldCatalog.parsePresence | `(Ljava/lang/String;)Ldev/codex/schubert/nk/protocol/layout/Presence;` | C1,C2 | parse -> parsePresence |
| LayoutFieldCatalog.paddingFor | `(Ldev/codex/schubert/nk/protocol/layout/WireType;)Ldev/codex/schubert/nk/protocol/layout/Padding;` | C1,F1 | parse -> paddingFor -> FieldDefinition validation; F1 independentpadding checks |
| LayoutFieldCatalog.validateFixedField | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;Ljava/lang/String;Ldev/codex/schubert/nk/protocol/layout/Presence;)V` | C1,C2 | parse -> validateFixedField |
| LayoutFieldCatalog.javaTypeFor | `(Ldev/codex/schubert/nk/protocol/layout/WireType;)Ljava/lang/Class;` | C1 | parse -> javaTypeFor; C1 assertSameclass |
| LayoutFieldCatalog.wireCode | `(Ldev/codex/schubert/nk/protocol/layout/WireType;)Ljava/lang/String;` | C1 | appendRows -> wireCode; independent389 fixture |
| LayoutFieldCatalog.presenceCode | `(Ldev/codex/schubert/nk/protocol/layout/Presence;)Ljava/lang/String;` | C1 | appendRows -> presenceCode; independent389 fixture |
| LayoutFieldCatalog.parsePositiveInt | `(Ljava/lang/String;Ljava/lang/String;)I` | C1,C2 | parse -> parsePositiveInt |
| LayoutFieldCatalog.lambda$parse$1 | `(Ljava/lang/String;Ldev/codex/schubert/nk/protocol/layout/FieldDefinition;)Z` | C1,C2 | parse -> areaFields.stream().anyMatch(existing -> existing.name().equals(name)) |
| LayoutFieldCatalog.lambda$parse$0 | `(Ljava/lang/String;)Ldev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog$MutableFields;` | C1 | parse -> parsed.computeIfAbsent -> new MutableFields |
| LayoutFieldCatalog.lambda$fieldCount$0 | `(Ldev/codex/schubert/nk/protocol/layout/LayoutFields;)I` | C1 | fieldCount -> mapToInt(fields -> dataFields.size+recordFields.size) |
| LayoutFieldCatalog.<clinit> | `()V` | C1 | RETAINED_STANDARD initializer -> parse(CATALOG_TSV, LayoutRegistry.standard()) |
| LayoutFields.<init> | `(Ldev/codex/schubert/nk/protocol/layout/LayoutDefinition;Ljava/util/List;Ljava/util/List;)V` | C1,C3 | Catalogparse/directnew LayoutFields -> constructor |
| LayoutFields.id | `()Ldev/codex/schubert/nk/protocol/layout/LayoutId;` | C1,C3 | C1/C3 directid andcatalogindexconstruction |
| LayoutFields.validateArea | `(Ldev/codex/schubert/nk/protocol/layout/FieldArea;ILjava/util/List;)V` | C1,C3 | LayoutFields canonicalconstructor -> validateArea forDATAandRECORD |
| Padding.<clinit> | `()V` | F1,C1 | F1 enum.values().length; C1 fixed389field semantics |
| Presence.<clinit> | `()V` | F1,C1 | F1 enum.values().length; C1 fixed389field semantics |
| WireType.<clinit> | `()V` | F1,C1 | F1 enum.values().length; C1 fixed389field semantics |

実Caseと独立期待：

- F1：dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#layoutIdAndFieldDefinitionAreStrictAndOneBased() / PT-PRO-001-L02,PT-PRO-001-F01。LiteraluppercaseASCII8, short/lowercase/null reject, ABCREQ01<ABCRSP01, literaltoString; FieldDefinition assertions aredifferentSource references andnotnewcredit.
- C1：dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalogTest#catalogMatchesIndependentUi234To236Fixture() / PT-PRO-001-F02,PT-PRO-001-L03。Independent389row UI234-236 TSV expected,64layouts/fourempty, immutablelist; X/N/B classes literalString/Long/Boolean. standardcatalog andparsefixture both actual againstoriginalfixture, not selfroundtrip only.
- C2：dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalogTest#parserRejectsMalformedUnknownAndDuplicateRows() / PT-PRO-001-F03。Handwritten8column invalid rows,unknownlayout/area/type/presence, disallowedfixedfield, nonnumeric/zero/negative/blank/name/rule,duplicateandgap rejected bytypedexception; nullcontainerprecondition.
- C3：dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalogTest#layoutFieldsRejectWrongAreaGapLengthAndNull() / PT-PRO-001-F01,PT-PRO-001-F03。Explicit1byte DATA field/layout; wrongarea/start2/length2/unusedrecord rejected; returnedlistimmutable/nullcontainer/elements rejected; IDliteral ABCREQ01.

全Source行/hash/実Test body hash/関連MQ017/UI232～236/SS322は[method-trace](../018_NK-OPS-001/evidence/PG24704-catalog-method33-trace-v1/method-trace.json)。専有RD空/P00102責任/費用を不変更。期待389行は独立UI表でproductionはactualのみ。固定値/異常/null/immutableとconstructor/privatehelper/lambda/staticinitの経路を区別する。

L184M33C8B76/I853全miss0は既normal120のsubset、Java/製品PT/coverage再測定0。compiler二classはXMLcounter空で標準filterであり、個別Source自然B0とは区別する。順manifest class行の汎用zeroラベルはindependent manifestのstandardCompilerClassBranchStatusOverridesを必須の適用性区分とし、自然Sourceゼロや人工class100に換算しない。元raw結果を改変しない。

新障害/新PASS/Source登録/leaf0・unique520/正式1964-53/工数null・全実操作HOLD保持。旧受入/nativeを現Mainへ転用せず、既成功確認再演0。
