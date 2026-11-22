# F02 SAXの明示File引数と借用Stream

NK-OPS-001、SS311、WBS-F02-a、SYS-005、BUG-3653／YKT-2871、PG-D-1200。

| Test ID | 独立した期待 |
| --- | --- |
| PT-F02-FILECALL011～013 | Controller・listener・ProtocolがSAXParserへFileを渡す直接呼出を、各所属規則に一件ずつ検出する。 |
| PT-F02-FILECALL014～016 | 同じ三所属の借用InputStreamはこのFile境界で検出しない。 |
| PT-F02-FILECALL017 | Batchのfile担当adapterに対する同File引数はこの境界に該当しない。 |

合成型はcompileと静的class inspectionのみ。JDKの二File overloadと四InputStream overloadを参照し、File型を独立oracleにする。既ImageIO・DOM等の53ケースの回帰を同じ工具で確認する。製品・XML・ファイル操作は実行しない。

PG43018で旧3検出欠落を確認。8237c1443fの新7と既53の合成期待はすべて一致。現Protocol176の許可済み物理を同工具で検査し、5規則0。製品試験とF02正式受入は加算0。[公開manifest](evidence/PG43018-f02-sax-direct-file-v1/manifest.json) SHA-256 `84f7d7ca9f74cf833f6ad8f1faa8c5f271cdee6980eb5cffeb826fa47b471744`。
