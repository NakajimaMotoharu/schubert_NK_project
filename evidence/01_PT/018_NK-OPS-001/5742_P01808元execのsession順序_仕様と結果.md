# P018-08 元execのsession順序の試験仕様と結果

NK-OPS-001、WBS-P018-08.03/2、SS352／354、451 §5/6、BUG-3643／YKT-2862。固定JaCoCo 0.8.15 RuntimeData.collectはsessionを出力してから実行データを出力する。元stream形式だけを校正対象とする。JDK25.0.4と固定JaCoCo/ASMで外部操作のない小さいclass fixtureを用いる。

| Test ID | 独立条件と期待 |
| --- | --- |
| PT-OPS-EXEC-ORDER-001 | 固定ヘッダー、UTC 1000/1001のsession、独立CRC計算のclass record。元形を受け入れ、単一probeにhit。 |
| PT-OPS-EXEC-ORDER-002 | sessionのみを受け入れ、対象classの実行証拠なしを明示。 |
| PT-OPS-EXEC-ORDER-003 | 選択classがsessionより先。Java strictとPythonは拒否、診断、coverage行0。Javaの従来モードの読取は維持。 |
| PT-OPS-EXEC-ORDER-004 | 対象外classがsessionより先で、対象classは後。両方式はstreamを拒否し、後続classを結果へ計上しない。 |

旧工具は負条件2件×2方式で期待不一致。正条件2件は成功。是正 `71608bf048a977eba653371a28dc3851c65f55b9` は解釈を二工具で統一し、計37工具試験、今回の4件を含め全成功。保存PG42902・PG42904は元execと九物理のhash・CRCを再確認し、是正後も無フィルター集計行・method・欠落を元結果と一致確認した。過去のJUnitは再実行0、製品code変更0。P018-08現native、451全製品と正式受入は継続。

実行 `python3 -B -m unittest discover -v -s tools/quality -p 'jacoco*test.py'`。公開manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG42910-p01808-original-exec-order-v1/manifest.json` SHA-256 `bca9b2a53a3934659aeb15027f9b869a778540ae4b38709b2ef0a41b3a9cfbd6`。元実行・固定工具・原exec SHA-256はmanifest参照。
