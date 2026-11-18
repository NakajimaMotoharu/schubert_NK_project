# BUG-3261 API GC固定modeが一致する条件の単体仕様

NK-OPS-001、RD171/UI252/SS351/354、F03/2-2・P018-09、YKT-2691。ApiGcMetricRegistration.install。元仕様[2841](2841_API標準SDK三whole44_単体テスト仕様.md)のAPIGC001〜016を保持。PG39214のAPI raw 14/16分岐を出発点にする。Web結果は当実行へ加えない。

APIGC017は固定modeと等しいJava hashを持つ異なる2値。同じhashが正規modeを許可する条件にならないことを確認する。独立計算はASCII値を `h = 31h + ord(c)` で畳み込む。末尾2文字の左を1下げ、右を31上げ、64,921,139／2,095,255,229になる別文字列を固定する。期待はどちらもIllegalArgumentException、固定CONFIG_INVALID、registry照会0・owner callback0・factory0・処理中close0。出力・期待は製品mode判定から生成しない。

製品Mainは不変。Root static、元16＋新1単一実行、独立XML/CRCとAPI対象の生四counter。実環境のmode変更、外部endpoint、外部JVM、その他SDKへの接続は対象外。
