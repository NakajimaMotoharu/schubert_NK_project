# BUG-3262 API JVM・System mode並行終了結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `5dd7102b9da00da9f7102f80ee3988d6e0534043`。PG39240でAPIJVM001〜014・APISYS001〜014が全28件初回成功、失敗・エラー・skip・未実行0。005は許可語と同じhashの異値2種もCONFIG_INVALIDで、014は元の64入力・256/128呼出を維持してworker停止を10秒以内に確認した。Main変更0。

PG39244独立で物理3・正CRC2。同一execの生値はAPI JVM 18L/4M/1C/18B/116I、API System 18L/4M/1C/18B/108Iで全到達。静的適用指摘0。PMD生14は前回の同構造の個別指摘根拠へ照合した。YKT2387/YKT2691は当二型完了、全scope・F03・451は継続する。

Linux amd64/JDK25.0.4/Maven3.9.12、dev-foundation。[独立証跡](evidence/PG39246-f03-api-jvm-system-independent-v1/manifest.json) SHA-256 `623c290ea57b0bb6acbd1c1786dff94ec2b349d6e83c5b10df6ac098baa8a657`。command・終端・XML・CRC・静的解析・生counterはmanifestから追跡できる。
