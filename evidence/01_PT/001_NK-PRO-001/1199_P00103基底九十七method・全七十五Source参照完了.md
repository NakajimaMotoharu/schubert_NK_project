# P00103基底97method・全75Source参照結合

G13.07 ORIGINAL_PLAN原0.5/3/7cap9、P00103責任参照追加費0。Main7aed/Test64f3/normal24642元120を保持。PG24774順0/138d66c1→PG24776独立逆0/33c2166b9c54d75ae97144113934e6ab1ed49ae6efd96669c1c58b03d785ddf6、7誤metadata否定。基底六Source/六physical（4測定/2抽象）、raw110=97測定+record10/utility1標準filter11+抽象fields()2。TypedFieldValues86methodはpublic/private/optional lambda/clinitの各責務へ限定したCaseを関連付け、親Sourceのlambdaとhelper呼出を逆確認。

全signature/行/Sourcehash/Testbodyhash/独立期待/要件は[method-trace](../018_NK-OPS-001/evidence/PG24774-base6-method97-trace-v1/method-trace.json)、abstract-contracts.jsonは抽象fields()2を実測methodと区別する。

|class.method|実Case参照|静的責務経路|
|---|---|---|
| FixedPayload.<init> | F1 | F1 direct FixedPayload constructors/mutation |
| FixedPayload.dataLength | F1 | F1 literal2 -> dataLength |
| FixedPayload.recordLength | F1 | F1 literal3 -> recordLength |
| FixedPayload.recordCount | F1 | F1 literal1 -> recordCount |
| FixedPayload.copyData | F1 | F1 input/outputmutation andliteral1,2 expected |
| FixedPayload.copyRecords | F1 | F1 mutations -> literal3,4,5 andclear rejection |
| FixedPayload.toString | F1 | F1 containsdataLength2/omits[1,2] |
| PayloadValues.<init> | V1 | V1 direct PayloadValues null/element/immutable cases |
| PayloadValues.toString | V1 | V1 explicitinputnoncontainment |
| TypedFieldValues.requiredText | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> requiredText |
| TypedFieldValues.requiredNumeric | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> requiredNumeric |
| TypedFieldValues.requiredFlag | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> requiredFlag |
| TypedFieldValues.optionalText | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> optionalText |
| TypedFieldValues.requiredString | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> requiredString |
| TypedFieldValues.requiredLong | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> requiredLong |
| TypedFieldValues.requiredInt | I1 | I1 direct requiredInt -> Math.toIntExact |
| TypedFieldValues.requireUnsignedRange | I3 | I3 direct requireUnsignedRange |
| TypedFieldValues.requiredBoolean | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> requiredBoolean |
| TypedFieldValues.optionalString | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> optionalString |
| TypedFieldValues.requiredId | I1 | I1 direct requiredId |
| TypedFieldValues.optionalId | I1 | I1 direct optionalId |
| TypedFieldValues.requiredEnum | I2 | I2 direct requiredEnum |
| TypedFieldValues.optionalEnum | I2 | I2 direct optionalEnum |
| TypedFieldValues.requiredHttpStatusCode | I3 | I3 direct requiredHttpStatusCode |
| TypedFieldValues.optionalHttpStatusCode | I3 | I3 direct optionalHttpStatusCode |
| TypedFieldValues.requiredElapsedMilliseconds | I3 | I3 direct requiredElapsedMilliseconds |
| TypedFieldValues.optionalElapsedMilliseconds | I3 | I3 direct optionalElapsedMilliseconds |
| TypedFieldValues.requiredInstant | SD,SN | SD/SN direct requiredInstant -> semantic factory |
| TypedFieldValues.optionalInstant | SD,SN | SD/SN direct optionalInstant -> semantic factory |
| TypedFieldValues.requiredUuid | SD,SN | SD/SN direct requiredUuid -> semantic factory |
| TypedFieldValues.optionalUuid | SD,SN | SD/SN direct optionalUuid -> semantic factory |
| TypedFieldValues.optionalAuthenticationContext | SD,SN | SD/SN direct optionalAuthenticationContext |
| TypedFieldValues.requiredSha256 | SD,SN | SD/SN direct requiredSha256 -> semantic factory |
| TypedFieldValues.optionalSha256 | SD,SN | SD/SN direct optionalSha256 -> semantic factory |
| TypedFieldValues.requiredRelativePath | SD,SN | SD/SN direct requiredRelativePath -> semantic factory |
| TypedFieldValues.optionalRelativePath | SD,SN | SD/SN direct optionalRelativePath -> semantic factory |
| TypedFieldValues.requiredDisplayPath | SD,SN | SD/SN direct requiredDisplayPath -> semantic factory |
| TypedFieldValues.optionalDisplayPath | SD,SN | SD/SN direct optionalDisplayPath -> semantic factory |
| TypedFieldValues.orUnset | T6 | T6/SD directtypedhelper orfrom required/optionalpublichelper -> orUnset |
| TypedFieldValues.text | SD,SZ | SD/SZ direct text |
| TypedFieldValues.numeric | SD | SD direct numeric |
| TypedFieldValues.flag | SD | SD direct flag |
| TypedFieldValues.id | I1 | I1 direct id |
| TypedFieldValues.optionalIdValue | I1 | I1 direct optionalIdValue |
| TypedFieldValues.enumValue | I2 | I2 direct enumValue |
| TypedFieldValues.optionalEnumValue | I2 | I2 direct optionalEnumValue |
| TypedFieldValues.httpStatusCode | I3 | I3 direct httpStatusCode |
| TypedFieldValues.optionalHttpStatusCodeValue | I3 | I3 direct optionalHttpStatusCodeValue |
| TypedFieldValues.elapsedMilliseconds | I3 | I3 direct elapsedMilliseconds |
| TypedFieldValues.optionalElapsedMillisecondsValue | I3 | I3 direct optionalElapsedMillisecondsValue |
| TypedFieldValues.optionalStringValue | SD,SZ | SD/SZ direct optionalStringValue |
| TypedFieldValues.instant | SD,SZ | SD/SZ direct instant |
| TypedFieldValues.optionalInstantValue | SD,SZ | SD/SZ direct optionalInstantValue |
| TypedFieldValues.uuid | SD,SZ | SD/SZ direct uuid |
| TypedFieldValues.optionalUuidValue | SD,SZ | SD/SZ direct optionalUuidValue |
| TypedFieldValues.optionalAuthenticationContextValue | SD,SZ | SD/SZ direct optionalAuthenticationContextValue |
| TypedFieldValues.sha256 | SD,SZ | SD/SZ direct sha256 |
| TypedFieldValues.optionalSha256Value | SD,SZ | SD/SZ direct optionalSha256Value |
| TypedFieldValues.relativePath | SD,SZ | SD/SZ direct relativePath |
| TypedFieldValues.optionalRelativePathValue | SD,SZ | SD/SZ direct optionalRelativePathValue |
| TypedFieldValues.displayPath | SD,SZ | SD/SZ direct displayPath |
| TypedFieldValues.optionalDisplayPathValue | SD,SZ | SD/SZ direct optionalDisplayPathValue |
| TypedFieldValues.requireEmpty | T6 | T6/SD directtypedhelper orfrom required/optionalpublichelper -> requireEmpty |
| TypedFieldValues.require | T6,SD | T6/SD directtypedhelper orfrom required/optionalpublichelper -> require |
| TypedFieldValues.wrongType | T6 | T6/SD directtypedhelper orfrom required/optionalpublichelper -> wrongType |
| TypedFieldValues.canonicalUuid | SD,SN | requiredUuid/optionalUuid -> canonicalUuid |
| TypedFieldValues.parseOptionalId | I1 | I1 publicIDhelpers -> parseOptionalId |
| TypedFieldValues.enumConstant | I2 | I2 publicenumhelpers -> enumConstant |
| TypedFieldValues.semanticId | I1 | I1 publicIDhelpers -> semanticId |
| TypedFieldValues.semantic | SD,SN,I1,I2,I3 | Required/optional semanticpublichelpers -> semantic |
| TypedFieldValues.lambda$optionalDisplayPathValue$0 | SD,SZ | optionalDisplayPathValue -> optional/lambda lambda$optionalDisplayPathValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalRelativePathValue$0 | SD,SZ | optionalRelativePathValue -> optional/lambda lambda$optionalRelativePathValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalSha256Value$0 | SD,SZ | optionalSha256Value -> optional/lambda lambda$optionalSha256Value$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalAuthenticationContextValue$0 | SD,SZ | optionalAuthenticationContextValue -> optional/lambda lambda$optionalAuthenticationContextValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalUuidValue$0 | SD,SZ | optionalUuidValue -> optional/lambda lambda$optionalUuidValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalInstantValue$0 | SD,SZ | optionalInstantValue -> optional/lambda lambda$optionalInstantValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalElapsedMillisecondsValue$0 | I3 | optionalElapsedMillisecondsValue -> optional/lambda lambda$optionalElapsedMillisecondsValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalHttpStatusCodeValue$0 | I3 | optionalHttpStatusCodeValue -> optional/lambda lambda$optionalHttpStatusCodeValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalEnumValue$0 | I2 | optionalEnumValue -> optional/lambda lambda$optionalEnumValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalIdValue$0 | I1 | optionalIdValue -> optional/lambda lambda$optionalIdValue$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$orUnset$0 | T6 | orUnset -> optional/lambda lambda$orUnset$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalDisplayPath$0 | SD,SN | optionalDisplayPath -> optional/lambda lambda$optionalDisplayPath$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalRelativePath$0 | SD,SN | optionalRelativePath -> optional/lambda lambda$optionalRelativePath$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalSha256$0 | SD,SN | optionalSha256 -> optional/lambda lambda$optionalSha256$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalAuthenticationContext$0 | SD,SN | optionalAuthenticationContext -> optional/lambda lambda$optionalAuthenticationContext$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalUuid$0 | SD,SN | optionalUuid -> optional/lambda lambda$optionalUuid$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalInstant$0 | SD,SN | optionalInstant -> optional/lambda lambda$optionalInstant$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalElapsedMilliseconds$0 | I3 | optionalElapsedMilliseconds -> optional/lambda lambda$optionalElapsedMilliseconds$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalHttpStatusCode$0 | I3 | optionalHttpStatusCode -> optional/lambda lambda$optionalHttpStatusCode$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalEnum$0 | I2 | optionalEnum -> optional/lambda lambda$optionalEnum$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalEnum$1 | I2 | optionalEnum -> optional/lambda lambda$optionalEnum$1; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$requiredEnum$0 | I2 | requiredEnum -> optional/lambda lambda$requiredEnum$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalId$0 | I1 | optionalId -> optional/lambda lambda$optionalId$0; sourcecapture/functionconversion only |
| TypedFieldValues.lambda$optionalId$1 | I1 | optionalId -> optional/lambda lambda$optionalId$1; sourcecapture/functionconversion only |
| TypedFieldValues.<clinit> | I1 | I1 optionalId initializes OPTIONAL_ID Pattern |
| TypedPayloadValues.<init> | T6 | T6 direct TypedPayloadValues null andclear rejection |
| TypedPayloadValues.toString | T3 | T3 typeddisplay omits FieldValue |

実Case/独立期待：

- F1：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#fixedPayloadIsDefensiveAndWireMessageChecksLengths() / PT-PRO-002-M01,PT-PRO-002-M02。Independentinput1,2 andrecord3,4,5 bytes preservedafterinput/outputmutation; literaldata2/recordlength3/count1; WireMessage mismatcheddata8vs9/record271vs272/count0vs1 andnullheader/payload rejected.
- V1：dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#valuesAreImmutableNullSafeAndRedacted() / PT-PRO-002-P03。Synthetic literal value isnotprinted; Numeric1/Flagtrue/Unset INSTANCE; nulltext/map/key/value/blankname/getnull rejected, namesimmutable,size1,getidentity/missingUnset,self/equal/different/wrongtype, equalhash contract. Absolutehashnumeric oracle notclaimed bythiscase.
- T6：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#typedModelsAndHelpersRejectNullMissingAndWrongKinds() / PT-PRO-001-T03,PT-PRO-002-P05。Explicitrequiredtext safe/numeric7/flagtrue/unset/optional contracts, nullvalues/catalog refs/typedmodel invariants rejected; sharedTypedFieldValues methods haveotherowner andnoacceptancecredit.
- T3：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes() / PT-PRO-001-T02,PT-PRO-002-P04。Generic minimuminput supplies64layouts,69distinctnamedtypes/14repeat; returneddata/record class andredaction; roundtrip consistency supplementedbyC1/C2 independentdirectional/table oracle.
- D1：dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest#allNamedTypesHaveIndependentDirectionalFieldMeaning() / PT-PRO-001-T02,PT-PRO-002-P04。Existing IndependentNamedFieldOracle.verifyAll ownsassertions: independentexplicitgetter-field bindings andfixedscalar values/SS/UI296component table; decode/getter andencode/fields checked separately, notProduction-generated expected.
- SD：dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest#semanticHelpersDecodeAndEncodeEverySupportedShape() / PT-PRO-SEM-D。Fixedstring42/true/JST20260902123456789 andInstant,canonicalUUID,synthetichex,path/display literals; required/optional present/unset decode andencode expectedFieldValue separate.
- SN：dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest#semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects() / PT-PRO-SEM-N。Feb30/invalidtext/uppercaseUUID/absolute-or-empty path rejected withLayoutValidationException/IAEcause andfixedsafe diagnostic, noUUIDecho.
- SZ：dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest#semanticEncodingHelpersRejectNullReferences() / PT-PRO-SEM-Z。Explicitnullreference forstring/Optional/instant/uuid/syntheticauth/sha/path encodehelpers -> Java boundaryNPE, notcaughtnormalProductreturn.
- I1：dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#typedHelpersConvertIntAndIdentifiersWithoutLosingWireKinds() / PT-PRO-001-T04。Literalint123/id42/000000000042/Unset andwire42; longMAXintoverflow/zeroID/ABC/allzero/13digit/nullfactory/nullid rejected.
- I2：dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#allAllowlistedEnumsExposeExplicitWireValuesAndGenericConversion() / PT-PRO-001-T04。Approvedenumtable andgenericrequired/optionalconversion/present/absent/unknown/null; valuesindependenttable-backed alreadypriorreview.
- I3：dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest#xNumericWrappersAndGeneratedNumericRangesRejectNonCanonicalValues() / PT-PRO-001-T04。Literalstatus200/elapsed999999999,zero wire; numericrange0/12nines accepted,-1/1000in3digits/0or19digits rejected, nullnames/wrappers/optionals rejected.

当六Source L186M97C4B38/I976全miss0は元normal120参照で新測定0。literal型/wire/時刻/UUID/数値、null/不正kind/semantic IAE cause/安全診断、defensivecopy/immutableを既実ケースへ分ける。個別Case probe帰属null、全分岐の全独立期待完了は主張しない。二record自然B0と二interfaceコードなしを人工100へ換算しない。

## P00103全75Sourceの参照結合

24776の[p00103-all75-reference-summary](../018_NK-OPS-001/evidence/PG24776-base6-method97-trace-independent-v1/p00103-all75-reference-summary.json)は既24762 named69/277methodと当六Sourceを非重複結合し、元ownedArtifacts全75/75Source・75physical・73測定class・374/374公式methodを同normal120のXMLへ逆一致させる。raw821=374測定+445標準filter+2抽象、実Case参照16。L1450M374C73B38/I7608全miss0は元単一exec部分集合で、新coverage測定・異execの合算なし。71Source自然B0=N-A/null・strict非空Source四gate1を保持する。

元P00103所有/専有RD空/関連MQ016017・原費用・acceptanceは不変更。この完成は参照結合だけで、owner品質/全G13/451の完了ではない。新Java/compiler/Analyzer/javap/PT/PASS/Source登録/leaf0・unique520/正式1964-53/工数null/全HOLD保持。工具失敗0、既成功確認再演0。

PG24778でWBS485/486へcurrentP00103AllMethodReferenceTrace20261109を同一観測として追記。75/75Source/374methodの参照結合完成だけで元acceptance/costは不変更、旧全値・既580guard/4誤参照否定を保持しroot486を現4857e19f3d0へ整合。前のnamed69/277部分観測も歴史値として保持。
