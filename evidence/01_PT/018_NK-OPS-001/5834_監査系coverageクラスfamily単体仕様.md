# 5834 監査系coverageクラスfamily明細

451、BUG-3802、YKT-2961。021・022の合成XML集計と共有class family validator。所定のowner別report選択を保ち、実CLI、DB、FileStore、Root、VM、実証跡ファイルへ接続しない。

| Test ID | 独立入力差分 | 固定期待 |
| --- | --- | --- |
| PT-OPS-F03-INS-COV001 / 005 | method内だけ未到達1 | 021／022とも拒否 |
| PT-OPS-F03-INS-COV002 / 006 | 本体classからmethodを削除 | 021／022とも拒否 |
| PT-OPS-F03-INS-COV003 / 007 | class行を同名で複製 | 021／022とも拒否 |
| PT-OPS-F03-INS-COV004 / 008 | NoCode内側型に行ありを偽記 | 021／022とも拒否 |

正常は独立固定8命令・1 method・1 class・4行、自然NoCode内側型の空counter、同prefixだけの別型は選択しない。Python工具既存回帰、8独立、正式006の既正規Protocol XML保存整合を記録する。製品PT／正式451／実環境の加算0。
