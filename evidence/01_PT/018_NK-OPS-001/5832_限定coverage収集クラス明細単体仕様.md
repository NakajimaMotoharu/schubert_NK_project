# 5832 限定coverage収集クラス明細

451 §5、F03/2-2-b、BUG-3798、YKT-2961。tools/quality/039・040のvalidate_coverageと共用のクラス明細検証。独立fixtureの一つの実行可能メソッドは1 method、8命令、2分岐。親classは3行、1class。実JMS／DB、元製品PT、正式受入なし。

| Test ID | 入力 | 期待 |
| --- | --- | --- |
| PT-OPS-F03-SEL-COV001 / 005 | メソッドだけでmiss 1 | 039／040とも拒否 |
| PT-OPS-F03-SEL-COV002 / 006 | メソッドを削除 | 039／040とも拒否 |
| PT-OPS-F03-SEL-COV003 / 007 | 同じ署名のメソッドを複製 | 039／040とも拒否 |
| PT-OPS-F03-SEL-COV004 / 008 | class集計の同名counterを複製 | 039／040とも拒否 |

正例の039はBRANCHが必須、040はBRANCHを持たない実装を許容する既条件。元006の正常なアーカイブ入力を共通化前後で比較する。Python 3の工具回帰と独立後確認を実施してPG44564に終端・ハッシュを保存する。
