# 5671 strict実行記録class名の実行結果

WBS-P018-08.03/2、SS354、仕様5670。BUG-3491。PG41414では空名class記録を元Java／元Pythonが受理。strict Javaの拒否と、Pythonには既定の形式読取互換を保つ明示strict引数を適用した。

PG41416でPython既定互換の期待1件にエラーを出した劣化をBUG-3492／YKT-2785で先行登録。元writer-formatテストの期待値はそのまま。PG41418でPython 36/36、元自試験12、strict Java負1・正1とlegacy正1、現PG41410元execのJava/Python読取を確認。Javaの負は診断あり・coverage出力0。実native、製品試験、coverage合算、正式加算各0。

- evidence/01_PT/018_NK-OPS-001/evidence/PG41414-strict-exec-empty-class-red-v1/manifest.json SHA-256 7d9985b2d4976adab65aed7eb0356f7702303795ffd5030b9dd2eaabfc38115b
- evidence/01_PT/018_NK-OPS-001/evidence/PG41416-strict-exec-empty-class-green-v1/failure.json SHA-256 46f7d3515cac049b3700f6e9496041431e339c452d824f0c3343d5df355144d0
- evidence/01_PT/018_NK-OPS-001/evidence/PG41418-strict-exec-empty-class-green-v2/manifest.json SHA-256 bf7a28b50b0fa49a3564d25a11e786386b7a8f956a76a7ba510d585f175fc682
