# BUG-3268 API標準監視のmode・worker結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `8ade2c7af24fd7f899f5e1fbd1753a8ad1be2309`。PG39338のAPISTD001〜013は全件初回成功、失敗・エラー・skip・未実行各0。005は同hashの異値2件の固定CONFIG_INVALIDと先行動作0、013は元の64組と総192を維持しawait10秒を実測。元Fixture・期待の逆変換一致、Main差0。静的適用0、PMD生7は有限fixture・明示閉済みownerを各siteで照合。

PG39342独立の物理5・CRC4。API標準本体の生counterは21L/6M/1C/14B/113I全到達。依存JVM/System/GC等は旧証跡と物理byte4点一致、既試験を再演せず、当execでの別生19未到達をそのまま保存。F03/451・YKT広域は継続。

Linux amd64、JDK25.0.4／Maven3.9.12／Micrometer1.17.1、dev-foundation。[独立証跡](evidence/PG39346-f03-api-standard-mode-independent-v1/manifest.json) SHA-256 `c7949246a2f4990c7da20792922c2fe9628b1e7f6ddff6aae4378d46046ae72f`。command、XML、終端、CRC、静的、coverageを参照できる。
