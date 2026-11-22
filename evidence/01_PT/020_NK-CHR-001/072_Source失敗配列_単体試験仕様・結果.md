# Source検証の失敗配列と成功条件

NK-CHR-001、SS355、WBS-P020-01.03/2、BUG-3654／YKT-2872。

PT-CHR-META011。source-verificationを模した独立固定JSONで、`failures: []` を成功、欠落・null・object・文字列・失敗項目とnullを含む配列を `SOURCE_FAILURES` と判定する。sourceの他の値は同じ。実運用の旧レポートの配列とhashを保存し、比較対象、Current、判定DIFへ変更を加えない。Characterization工具の合成通常試験と当該閾値の無フィルター測定を別に記録する。
