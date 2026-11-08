# Layout五Source・25methodの要件/Test参照

G13.07 ORIGINAL_PLAN原0.5/2/5cap7、関連P00102費用追加0。Main7aed/Test64f3/normal24642全120を再実行せず参照。PG24692順0/9a4c9971→24694独立逆0/bc08487b765315335c646f1360a7873e3cf033e5f3eaf75b73404781dfcc8884、7型保持metadata変異を拒否。40raw=25公式測定+LayoutDefinition record生成11/LayoutId record3+bridge1の標準filter15、手動除外/人工呼出0。五Source元owner/costOwner P00102、専有RD空を維持し関連MQ014/017は参照のみ。

|class.method|descriptor|実Case参照|静的責務経路|
|---|---|---|---|
| LayoutDefinition.<init> | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;ILdev/codex/schubert/nk/protocol/header/MessageKind;Ldev/codex/schubert/nk/protocol/header/InteractionKind;III)V` | L3 | LayoutMetadataTest d -> sevenargument -> canonical eightargumentconstructor; directeightargumentwrongtotal rejected |
| LayoutDefinition.<init> | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;ILdev/codex/schubert/nk/protocol/header/MessageKind;Ldev/codex/schubert/nk/protocol/header/InteractionKind;IIII)V` | L3 | LayoutMetadataTest d -> sevenargument -> canonical eightargumentconstructor; directeightargumentwrongtotal rejected |
| LayoutDefinition.totalLengthFor | `(I)I` | L3 | L3 fixed264/274/284 literal calls totalLengthFor |
| LayoutDefinition.validateDeclaredLength | `(Ljava/lang/String;I)V` | L3 | Canonicalconstructor andcalculateMaximumTotal -> validateDeclaredLength |
| LayoutDefinition.calculateMaximumTotal | `(III)I` | L3 | Delegating/canonicalconstructor andtotalLengthFor -> calculateMaximumTotal |
| LayoutId.<init> | `(Ljava/lang/String;)V` | L4 | LayoutMetadataTest direct new LayoutId |
| LayoutId.compareTo | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;)I` | L4 | L4 first.compareTo(second/null) |
| LayoutId.toString | `()Ljava/lang/String;` | L4 | L4 explicit fixedliteral vs first.toString |
| LayoutId.<clinit> | `()V` | L4 | Initialization prerequisite of LayoutId constructor |
| LayoutRegistry.<init> | `(Ljava/util/Collection;)V` | L1,L2 | Class<clinit> -> new LayoutRegistry(standardDefinitions()); L1 all andrequire observations |
| LayoutRegistry.validateDefinitions | `(Ljava/util/Collection;)V` | L2 | L2 direct package-level validateDefinitions |
| LayoutRegistry.validatedIndex | `(Ljava/util/Collection;)Ljava/util/LinkedHashMap;` | L1,L2 | Constructor andvalidateDefinitions -> validatedIndex |
| LayoutRegistry.standard | `()Ldev/codex/schubert/nk/protocol/layout/LayoutRegistry;` | L1 | L1 direct LayoutRegistry.standard() |
| LayoutRegistry.all | `()Ljava/util/List;` | L1 | L1 standard().all() expectedTSV andclear rejection |
| LayoutRegistry.require | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;I)Ldev/codex/schubert/nk/protocol/layout/LayoutDefinition;` | L1 | L1 directString andtypedrequire; String delegates typed |
| LayoutRegistry.require | `(Ljava/lang/String;I)Ldev/codex/schubert/nk/protocol/layout/LayoutDefinition;` | L1 | L1 directString andtypedrequire; String delegates typed |
| LayoutRegistry.key | `(Ldev/codex/schubert/nk/protocol/layout/LayoutId;I)Ljava/lang/String;` | L1,L2 | validatedIndex andtypedrequire -> key |
| LayoutRegistry.validateIdentifierKind | `(Ldev/codex/schubert/nk/protocol/layout/LayoutDefinition;)V` | L1,L2 | validatedIndex -> validateIdentifierKind |
| LayoutRegistry.ifEvent | `(Ljava/lang/String;)Z` | L1,L2 | validateIdentifierKind -> ifEvent, literal64tuple andQWKmismatch fixture |
| LayoutRegistry.standardDefinitions | `()Ljava/util/List;` | L1 | <clinit> -> standardDefinitions; L1 entireUI233 fixtureequal |
| LayoutRegistry.d | `(Ljava/lang/String;Ldev/codex/schubert/nk/protocol/header/MessageKind;Ldev/codex/schubert/nk/protocol/header/InteractionKind;IIII)Ldev/codex/schubert/nk/protocol/layout/LayoutDefinition;` | L1 | standardDefinitions -> d -> LayoutDefinitioneightarg |
| LayoutRegistry.<clinit> | `()V` | L1 | RETAINED_STANDARD initializer -> standardDefinitions -> constructor |
| LayoutValidationException.<init> | `(Ljava/lang/String;)V` | L2,L3,L4,H7 | LayoutId/LayoutDefinition/LayoutRegistry/CommonHeader constructors throw new LayoutValidationException |
| LayoutValidationException.<init> | `(Ljava/lang/String;Ljava/lang/RuntimeException;)V` | L2,L3,L4,H7 | LayoutId/LayoutDefinition/LayoutRegistry/CommonHeader constructors throw new LayoutValidationException |
| UnsupportedLayoutException.<init> | `(Ljava/lang/String;)V` | L1 | LayoutRegistry.require -> new UnsupportedLayoutException |

実Case名/元TestID/独立期待値：

- L1 dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#registryMatchesIndependentUi233Catalog() / PT-PRO-001-L01,PT-PRO-001-L03。IndependentUI233 TSV all64 orderedtuples: kind,interaction,data/record/maxCount/total,version1/unknown2,immutablecollection; registry actuals neverexpected.
- L2 dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#registryRejectsEmptyNullDuplicateAndKindMismatches() / PT-PRO-001-L02。Fixedempty/nullcontainer/nullmember/duplicate andREQ/RSP/unknown/QWK/QSB typeinteractionmismatches rejected; validcustomrequest accepted.
- L3 dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#layoutDefinitionChecksEveryLengthAndKindInvariant() / PT-PRO-001-L02。Literal264/274/284 =256+8+10*0/1/2; count-1/3,version2/negative/1000000,recordpair0/non0,total257,eventprofile/overflow/null rejected.
- L4 dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest#layoutIdAndFieldDefinitionAreStrictAndOneBased() / PT-PRO-001-L02,PT-PRO-001-F01。LiteraluppercaseASCII8, short/lowercase/null reject, ABCREQ01<ABCRSP01, literaltoString; FieldDefinition assertions aredifferentSource references andnotnewcredit.
- H7 dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerLengthArithmeticAcceptsExactMillionAndRejectsTheNextByteAndOverflow() / PT-PRO-HDR3266-002。Literal999744+256=1000000 accepted,999745+256=1000001 rejected;999999*999999 overflow wraps ArithmeticException withfixeddiagnostic.

全source行/実case bodySHA/元normal/個別methodcounterは[JSON参照](../018_NK-OPS-001/evidence/PG24692-layout-method25-trace-v1/method-trace.json)。UI232/233とSS322正本byte一致、独立UI233 TSVの64tuple/正本式が期待値、registryはactualのみ。L168M25C5B60/I1157全miss0は元XMLのsubset参照で新coverage0、例外二型自然B0はN-A/null。個別Case probe帰属null、全分岐独立期待値完成/全scope受入は未主張。既107の歴史受入や全3701/nativeを現Sourceへ転用しない。

製品変更/新PT/新PASS/Source登録/leaf受入0、unique520/正式1964-53/工数nullと全HOLD維持。追加障害0、既成功試験確認再演0。
