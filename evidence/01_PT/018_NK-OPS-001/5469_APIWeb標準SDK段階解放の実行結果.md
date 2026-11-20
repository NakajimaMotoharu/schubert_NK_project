# API／Web標準SDK段階解放の実行結果

元source `55add7630760e956c20e534dca8f6c90d93707b7`、PG40876のAPIHOST017／WEBHOST017は各1件不一致。GC→registry→GC→registryを再現した。修正source `9ee35bb454768ef48b4a62aca61e3a4c6ad2e1a8` のPG40878では、解放に成功したハンドルを退役させ、再試行を未解放分に限定した。

| 対象 | 成功（新規＋必要回帰） | line | method | class | branch | instruction |
|---|---:|---:|---:|---:|---:|---:|
| API | 17（1＋16） | 45/45 | 9/9 | 1/1 | 19/19 | 194/194 |
| Web | 17（1＋16） | 42/42 | 9/9 | 1/1 | 16/16 | 179/179 |

両方ともfailed・error・skippedは0、Java 25のWerror、書式、Checkstyle終了0。対象classごとの局所測定。Batchの元17は独立した旧sourceのまま保全し、全451・実監視・正式受入への合算は行わない。[API実測](evidence/PG40878-api-web-standard-gc-partial-close-v1-after-api/manifest.json) [Web実測](evidence/PG40878-api-web-standard-gc-partial-close-v1-after-web/manifest.json)
