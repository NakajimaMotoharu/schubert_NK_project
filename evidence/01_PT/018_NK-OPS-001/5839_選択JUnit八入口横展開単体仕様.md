# 選択JUnit八入口の横展開単体仕様

品質工具NK-OPS-001、RD TST-101、SS354、451、WBS-F03/2-2-b。BUG-3807／YKT-2965、PT-QA-JUNIT-SCOPE002。

対象は034、035、036の通常とreadiness、038、039、040の通常と資源。正常な合成testsuiteと明示0、properties、文字列出力を各入口の件数に合わせて与える。失敗、エラー、skipの欠落、ゼロの非正準文字列、異root、未知の直下要素、出力の入れ子、properties重複、property値欠落、properties中の余剰文字を別々に与え、全入口で拒否を期待する。既存の選択class、method、Test ID、件数および正常XMLは維持する。外部実行は使用しない。
