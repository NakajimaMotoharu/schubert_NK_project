# NK-DAT-001 Expiry batch監査DDL 実行結果

PG245/SSC-077/BUG-237/YKT-188、PT-DB-016/017。2026-09-24時点は正式source commit/全reactor/coverage/48scope hashが未確定。**本ファイルの存在をもってPT合格とはしない。**

検証対象は対の064仕様書に固定した独立期待値。PostgreSQL18.6隔離clusterを用いる。未commit候補の選択実行は2026-09-24 13:32:23 JST終了、`/tmp/PG245-selected.log`、exit0、API33件（DB17/StepCleanup8/InspectionParent8）、failure/error/skipped0。V021適用21件・旧SUCCESS安全停止20件・他step監査NULL・正負CHECK/権限を実PGで確認した。選択探索結果なので正式認定へ流用しない。正式clean verify後にrun ID/source commit、日時、OS/JDK/Maven/Flyway/pgJDBC、branch、command/exit code、全Test IDの期待・実際、coverage、static/secret scan、evidence path・SHA256を追記する。PG244正式`PT-WEB-20260924-37`は本V021を含まない。

障害票BUG-237と横展開YKT-188は、親による同transaction監査値保存・同run再実行・commit不明・rollbackのPTが残るため対応中。PG/PT全体は未完了。
