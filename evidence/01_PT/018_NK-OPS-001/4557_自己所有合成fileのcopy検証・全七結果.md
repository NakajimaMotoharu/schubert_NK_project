# 4557 自己所有合成ファイルの単体試験結果

Core `b00f871804b6d25f1c3e5e6d3b77d7bcca340923`、Unit `b00f871804b6d25f1c3e5e6d3b77d7bcca340923`、run `PG38196-BORROWED-FILE-WHOLE7`。仕様4556に従い、元5件と非インスタンス契約2件を同じJVMで実行した。7件成功、失敗・エラー・skip・未実行0。専用一時ディレクトリは同一UIDが所有し、実行後に空であることを確認した。独立照合で180クラスのSHA/CRC、単一exec、XMLケース集合を確認した。

対象2クラス、line 43・method 4・class 2・branch 22・instruction 185はすべて網羅。元5件のsource byte、依存178 class byte、全可視性ABI4は一致。製品差分は両private constructorの固定AssertionErrorのみ。Root compiler NullAway/Werror、SpotBugs Max/Low、Checkstyle、書式は成功。PMD 10件はPG38194に個別根拠を保存した。

BUG-3209を当範囲で完了。YKT-2664の他候補は未完。F03、P008-03、P009-04へ限定証拠を返却した。正式元項目の増加0。モデル切替後の共有差は当群のreset識別値が不一致のためnull、専有実費null。計画上の追加完了価格は2pp。

証跡 `evidence/01_PT/018_NK-OPS-001/evidence/PG38198-borrowed-file-whole7-independent-v1/manifest.json` SHA256 `9a43a88185a4cf30dc6746bd2709f06c427cc7321de5fac67382606a619292af`。
