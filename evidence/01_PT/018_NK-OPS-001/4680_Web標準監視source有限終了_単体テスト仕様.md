# Web標準監視sourceの有限終了と固定mode

F03/2-2、P018-09、BUG-3287、YKT-2387/2691、SS351/354、UI252。1810のWEBHOST001～016を保持する。

WEBHOST004は元nullとunknown/空文字を維持する。さらに同hash別文字列の入力二値をbindとscrapeの両方へ渡し、固定拒否文字列と取得0を独立照合。WEBHOST016は元の2worker、入力二操作、latch/待機10秒、既ownerのscrape継続と完了後の拒否を維持する。外側の暗黙closeを除き、既finallyの有界確認を終了条件とする。

通常JDK25、既Micrometer/Prometheus 11依存、自有メモリ、実サービス・接続・稼働状況なし。PG39536で元16一run、全静的、独立物理・単一exec、生範囲と支援不足を確認する。
