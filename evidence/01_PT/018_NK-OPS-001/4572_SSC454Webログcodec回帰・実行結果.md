# SSC-454 Webログcodec回帰の実行結果

PG38414、Core 1224e04183d4f291e97cdb52832c3004bbe41289、Unit 6ac12a450d60268cee795a9f1d9f38b7142783c4。原9と既存weblogOwn001の合計10件、初回成功10、失敗・エラー・skip・未実行0。開始分母9は、旧PG33790にも存在する10番目を含めて実行前に訂正。Testは新規追加0。

JDK25／原合成fixtureの専用JVM。電文goldenと暗号envelope固定期待は維持。診断一箇所は独立SS351に従う。厳格compileは成功。PMDの18件は個別に従前のrule・行・根拠を確認、適用0・未分類0。Checkstyle 0。hold対象のclass初期化0。codecの生136L/12M/1C/50Bは全到達。closeの例外cleanup経路6命令未到達は歴史結果と同一CRC／同数。未実行を成功へ加算しない。六module品質とYKT2674は未完。

証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG38414-p01810-ssc454-web-log-codec-nine-v1/manifest.json SHA256 1a4d901085e4a5d5bc24f46ca46ed80f1ae9012329e2927b8b1f68716efdf1b9。
