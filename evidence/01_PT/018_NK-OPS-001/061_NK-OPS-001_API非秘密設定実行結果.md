# NK-OPS-001 API非秘密設定実行結果

PG272/PT-OPS-API-CFG-001～006。2026-09-25、Java25.0.4/Maven wrapper/SnakeYAML Engine3.1.1。選択6/6、failure/error/skipped0。初回compileはNullAwayのMap.get null契約4件で停止し、`Objects.requireNonNull`で固定default不変条件を明示して再実行した。初回はPT合格に算入しない。初回API全体`clean verify`は758PT成功も新classのbranch66/68で停止。BUG-251を修正前起票し、YAML decoded空値・placeholderを独立負例へ加えた。API全体再実行は758PT成功・Production全coverage100%・静的0でexit0。後続の複数document負例を含む選択6/6も成功。ただし正式全reactor、manifest/hashは未確認のためPG272は合格認定しない。秘密credentialや運用configは入力・保存しない。
