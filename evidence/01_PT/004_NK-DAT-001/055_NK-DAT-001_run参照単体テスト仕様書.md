# NK-DAT-001 run参照単体テスト仕様書

PG159/SSC055、先行4c5dcb85、OPS-009/DAT-009/UI251/SS331 §3.12/332/343。実装前仕様。RunReferenceBoundaryTest/V018。隔離PostgreSQL18/Flyway、固定UUID2件・UTC/JST date/cutoffの非秘密fixture。3table存在flagとcutoff/日付を独立SQL後条件として決め、production functionからexpectedを生成しない。

| Test ID | method | 入力/操作・期待値 |
|---|---|---|
| PT-DB-INBOX-241 | referenceCombinations | 3tableの全8組合せ、別run、状態/年齢に関係なく正しい3flag、存在なしconsistent true |
| PT-DB-INBOX-242 | identityConsistency | 同cutoff/違うµs・全履歴JST日付/1不一致・両進捗各不一致、step時刻は独立で補完しない |
| PT-DB-INBOX-243 | temporalAndNullBoundaries | SQL NULL/±infinity/UTC0001未満/10000以上拒否22023、0001/9999・µs/JST日付境界受理 |
| PT-DB-INBOX-244 | lockOwnership | 自己exclusive/currentDB/71419602だけ受理、無lock/shared/two-int/別backend拒否55000、lock勝手取得/解放0 |
| PT-DB-INBOX-245 | roleAndCatalog | batchだけ許可、app/Web/backup/ops/inspector/PUBLIC拒否、owner/SECURITY DEFINER/search_path/UTC、table権限不変 |
| PT-DB-INBOX-246 | transactionVisibility | 自分の未commit書込/rollback、別connection commit前後をREAD COMMITTEDでfresh観測、readによるDMLなし |
| PT-DB-INBOX-247 | concurrentOwnership | 別backend排他競合の不正観測拒否、解放後明示獲得して観測、独立run混入なし |
| PT-DB-INBOX-248 | migrationAndReadOnlyHistory | V001～017 hash不変/V018だけ追加・Flyway validate、全row履歴/progress不変・新SELECT grantなし |

SQL分岐は上表を独立根拠としJaCoCo値に偽装しない。Java全4coverage/static/全reactor、負canary/collector/schema inventoryを一致させる。Failed/flaky/skipped/not-run非合格。実行command/時刻/commit/環境/入力期待値実値/BUG/hashは056・evidence/run-references/manifestへ正式時に記録する。新run/GC/親結線/実NK CHR/ITSTは別未完了。
