# 1755 HTTP histogram CDF寿命・独立追加PT

NK-OPS-001/RD171/UI252/SS351/1725/1752/1754、WBS-P018-09/C07、group1982。開始0.5/2/5pp・cap10、候補Main source7cba540ba同byte/正常8270を参照する。後続索引は1752/1751/1725、元httpDur005はmax/count/sumの窓経過だけでCDF未検証。この新三観点は確認だけの元12再演ではない。

|Test ID|fixture/操作|独立期待値|
|---|---|---|
|HTTPCDF001|MockClock、expiry1秒/buffer2、供給ns=0/1/50000000/50000001/5000000000/Long.MAX_VALUE二件。3秒進め再snapshot→1ns追加→100日進め再snapshot|count7、有限9CDF=3/4/4/4/4/4/4/4/5、3秒後も同値でmax0。追加後count8/CDF4/5/5/5/5/5/5/5/6、100日後も同値。sumは独立BigDecimalの整数ns加算/1e9、binary64全範囲の固定8µs誤差内、Production出力をexpectedへ使わない|
|HTTPCDF002|同MockClock・別registry二owner、A50ms/B5秒、3秒経過後Aだけ50ms+1ns追加|A/BのfiniteCDFを別literalで保持、maxだけ0へ、別ownerへ増分漏れなし。sourceをexport操作でcloseしない|
|HTTPCDF003|own4worker・64供給イベント各1ns、有限Future待機/cleanup後3秒・さらに3秒経過|count64/全9CDF64/sum64ns/max0を両時点で維持。実thread timingをlatency oracleにしない|

すべてordinary memory SDK PT、実HTTP/Browser/DB/JMS/VM/Root/時計OS変更なし。bucketは秒のSS九境界に対応するliteral ns、cumulative countの寿命は窓maxと区別する。元SDK bytecodeだけから成功と推定しない。

まず新三件だけを同source六Jar/SDKでfresh JUnit実行（PG8284）。既Main変更0なら新限定観点のactual成功だけを記録し、旧source coverageと合算しない。既実装が累積histogram契約に違反したら修正前915/916起票→原因/最小是正→必要既12＋新3等を同新sourceで実行し四coverage100/静的/traceへ。snapshot/operator/fixtureの誤りは先に独立根拠と照合し、実際値へoracleを合わせない。

未実行/失敗をPASSへしない。1756と公開manifestへ実command/JDK/OS/source/actual XML/終了/exec/hash/BUG/再試行費を記録する。現時点PT0/coverage未測定、正式1964-53/原190新受入0/工数null/QA051final/PTALT0/全actual HOLD不変。次Timer/counterの標準encoderへ継続、通常小区切り停止0。
