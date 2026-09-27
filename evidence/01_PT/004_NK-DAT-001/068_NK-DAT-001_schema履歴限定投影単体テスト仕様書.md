# PG312 schema履歴限定投影PT（暫定）

Program NK-DAT-001、append-only V023__startup_schema_history_projection.sql・StartupSchemaProjectionTest。RD DAT009/SYS002/OPS009、UI212/253、SS3313.3/3439.1、SSC095。隔離PostgreSQL18/Flyway13.4、role provisioning＋001..023を試験用clusterだけへ適用、運用DB/history/秘密を変更しない。

| Test ID | 入力・操作 | 独立期待値/根拠 |
|---|---|---|
| PT-DB-SCHEMA001 | schubert_app固定query | SCHEMA0（quoted schema/NULL version・CRC）＋literal001..023 SQL順/全24行success、六列型。CRC値自体のProduction期待照合はOPS147 |
| DB-SCHEMA002 | catalog/function定義/ACL | owner nk_owner・SQL STABLE/SECURITY DEFINER・search_path pg_catalog,pg_temp・引数0/六列型・完全修飾history・WHERE無し・PUBLIC ACL0 |
| DB-SCHEMA003 | app/web/batch/backup/inbox-inspector/ops-ro/未認定role | 先頭3roleだけ24行読取可、他42501 |
| DB-SCHEMA004 | tableSELECT/metaCREATE/SET ROLE/business schema | app/web/batch historySELECT/metaCREATE/owner membership禁止。Web業務schema USAGE無し維持 |
| DB-SCHEMA005 | 隔離admin txnでrank23をfailed/NULLversionへ変更→rollback | 投影が両状態を隠さず24行返す、rollback後失敗0 |
| DB-SCHEMA006 | temp同名table/search_path変更 | qualified historyから全24行を返しtemp値9999非採用 |
| DB-SCHEMA007 | readonly txnとbusiness後条件 | readonly24行成功、batch_runs0、投影が業務更新しない |
| DB-SCHEMA008 | 3role barrier実並行接続 | 独立接続が全24行、相互資源共有なし |

期待inventory/role/列数/権限はSSからliteralで記述、Production migrationや観測DBをexpected生成に使わない。Java試験8件/DDL catalog・権限全分岐、失敗/skipped/not-run非合格。command/commit/hash/log/XML/関連BUG・静的・coverageは069と018148/provisional PG312へ記録。横断DDL/security triggerとして全6module回帰が必要、限定試験を正式全PGPT認定としない。
