# BUG-3261 API GC固定modeの同hash不正値結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `f936fdc9ea92bdaa01743800ad4a847d9d3d03c5`。PG39224のAPIGC001〜017は17件初回全成功、失敗・エラー・skip・未実行0。旧16本文は同一。新017で2つの独立合成modeは同hashでも両方CONFIG_INVALID、registry・owner・factory呼出と処理中closeは0。

PG39228独立の同物理2、正CRC1。PG39230の生18L/5M/1C/16B/97Iは全到達（元B14/16）。Mainと物理byteは前と同一。Root静的適用0、PMD生15を同原指摘・元対処箇所に照合。Web全16は再実行せず、F03・451・YKT2691広域は継続。

Linux amd64/JDK25.0.4/Maven3.9.12、dev-foundation。[PG39230](evidence/PG39230-f03-api-gc-mode-negative-independent-v1/manifest.json) SHA-256 `57d7b9e9c9825702500b766886063d27fd58e79e72037ebf758f06640029eb8c`。command、入力、終端、XML、単一exec、CRC、static、coverageを保存。
