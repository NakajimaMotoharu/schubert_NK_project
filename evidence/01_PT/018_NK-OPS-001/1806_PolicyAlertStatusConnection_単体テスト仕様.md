# 閾値→alert保持→status表示の接続PT

NK-OPS-001 / RD171 MON005～013/UI252/SS351§7・12、WBS-P018-09主/C07追加費0。group2035/開始fresh40残60/reset1793382075/1-2-4pp/cap10。Production f817/正常8632全input byte不変、新Main0。元build/4222/旧54/旧renderer6を再演しない。

着手前431のMONPIPE1549～1550・MONSTATUS1558～1559と現二Test sourceを確認。旧engine試験はengine/registry、旧renderer試験はAlertLifecycleから直接fixtureを作るため、engineの全12閾値結果→activeAlerts→renderの接続は未実施。architecture fixtureにも当接続なし。BUG1710/YKT1461の選定前照合を適用する。供給観測だけを用い実poll/provider/DB/MQ/filesystem/Backup/network/VM/停止/通知の操作0。

tools-side PolicyAlertStatusConnectionTest 新4件/1suite、固定fixture AT=2026-10-24T00:00:00Z・BATCH、normal/warning/critical/continuityを同engineに供給する。期待フレームは固定UTC/condition順/整数count/独立literalで手書きし、production formatter/thresholdから算出しない。

| Test ID | 操作 | 独立期待 |
|---|---|---|
| ALERTPIPE001 | 12閾値を逆順入力。filesystem80%5m、transfer3.5GB、async5000、weblog5000、DLQ1調査済非増加、expiry1000、pool80%5m、heap75%10m、p95=2.1s5m、backup当日成功なし、restart1、integrity1 | canonical順12行、先11 WARNING/integrity CRITICAL、count1・AT同一・STANDARD frame全量 |
| ALERTPIPE002 | transfer WARNINGを0/1分に供給、2分から正常、7分直前/到達 | count2/first0/last1分保持、正常5分直前open・到達closed/空status |
| ALERTPIPE003 | transfer critical→正常10分・原因未確認→確認、別DLQ/integrity critical→正常30分＋原因確認 | 未確認critical保持、確認後transferのみclose、調査必須二条件はopenの固定2行 |
| ALERTPIPE004 | warning→正常1分→欠測5分→正常6分、UTC大幅前進/後退・monotonic11分直前/到達 | 欠測で回復期間reset、UTCで短縮0、5分正常の境界でのみ空status |

元8660 JUnit4/1 F-E-S0/実XML/log/exec-session→独立8662で全source/input/deps/tool/XML/実環境/七metadata反例・同session1→1807。実command `env PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg8660_policy_alert_status_host.py`。全hash/開始終端/OS/JDK/branch/期待-実際はmanifestと1807へ。着手時4 UNRUN、failed/skipped/notrunをPASS化0、新coverage/static資格0・旧counter合算0。障害修正前915/916。formal1964-53/原190新受入0/工数null/QA051final/whole451/全actualHOLD不変更。
