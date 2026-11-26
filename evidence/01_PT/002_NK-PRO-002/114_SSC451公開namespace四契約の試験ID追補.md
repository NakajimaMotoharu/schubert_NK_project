# SSC-451 公開namespace 4契約の試験ID追補

Program NK-PRO-001〜003。既存試験仕様102の公開namespace 4件を対象に、試験を増やさず台帳用のTest IDを追加した。以前の記録で使ったJUnit classname・methodも引き続き識別子とする。

関連はRD SYS-011、SS322・323・333、SSC-451、451。承認・実装要件の差分なし。対象版はPG45722の 1c927105b6d12de93c3b996846d601692731a804、製品Core cf08e414be9f877b851a387704350d5e7c980209。

各ケースは対象typeがinterface、public constructorとfieldは0、すべての公開メソッドがstatic、固定のメソッド名集合に過不足がないことを確認する。期待値はSSC-451と設計の固定APIから採用。JDKのpublic metadataのみを検査する。ローカル型のため、DB・JMS・ファイル・ネットワークや再送は対象外。

| Test ID | 既JUnit method | 対象 | 独立期待の公開メソッド集合 |
| --- | --- | --- | --- |
| PT-PRO-NS-001 | fieldCodecHasOnlyTheEightDesignedStaticOperations | FieldCodec | encodeText, decodeText, encodeNumeric, decodeNumeric, decodeNumericOrErrorFiller, encodeBoolean, decodeBoolean, requireSpaces |
| PT-PRO-NS-002 | semanticValidatorRetainsBothDesignedEntryPointsOnly | PayloadSemanticValidator | validate, validateScenarioSequence |
| PT-PRO-NS-003 | mediaValidatorExposesNoGrammarCacheOrInstanceOperation | MediaDescriptorValidator | validate |
| PT-PRO-NS-004 | largeResultCodecHasOnlyWriteAndDecodeOperations | LargeResultRecordCodec | write, decode |

実行はPG45722のMaven verify、JDK 25.0.4。同一sourceに製品174、補助2、失敗・エラー・skip各0。Coverageは同一verify内のProtocol module集計 L3639/M1432/C162/B1080、各未到達0。個別試験のcoverageは未分離。実行環境・command・終了と元XMLのSHA-256は下記証跡。関連の新規BUGなし。

[元実行manifest](evidence/PG45722-current-protocol-176-module-verify/manifest.json)
