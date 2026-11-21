# 5670 strict execの名前なしclass記録を拒否する試験

WBS-P018-08.03/2、SS354、BUG-3491／YKT-2784。Javaのstrict originalとPythonの独立subsetで、クラス名長0の実行記録をcoverageの入力として拒否する。既存の非strict経路と公開形式集計の役割は継続する。

| Test ID | 入力 | 期待 |
|---|---|---|
| PT-OPS-EXEC-NAME001 | 公開fixture header、正規session、既知X、別CRCの名前なしrecord。subsetの選択空／Xを指定 | どちらも固定エラー。正規Xも合格へ計上しない |
| PT-OPS-EXEC-NAME002 | 同元bytesと自前のPlain.classをJava strictへ渡す | 終了1・固定診断、coverage出力0 |
| PT-OPS-EXEC-NAME003 | 同じstreamから名前なしrecordを除いた独立正対照。修正後は既存の当JDBC単一execも読取 | 公開fixtureと既存正規記録は読み取れる。新規製品試験・native実行なし |

既subset suite及びG07集計の公開異常UTF suiteを確認する。公開fixtureには実session・シークレット・製品ソースを含めない。実採取の所有・現source/boot/receipts及び451を別条件として保持する。
