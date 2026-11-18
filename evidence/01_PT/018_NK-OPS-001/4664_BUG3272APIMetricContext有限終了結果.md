# BUG-3272 API MetricContextの有限終了とmode結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `95af03fbc9e2271bd2b51cfc0e1a88adcd0f0fdd`。PG39374のAPIMCTX001〜033は初回全成功で失敗・エラー・skip・未実行0。004の追加不正modeは固定CONFIG_INVALID、021/023/024/033で元の30秒以内の待ち／worker終了と全40 assertionを保持。試験本文の変更5項目と製品Main差0を照合した。静的適用0、PMD生25は個別の有限fixture23と同期更新／一貫snapshot二箇所。

PG39378独立は物理27・正CRC19。PG39382の当本体生80L/13M/1C/34B/366Iは全到達。前依存6点は同byteで別試験を再演していない。支援側の当run生292箇所は保存。事前style1と独立工具2の失敗を保存して修正し、製品・生計測の再実行0。全F03・451・YKT広域は継続。

Linux amd64、JDK25.0.4/Maven3.9.12/Micrometer1.17.1/Prometheus1.7.0、dev-foundation。[独立証跡](evidence/PG39382-f03-api-context-finite-independent-v1/manifest.json) SHA-256 `2c224be355a8face8c1be2af922877f952d6bd5b187a6c87e533be57d2e396b3`。実command、XML、終端、CRC、静的及び生counterを参照可能。
