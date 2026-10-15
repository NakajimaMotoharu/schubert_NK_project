# Header輸送・恒久例外の現source個別受入

2026-10-15、Production a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25。
対象はWBS-P002-03/04のみ。P002-02の並行oracle BUG1285/P09及びP001-03のDTO component監査は未完として分離し、本票で認定しない。

## 独立oracle・実行集合

001/106のPG3274実3701/542/1643→3276独立0/六静的0/FES-flaky-notrun0→3278同a9全1643Main/79resource/debug byte/CRC0/native28を使用。001のPG3286公開witnessは17suite/84実JUnit method、元XML SHAと現Test/resource同byteを照合した読取証拠であり、新規試験加点0。001/107はUI233～236の64tuple/389field、SS323全64型対応を正本から直接検証済み。

PG3292工具d472d03b6・純三・actual0（08:46:44.510062Z）はUI正本から全64layoutのminimum/maximum DATA・RECORDと31response errorを独立に構成、287個のSHA-256が固定golden TSVに完全一致、非response error33セルは明示`-`。Production Java/catalog/encoderは期待値へ使用0。Xは右space、Nは左zero、Bは0/1/error space、固定REQUEST/予約spaceを原文から構成する。generic codec境界vectorであり、業務semantic validatorを通る要求だとは主張しない。原fixtureへ書換え0。

## P002-03全5artifact

| 対象 | Test ID／実method／独立期待値 |
|---|---|
| HeaderCodec | H01/H02、MessageCodecTest.headerEncodingMatchesIndependentUi232GoldenVector：UI232 §3の固定256byte/17fieldをTest独立offset builderで構成して全byte照合。headerDecoderRejectsEveryFixedFieldAndProfileCorruption：protocol/version/予約/結果/context/UUID/長さを個別破壊しPermanentProtocolExceptionを要求。Login/Q/S/E成功とredaction、未知送信layoutはMessageEncodingException |
| ExpectedRoute | T01/M02、transportAndRouteContractsRejectEveryMismatch/metadataAndExpectedRouteEstablishNullAndRangeContracts：固定direction/interaction/destination/replyToと同期必要条件。null/空/不正組合せ、event route、actualと期待routeの各一不一致を検査 |
| TransportMetadata | T01、上記二method：Bytes/persistent2/期限/message/correlation/layout/version/destination/replyTo/deliveryCountを固定値から設定、各不一致/0・負数/空/nullを拒否。実JMS brokerの受入ではなくtransport metadataの純契約 |
| TransportBodyType | T01、四種BYTES/TEXT/OBJECT/MAP宣言、valueOf/BYTES、非BYTESの実route拒否。enum数だけでwire body受入とはしない |
| MessageEncodingException | H02/M02、fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizes/未知layout送信：固定diagnostic文字列・送信側型付き例外、header validation原因を保持。生password/body/contextをdiagnosticへ埋込まないsource review |

対象は485全5path/hash、専有RD0、共通P001-01/02の同source受入が終了依存で双方成立。`HeaderCodec.standard()`は新immutable instanceでありsingletonだと誤認しない。codec/route/metadataはDB/IO/transaction/再送状態を持たず、実JMS接続・所有・再送副作用は他ownerへ残す。

## P002-04全1artifact・error profile

所有はPermanentProtocolException一path。H02/M02/T01/X03/N02/B01の実assertThrowsで受信恒久拒否と送信MessageEncodingExceptionを区別、HeaderCodecの再throwとIllegalArgumentException原因wrap双方が当source rawcounterで実行済み。null/短body255/過長1000001/length不一致/未知layout・field破壊・route/property不一致に対し業務object生成前に拒否する。java例外型は資源を所有せず、constructorのmessage/cause保持はjava RuntimeExceptionへ委譲、本文値をerror messageに再構成するcodeなし。

WBSの題名にあるerror応答profileは他owner共通実装も参照し、専有artifact一件だけで全仕様充足とは扱わない。E01/E02/P02及びAUTHERR001～003：PayloadCodecTest.everyResponseLayoutUsesExactErrorFillersAndNoRecords/resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState、AuthenticationErrorProfileTestの実三method、PayloadGoldenVectorTestの独立287hashを対応付けた。通常成功0000/0200とerror、全31responseのF固定/Xspace/Nzero/Bspace・record0、Loginのretry0/1/900・残回数000・固定messageだけ、取消0107の最新stateだけというUI232 §5.1/UI234/236の個別許可を検査する。恒久protocol errorを業務result codeへ変換しない。user不正値・機密echo・不正error filler/型/欠落を拒否する。P09並行expected由来のBUG1285とは別Test/別期待値であり、未是正のP09をこのerror受入へ使用しない。

## 三criteria・限界

contract＝上表の入力/戻り値/例外/offset/個別error条件を既Program仕様Test IDと実JUnit methodへ全件join。scope＝03全5/04全1path・専有RD0/shared参照空を485と一致、既共有実装費を二重計上0。quality＝当各familyの現同source四miss0、全Protocol実84/四100、全六static0・実3701/同byte28を照合、normal/boundary/null/unknown/exception/redactionと資源非該当根拠を明示。終了依存は両項目ともP001-01/P001-02で同source ACCEPTED。全criteria/source/hash/依存を既strict auditで前/候補/後照合してから各leafを認定する。

本票の受入はP002-01/02、DTO全component、現実JMS/全CHR/全PGPTを含まない。正式1964PT/53scope、全体603L115M470B未網羅、工数null、QA051final保留は維持。実時刻・実command・対象source・環境・hashは001/106/公開witness/PG3292 manifest及び元3276/3278私有receiptへ参照し、必要性のない全回帰・配備・業務処理の反復0。
