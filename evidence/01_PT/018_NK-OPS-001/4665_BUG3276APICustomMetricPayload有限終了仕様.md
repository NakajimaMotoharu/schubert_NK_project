# BUG-3276 API custom metric payloadの有限fixture

WBS-F03/2-2、WBS-P018-09、UI252、SS351/354。Core bcc9e0673287c51950ecab9b36350abfcd4b2c69。元ApiCustomMetricPayloadTest全26とtest fixtureを保持。APIFULL011/012は一owned executorを明示し、Release latch、shutdownNow、await30秒でworker真正終了後にlocal Bundleとregistry ownerを解放する。元全64、各Future期限、local runtime availableProcessorsに対応する明示golden text、部分応答なし、採取0、別ownerのassertionを保持する。

APIFULL004はSS351固定modeを参照、PG39230の二同hash異値を元unknownに加える。元null、CONFIG_INVALID、供給回数0、標準scrape0を独立期待とする。Main差0。JDK25.0.4、Maven3.9.12、Micrometer1.17.1／Prometheus1.7.0、Linux, dev-foundation。既SDK11点は元実物同一。アプリHTTP・外部scrape・DB・OS・保護型なし。選択26、一固定試験source・XML/終了・CRC・静的・対象生counterと支援側未到達をPG39400に記録。0.4/1.65/3.9pp、cap5.5、元行追加完了価格0。
