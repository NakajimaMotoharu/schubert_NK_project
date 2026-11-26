# 移行mapping四並行条件の一次診断

WBS-P019-03.02/2、F03、SS343・354、BUG-3956／YKT-2997。対象は表の既試験だけ。元仕様の別列、byte列、借用stream終端、元入力・期待値と依存を保持する。

| ID | 選択メソッド | 独立期待値の元仕様 |
| --- | --- | --- |
| PT-MIG-AUDIOMAP024 | AudioMigrationMapTest#audioMap024FiniteConcurrentCallsHaveIndependentOutputs | [116](116_Current音声ID対応・asset・ms変換・独立二十四仕様.md) |
| PT-MIG-ORDER012 | ScenarioEntryMigrationMapTest#order012ConcurrentIndependentReturnOwnership | [011](011_Scenario現行ID順移行対応・独立十二仕様.md) |
| PT-MIG-FILEORDER012 | ScenarioFileMigrationMapTest#file012ConcurrentReturnsRemainIndependentlyOwned | [013](013_Scenariofileゲーム内順と前後対応・独立十二仕様.md) |
| PT-MIG-SPEAKERMAP024 | SpeakerMigrationMapTest#speakerMap024FiniteSharedMapReadersRetainIndependentRowsAndTerminate | [074](074_Current話者ID対応と既存列保持COPY変換・独立二十四仕様.md) |

各workerと入力の個数、5秒結果取得・10秒終了は元仕様に従う。一次失敗と終了失敗が重なる検証は既MigrationFixtureWorkers試験を参照する。各今回TestIDの終端を当正規Bootstrapの一つのexecで取得。通常の既済別試験、実DB／原本／領域アクセスは対象外。
