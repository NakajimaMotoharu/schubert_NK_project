# NK-BAT-001 親Inspector_summary単体テスト仕様書

PG162/SSC049、先行d23b1afd、OPS009/DAT009/MQ008/UI212/241/251/SS311・331 §3.13・332・341 §7.3。実装前仕様、InspectionSummaryRepositoryTest。親用非秘密read/純照合だけであり、実子fresh起動・終端/OS排他/backup・親全stepは未完了。正式PG161/run04中はsource/collectorを変更しない。

| Test ID | class/method | 目的・fixture/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-114 | InspectionSummaryRepositoryTest.summaryValueInvariants | BatchRun/CleanupCounts/complete true/false、null拒否・immutable equality/hash/redact、件数不変条件は共用型を維持 |
| PT-BAT-115 | InspectionSummaryRepositoryTest.realBoundedRead | 実PG/V019の0行Optional.empty/未END/END・3件数独立期待値、固定UUID/cutoff・4列のみ |
| PT-BAT-116 | InspectionSummaryRepositoryTest.parentStateAndLock | autoCommit true/readOnly false/ReadCommittedだけ、lockなし/shared/別backend拒否、借用connection非変更 |
| PT-BAT-117 | InspectionSummaryRepositoryTest.projectionAndNull | constructor/run/statement/row/4column null、0/1/2行、負/不整合counts・bind値/timeout5・所有を確認 |
| PT-BAT-118 | InspectionSummaryRepositoryTest.allJdbcFailurePositions | 正常1行は独立16call、0行11callの全位置SQLException/両close複合故障、fixed BatchRepositoryException/cause suppressed0/owned0 |
| PT-BAT-119 | InspectionSummaryRepositoryTest.historicalUtcIdentity | 手書SQL0001/1582/1900/1970/JST境界/9999とOffsetDateTime UTC bind同一性、Production expected生成禁止 |
| PT-BAT-120 | InspectionSummaryRepositoryTest.freshVisibilityAndBorrowing | 実別commit/rollback前後のfresh再読と同run再開、caller commit/rollback/close/config変更0 |
| PT-BAT-121 | InspectionSummaryRepositoryTest.interruptAndRuntime | 開始/最終割込flag保持、未知runtime/NPEは成功化しない、全owned資源終了、provider詳細非流出 |

SQL/Repository fixtureは隔離PostgreSQL18.6/Flyway/JDBC42.7.13と独立SQL literal、pure照合は手計算したcounts/0・10を正とする。現在時刻やProduction read/reconcileの結果からexpectedを作らない。正常/境界/異常/例外/null/再実行/並行/資源を網羅し、line/method/class/branch100%・NullAway/SpotBugs/Spotless・全reactorを必須とする。Failed/flaky/skipped/not-runは合格に算入しない。障害は修正前に915/必要時916へ登録する。

実行command・日時・OS/JDK/tool・branch/source commit・exit・input/expected/actual・coverage・BUG/SSC・evidence hashは018とmanifestへ実行後に記録する。現時点は未実装/未実行・認定0。秘密情報・raw session/token/DB dumpは記録しない。
