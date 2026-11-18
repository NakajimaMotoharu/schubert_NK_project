# BUG-3260 API・Web GC登録fixtureの有限終了単体仕様

NK-OPS-001、RD171/UI252/SS351/354、WBS-F03/2-2・P018-09、YKT-2387。APIGC001〜016／WEBGC001〜016。元[API仕様2841](2841_API標準SDK三whole44_単体テスト仕様.md)と[Web仕様2837](2837_Web標準SDK五whole73_単体テスト仕様.md)の依存順、通常、null、未知mode、owner拒否・例外同一性、close後条件を維持する。

各013は4 worker、64の独立合成ownerとregistry、期待するbind・close各1、合計64、Future get10秒。finallyで停止を要求し、10秒以内に全worker終了を確認。GC SDKは自己所有child JVMのみ、強制GC、外部JVM、attach、構成操作や運用データは不要。Root NullAway、静的、全32、独立CRC/XMLと対象生counterを検証する。生未到達は保全・報告する。
