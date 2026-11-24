# 5831 正式coverage収集の同一クラス名簿と内訳

WBS-F03/2-2-b、451 §5、BUG-3797／YKT-2961。対象は tools/quality/006_collect_scenario_evidence.py の validate_module_coverage と実コンパイル名簿の呼出境界。独立期待は既存正規Protocol XMLと同一targetのclassの名前。対象外は別collector、実サービス、別run、プローブ網羅の再計測。

| Test ID | 入力 | 固定の期待 |
| --- | --- | --- |
| PT-OPS-F03-COV-ROSTER001 | 元XMLのclass一件を削除 | 物理名簿の欠落で拒否、親合計が同値でも終了失敗 |
| PT-OPS-F03-COV-ROSTER002 | 元XMLのclass一件の名前だけ差替 | 元の欠落と未知があるため拒否 |
| PT-OPS-F03-COV-ROSTER003 | 元XMLのclass一件を重複 | 重複として拒否 |
| PT-OPS-F03-COV-ROSTER004 | 元XMLのCode持ちclassからmethod一件を削除 | 加算可能なclass内訳と不一致で拒否 |
| PT-OPS-F03-COV-ROSTER005 | method instructionのcoveredを別値へ置換 | 加算可能なclass内訳と不一致で拒否 |

正常はPG43646の四指標3551/751/162/1080、class XML169、package metadata 7（測定命令のないpackage-info）を持つ既存XML。独立比較は入力ファイルを変更せずメモリ内コピーへ一点操作する。真のsource/runは旧PG43646のまま。ローカルPython 3でtool単体と独立後確認を実施し、通常製品PT・451正式受入・coverage計数を増加しない。終端とハッシュはPG44562 manifestへ保存する。
