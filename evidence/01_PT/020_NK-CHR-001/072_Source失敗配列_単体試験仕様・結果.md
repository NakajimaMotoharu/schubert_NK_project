# Source検証の失敗配列と成功条件

NK-CHR-001、SS355、WBS-P020-01.03/2、BUG-3654／YKT-2872。

PT-CHR-META011。source-verificationを模した独立固定JSONで、`failures: []` を成功、欠落・null・object・文字列・失敗項目とnullを含む配列を `SOURCE_FAILURES` と判定する。sourceの他の値は同じ。実運用の旧レポートの配列とhashを保存し、比較対象、Current、判定DIFへ変更を加えない。Characterization工具の合成通常試験と当該閾値の無フィルター測定を別に記録する。

PG43024-v1は新1件が二重診断で失敗。共通入口で一度だけ判定した 67755f6336／PG43024-v2で合成226件が全成功。Checkstyle 0、対象二物理の無フィルターL521/M68/C2/B273各全数。[公開manifest](evidence/PG43024-characterization-source-report-failures-v2/manifest.json) SHA-256 `7db211ca0b68b9b53707f5a0cba8c52956b6907341db14bbd8e351247dfcaef8`。実環境・Current原本・native等の結果は内数0。
