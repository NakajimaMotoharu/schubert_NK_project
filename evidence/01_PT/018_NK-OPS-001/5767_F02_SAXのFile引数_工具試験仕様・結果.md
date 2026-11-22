# F02 SAXの明示File引数と借用Stream

NK-OPS-001、SS311、WBS-F02-a、SYS-005、BUG-3653／YKT-2871、PG-D-1200。

| Test ID | 独立した期待 |
| --- | --- |
| PT-F02-FILECALL011～013 | Controller・listener・ProtocolがSAXParserへFileを渡す直接呼出を、各所属規則に一件ずつ検出する。 |
| PT-F02-FILECALL014～016 | 同じ三所属の借用InputStreamはこのFile境界で検出しない。 |
| PT-F02-FILECALL017 | Batchのfile担当adapterに対する同File引数はこの境界に該当しない。 |

合成型はcompileと静的class inspectionのみ。JDKの二File overloadと四InputStream overloadを参照し、File型を独立oracleにする。既ImageIO・DOM等の53ケースの回帰を同じ工具で確認する。製品・XML・ファイル操作は実行しない。
