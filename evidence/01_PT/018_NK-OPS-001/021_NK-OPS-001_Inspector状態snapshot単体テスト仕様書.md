# NK-OPS-001 Inspector状態snapshot単体テスト仕様書

PG167/SSC060先行81e0e64b。OPS009/UI251/SS311・341 §7.4・343 §6.8。PG166正式10のsource凍結中にSS/PT仕様のみ先行し、未実装・未実行・認定加算0。

## 独立fixture

手書ASCII373bytes、SHA256=2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6。Python hashlibで実装前算出。以下は合成ID/時刻であり実InvocationIDやprocess commandlineではない。末尾LF1つ。process空vectorはASCII `a(sus) 0\n` の9bytes。

```text
Id=schubert-nk-inbox-inspector.service
LoadState=loaded
ActiveState=active
SubState=exited
Job=
MainPID=0
ControlPID=0
InvocationID=123456789abcdef08123456789abcdef
ExecMainCode=1
ExecMainStatus=10
ExecMainStartTimestampMonotonic=1234567
ExecMainExitTimestampMonotonic=2345678
Result=success
Type=oneshot
Restart=no
RemainAfterExit=no
KillMode=control-group
SendSIGKILL=no
```

## Test ID・全観点

| Test ID | class/method | fixture/入力/操作・独立期待値 |
|---|---|---|
| PT-OPS-UNIT-001 | InspectorUnitSnapshotTest.strictGolden | 18field独立373byte literal。quiescent必要条件true、IDは合成UUID、開始1234567/終了2345678、fresh receipt10、同IDは空。値toStringへ含めない。 |
| PT-OPS-UNIT-002 | InspectorUnitSnapshotTest.propertyInventory | 18各fieldの欠落/重複/未知・行数/順序と空行、Id/loaded/oneshot/no/control-group/no固定契約。全順序反転は受理し同snapshot。 |
| PT-OPS-UNIT-003 | InspectorUnitSnapshotTest.byteBoundaries | 0/1/2047/2048/2049、全373位置のNUL/CR/高bit/余分LF/欠落LF、ASCIIとtoken境界。任意変更が別の妥当値なら不正と決め付けず別観測を確認。 |
| PT-OPS-UNIT-004 | InspectorUnitSnapshotTest.scalarBounds | PID/Job uint32±1、code0..6/status0..255、monotonic uint64±1、leading0/符号/空/空白/指数、Invocation空/lower32hex/non-nil/不正を個別検査。 |
| PT-OPS-UNIT-005 | InspectorUnitSnapshotTest.quiescentStates | 3許容state組合せと全job/PID/substate否定、ACTIVEやunknownなど不正形式/非終端は区別し成功禁止。snapshotだけでは全子終端を主張しない。 |
| PT-OPS-UNIT-006 | InspectorUnitSnapshotTest.freshReceipt | 旧ID/新ID/空ID、start0/exit0/逆転/同時刻/max、result/正常code1/0・10のみ、failed/signal/code/255を交差しOptionalInt値を独立期待。 |
| PT-OPS-UNIT-007 | InspectorUnitSnapshotTest.immutabilityAndNull | source byte改変後も不変、同値/別値matches、全API null、redacted診断、returned Optional/UUIDの不変性。 |
| PT-OPS-UNIT-008 | InspectorUnitSnapshotTest.concurrentSnapshots | 64並行parse/receiptで独立ID/0・10/byte所有を確認。shared state/cacheなし。 |

Productionの全public/private method・constructor・native ownership helperを対象とし、line/method/class/branch100%、NullAway/SpotBugs/Spotless成功・negative/例外/境界/NULL/並行を確認する。除外追加や同Productionを使うexpected生成、Failed/flaky/skipped/not-runの合格算入は禁止。PG/PT中の差異は修正前915/共通原因916、設計変更はSSC060/親SSC049に追跡。

## 実行・証跡

421のJava25.0.4/Maven3.9.12/systemd259.5/Ubuntu26.04.1。選択Batch PTと全module clean verify、017/019証跡負canary・018全scope収集を実行する。実source commit/branch、日時、OS/tool、command/exit、全coverage、関連BUG/SSC、独立input/expected/actualとhashを対応する実行結果およびevidence/manifest.jsonへ記録する。工具native defaultを使う観測はread-onlyのみで、実配備ROOT/child起動/DB排他/backup/全親/IT/STは証明しない。raw InvocationID/process名前/secretは保存しない。

SG060のquiescent/fresh receiptはその観測時の必要情報だけ。start要求の確定性、callback中の全子終端、OS lockを閉じる時点、同run環境/summary・親step結線は別gateとして残す。
