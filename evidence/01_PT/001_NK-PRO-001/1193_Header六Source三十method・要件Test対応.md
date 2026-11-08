# Header六Source・30methodの要件/Test参照

Main7aed/Test64f3、PG24642全120の既存実結果と現23972 metadataを参照する。PG24676順0/4ee5dac5、PG24678独立逆0/ae51094f0453b0f361064b3d5186b4badafac04204b044f75ee01482cd6c89f4、7変異metadata拒否。新製品実行・新PASS・coverage測定・leaf受入0。各case別probe帰属はnullで全branch独立oracle完成を主張しない。

|class.method|関連RD|Test参照|静的責務経路|
|---|---|---|---|
| AuthenticationContext.<init> | MQ-014,MQ-015 | H2 | AuthenticationContext.of -> new AuthenticationContext |
| AuthenticationContext.of | MQ-014,MQ-015,MQ-017 | H2 | HeaderModelTest -> AuthenticationContext.of |
| AuthenticationContext.wireValue | MQ-014,MQ-015,MQ-017 | H2 | H2 direct actualwirevalue assertion |
| AuthenticationContext.equals | MQ-014,MQ-015,MQ-017 | H2 | H2 assertEquals/assertNotEquals -> equals |
| AuthenticationContext.hashCode | MQ-014,MQ-015,MQ-017 | H2 | H2 explicitactual hashCode calls |
| AuthenticationContext.toString | MQ-014,MQ-015,MQ-017 | H2 | H2 explicit literaltoString assertion |
| AuthenticationContext.<clinit> | MQ-014,MQ-015,MQ-017 | H2 | Class initialization prerequisite of AuthenticationContext.of |
| CommonHeader.<init> | MQ-014,MQ-015,MQ-017 | H3,H4,H6,H7,H8 | HeaderTest header/base/build/headerWithMissingReference andMessageTest requestHeader -> new CommonHeader |
| CommonHeader.validateAgainst | MQ-014,MQ-015,MQ-017 | H3,H5 | H3 direct/H5 assertMismatch -> validateAgainst |
| CommonHeader.calculateTotal | MQ-014,MQ-015,MQ-017 | H3,H4,H7 | CommonHeader compactconstructor -> calculateTotal |
| CommonHeader.validateKinds | MQ-014,MQ-015,MQ-017 | H3,H4 | CommonHeader compactconstructor -> validateKinds |
| CommonHeader.validateCorrelation | MQ-014,MQ-015,MQ-017 | H3,H4 | CommonHeader compactconstructor -> validateCorrelation |
| CommonHeader.validateResult | MQ-014,MQ-015,MQ-017 | H3,H4 | CommonHeader compactconstructor -> validateResult |
| CommonHeader.validateAuthentication | MQ-014,MQ-015,MQ-017 | H3,H4 | CommonHeader compactconstructor -> validateAuthentication |
| CommonHeader.toString | MQ-014,MQ-015,MQ-017 | H3 | H3 directtoString containsfixedmarker andomitsinput |
| InteractionKind.<init> | MQ-014,MQ-015,MQ-017 | H1 | enum <clinit> -> constructor -> H1 directwire assertions |
| InteractionKind.wireValue | MQ-014,MQ-015,MQ-017 | H1 | H1 forliteralrows -> valueOf(...).wireValue() |
| InteractionKind.fromWire | MQ-014,MQ-015,MQ-017 | H1 | H1 direct fromWire calls |
| InteractionKind.<clinit> | MQ-014,MQ-015,MQ-017 | H1 | H1 values length andliteralconstant iteration afterclass init |
| MessageKind.<init> | MQ-014,MQ-015,MQ-017 | H1 | enum <clinit> -> constructor -> H1 directwire assertions |
| MessageKind.wireValue | MQ-014,MQ-015,MQ-017 | H1 | H1 forliteralrows -> valueOf(...).wireValue() |
| MessageKind.fromWire | MQ-014,MQ-015,MQ-017 | H1 | H1 direct fromWire calls |
| MessageKind.<clinit> | MQ-014,MQ-015,MQ-017 | H1 | H1 values length andliteralconstant iteration afterclass init |
| ResultCode.<init> | MQ-014,MQ-015,MQ-017 | H1 | enum <clinit> -> constructor -> H1 directwire assertions |
| ResultCode.wireValue | MQ-014,MQ-015,MQ-017 | H1 | H1 forliteralrows -> valueOf(...).wireValue() |
| ResultCode.usesSuccessProfile | MQ-014,MQ-015,MQ-017 | H1 | H1 literal boolean table -> usesSuccessProfile |
| ResultCode.fromWire | MQ-014,MQ-015,MQ-017 | H1 | H1 direct fromWire calls |
| ResultCode.lambda$fromWire$1 | MQ-014,MQ-015,MQ-017 | H1 | ResultCode.fromWire -> orElseThrow supplier |
| ResultCode.lambda$fromWire$0 | MQ-014,MQ-015,MQ-017 | H1 | ResultCode.fromWire -> stream.filter candidate.encodedValue.equals(value) |
| ResultCode.<clinit> | MQ-014,MQ-015,MQ-017 | H1 | H1 values length andliteralconstant iteration afterclass init |

全signature/descriptor/実Source行・SHA/各method coverage参照は[method-trace](../018_NK-OPS-001/evidence/PG24676-header-method30-trace-v1/method-trace.json)へ固定する。

- H1：dev.codex.schubert.nk.protocol.header.HeaderModelTest#enumsMapOnlyApprovedWireValues()／PT-PRO-001-H01。UI232 fixed Q/S/E and S/A/I name/wire pairs plus12 fourbyte result literals; only0000 and0200 success. Unknown/empty/multichar/null rejected.
- H2：dev.codex.schubert.nk.protocol.header.HeaderModelTest#authenticationContextValidatesAndRedacts()／PT-PRO-001-H01,PT-PRO-001-H03。Synthetic a repeated64 accepted,63 anduppercase64 rejected; distinct b64 not equal, literal redacted diagnostic; samevalue hash equality andwireValue. No actualcredential.
- H3：dev.codex.schubert.nk.protocol.header.HeaderModelTest#validHeadersCoverRequestResponseErrorAndEventProfiles()／PT-PRO-001-H02。Fixed independent537=256+9+272, loginwithoutcontext/eventinternal/nocontext andresponseprofile; redaction omits synthetic context.
- H4：dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerConstructorRejectsEveryStructuralViolation()／PT-PRO-001-H03。Fixed unsupportedmagic/version,256header,sixdigitnegative/overflow,countwithoutrecord,wrongtotal/submillis/profile/correlation/context violations typed LayoutValidationException.
- H5：dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerValidateAgainstRejectsEachMetadataMismatch()／PT-PRO-001-H03。Explicitdifferentid/kind/interaction/dataLength/recordLength/maxCount definitions rejected; nullprecondition.
- H6：dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerReferencesRejectNullAtTheNamedInvariantBoundary()／PT-PRO-HDR3266-001。Explicitnine nullable Java references rejected at exact named constructor boundary; validheader256 andfixedcorrelation.
- H7：dev.codex.schubert.nk.protocol.header.HeaderModelTest#headerLengthArithmeticAcceptsExactMillionAndRejectsTheNextByteAndOverflow()／PT-PRO-HDR3266-002。Literal999744+256=1000000 accepted,999745+256=1000001 rejected;999999*999999 overflow wraps ArithmeticException withfixeddiagnostic.
- H8：dev.codex.schubert.nk.protocol.codec.MessageCodecTest#headerEncodingMatchesIndependentUi232GoldenVector()／PT-PRO-002-H01。Independent256byte array ofASCIIspace; offsets0/8/11/19/22/24/60/96/177/181/187/193/199 filled literal UI232 fields; expected never from Production encoder.

raw57=実測30+標準生成filter27（record accessor16＋equals/hashCode2、enum三型各values/valueOf/$values3）。package-info @NullMarkedはmethod0でcoverage class100に人工換算しない。元Normalのsubset L137M30C5B88/I687全miss0参照で、新測定0。六Source全て元owner/costOwner P00101、関連P002の黄金値と実製造受入は二重計上しない。UI232/SS322はorigin/main現正本byte一致、MQ014～018の専有範囲不変更。

BUG2550は工具期待のMQ-14という3桁padding漏れ。PG24680 source/command/初guard1を修正前保全、正本MQ-014へ工具だけ是正し現6scope/全30rule/producer/postの範囲を確認。正本・製品・成功120は不変更。YKT2274限定、静的参照の正しさのみでwholeG13/451閉鎖はしない。unique520/正式1964-53/工数null・全実操作HOLD保持。
