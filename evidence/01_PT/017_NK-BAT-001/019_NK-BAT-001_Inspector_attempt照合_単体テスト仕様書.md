# NK-BAT-001 Inspector_attempt照合単体テスト仕様書

PG162/SSC049、先行d23b1afd、OPS009/DAT009/MQ008/UI212/241/251/SS311・331 §3.13・332・341 §7.3。実装前仕様、InspectionAttemptTest。親用非秘密read/純照合だけであり、実子fresh起動・終端/OS排他/backup・親全stepは未完了。正式PG161/run04中はsource/collectorを変更しない。

| Test ID | class/method | 目的・fixture/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-122 | InspectionAttemptTest.matchingSuccessAndWarning | 同run/END、累積保護0→0/保護あり→10の固定結果、attempt/cumulativeを明示数値比較 |
| PT-BAT-123 | InspectionAttemptTest.zeroAndResumedAttemptCounts | 未開始→END0/処理あり、before累積(5,2,3)→after(9,5,4)のattempt(4,3,1)、同時にrun累積保持 |
| PT-BAT-124 | InspectionAttemptTest.completedBaselineImmutability | before既END/同counts→attempt0、保護ありならWARNINGを維持、END解除/累積変更は拒否 |
| PT-BAT-125 | InspectionAttemptTest.countRegressionAndOverflow | target/deleted/protected各非減少・constructor各attempt<=cumulative、longMAXと差分境界、overflowや減少を丸めない |
| PT-BAT-126 | InspectionAttemptTest.runIdentityAndMissingEnd | expected/before/afterのUUID/cutoff各相違、after未END拒否、同値record別instance正常 |
| PT-BAT-127 | InspectionAttemptTest.receiptCodesAndNulls | 0/10と保護有無相違、-1/1/20/30/50/70/MIN/MAX拒否、全record/factory引数nullは契約違反 |
| PT-BAT-128 | InspectionAttemptTest.redactionAndValueOwnership | immutable equality/hash、toStringのidentity秘匿、累積/差分/outcome定義・constructor不変条件 |
| PT-BAT-129 | InspectionAttemptTest.independentConcurrentObservations | 64固定run/数値を独立threadで照合、共有mutable状態なし、別run混入/結果配列共有なし |

SQL/Repository fixtureは隔離PostgreSQL18.6/Flyway/JDBC42.7.13と独立SQL literal、pure照合は手計算したcounts/0・10を正とする。現在時刻やProduction read/reconcileの結果からexpectedを作らない。正常/境界/異常/例外/null/再実行/並行/資源を網羅し、line/method/class/branch100%・NullAway/SpotBugs/Spotless・全reactorを必須とする。Failed/flaky/skipped/not-runは合格に算入しない。障害は修正前に915/必要時916へ登録する。

実行command・日時・OS/JDK/tool・branch/source commit・exit・input/expected/actual・coverage・BUG/SSC・evidence hashは020とmanifestへ実行後に記録する。現時点は未実装/未実行・認定0。秘密情報・raw session/token/DB dumpは記録しない。
