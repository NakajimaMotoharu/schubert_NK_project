# NK-WEB-002 Web・API実Login縦結線実行結果

2026-09-24 PG255/PT-SCR-134選択段階: `WebLogApplicationRuntimeTest` 7/7、failure/error/skipped0。隔離PostgreSQL18/Flyway、実Artemis、実HTTP GET/POST、Production Web/API親の同時稼働で合成USERの認証、CSRF、Secure/HttpOnly匿名→認証cookie rotation、保護Menu GET200、API Inbox/session/audit各1を確認。JCA独立PBKDF2 fixture、HTTP/SQL literal oracleは041仕様。全reactor/coverage/静的解析/証跡hashの正式gate前であり、この選択結果を合格認定や実NK CHRへ算入しない。後続の正式run/commit/時刻/manifest/hashを追記する。
