# Current合成mappingの並行四試験

WBS-P019-03.03/2、F03、SS331・343・354、BUG-3940／YKT-2997。対象は表の既試験だけ。元仕様の別列、byte列、借用stream終端、元入力・期待値と依存を保持する。

| ID | 選択メソッド | 独立期待値の元仕様 |
| --- | --- | --- |
| PT-MIG-ENTRYMAP024 | CurrentScenarioEntryMapperTest#entryMap024ConcurrentCallsShareOnlyImmutableMappings | [103](103_Current entry対応・COPY接続・独立二十四仕様.md) |
| PT-MIG-FILEMAP024 | CurrentScenarioFileMapperTest#fileMap024FiniteParallelCallsConsumeOnlyPrivateClaimMaps | [107](107_Current file・宣言asset・COPY接続・独立二十四仕様.md) |
| PT-MIG-AUDIOLINKMAP024 | CurrentAudioLinkMapperTest#linkMap024FiniteSharedMapperCallsHaveOwnedSnapshots | [120](120_Current音声link宣言対応・独立二十四仕様.md) |
| PT-MIG-MAPVERIFY016 | CurrentMigrationMappingVerifierTest#mapverify016SharedVerifierHasFiniteIndependentSnapshots | [138](138_対応表読戻し期待SHA・形式ID結合全976仕様.md) |

各workerと入力の個数、5秒結果取得・10秒終了は元仕様に従う。一次失敗と終了失敗が重なる検証は既MigrationFixtureWorkers試験を参照する。各今回TestIDの終端を当正規Bootstrapの一つのexecで取得。通常の既済別試験、実DB／原本／領域アクセスは対象外。
