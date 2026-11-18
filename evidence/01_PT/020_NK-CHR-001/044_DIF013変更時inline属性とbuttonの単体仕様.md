# DIF-013 Game変更時のinline属性と代替buttonの比較単体仕様

NK-CHR-001、`ArtifactComparator.compare`、WBS-P020-01.02/2、BUG-3321、YKT-2699、TST-002、UI264 CHR-S02／DIF-013、SS352・355 §8。Currentの `CHR-S02.json` で `gameOnchange` は `this.form.submit()`、`javascriptDisabledSubmitButton` は真。NKでDOM属性がない場合は `getAttribute` 投影の明示JSON nullとし、JavaScript無効時のsubmit buttonの観測を両側で保持する。比較値を独立した一時JSONに設定する。

| Test ID | 合成操作 | 独立期待 |
|---|---|---|
| PT-CHR-DEF043 | 既存inline文字列と明示null、両側に真のbuttonを記録 | 正規DIF-013、比較成功 |
| PT-CHR-DEF044 | NKの観測フィールド自体を削除 | 属性なしの観測不足、未登録差分 |
| PT-CHR-DEF045 | NKの別inline文字列を自己申告と同時に変更 | 承認NK値と不一致、未登録差分 |
| PT-CHR-DEF046 | 同じ二値を別フィールドに作りDIF観測先を移す | pointer違い、別フィールド差分も未登録 |
| PT-CHR-DEF047 | 両artifactのbuttonをfalseにする | 一致していても両側の代替操作欠落を検出 |
| PT-CHR-DEF048 | S02のDIF観測だけを削除 | 必須観測未成立、承認対象の差分も未登録 |

同一工具sourceで元170と新6の全176件を実行し、対象の生coverage、静的解析、証拠hashを対の結果へ記す。外部JSの同一origin・CSP・実動作は同source実Browserで検証する。並行・再送は純比較に非該当。
