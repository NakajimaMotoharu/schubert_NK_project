# RequestLogDetails現入力境界と静的非生成の実行結果

PG42912、2026-11-23 JST、dev-foundation、Core `e8368d22c4da2ec841f008df793594d3be9066af`、試験 `4c6cdbf37f445f334c4a3d1a0be85c80394b442b`。独立期待の通常8件、失敗・エラー・skip・選択漏れ0。従来の許可済み結果を試験元そのまま保持し、新RAW004は1024 literal受理／1025拒否。RAW001の反射による私有constructor呼出は現行から除外して旧試験を履歴保全。PT-LOG-STATIC001は実体化せずJDK classfileのprivate一件を確認し、通常8に加算しない。NullAwayと試験Checkstyleの指摘0、製品実経路と六製品品質は未実施。

| 対象 | 標準covered/total | 無フィルターcovered/total |
| --- | ---: | ---: |
| 行 | 48/50 | 49/51 |
| method | 4/5 | 4/5 |
| class | 1/1 | 1/1 |
| branch | 23/23 | 36/36 |
| instruction | 167/174 | 201/208 |

残りはprivate constructorの2行・1 method・7命令。元reflection実行からの加算、除外、正式認定変更は0。BUG-3644局所の試験手法を是正済み、coverageとYKT-2863はOPEN。元準備で失敗履歴v1選択をガードで停止し、対象v2を選び直した。最初の準備ではcompile／JUnitを起動していない。

公開manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG42912-request-log-details-without-private-reflection-v1/manifest.json` SHA-256 `8cd222fe07d107632afe9e858353121197bd0e2042cb7a58e0129d84edc67fab`。
