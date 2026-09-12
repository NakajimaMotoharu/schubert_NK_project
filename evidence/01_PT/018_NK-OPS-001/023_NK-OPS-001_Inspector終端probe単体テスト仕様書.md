# NK-OPS-001 Inspector終端probe単体テスト仕様書

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
| PT-OPS-UNIT-009 | InspectorUnitProbeTest.fixedCommands | 固定show/busctl argvと環境5変数（PATH/LANG/LC_ALL/SYSTEMD_COLORS/TERM）・stderr破棄、任意unit/commandなし。18field読取と空process vector9byteを独立文字列で照合。 |
| PT-OPS-UNIT-010 | InspectorUnitProbeTest.stableTerminalAndReceipt | 初回read→9byte空process→同18field再readの3commandのみquiescent、fresh0/10。旧ID/空/不成立は空、単独PID0だけで成功禁止。 |
| PT-OPS-UNIT-011 | InspectorUnitProbeTest.unstableAndNonempty | 前後18fieldそれぞれの別の妥当値/不正値とprocess非空/余分byte/未知/空を拒否。前段非終端はprocess照会なし。code/ID同じでも全snapshot変化は不成立。 |
| PT-OPS-UNIT-012 | InspectorUnitProbeTest.commandFailures | start/exit非0/IO/NULLProcess/unknownRuntime/Errorと各command位置を注入、固定diagnosticで偽成功しない。 |
| PT-OPS-UNIT-013 | InspectorUnitProbeTest.boundedOutputAndTimeout | show2048/2049・process9/10上限、0read/output欠落、5秒false、実工具のbounded wait/TERM・SIGKILLなし。timeoutを実unit停止証明にしない。 |
| PT-OPS-UNIT-014 | InspectorUnitProbeTest.interruptions | 開始/各command・wait/read/全close/isAlive/destroy/返却境界の割込、flag保持・非成功・byte消去、query子とInspector寿命を区別。 |
| PT-OPS-UNIT-015 | InspectorUnitProbeTest.allResourceFailures | stdout/stdin/stderr取得順・各closeとprimary IO/Runtime/NPE/Error複合、先行所有resource解放・raw suppressed除去、byte所有、同errorを成功へ変換禁止。 |
| PT-OPS-UNIT-016 | InspectorUnitProbeTest.nativeEnvironmentAndConcurrency | 実systemctl/busctlの読取専用toolchain確認、固定env、64独立query/同probe呼出しとpublic合成trace。NK実unit起動/停止はしない。 |

Productionの全public/private method・constructor・native ownership helperを対象とし、line/method/class/branch100%、NullAway/SpotBugs/Spotless成功・negative/例外/境界/NULL/並行を確認する。除外追加や同Productionを使うexpected生成、Failed/flaky/skipped/not-runの合格算入は禁止。PG/PT中の差異は修正前915/共通原因916、設計変更はSSC060/親SSC049に追跡。

## 実行・証跡

421のJava25.0.4/Maven3.9.12/systemd259.5/Ubuntu26.04.1。選択Batch PTと全module clean verify、017/019証跡負canary・018全scope収集を実行する。実source commit/branch、日時、OS/tool、command/exit、全coverage、関連BUG/SSC、独立input/expected/actualとhashを対応する実行結果およびevidence/manifest.jsonへ記録する。工具native defaultを使う観測はread-onlyのみで、実配備ROOT/child起動/DB排他/backup/全親/IT/STは証明しない。raw InvocationID/process名前/secretは保存しない。

SSC060のquiescent/fresh receiptはその観測時の必要情報だけ。start要求の確定性、callback中の全子終端、OS lockを閉じる時点、同run環境/summary・親step結線は別gateとして残す。実装後の境界・fault注入と横展開は025へ記録する。
