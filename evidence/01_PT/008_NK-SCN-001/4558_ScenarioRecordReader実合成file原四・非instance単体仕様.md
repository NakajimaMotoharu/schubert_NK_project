# ScenarioRecordReader 単体テスト仕様

NK-SCN-001、WBS-P008-06・F03。RD FIL-006/007、UI234/237、SS333 §6、451。対象は借用済みchannelの `ScenarioRecordReader.read/scan` と固定namespaceのprivate constructor。既試験の仕様は001のPT-SCN-008-RD03/RD04を参照。元4件はPG15854/15856/15859と既Jupiter XMLを参照し、期待値・元4試験全文・手書きScenarioFileFixtureを保持する。

| ID | 入力と実施 | 独立期待値 |
|---|---|---|
| PT-SCN-008-RD03 | JUnit専用一時領域の手書き4800 byteレコード1、201、10000件、借用channelを使用 | 固定順序と字段値を元UI黄金値で照合。最大buffer 4800、全長の2回読取り、巻戻し1回、結果immutable、channelを閉じない。 |
| PT-SCN-008-RD04 | null、位置不正、閉じたchannel、短い／長い入力、SHA不一致、進捗0、I/O例外、二読み間の所有合成内容差分、本文・順序違反 | 元Oracleの段階・例外を維持。独立固定offset・JCA digest・合成負値によって、部分結果なしとchannel所有を照合。 |
| PT-SCN-008-NAMESPACE | 対象binaryの無引数constructorのmodifierを確認し、専用fixtureで一度呼ぶ | final class、private constructor、通常入口static、インスタンス生成が固定 `AssertionError("static namespace")` で拒否される。アクセシビリティをfinallyで元へ戻す。 |

製品の業務経路・公開ABI・byte処理は変更しない。正負条件は当whole5で実施し、旧測定の自然除外や別sourceの成功を新runへ加算しない。使用可能な対象は自有の合成fileのみ。channel保持・実マスタ・実DB・native・署名／鍵・権限・配備に関する状況は対象外。OS/JDK/command/exit/source/test hashes/coverageはPG38208以降の公開manifestに記録し、全Codeと四counterを同一run・物理CRCで検証する。BUG-3212、YKT-2664。
