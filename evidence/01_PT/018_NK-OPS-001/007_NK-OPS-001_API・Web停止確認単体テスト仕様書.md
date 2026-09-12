# NK-OPS-001 API・Web停止確認単体テスト仕様書

ApplicationStopGate/UnitStateParser/SystemctlStateSource / OPS-009・AVL / UI251 / SS311・341 §7.1・343 / SSC-049・PG-D-148。readonly状態観測の部分PTであり停止実行・親全体・実backup/DB引渡しは未完了。

## 1. Oracleと環境

BUG-157/YKT-122先行f156611a（正式20260912-05のsource凍結解除後に追加実行）: STOP016でProcess null、stdout/stdin/stderr各getterの未知runtimeとnullを独立に注入する。既取得streamは各1回close、未取得は0回、getter失敗は待機/read0回、生存子だけTERM。nullを正常な空streamと扱わずNPE契約違反、未知runtimeは非成功のまま伝播する。全資源取得を直接TWRへ登録する変更だけで、固定argv/5秒/1024byte/診断/順序oracleは不変。PG155のGID005を同種所有の非回帰対象とする。既存16 method内のcase追加で件数水増しなし。

独立literal7field: Id=固定APIまたはWeb、LoadState=loaded、ActiveState=inactive、SubState=dead、Job=空、MainPID=0、ControlPID=0。順序は問わず一意必須。ASCII/末尾LF/最大1024、欠落/重複/未知field・不正byte拒否。実systemd259.5のnot-found/inactiveは合格ではない。Production methodでexpectedを作らず、固定vector・fake Processの呼出/close/TERM・実read-only systemctl outputの構造を照合する。host unitの起動停止や配備をしない。

| Test ID | class.method | 操作・期待 |
|---|---|---|
| PT-OPS-STOP-001 | ApplicationStopGateTest.literalAndOrder | API/Web・順序入替、全7literalで停止確認 |
| PT-OPS-STOP-002 | ApplicationStopGateTest.nonStoppedStates | 各state/not-found/masked/Job/PIDを個別変更、全て後続拒否 |
| PT-OPS-STOP-003 | ApplicationStopGateTest.malformedFields | 重複/欠落/未知/別Id/=不正を拒否 |
| PT-OPS-STOP-004 | ApplicationStopGateTest.byteAndNullContracts | 0/1024/1025byte・各位置NUL/CR/高bit/末尾LF・nullを拒否 |
| PT-OPS-STOP-005 | ApplicationStopGateTest.gateOrderAndFreshReads | 固定API→Web、失敗時後続0、再実行fresh・両方必要 |
| PT-OPS-STOP-006 | ApplicationStopGateTest.interruptAndFailure | 開始/各境界割込保持、source/runtime失敗を正常化しない |
| PT-OPS-STOP-007 | ApplicationStopGateTest.concurrentChecks | 64並行・各呼出独立、cache/共有中間状態なし |
| PT-OPS-STOP-008 | ApplicationStopGateTest.factoryAndContracts | 固定factory/enum/exception/constructor契約、実診断は配備合格としない |
| PT-OPS-STOP-009 | SystemctlStateSourceTest.fixedCommandAndSuccess | 固定argv/2unit・5秒wait・実byte・全stdio close後だけ返却 |
| PT-OPS-STOP-010 | SystemctlStateSourceTest.commandFailure | 起動IO/exit非0、診断/cause/suppressed非露出 |
| PT-OPS-STOP-011 | SystemctlStateSourceTest.timeoutAndTermination | wait falseは失敗・生存照会子へTERM、SIGKILL/service操作なし |
| PT-OPS-STOP-012 | SystemctlStateSourceTest.interruptedWait | InterruptedExceptionを再割込＋失敗、資源回収 |
| PT-OPS-STOP-013 | SystemctlStateSourceTest.outputBoundaries | bounded読取/過長/IO、空はparserで拒否 |
| PT-OPS-STOP-014 | SystemctlStateSourceTest.closeFailures | 各stdio close failure・複合故障は成功にしない |
| PT-OPS-STOP-015 | SystemctlStateSourceTest.nativeEnvironmentAndRead | 実builder環境5値・stderr discard・show実行、7field/Id構造のみ認定 |
| PT-OPS-STOP-016 | SystemctlStateSourceTest.nullAndRuntimeContracts | null依存/unit・想定外runtime、cleanup、例外固定契約 |

## 2. Gate・証跡

Batch53（既存37＋新16予定）、全reactor clean verify・6 Java module line/method/class/branch100%、NullAway/SpotBugs/Spotless。022 OPS scopeと019独立inventory、020 shared Batch Program分離を同期する。Failed/flaky/skipped/not-runは不合格。008へ対象source/run/branch・日時/OS/JDK/tool・command/exit・全結果/coverage・BUG/SSC・manifest/hashを記録する。旧43へ遡って認定しない。
