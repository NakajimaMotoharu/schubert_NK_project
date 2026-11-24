# SpotBugs証跡の診断と物理名簿の単体仕様

NK-OPS-001、WBS-G08、F03、SS354、451、BUG-3794、YKT-2958。対象はSpotBugs原XMLを読む品質工具。入力は合成XMLと固定のcompiled Main名簿。

| Test ID | 独立入力と期待値 |
|---|---|
| PT-QA-SB-SHAPE001 | 二つの正規ClassStatsを持つ原XMLは受理し実際の2を返す。 |
| PT-QA-SB-SHAPE002 | 診断が正規Errors外のErrorまたは入れ子MissingClassにあれば、カウンタ0でも拒否。 |
| PT-QA-SB-SHAPE003 | ErrorsやFindBugsSummaryの入れ子重複、または入れ子だけの場合は拒否。 |
| PT-QA-SB-SHAPE004 | 正規欄と一致しても欄外のClassStatsが余分または重複なら拒否。 |
| PT-QA-SB-SHAPE005 | 元019の全正常・不足・件数差・重複・診断canaryを維持。 |
| PT-QA-SB-SHAPE006 | 正規集計にcompiled metadataを登録する場合は一致を要求し、不足や余分を除外で埋めない。 |

入力、期待値、実際値とsourceはPG44526に固定する。現製品解析や実環境実行は行わない。原実行終端・同source全451を別途要求する。
