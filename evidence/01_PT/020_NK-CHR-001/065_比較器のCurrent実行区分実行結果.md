# 比較器のCurrent実行区分 実行結果

WBS-P020-01.02／2、SS355 §5／§8／§10、PT-CHR-DEF081／082。対象工具commitは `3ab80b846e27308aab029821581b113ecaf78fc9`。製品source `62b239d4dad561da007e15a290f8a271a165dda9`。

| 証拠 | 結果 |
| --- | --- |
| PG41334 修正前 | 2件ともCurrent区分を変更しても合格判定、独立期待に対して失敗 |
| PG41336 比較器 | 77件成功、失敗・エラー・skip・選定未実行0。新2件とも固定診断を確認 |
| PG41340 gateの純定義 | 元12件を変更工具に対して実行し全件成功。台帳化wrapperの分母誤認1を元実行を再演せず訂正 |
| PG41338／PG41342 | 同一run original CRCを個別照合。規則methodの2分岐と比較器outerの全指標に到達。既ComparisonResultのobject method3件は局所runで未達。Checkstyle・SpotBugs指摘0、PMD5は従来のメソッド内Mapと一致 |

比較器とreportの定義検査は同じ規則を使う。実環境、Current baseline、CHR、正式coverage・451に加算しない。

[独立結果](evidence/PG41342-p020-current-role-dispositions-v1/manifest.json)
