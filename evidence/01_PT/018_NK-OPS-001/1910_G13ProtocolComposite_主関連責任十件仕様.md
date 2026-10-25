# G13.07・protocol複合source十件の主担当/関連担当

2026-10-25 13:57 JST、source64446不変更、G13_PROTOCOL_COMPOSITE10_EXPLICIT_V1、開始.5/2/4pp・cap10、fresh65残35/reset1793382075（04:56:45UTC）。全core/正式受入の再認証ではなく、未登録291中のprotocol十件だけを既source/原PT仕様/元WBS責任へ対応する。

以下のpathは`src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/`に対する相対path。複数の本物のMain責任を一つと偽らず、主担当/cost候補と関連WBS全集合を区別。実行費はG13.07一回のみ、主担当へ元費用を再配賦しない。原941のMain担当を変更しない。

|source|主担当/cost|主な製造責務（既Main）|原PT/設計根拠|
|---|---|---|---|
|codec/AuthenticationErrorProfileTest.java|WBS-P002-02|PayloadCodecのerror payload encode/decode|PT-CODEC-AUTHERR-001/原codec仕様§追加error profile、UI234|
|codec/MessageCodecTest.java|WBS-P002-03|HeaderCodec/transport/header-message検査|WBS selector MessageCodec/HeaderCodec、UI232/SS322|
|codec/PayloadGoldenVectorTest.java|WBS-P002-02|PayloadCodec全layout golden/record|PT-PRO-002-P07/P08/P09、UI233..236/SS322|
|codec/ScenarioRecordEncodingTest.java|WBS-P002-02|PayloadCodec.encodeRecord/decodeRecord|PT-SCN-008-W03、UI234独立offset|
|header/HeaderModelTest.java|WBS-P001-01|CommonHeader/MessageKind/InteractionKind/ResultCode|PT-PRO-001-H01..03、UI232/SS323|
|layout/IndependentNamedFieldOracle.java|WBS-P001-03|TypedPayloadValues/SS323 named DTOの独立fixture oracle|PT-PRO-001-T01/T02、named-types-ss323.tsv/named-accessors-independent.tsv|
|layout/LayoutMetadataTest.java|WBS-P001-02|LayoutRegistry/LayoutDefinitionの64定義|PT-PRO-001-L01..03、UI233/SS322323|
|layout/SemanticFieldValueTest.java|WBS-P001-03|TypedFieldValuesのnamed field Java型変換|PT-PRO-001-T03、SS323§2、semantic value補助はP00201関連|
|layout/semantic/EnumWireCompatibilityTest.java|WBS-P002-01|AnswerState等wire semantic enum互換|PT-PRO-F03-ENUM001、SS323/333/354、他module enum関連は保持|
|layout/semantic/ProtocolSemanticTypeTest.java|WBS-P002-01|wire enum/semantic range値を固定literalと比較|PT-PRO-001-T04、UI234..236/SS333351|

処理：元9386v3の有限十source/CP参照と現在hash・正常9246snapshotを照合し、JDK javap metadataを別に確認する。主担当は上記literal表で凍結し、CP参照数/多数決/名前だけから計算しない。関連Main担当は元graph集合をそのまま保持し、Primaryが集合内か、named DTO fixtureの独立根拠に含まれることを要求する。reflectionのあるIndependentNamedFieldOracleは実行しない。静的fixture列にあるnamed DTO名と当Main source/class/既ownerを確認するだけで、reflectionやPTの代替成功を加算しない。

旧673canonicalを保持、十個だけexact登録し、primary/cost別field不一致・関連集合改変・隣接path・hash/status等のnegativeを確認する。見込登録1498→1508/1789、Test533→543/824、残291→281、限定673→683。正式1964-53/17-190/工数null/QA051final/全actualHOLDと元予算/941943を保持。BUG1746全WBS auditHOLDは別。

target compile/load/JUnit/VM/DB/鍵/外部job0、既成功PT/全回帰確認再演0。ここでのfile責任を全method/要件/TestIDの完了へ変換しない。終了後も残281の独立PG/PTへ自走する。停止はfresh現在窓残10以下/取得不能等、旧累計80/90を適用しない。
