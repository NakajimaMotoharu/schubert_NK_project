# F03 6モジュール試験ソースのCheckstyle差分

対象はWBS-F03/2-2、Core `29f3b433952ad19d4ad34c4e1a31ed310bebde6a`、候補 `2ed5c3a75e1cb19ed83d3d1eff217fc021395438`。Checkstyle 14.3.0、原Root設定のSHA-256一致。PG38504以後のGit差分は25ファイル。保留2件の差分は名前だけ扱い、残23のうち18件は元の入力hash・真正終了0・XMLを照合した。残5件をPG39104で静的検査し、指摘0。保留一覧全32の内容、製品classの生成、試験実行は対象外。

| module | 現ソース数 | 照合済み |
| --- | ---: | ---: |
| schubert-nk-api | 338 | 334 |
| schubert-nk-batch | 306 | 280 |
| schubert-nk-bootstrap | 120 | 120 |
| schubert-nk-protocol | 36 | 36 |
| schubert-nk-storage | 37 | 35 |
| schubert-nk-web | 295 | 295 |

[PG39102 差分・元証拠](../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG39102-f03-six-test-source-checkstyle-delta-v1/manifest.json)、[PG39104 新規静的検査](../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG39104-f03-five-current-test-source-checkstyle-v1/manifest.json)。確認数は1,094/1,126から1,100/1,132に更新。QA-056/057、残型付き品質、全六module製品条件と451の正式判定は継続。
