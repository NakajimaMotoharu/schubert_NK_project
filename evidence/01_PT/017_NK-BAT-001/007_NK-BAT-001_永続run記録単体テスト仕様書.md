# NK-BAT-001 永続run記録の単体テスト仕様書

PG-D-156/SSC-055先行b6b5f0f6、OPS-009/UI251/SS311/331 §8.2/341 §3/343 §6.13。MaintenanceRecords・MaintenanceActivation・MaintenanceCompletion/Outcome。実装開始前の仕様。root file store/親/400日GC/実rebootは対象外の未完了実装であり後工程へ移管して完成扱いしない。

| Test ID | class/method | 入力/操作と独立期待値 |
|---|---|---|
| PT-BAT-038 | MaintenanceRecordsTest.literalRecords | 3種の手書きASCII72/109/140・141byte、nilでない固定UUIDと6桁UTC、0/10。encode出力とliteralを比較し、decode値はfixture UUID/Instant/Outcomeと一致 |
| PT-BAT-039 | identityTemporalBoundaries | UUID全0/全f、UTC0001/9999・µs端、JST日付境界、decodeの値とyear/桁の独立値、completion同時刻以上 |
| PT-BAT-040 | malformedSources | size±1/空/余分行/BOM/CRLF/制御/highbyte、固定header/LF位置の全byte変異、型取り違え。固定IOException/cause0/suppressed0 |
| PT-BAT-041 | scalarAliases | uppercase/短縮UUID、同値offset/小数桁差/leap second/日付不正、status00/01/11/50/70/未知/追加spaceを拒否。正規の別ID/別時刻はdecodeして別値になることも明示 |
| PT-BAT-042 | completionInvariants | ended<cutoff/上限超/非µs/nullを拒否、SUCCESS/WARNINGだけ。timestampを丸め/補完しない |
| PT-BAT-043 | nullContracts | 全公開codec入力・model各field/Outcome null、契約違反を正常/空値にしない |
| PT-BAT-044 | ownershipAndRedaction | 入力byte不変、返却配列相互独立、モデル同値/相違とaccessor・redacted toString、getterが値を取り違えない |
| PT-BAT-045 | concurrentUse | 64独立activation/各0・10、独立fixtureのID/cutoff/結果集合、5秒Future bound、共有可変byteなし |

Production encodeをexpected生成に使わない。round-tripだけで成功とせずliteral byteと各fieldを別々にassertする。parserにはfile所有/expected run検証の責務がなく、正規の別runを誤って不正期待値にしない。全line/method/class/branch100%、NullAway/SpotBugs/format、18負canary/全reactor/35scope・所属一意性を確認する。実行command/環境/commit/結果/coverage/BUG/hashは008とmanifestへ記録。未実行・failed・flaky・skippedは未合格。
