# Headercodec五Source・14methodの要件/Test参照

G13.07 ORIGINAL_PLAN原0.25/1/3cap5・P00203追加費0、Main7aed/Test64f3/normal24642元120を保持。PG24806順0/18cbc1ae（JSON）→24808独立逆0/dd40ac9440700fbb1753b0f15c8c6753372fae2488b54b6c939b863be1454e87、7誤metadata否定。元全五Source/五class、raw40=14測定+record22/enum4標準filter26。元actual7Caseと独立256byte golden/offset・QSE profile・nullablebody/field破壊/transport-route-null・Payload sender拒否をmethodへ限定結合。

|class.method|descriptor|実Case参照|静的責務経路|
|---|---|---|---|
| `ExpectedRoute.<init>` | `(Ldev/codex/schubert/nk/protocol/header/MessageKind;Ldev/codex/schubert/nk/protocol/header/InteractionKind;Ljava/lang/String;Ljava/util/Optional;Z)V` | M7,MT | M7 directExpectedRoute constructors andMT routefixtures |
| `HeaderCodec.<init>` | `(Ldev/codex/schubert/nk/protocol/layout/LayoutRegistry;)V` | H1 | H1 HeaderCodec constructor/standard factory |
| HeaderCodec.standard | `()Ldev/codex/schubert/nk/protocol/codec/HeaderCodec;` | H1,H2 | H1/H2 direct HeaderCodec.standard |
| HeaderCodec.encode | `(Ldev/codex/schubert/nk/protocol/header/CommonHeader;)[B` | H1,H2,H3 | H1 independentgolden/H2 profiles/H3 unknownheaders -> encode |
| HeaderCodec.peek | `([B)Ldev/codex/schubert/nk/protocol/header/CommonHeader;` | H1,H2,H3 | H1/H2/H3 direct peek |
| HeaderCodec.canonicalUuid | `(Ljava/lang/String;)Ljava/util/UUID;` | H1,H3 | peek -> canonicalUuid |
| HeaderCodec.requiredText | `([BII)Ljava/lang/String;` | H1,H3 | peek -> requiredText -> slice |
| HeaderCodec.numericInt | `([BIIII)I` | H1,H3 | peek -> numericInt -> FieldCodec.decodeNumeric |
| HeaderCodec.slice | `([BII)[B` | H1,H3 | peek/requiredText/numericInt -> slice |
| HeaderCodec.put | `([BI[B)V` | H1,H2 | encode -> put; H1 independentlyplacedexpectedbytes |
| `MessageEncodingException.<init>` | `(Ljava/lang/String;)V` | PE | PayloadCodec.encode checks -> new MessageEncodingException(message) |
| `MessageEncodingException.<init>` | `(Ljava/lang/String;Ljava/lang/Throwable;)V` | H3,MF | HeaderCodec.encode/FixedWidthEncoder.encode -> new MessageEncodingException(message,cause) |
| `TransportBodyType.<clinit>` | `()V` | MT,M7 | MT mismatchedbodytype/validBYTESmetadata -> enum initialization |
| `TransportMetadata.<init>` | `(Ldev/codex/schubert/nk/protocol/codec/TransportBodyType;Ljava/lang/String;Ljava/util/UUID;Ljava/util/Optional;JIILjava/util/UUID;Ldev/codex/schubert/nk/protocol/layout/LayoutId;Ljava/lang/String;Ljava/lang/String;)V` | M7,MT | M7 directTransportMetadata constructors andMT metadatafixtures |

実Caseと独立期待：

- MF：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizes() / PT-PRO-002-M01,PT-PRO-002-M02。Explicit537byte header+data+record structure,lengthbounds/null/actualdeclared mismatch/unknownlayout anddefensivebytecarrier; headerindependentgolden sharedproof1961/2639 notselfroundtrip-onlyclaim.
- MT：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#transportAndRouteContractsRejectEveryMismatch() / PT-PRO-002-T01。Explicitbodytype/PERSISTENT2/version001/IDs/layout/correlation/route/replyTo/expiry mismatch typedpermanent rejection; syntheticmetadataonly, noactualJMS.
- H1：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#headerEncodingMatchesIndependentUi232GoldenVector() / PT-PRO-002-H01。IndependentASCII-space256byte expectedarray withfixedUI232 offsets/literals,exactbytecomparison; noexpectedProductionmethod.
- H2：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#responseAndEventHeadersRoundTripWithoutLeakingContext() / PT-PRO-002-H01。Explicitresponse/event profiles andcontextabsence/redaction; QSE headerprofile compatibility.
- H3：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#headerDecoderRejectsEveryFixedFieldAndProfileCorruption() / PT-PRO-002-H02。Fixedoffset onefieldcorruptions/protocol/version/UUIDcase/context/result/reserved/unknownlayout/declaredlimits typedpermanent rejection; senderunknownlayout MessageEncodingException.
- M7：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#metadataAndExpectedRouteEstablishNullAndRangeContracts() / PT-PRO-002-T01。Namedconstructor null/blankaddress/negativeexpiry/zeroDeliveryCount/requiredreply/event-expiry pair violations explicitly rejected.
- PE：dev.codex.schubert.nk.protocol.codec.PayloadCodecTest#encodeRejectsUnknownMissingWrongTypeAndRecordViolations() / PT-PRO-002-P03。Explicitunknown/fixed/missing/wrongkind/recordprofile invalidinputs -> MessageEncodingException throughoneStringctor; inputconstructed independentliteralfields.

全Source行/hash/元body hash/関連MSG-MQ/UI231232233/SS322は[method-trace](../018_NK-OPS-001/evidence/PG24806-headercodec5-method14-trace-v1/method-trace.json)。MessageEncodingException一引数ctorは他ownerのPayloadCodec側PE、cause付きctorはHeader/Frame encode H3/MFを区別し、呼出先の製造・試験費/受入を二重計上しない。L113M14C5B36/I644全miss0は元同normal120参照・新測定0。例外/enum二Source自然B0=N-A/null/strictSource四gate1、個別probe null・全branch独立oracle完成未主張。

BUG2555/YKT2279：順toolのコンソールだけ104method/101filterというコピー元値が残存し、実JSONは正しい14/26。before24810へ元toolを保存し元JSONを改変せず、current809末尾printだけrows/filtered/casesの実長へ修正。24808が旧tool SHAとbeforeを照合・末尾print以外AST同一/計算長を確認、元producerは再演0。24790の別工具不備とは別件であり、製品試験の失敗ではない。24812同系十producerを静的確認し旧九の表示値は各manifestと一致・非該当/無変更、当一だけ修正済み。

元P00203全5artifact/専有RD空・責任/費用/acceptance不変更。参照結合だけでowner品質/全G13/451を受入にしない。新Java/compiler/Analyzer/製品PT/PASS/coverage/Source登録/leaf0・unique520/正式1964-53/工数null/全HOLD保持。

PG24814でWBS485/486へcurrentP00203AllMethodReferenceTrace20261109を同一観測として追記し全5/14参照を記録。旧全値/受入/費用・既580guard/4誤参照否定を保持、root486は現485bde5acfcへ同時整合。
