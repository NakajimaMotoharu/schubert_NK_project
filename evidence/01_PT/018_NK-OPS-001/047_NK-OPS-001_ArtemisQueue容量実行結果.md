# NK-OPS-001 Artemis Queue容量 PT実行結果

PG242/PT-OPS-MQ-019～021の選択3/3成功。認証有効の隔離Artemis2.56.0で6 Queueの実`messageCount`/`persistentSize`をOps管理から読み、空Queue全NORMAL、app role管理拒否、一時返信Address残存0を確認。独立SS321閾値の全6 Queue件数/byte境界±1、DLQ1件alert、負値/null/不正型/provider失敗を確認。Batch `clean verify`全390PT、failed/error/skipped0、全coverage check PASS/SpotBugs0。

正式`PT-WEB-20260924-35`、対象source `77fcddb89b1e89af13da3265f74cb3aa4b9d65be`、全1829PT（CHR41/Protocol80/Storage82/API723/Web513/Batch390）、failed/error/skipped0。Java6 module全instruction/line/method/class/branch missed0、Production SpotBugs0、collector負canary98件、48scope/hashと保存manifestの再照合PASS。root `evidence/01_PT/008_NK-SCN-001/evidence/manifest.json` SHA-256 `10b2c0841fad930e73525ed7187cac8c5eb0e4a9797fa5daa3d7580af93a3e47`、本program `evidence/01_PT/018_NK-OPS-001/evidence/manifest.json` SHA-256 `6f66caa33f7656b3034ae5f478335bc3a6ef548c5cd30433e70040b76d1a450f`。PG242はこの限定範囲だけ認定。full readiness、起動阻止policy、Expiry purge、Production credential、実NK CHR-L01は未完了。
