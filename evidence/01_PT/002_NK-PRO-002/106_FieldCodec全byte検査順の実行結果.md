# FieldCodec全byte検査順の実行結果

NK-PRO-002、MSG-004、UI232、SS322 §6.2、PT-PRO-002-N03、BUG-3479／YKT-2775、WBS-P002-01・F02-a／F03/2-2。修正sourceは `62b239d4dad561da007e15a290f8a271a165dda9`。数字の全byteを検査してから演算する。従来の正常、overflow診断、filler、例外型は維持。

| 実行 | 判定 | 証拠 |
|---|---|---|
| PG41298 | 修正前の1件は期待非数字に対して実測overflow、F1で終了1 | [反例・hash](evidence/PG41298-protocol-numeric-byte-precedence-v1/manifest.json) |
| PG41300 | 対象FieldCodec 8件、失敗・エラー・skip・未実行0 | [局所再試験](evidence/PG41300-protocol-numeric-byte-precedence-fixed-v1/manifest.json) |
| PG41302／304 | 当Protocol Maven verify終了0、39 suite全171件。元一execと176物理、実行162 CRC、製品一物理の変更。無除外でL3639／M1432／C162／B1080／I20363、未到達0。SpotBugs指摘・欠落・実行エラー0。 | [独立測定・XML hash](../018_NK-OPS-001/evidence/PG41304-protocol-numeric-physical-independent-v1/manifest.json) |
| PG41306 | 現同JARで176物理の依存と呼出を検査、五規則各0。差分二ファイルのCheckstyle／型付きPMD各0。四保全物のSHA一致。 | [現型付き・保全](../018_NK-OPS-001/evidence/PG41306-protocol-numeric-current-quality-v1/manifest.json) |

現カタログのN型135項目は最大17 byte、Headerの直接数値7項目は最大9 byte。両異常が同時に発生する最小20 byteに達しない。現行64 layoutの固定幅、正常byte結果、外部インターフェースに差分なし。直接FieldCodecの個別契約を是正した。

WBSの現有効受入は16/190。ベースライン17件のうちP002-01を再確認へ戻した。旧認定の1964 PT／53 scopeと当単独Protocol結果は別に保全する。同候補の正式451等の終了依存を満たすまで再受入は行わない。
