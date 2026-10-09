# InspectorUnitSnapshot残条件の独立追加試験

Program NK-DAT-001/NK-OPS-001、WBS主担当P004-04（他programへの共通費二重計上0）。class/method InspectorUnitSnapshot.heldCleanup/heldMaintenance/brokerStoppedNormally/inactiveBaseline/backupTerminalAfter/normalRejectedAfter/running。RD DAT-009/OPS-009、UI212/251、SS341§7.4/343/352。開始Production e016/current862、PG908当20native残class22branch/4line/1method。着手前既leaf予算low.5/base1.5/high3.5週次枠pp/LOW、共有費を個別配賦しない。

fixtureは全18key/固定Unit名/oneshot又はsimple/Restart/Remain/zero PID/Job/固定独立inv/Code1/Status0/monotonic100～200の手書き値をASCII LFへencode。expectedはSSの必要条件と独立literal真偽・SUCCESS/FAILED enum、Productionの判定を呼んでexpectedを生成しない。snapshotは観測dataだけでkernel/NSS/source/親/許可/実Unit成功の代替ではない。

| Test ID | 目的・入力 | 独立期待値 |
|---|---|---|
| PT-SNAPSHOT-911001 | 閉鎖8Target/held active-exited、全PID/Job0 | heldCleanupはCleanupのみ、heldMaintenanceはCleanup/Inspector/Expiryのみ |
| PT-SNAPSHOT-911002 | 各owner State/SubState/Job/MainPID/ControlPIDを一件変異、Inspector/Expiry Remainno | 各保持判定false、停止条件の部分一致を受理しない |
| PT-SNAPSHOT-911003 | Artemis Code1/status143/start100/end200、inactive-dead-success又はfailed-failed-exit-code | normal stop data true。PID/Job/INV欠落/Code2/Status0/時刻0逆転/Resulttimeout/異stateはfalse。違うTargetもfalse |
| PT-SNAPSHOT-911004 | inactive-dead/JobPID0、Inspector Remainyes/no、SubState異物/Job1 | exact idleだけtrue。InspectorRemainnoはfalse |
| PT-SNAPSHOT-911005 | Backup新INV Code1/正常0又は正常nonzero70、同INV/partial/JobPID/時刻0逆転/Code2/未知Result | exactSUCCESS又はFAILED。旧同INV・unknown/signal/partialはempty |
| PT-SNAPSHOT-911006 | Cleanup/Expiry正常30新INV、oldsame/時刻0逆転、Artemis active-running Main17/Code0/Status0/start100/end0（SS341 SSC125）、同INV又は別PID/INV | 既知拒否は該当Targetだけtrue、same/partialはfalse。running dataは完備live profileの同PID/INVだけtrue。Code1/end200の終了済みdefaultはfalse |

入力と操作のtest codeはInspectorHeldStateContractTest各method、関連既InspectorUnitSnapshotTest/InspectorUnitCycleTest/InspectorUnitProbeTest/MorningControlScopeTestも選択し回帰する。初回失敗は未実装追加oracleの調整と既実装違反を区別し、後者のみ修正前BUG/YKT登録。null/欠落/未知は既parser試験と新state/partial負例を併用、NPEをcatchして正常扱いしない。並行/再送/所有/IOは実actor判定ではなく明示outstanding PID/Job/旧同INVのデータ境界として扱い、全プログラムの並行試験を代用しない。

実行予定 `python3 -B tools/quality/vm/050_s1/pg911_snapshot_selected.py`、Java25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4/NullAway0.14.1、offline専用m2。Source/Test/工具hashを開始clean HEADへ固定しprivate WorkPG379/pg911-snapshot-selected-v1へXML/coverage/static/JAR/終了codeを保存。主source変更無しと当class byteを857へ独立比較した後だけ、旧当source診断coverageとの比較を許す。selectedを全回帰/正式へ加算せず、必要なfull regression triggerと未実行を別記録。

開始時点=未実行、coverage結果/実source/実count/関連BUG/実行command・OS・branch・hashは実測後追記する。到達不能除外/意味のないassertion/別source成功流用0。残条件がinvariantによる冗長なら独立論証と実装判断を先行し、品質条件は緩和しない。
