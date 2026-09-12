# NK-DAT-001 親Inspector_summary単体テスト仕様書

PG162/SSC049、先行d23b1afd、OPS009/DAT009/MQ008/UI212/241/251/SS311・331 §3.13・332・341 §7.3。実装前仕様、InspectionParentBoundaryTest。親用非秘密read/純照合だけであり、実子fresh起動・終端/OS排他/backup・親全stepは未完了。正式PG161/run04中はsource/collectorを変更しない。

| Test ID | class/method | 目的・fixture/入力/操作・独立期待値 |
|---|---|---|
| PT-DB-INBOX-251 | InspectionParentBoundaryTest.summaryStatesAndCounts | 手書SQLで未開始0行・0未END/0END・deleted/protected混在・longMAXを用意し4列完全一致、cursor/本文なし |
| PT-DB-INBOX-252 | InspectionParentBoundaryTest.identityAndTimeBoundaries | 同UUID異cutoff/違うrun、NULL/±infinity/0001～9999外、µs/UTC-JST-NewYork/1582暦境界を独立SQL literalで確認 |
| PT-DB-INBOX-253 | InspectionParentBoundaryTest.parentLockNamespaces | lockなし/shared/two-int/他backend拒否、自己exclusiveだけ通過、既保持数/接続設定・lock所有を変更しない |
| PT-DB-INBOX-254 | InspectionParentBoundaryTest.roleAndCatalog | batchだけEXECUTE、他app/Web/backup/ops/inspector/PUBLIC拒否、owner/SECURITY DEFINER/search_path/TimeZone固定、基表権限不変 |
| PT-DB-INBOX-255 | InspectionParentBoundaryTest.freshReadAndRollback | 初期0行→別transaction作成→未END→END、各fresh snapshot/rollback後条件、値をcache/補完しない |
| PT-DB-INBOX-256 | InspectionParentBoundaryTest.concurrentOwners | 実別connection/threadのlock競合と引渡し、別run混入せず、並行未commit行を成功へ流用しない |
| PT-DB-INBOX-257 | InspectionParentBoundaryTest.noMutationOrPrivateProjection | 呼出前後のtable/index/row/full checksum不変、backupなしもreadだけ可、出力列名型は4列のみ、cursor/message/secretを返さない |
| PT-DB-INBOX-258 | InspectionParentBoundaryTest.appendOnlyMigration | V001～018の独立hash不変、V019再migration/clean schema inventory・function定義・permissionを確認 |

SQL/Repository fixtureは隔離PostgreSQL18.6/Flyway/JDBC42.7.13と独立SQL literal、pure照合は手計算したcounts/0・10を正とする。現在時刻やProduction read/reconcileの結果からexpectedを作らない。正常/境界/異常/例外/null/再実行/並行/資源を網羅し、line/method/class/branch100%・NullAway/SpotBugs/Spotless・全reactorを必須とする。Failed/flaky/skipped/not-runは合格に算入しない。障害は修正前に915/必要時916へ登録する。

実行command・日時・OS/JDK/tool・branch/source commit・exit・input/expected/actual・coverage・BUG/SSC・evidence hashは060とmanifestへ実行後に記録する。現時点は未実装/未実行・認定0。秘密情報・raw session/token/DB dumpは記録しない。
