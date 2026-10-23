# 1567 Registry欠測接続 単体テスト仕様書

2026-10-23、PG-D525/P018-09/C07共有費0。着手0.5/1/2pp・上限10pp、共有10/残90/reset1793306748、元開始0。RD MON005～013/UI252/SS351§7・10。既72key ownerのAlertRegistry.interruptContinuity(condition,service,elapsed)とMonitoringPolicyEngine.observationMissingを、既Lifeの同APIへ接続する。新target/collector/clock/clearance/制御/外部状態を取得0。欠測でevent/count/firstSeen/lastSeen/criticalを変えず、回復期間だけを切断する。外部Durationを使う従来engine入口は観測期間の真正性を証明せず、そのcaller責務も変えない。

|Test ID/method|独立期待値と根拠|
|---|---|
|PT-OPS-MONMISSING001 / monMissing001|12×6=72のregistry key、各抽象WARNING state/count1/同UTCを保持。正常1秒→欠測300秒→正常301秒から改めて5分必要、600秒open/601秒close。全conditionの本来severity再判定ではなく共通registry状態契約の試験 |
|002 / monMissing002|engineのnull condition/service/elapsed、負・逆行で無変更、別keyの時点を混同しない。未知状態をNORMAL/原因撤去へ補完しない |
|003 / monMissing003|一ownerの64同時刻欠測、event/count/UTC不変・新正常期間から満5分でclose、immutable snapshot・自己所有executor終端 |

新3＋必要同package70=73PT/11suiteを一固定sourceから実行。Production expectedを呼び出して生成せず、固定72/1/300・601秒/UTC/状態表を使用。allkey列挙には閉enumをscope走査として使用するが個数72/回復境界/count/不変期待はliteral。Main実19class＋metadata1、四counter100/単一sessionCRC/静的、正規Jar byte・追加src所有を検証。設定5/4や旧4222/common44と合算0、必要回帰以外の成功確認再演0。実collector/配布/全体451/native/CHR/正式は未受入、HOLD/QA051final/PTALT0/工数null維持。
