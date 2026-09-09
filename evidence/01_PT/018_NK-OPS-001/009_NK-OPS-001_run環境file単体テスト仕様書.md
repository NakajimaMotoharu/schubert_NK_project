# NK-OPS-001 run環境file単体テスト仕様書

PG-D-149/SSC-049、RD OPS-009、UI251、SS311/343 §6.8。InspectorRunEnvironment.encode/requireMatches。PGと同時に実装・実行する。永続runの正本決定SSC-055と実file publisherの試験ではない。

| Test ID | method | 事前条件・入力・操作・独立期待値 |
|---|---|---|
| PT-OPS-ENV-001 | independentGolden | UUID 00000000-0000-0000-0000-00000000005e、時刻2026-09-17T00:00:00Z。SSの2固定key/順序/ASCII/LFを直接書いたliteralとencodeのbyte完全一致、literalをrequireMatchesで受理。caller配列は不変 |
| PT-OPS-ENV-002 | mutationAndRunBinding | literalの全位置を元値以外の全256byteへ置換、空/短縮/追加/重複/別順/quote/CRLF/未知key/別UUID全128bit/時刻±1μsを拒否。固定診断/causeなし/suppressed0。expectedはliteral/独立操作でありProduction生成値を使わない |
| PT-OPS-ENV-003 | boundariesNullAndOwnership | 最小0001年/最大9999年microsecondを独立literalで比較。null run/observed拒否。2回encodeは等値別配列、1枚改変しても他と後続結果不変。時刻丸め/新UUIDなし |
| PT-OPS-ENV-004 | concurrentUse | 64並行で固定literalと等値、全結果のarray identity独立・呼出間共有なし、照合失敗が他呼出に影響しない |

実行command・OS/JDK/tool・branch/source・日時/exit・line/method/class/branch100%・Test ID/結果/BUG・source/evidence hashは010とevidence/manifest.jsonに記録する。failed/flaky/skipped/not-runを合格にしない。byte codecはfile IOをしないため実root所有/ACL/容量制限付きread/atomic publish/再読/子未稼働は未検証の別責務。既存BatchRunの年/精度/null契約はPT-BAT-001で回帰し、codecで緩和しない。
