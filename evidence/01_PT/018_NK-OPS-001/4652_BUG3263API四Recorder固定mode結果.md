# BUG-3263 API四Recorderの固定mode結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `5825a18e141a9816df2a102926387ff108e046a8`。PG39256は元32初回成功、失敗・エラー・skip・未実行0。元4不正mode項目に8反例を追加し、固定CONFIG_INVALIDと登録0を確認した。全32試験定義維持、Main変更0、静的適用0（PMD生26、有限workerと参照同一性の元oracleを個別に確認）。

PG39260の独立で物理11・正CRC10、JaCoCo標準counter 157L/38M/10C/74B/813I全到達。PG39264の生counterで四constructorとも14/14B、本体4型の各生counterは全到達。生の生成コードはenumのvalueOf 3とCounts recordのequals/hashCode/toString 3が未到達。標準計測結果と両方を残し、同runの全生methodを100%とは判定しない。全F03/451とYKT2691広域はOPEN。

Linux amd64/JDK25.0.4/Maven3.9.12、dev-foundation。[独立証跡](evidence/PG39264-f03-four-api-recorder-mode-independent-v1/manifest.json) SHA-256 `0076d561f39ff06c8dab18f51191596db5658e818f73669abed133277e6121d5`。証跡からcommand・真正終端・XML・同一CRC・静的・counterに追跡できる。

進捗表示のCRを含む二streamは、元hashが一致するgzipへ保全した。[追加保全表](evidence/PG39264-f03-four-api-recorder-mode-independent-v1/retention-addendum.json) SHA-256 `b9b99117b16142fe763980e18feb4a5a1acfe3de3a6bfbed96203f72a8e532fd`。
