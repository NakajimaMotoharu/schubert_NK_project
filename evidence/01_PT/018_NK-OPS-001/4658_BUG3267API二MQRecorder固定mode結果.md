# BUG-3267 API MQ圧力・再配送の固定mode結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `c5ba79c466b9e077733cd4389d18711715212814`。PG39320で元16初回成功、失敗・エラー・skip・未実行各0。二つの元modeに独立な同hash異値を各2件追加し、CONFIG_INVALIDと登録0を確認。Main変更0、元試験他本文の逆変換一致。静的適用0、PMD生11は各有限worker site・null equalsの明示oracleを照合した。

PG39324独立の同一物理6・正CRC4。PG39328の生constructorは圧力14/14分岐、再配送16/16。圧力43L/9M/1C/22B/221I、Snapshot 5L/10M/1C/10B/74I、再配送29L/3M/1C/24B/153Iは全到達。依存BrokerTopologyの生7箇所、L5/M5/B3未到達は当scopeに記録。全F03/451や実JMSは継続する。

Linux amd64、JDK25.0.4／Maven3.9.12、dev-foundation。[独立証跡](evidence/PG39328-f03-mq-recorder-mode-independent-v1/manifest.json) SHA-256 `c5d579048b8a4bbe3b1f8ba302dac5de8f657d6a0a6facfa580c5c244f892f83`。command、XML、真正終端、CRC、静的、coverageを追跡できる。
