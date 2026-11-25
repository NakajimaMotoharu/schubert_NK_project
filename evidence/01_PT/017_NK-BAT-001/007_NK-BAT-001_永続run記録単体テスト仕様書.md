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

Production encodeをexpected生成に使わない。round-tripだけで成功とせずliteral byteと各fieldを別々にassertする。parserにはfile所有/expected run検証の責務がなく、正規の別runを誤って不正期待値にしない。全line/method/class/branch100%、NullAway/SpotBugs/format、19負canary（017の1＋019の18）/全reactor/35scope・所属一意性を確認する。実行command/環境/commit/結果/coverage/BUG/hashは008とmanifestへ記録。未実行・failed・flaky・skippedは未合格。

PT038は4種の実encode返却byteを`target/maintenance-record-traces/PT-BAT-038-{anchor,activation,completion-0,completion-10}.txt`へ保存する。020 collectorは独立literalと完全一致、4fileの過不足0を確認し、期待値をevidence/input/maintenance-records、実際値をoutput/maintenance-recordsへ別保存する。manifestの各file hashへ追跡する。実際値をcollector側でProductionから再生成しない。019は欠落/余分/改変traceを不合格にする。

| Production method | Test ID |
|---|---|
| MaintenanceRecords.anchor/readAnchor、identity/run/ascii/lines/require/invalid | PT038～041・043～045 |
| MaintenanceRecords.activation/readActivation | PT038～041・043～045 |
| MaintenanceRecords.completion/readCompletion | PT038～045 |
| MaintenanceActivation constructor/run/id/businessDate/toString/value equality | PT038～039・043～045 |
| MaintenanceCompletion constructor/activation/endedAt/outcome/toString/value equality、Outcome constructor/exitCode | PT038～039・042～045 |

PT-BAT-045（BUG-3860／YKT-2997）。8 worker、64合成完了記録、SUCCESS／WARNING 32ずつ、各Future 5秒、終了10秒と手書きASCII期待値を継承。共用Batch補助に一次失敗と抑制例外の保持を委譲する。実保持原本・DB・実行退役は別試験。PG45398で変更した経路だけの再試験を記録する。
