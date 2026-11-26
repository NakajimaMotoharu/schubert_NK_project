# 五宣言行の純JDK代理と並行一次診断

WBS-P019-03.02/2、F03、SS343・354、BUG-3964／YKT-2997。対象は表の既試験だけ。各元仕様の固定行、borrowed Connection、各owned Statement/ResultSetと元の64呼出を維持する。

| ID | 選択メソッド | 独立期待値の元仕様 |
| --- | --- | --- |
| PT-MIG-AUDIOLINKREAD020 | CurrentAudioLinkProjectionReaderTest#audioLinkRead020SharedStatelessReaderUsesOnlyPerCallOwnedResources | [118](118_Current音声link三列projection・独立二十仕様.md) |
| PT-MIG-AUDIOREAD020 | CurrentAudioProjectionReaderTest#audioRead020SharedStatelessReaderUsesOnlyPerCallOwnedResources | [111](111_Current音声十列projection・独立二十仕様.md) |
| PT-MIG-ENTRYREAD020 | CurrentScenarioEntryProjectionReaderTest#entryRead020SharedStatelessReaderUsesOnlyPerCallOwnedResources | [101](101_Currentシナリオ十列projection・独立二十仕様.md) |
| PT-MIG-FILEREAD020 | CurrentScenarioFileProjectionReaderTest#fileRead020SharedStatelessReaderUsesOnlyPerCallOwnedResources | [105](105_Currentシナリオfile八列projection・独立二十仕様.md) |
| PT-MIG-SPEAKERREAD020 | CurrentSpeakerProjectionReaderTest#speakerRead020SharedStatelessReaderUsesOnlyPerCallOwnedResources | [076](076_Current話者六列読取り・独立二十仕様.md) |

各workerと入力の個数、5秒結果取得・10秒終了は元仕様に従う。一次失敗と終了失敗が重なる検証は既MigrationFixtureWorkers試験を参照する。各今回TestIDの終端を当正規Bootstrapの一つのexecで取得。通常の既済別試験、実DB／原本／領域アクセスは対象外。
