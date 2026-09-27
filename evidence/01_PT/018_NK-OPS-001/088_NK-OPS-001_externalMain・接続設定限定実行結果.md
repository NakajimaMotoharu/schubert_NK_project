# PG285/286 限定実行結果（正式未認定）

2026-09-27 JST、Linux/JDK25.0.4/Maven wrapper、branch dev-foundation、base3790557e6からの変更。API限定15:58:47終了exit0・19PT、Web限定15:59:47終了exit0・20PT、failure/error/skipped0。API CFG6/LOAD5/INPUT4/MAIN4、Web CFG7/LOAD5/INPUT4/MAIN4。019 collector負canary103/103成功。外部JVMの実際exit70/stdout空/fixed stderrはMAIN004のassertで確認。実業務success/実NK CHRは未実行。

BUG263を経た同日追加再試験: API16:04:49終了exit0・19PT、Web16:06:21終了exit0・20PT。mainをJava25標準instance mainとし、native default constructorはOS exit、限定constructorの終了portは要求codeを独立確認する。本番argv/Unit class名/起動拒否は不変。API/Web mainとWebNonSecretConfigのinstruction/branch/line/method/class missed0を限定reportで照合。除外なし。

source SHA-256: ApiProcessMain `fb55f7d860b18f85eafefed03fde0971f1072acc0eb54d50e69bff12823bc80d`、WebProcessMain `1685a74a66448be66f05be3eccd161de3e89c4f7028bd317adac42498d117b7d`、WebNonSecretConfig `671f1e21fbeb79bccea4275eea4118487c2ee93d4dd7b60b9e3ca5183f7859ef`。source commitは本書と同時保存commitから追跡する。086/087の限定command、実logは/tmp/PG285-api-instance.log・PG286-web-instance.log（次の正式収集前の暫定log、これだけを永続認定根拠にしない）。

BUG261 RED exit1（Web CFG007 unknown）、BUG262 RED exit1（API MAIN002未知IllegalArgumentが伝播しない）を経て修正。BUG261/262、YKT195/196は限定再試験済・正式再試験待ち。native startは必須assembly未結線の固定IO50であり、入口だけをR1完了にしない。

JaCoCoは限定test後の対象classを照合し、全moduleの100%・静的解析・trace・53scope/hash正式gateは未実行。最後の正式認定は既存run PT-WEB-20260925-24/source858713c0b、1,964PTで不変。新規sourceのPG/PT完了認定はしない。
# 後続PG288との区別

本書のAPI main hash/100%はResource scope結線前の限定実行時点の履歴。PG288でnative経路を変更した後のmainは未網羅が残り、正式合格ではない。最新のsource/hashと未実行範囲は092/provisional PG288 manifestを参照する。旧結果を新sourceへ転用しない。
