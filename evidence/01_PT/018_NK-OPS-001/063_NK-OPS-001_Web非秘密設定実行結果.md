# NK-OPS-001 Web非秘密設定実行結果

PG273/PT-OPS-WEB-CFG-001～006。2026-09-25、Java25.0.4/Maven wrapper/SnakeYAML Engine3.1.1。選択6/6、failure/error/skipped0。初回はSpotless未整形でcompile前停止し、format後に選択再実行した。初回停止はPT合格に算入しない。Web module `clean verify`は全541PT、failure/error/skipped0、Production全coverage100%、SpotBugs0でexit0。ただし正式全reactor、manifest/hashは未確認であり、PG273を合格認定しない。秘密credentialや実運用configは入力・保存しない。
