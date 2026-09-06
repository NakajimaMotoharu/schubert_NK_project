# BUG-015 SQL NULL guard修正前記録

- 2026-09-07 / dev-messaging / b3b5740。YKT-012で全maintenance functionの引数・上限を確認した際に発見。
- V005の全6関数は `IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit NOT BETWEEN 1 AND ... THEN`。run/cutoffが正常でp_limitがNULLの場合、式はNULLでありPL/pgSQLのIFは例外へ分岐しない。
- 候補SQLの `LIMIT p_limit` もNULLなら上限なしとなる。既存DatabaseMigrationTestはp_limit=0/上限+1を試験するがp_limit=NULLを欠く。
- BUG-015を修正前起票しYKT-012の共通guard確認へ加える。各関数へNULLを渡す実PostgreSQL回帰試験でSQLSTATE 22023を独立期待値とする。
- V005原本のchecksumは維持し、追加migrationで修正する。未修正時の試験は合格へ算入しない。
- 実PG再現（2026-09-07 08:02:21 JST終了、Maven exit1）: `cleanupNullLimitsAreAlwaysRejected` は最初のnotifications呼出しでSQLSTATE22023の例外を期待したが例外なし。BUG-014の回帰testと合わせて2件失敗。修正前ログは`/tmp/pgpt-cleanup-before.log`（raw propertiesはGit格納しない）。
