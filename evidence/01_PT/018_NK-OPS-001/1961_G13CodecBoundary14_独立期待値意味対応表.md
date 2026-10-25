# Codec境界十四methodの独立oracle対応

1960/current64446/群2193。全三TestとFieldCodec/encoder/decoder/ProtocolValidator/metadata/route/payload及びHeaderCodec全体、PayloadCodecの単一record/area処理を読取。既Program002とScenario仕様のRD/UI/SS参照を保持。型/null/例外・byteと所有copyの対応であって実JMS/DB/native/終了ownerの資格ではない。

| class | method | 既存Test ID family | 独立期待値と読取根拠 | 範囲・限界 |
|---|---|---|---|---|
| FieldCodecTest | textEncodeNormalizesUtf8AndPadsWithAsciiSpace | PT-PRO-002-X01, PT-PRO-002-X02 | AB→41 42 20 20、NFD e+accent→c3 a9 20 20、あ3/emoji4byte、任意空はspace。control/末尾space/surrogate/超過拒否 | Productionはactual側、fixed byte又はJDK UTF8がexpected。切捨て/replacementなしをsourceでも照合 |
| FieldCodecTest | textDecodeIsStrictCanonicalAndOptionalAware | PT-PRO-002-X01, PT-PRO-002-X02, PT-PRO-002-X03 | 内部space保存/末尾padding除去、任意全spaceはempty、必須全space・c3 28・NFD・四control拒否 | null/空sliceは内部precondition。X03の全境界切断/全padding異常を単独で証明しない |
| FieldCodecTest | numericCodecChecksDigitsRangeAndOverflow | PT-PRO-002-N01, PT-PRO-002-N02 | 固定000/001/999と数値1/999、符号+・:・小数点・19桁9overflow、range/桁/長0の型別例外 | timestamp部分は別Test。全signed long境界の新実行を主張しない |
| FieldCodecTest | numericErrorFillerDoesNotBecomeBusinessZero | PT-PRO-002-N02 | error時00→unset、通常00→0、01→1、null/空拒否。SS322 §6.2で全0はsemantic parseしない | fillerを通常rangeで拒否するよう期待値変更しない。誤った内部range設定の完全validationをこのAPIへ推測追加しない |
| FieldCodecTest | booleanAndReservedFieldsRejectUnknownBytes | PT-PRO-002-B01 | 固定0/1/spaceとfalse/true/unset、2/二byte/許可なしspace拒否、reserved全spaceと混入x | nullは内部NPE、unknown wireはPermanentProtocolException。reserved追加観点は既B01補助で新IDを捏造しない |
| MessageCodecTest | responseAndEventHeadersRoundTripWithoutLeakingContext | PT-PRO-002-H01 | GAMRSPとWLGEVTの構造等値/response context保持 | encode→peek自己roundtripで単独の独立byte oracleではない。1953の別LGN golden補助のみ、method名だけでtoString redactionを確認済みとしない |
| MessageCodecTest | headerDecoderRejectsEveryFixedFieldAndProfileCorruption | PT-PRO-002-H02 | UI232のoffset0/8/11/19/22/23/24/60/96/113/177/181/187/193/199/208/212の単項破壊、未知result/profile/送信未知layout拒否 | seedはProduction encode。破壊位置/禁止値は独立だが多重異常の検証順・すべての値域/例外messageをassertしていない |
| MessageCodecTest | fixedPayloadIsDefensiveAndWireMessageChecksLengths | PT-PRO-002-M02 | 固定{1,2}/{3,4,5}を入力/戻り配列/元listから変更してもcopy不変、null/負record/個別長/宣言三要素不一致拒否 | 全wire boundary M02の一部。toStringは長さのみ/配列値なしを実assert。全型付きpayload/redactionの代用でない |
| MessageCodecTest | fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizes | PT-PRO-002-M01, PT-PRO-002-M02 | GAMRSPの256+9+272=537、data/record固定space、body255/1000001/async1001/extra1/null/未知layout拒否 | 全64 layoutの0/1/maxは他Test。本methodはbody全byteの独立goldenではなくfield/header等値/別配列を確認 |
| MessageCodecTest | transportAndRouteContractsRejectEveryMismatch | PT-PRO-002-T01 | BYTES/persistent2/version001/message/layout/correlation/kind/interaction/destination/reply/expirationの明示一条件差、null | metadataは値snapshotのみで実provider接続なし。三OR条件は各identityを変えているが全cross-product証明ではない |
| MessageCodecTest | metadataAndExpectedRouteEstablishNullAndRangeContracts | PT-PRO-002-T01 | expiration負/deliverycount0/blank各値、event/internal・request/reply・event/expiry関係を手書き組合せで拒否 | method名のnull契約全網羅を認定しない。本体はrange/blank/相関中心、constructorの全nullは本methodでは未証明 |
| ScenarioRecordEncodingTest | w03SingleRecordGoldenHasNoInventedDataAndRejectsNullUnknownAndNonRecordLayouts | PT-SCN-008-W03 | UI234 SCNRSP record固定4800byte、Entry71/seq1/line42/narration/本文/audio0、offset0/12/18/26/164/4260、残space | DATA/headerを作らず単一recordだけ。元encode結果変更後再encode一致、全list sequence/filehash/件数上限は対象外 |
| ScenarioRecordEncodingTest | rd02SingleRecordDecodeUsesLiteralGoldenAndOwnsItsValues | PT-SCN-008-RD02 | 同手書きgoldenから個別6値とoptional三unset、入力fill#後も71/本文保存 | expected/inputはProduction encodeを使わない。音声あり/全file integrityの代用でない |
| ScenarioRecordEncodingTest | rd02RejectsNullUnknownNonRecordLengthAndMalformedFieldBytes | PT-SCN-008-RD02 | null/unknown/nonrecord、長0/4799/4801、必須N空・不正UTF8 c3 28・NFD・末尾reserved#を固定投入 | null内部契約と受信wire恒久拒否を区別、各异常の全組合せや検証順を主張しない |

family部分関係は実行PT/全family合格/四100/正式受入に加算しない。X01のtimestamp等、M01の全64/max、H02の多重異常/検証順、T01の全null・全真理表は当群単独の未証明範囲。既header/layout同byteの成果は参照のみで二重計上0。新規製品仕様違反はこの読取範囲で確定していない。

## SCNRSP01の独立byte算出

UI234 §10.3の10fieldは1開始で1/13/19/27/37/165/4261/4264/4276/4788、長12/6/8/10/128/4096/3/12/512/13。総和4800、offset=start-1。NarrationのSpeaker/audio文字列は全space、六代入のnumeric/UTF8は固定値でありProduction catalog/parserから生成しない。UI本文はorigin/main、元3284と同byteであることを前群1957が確認。関連SS322/333と原SCN仕様はそのまま維持。
