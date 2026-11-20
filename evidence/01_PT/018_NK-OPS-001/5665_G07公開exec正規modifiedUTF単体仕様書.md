# G07 公開exec形式のmodified UTF単体仕様

WBS-G07、BUG-3480／YKT-2776、451と3021の限定形式境界。対象は `public_jacoco_exec_format_v1.parse`。テストは完全に合成したメモリbyteを使う。製品クラス、実coverage agent、既存raw evidence、外部環境に接続しない。

| Test ID | 入力と操作 | 独立した期待値 |
| --- | --- | --- |
| PT-G07-EXECUTF001 | sessionとclass名に、2/3byteの過長ASCII、直書きNUL、NULの別表記、途中で切れた3byte、通常UTF-8の4byteを一つずつ入れて解析 | Java writerの1/2/3byte形式に当てはまらないため、全12入力を値なしの固定ValueErrorで拒否 |
| PT-G07-EXECUTF002 | 正規ASCII、正規NUL、2/3byte境界、サロゲート対を固定byteで両フィールドへ与える | 各8 code unit、ASCIIは各0、時刻1件、class1件、probe3件中2hit、全byte消費 |
| PT-G07-EXECUTF003 | 既19形式vectorの固定期待値と4 API型拒否を、変更された形式読取で検証 | 正常5、異常14、型4を同じ独立oracleどおりに判定し、印字ASCII集計と既存のpadding検出を維持 |

`PYTHONPATH=tools/quality python3 -B -m unittest tools/quality/public_jacoco_exec_format_utf_test.py`。実行source・終了コード・証跡hashは結果manifestに結ぶ。秘密値とsession/classの生値は記録対象外。
