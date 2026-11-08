# Payload codec・意味検証のmethod参照結果

Production Main `7aed8eace7c844c2f79f2e39db766faf914890d5`、Test source `64f3a72753434347889f0eabd5d9f9dca67c6bfb`。P00202の2 Source、3 physical class、2測定class。raw63 = 公式61 + 標準filter2（空utility constructorとcompiler switchmap）。標準filterは24594の同一class SHA/CRCの既存証拠を使用し、新しい除外や実行はない。

PG24822の順方向照合・PG24824のXML起点逆照合は終了0。実行済みnormal120（PG24640/24642）の38個のケースを、入力・独立golden・失敗境界・例外・helper・method signatureへ結び付けた。ResultCode overloadとboolean/private overloadを区別し、ページ上限、日数、password境界、ログ種別を現在の専用ケースへ対応。関連RD MSG/MQ、UI232～236、SS322の参照は承認済みorigin/mainとのbyte一致を確認した。case単位のprobe帰属はnull、全分岐の個別oracle検証は未認定。

元run参照の集計はL491/M61/C2/B347/I2392、missed全0。compiler switchmapの測定空集合を自然B0と混同しない。新規製品PT・compiler・coverage実行0。BUG2556/YKT2280は証跡field名の工具誤りを修正前PG24826へ保存し、正式field officialMeasuredMethodsを厳密型で参照して是正。PG24828で同系4工具を確認し、旧2は無変更・現producer修正・独立post正常、再現元の成功試験再演0。PG24830はWBS旧値を全保持し、485/486の参照観測だけを追加、root hashと4否定検査を確認。

正式1964PT/53scope、unique520、candidate114/pending12/whole93、新規leaf0、工数率nullは不変。全451/G13やowner受入を宣言しない。既存全HOLDを維持する。

|成果|path|SHA-256|
|---|---|---|
|順照合|`evidence/01_PT/018_NK-OPS-001/evidence/PG24822-payload2-method61-trace-v1/manifest.json`|`005cf9b180b97b469eb040fc15f9eed854df77388807138e67e1f5a8f4586005`|
|独立逆照合|`evidence/01_PT/018_NK-OPS-001/evidence/PG24824-payload2-method61-trace-independent-v1/manifest.json`|`fd64441513f3fe65bd21c4a3e44a18112a26a121d0faa0065e877f7ccae231c3`|
|修正前|`evidence/01_PT/018_NK-OPS-001/evidence/PG24826-payload-filter-schema-before-v1/manifest.json`|`e0c7b2c892cbe2889e3a8b2de3d194de52fe860c34c95ad939624e7ba94ffeeb`|
|横展開|`evidence/01_PT/018_NK-OPS-001/evidence/PG24828-payload-proof-schema-spread-v1/manifest.json`|`77b1d335c8b632c6f01a01d6f3144d261e70a9f6913eff7f415804d0675d89ff`|
|WBS観測|`evidence/01_PT/018_NK-OPS-001/evidence/PG24830-p00202-all2-wbs-observation-binding-v1/manifest.json`|`7932edde57a3d2b39e059f68c1c8d1f275ce21dbe1df7048e1ebe0208dc139b4`|

実行commandは815/816/818 Python工具（各終了0）。製品試験commandは今回未実行。前提と38Test IDは814 scope・case-oracles.json、各method対応はmethod-trace.jsonを参照。元期待値はSS byte位置・独立固定値/境界値で、production methodからexpectedを生成しない。
