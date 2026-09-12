# NK-BAT-001 step値単体テスト仕様書

PG163/SSC055、先行898cc267、OPS009/DAT009/UI251 §11・12/SS311・331 §8.3・332・341 §3/11。実装前仕様。原本/fresh子全終端/OS排他/実backup/親全工程は未完了。PG162正式06中はsource/collectorを変更しない。

| Test ID | class/method | 目的・fixture/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-130 | BatchStepValuesTest.closedStepsAndBackupPolicy | 閉10名を独立literalで順序とbackup2だけ例外を比較。任意名/null/未知enumを受理しない |
| PT-BAT-131 | BatchStepValuesTest.attemptIdentityAndBounds | id1～999999999999・attempt1～99・原本cutoff/step time・skip。0/負/上限超、別runは同値にしない |
| PT-BAT-132 | BatchStepValuesTest.terminalStatesAndReasonMatrix | 全Status×Reasonの許可表を独立列挙、NONE成功/skip2/保護WARNING/ABANDONED FAILED/一般WARNING・FAILED。保存固定code/summaryを比較 |
| PT-BAT-133 | BatchStepValuesTest.counterAndStatusBoundaries | 4非負longの0/MAX/各負、SUCCESS failure0・SKIPPED全0、不正値を補完しない |
| PT-BAT-134 | BatchStepValuesTest.temporalContractAndBusinessDay | UTC0001/1582/9999/µs、cutoff同値/前1µs、日跨ぎ・UTC9999/JST10000、non-µs拒否 |
| PT-BAT-135 | BatchStepValuesTest.nullContractsAndRedaction | 全constructor引数null拒否、identity/診断をtoStringへ出さない、固定エラーcause/suppressedなし |
| PT-BAT-136 | BatchStepValuesTest.immutableValueSemantics | 同値別instance equality/hash/accessor、異なるid/run/step/attempt/time/skip/resultの非同値、field所有 |
| PT-BAT-137 | BatchStepValuesTest.independentConcurrentValues | 64固定run/time/step/countを別threadで構築し独立期待値、共有mutable状態なし |

Fixtureは隔離PostgreSQL18.6/Flyway V001～019/JDBC42.7.13、時刻/UUID/step/countは明示public literal。期待値はSS順序・固定SQL後条件・手計算のattempt/件数/固定文から算出し、Production methodの出力や観測件数から生成しない。null/未知/空/境界/異常/例外/並行/再試行を網羅。JDBC fault位置の表は実装後・fault期待値設定前に別途SQL/資源順序から独立計数し、全発火・close・rollbackを検証する。

実行commandは421 JDK/M2指定offline Maven -pl src/schubert-nk-batch -am test/verify、4coverage100/NullAway/SpotBugs/Spotlessを要求。failed/flaky/skipped/not-runは合格にしない。障害は修正前915、共通原因は916、上位修正は所定台帳へ先行する。branch/source commit/環境・日時・command/exit/input/期待/実際/coverage/BUG・SSC/evidence path・hashは022とmanifestへ実行後に記録する。現時点未実装/未実行、認定0。
