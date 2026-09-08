# BUG-041 修正前記録

2026-09-08、source9790151、正式PT-SCN-20260908-22は全486件/coverage100%/SpotBugs0、終了11:43:07 JST。collector006実行はcode1 `missing required Scenario lifecycle Test ID/method evidence`。manifestは前の正式20のまま。途中生成outputを正式収集完了とは扱わない。

JUnitの実名は `brokerSendAndAckFailuresReplayOneCommittedResult(Path)` と `realWriterInspectorAndDatabaseRegenerationShareExactFrozenBytes(Path)`。required_methodsのT06/T07で `(Path)` を欠落していた。全tools/qualityのrequired_methods/testIdMethodsを検索し、この厳密照合は006だけ。他のcollectorは実JUnitからmethod名を採取するため非該当、共通原因対象複数なしで新規YKT不要。

修正前に915へ起票。実完全名2箇所へ訂正し、厳密一致を緩和しない。PG/PT source/collector固定後の次の正式runで全required method実在とsanitized manifest/hashを検証する。実行失敗をPASSへ読み替えない。

正式22 collectorの途中生成output/coverageはsanitizedデータだが、旧manifest20/hashと対応しないため未証明状態。次の正式23で全reports/coverageを再収集し、manifest/checksumsを一括再生成・照合するまで008証跡完了を宣言しない。旧manifest20の認証済み状態はcommit cd5fce6から復元可能。
