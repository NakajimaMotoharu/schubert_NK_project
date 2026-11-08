# 不変carrier七Source・14methodの要件/Test参照

Main7aed/Test64f3/normal24642元120参照。PG24716順0/600d2262→PG24718独立逆0/e272cdbeb727ed25ef38528fb683257f3ecd5be8bfd53dccc50ceab0795e031a、7誤metadata反証。七Source/十一物理/六測定class、39raw=14測定+20標準生成filter+5抽象method。FieldValueはmarker method0、LayoutPayloadは抽象5、package-info三枚はmethod0で実行coverageへ人工加点しない。全owner/costOwner P00102・専有RD空/共有MQ017018参照不変更。

|class.method|descriptor|実Case参照|静的責務経路|
|---|---|---|---|
| FieldValue$Flag.<init> | `(Z)V` | V1 | V1 direct new FieldValue.Flag |
| FieldValue$Numeric.<init> | `(J)V` | V1 | V1 direct new FieldValue.Numeric |
| FieldValue$Text.<init> | `(Ljava/lang/String;)V` | V1 | V1 direct new FieldValue.Text |
| FieldValue$Text.toString | `()Ljava/lang/String;` | V1 | V1 callssecret.toString thenassertFalsecontainssecret.value |
| FieldValue$Unset.<clinit> | `()V` | V1 | V1 explicit INSTANCE.toString literal andmissingname defaults |
| FieldValueSet.<init> | `(Ljava/util/Map;)V` | V1 | V1 directconstructors |
| FieldValueSet.empty | `()Ldev/codex/schubert/nk/protocol/layout/FieldValueSet;` | V1 | V1 equalityagainstFieldValueSet.empty |
| FieldValueSet.names | `()Ljava/util/Set;` | V1 | V1 names().clear rejects |
| FieldValueSet.getOrUnset | `(Ljava/lang/String;)Ldev/codex/schubert/nk/protocol/layout/FieldValue;` | V1 | V1 direct getOrUnset |
| FieldValueSet.size | `()I` | V1 | V1 literalsize1 |
| FieldValueSet.equals | `(Ljava/lang/Object;)Z` | V1 | V1 assertEquals/assertNotEquals -> equals |
| FieldValueSet.hashCode | `()I` | V1 | V1 explicit equalvalues hashCode calls |
| FieldValueSet.toString | `()Ljava/lang/String;` | V1 | V1 safeNamecontains andvalueomit assertions |
| WireMessage.<init> | `(Ldev/codex/schubert/nk/protocol/header/CommonHeader;Ldev/codex/schubert/nk/protocol/layout/LayoutPayload;)V` | W1 | W1 direct new WireMessage andfixedlength mismatchinputs |

実Caseと独立期待：

- V1：dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#valuesAreImmutableNullSafeAndRedacted() / PT-PRO-002-P03。Synthetic literal value isnotprinted; Numeric1/Flagtrue/Unset INSTANCE; nulltext/map/key/value/blankname/getnull rejected, namesimmutable,size1,getidentity/missingUnset,self/equal/different/wrongtype, equalhash contract. Absolutehashnumeric oracle notclaimed bythiscase.
- W1：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#fixedPayloadIsDefensiveAndWireMessageChecksLengths() / PT-PRO-002-M01,PT-PRO-002-M02。Independentinput1,2 andrecord3,4,5 bytes preservedafterinput/outputmutation; literaldata2/recordlength3/count1; WireMessage mismatcheddata8vs9/record271vs272/count0vs1 andnullheader/payload rejected.

全Source行/hash/元Test bodyhash/要件は[method-trace](../018_NK-OPS-001/evidence/PG24716-carrier-method14-trace-v1/method-trace.json)、抽象5は同directory abstract-contracts.json。UI232233/SS322現正本一致。別Carrier6ケースは2789の独立期待補足でnormal120のactualCaseKeysへ混入0。原map変更/厳密絶対hash/equals nullやText全境界は当V1単独では未主張、旧成功を現runへ合算しない。

参照L36M14C6B16/I180全miss0は既XML subset・新測定0。個別probe null/全分岐独立oracle完成未主張。BUG2551はWireMessageのgeneric宣言をnongenericとした固定guard初1。before24720保全→当四record宣言（三non-generic/一generic）の実表記だけに限定是正、24718で全四確認と7誤metadata否定。新parser/製品変更/Java/compiler/Analyzer/PT再実行0。

G13 ORIGINAL_PLAN原0.5/2/5cap7・関連P00102追加費0。新PASS/Source登録/leaf0、unique520/正式1964-53/工数null/全HOLD維持。
