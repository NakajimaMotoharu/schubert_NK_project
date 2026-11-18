# Web Outboxの単一型付き解放の結果

候補Core `f8b668a320e091ce8ebb6c8835aac47366d8ca70`、試験 `df88f52a985b7d3d391787d41c518a95c135685d`。正本SS332は[PR #436](https://github.com/NakajimaMotoharu/schubert_NK_project/pull/436)で公開した。元26＋独立1の27件は初回合格、失敗・エラー・skip・未実行各0。逆展開で元26の期待を保持し、同一Throwableの拒否と行・文の解放順を確認した。現物理6の変化は一つ、公開ABIは一致。

当scopeの生line135・method36・class5・branch82・instruction747は全到達。初期の静的適用指摘1はBUG-3291で是正し、現静的適用0、PMD生42。実接続と全451・正式認定は継続。

[公開manifest](evidence/PG39578-p00405-web-outbox-typed-close-independent-v1/manifest.json)。SHA256 `5996db206a76880d07ee015e862d666a087ecf43c4beb6ddada8ec72dfd4c1ea`。仕様4684、BUG-3290/3291。
