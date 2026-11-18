# Web Outbox借用観測の結果

対象 `8f30415416465ee4424fb958c547afad8787cf19`、Core `28465379638bfee7fe6d13c7974f57ba087255ac`。PG39546/39550と独立PG39554で、元DB10・Collector8・Recorder8初回成功、失敗・エラー・skip・未実行0。三workerの有界終了、固定SQLと借用Connectionの無変更、完全read後の公開、二fixed mode拒否を確認した。初期PMDの適用三項目は修正前登録し、採用候補で静的適用0。

既定四counterは全到達。生counterはL115/M34/C5/B82/86/I727。未到達4件の実際の場所を保全し、全生branch未成立のままとする。プログラム全体、実DB、六module正式受入は継続。

[公開manifest](evidence/PG39554-p00405-web-outbox-proxy-independent-v1/manifest.json)。SHA256 `dfd372a59868de84a798b5bcc16509c3fa9ce95b39ba2e1502772d2c72eb6582`。仕様4682、BUG-3288/3289、YKT-2387/2691/2187。
