# 169 親固定停止client：限定実行結果

2026-09-28 JST、SSC102/SS341§4–5/343、NK-OPS-001、`MaintenanceUnitStopClient.create/stop/Attempt.awaitClient`。関連RD SYS002/004/OPS009、UI251/253、PT-OPS-MCLIENT001～008/NATIVE031。実装開始前にSSC102を914へ登録済み。これは8 Unit全停止・業務起動の認定ではない。

| Test ID | 独立期待 | 実測 |
|---|---|---|
| MCLIENT001～008 | 固定8完全Unit名・argv、真正root/policy先行、非0/timeout/割込/stdio/unknownで成功を返さず、未終端clientを自動kill/destroyしない。factory/nullと同owner再reap、無害native portを確認 | `PG319-stop-client-GREEN-3`：Storage8＋Bootstrap8＋Batch16＝32PT、F/E/S0。SpotBugs0、NullAway/ErrorProne既定。新classとnestedのline/method/class/branch missed0、独立collector canary105全PASS。初回format gateはBatch未実行、最終実行08:02:31。 |
| NATIVE031 | 隔離VM真正root Morning/M+A中にcold loaded Backupへ固定実stopを発行。client exit0とfresh Unit terminalを別判定。active Caddy PID不変、Morning停止後leaf不在 | Production Batch jar SHA256 `478858b97bafc15082a7bd92893dde7d00acb90dc4dd3fd08fcf5b0ddbc8dd6b`。probe ExecMainStatus0、`PT-OPS-NATIVE-031 PASS`、Backup inactive/PID0、Caddy active PID1090不変、Morning inactive/PID0/leaf不在。原本active/begin/runのSHAと旧current不変、approvalなし。 |
| NATIVE032 | 同じProduction jar、active Caddy PID1090・実効`SendSIGKILL=no`。真正root Morning/M+A中の実固定stop client exit0とfresh Unit/kernel終端を別判定し、Backup不変 | `PT-OPS-NATIVE-032 PASS`、Morning ExecMainStatus0、Caddy inactive/PID0/exact cgroup leaf不存在、Backup inactive、Morning後停止inactive/PID0/leaf不存在。原本3SHA/旧current/approvalなし不変。Native-only coverageは4指標100%ではなく正式採用しない。 |
| MCLIENT009～011 | 停止命令前に固定8 policyを全件検査、元rootを前後17回再検査。1/4/8件目不適合と途中root故障・割込はstop0、割込保持 | `PG323-preflight`：Storage8＋Bootstrap8＋Batch11＝27PT F/E/S0、SpotBugs3module0、NullAway/ErrorProne compile合格。`MaintenanceUnitStopClient` classのline40/40、method7/7、class1/1、branch6/6（no-clean累積・限定）。実Unit全8のpolicy合格は5件not-foundのため未認定。 |
| NATIVE035 | VM真正root Morning/M/A下、Caddy loaded後のWeb not-foundをProduction全件preflightが検出し、stop0・元原本不変 | 新PG323 Batch jar d19632b9…、test-only probe class9c8acd4a…。Morning ExecMainStatus0/`PT-OPS-NATIVE-035 PASS`、本物のWeb `LoadState=not-found`拒否、Caddy/Backup/Artemis inactive/PID0、Morning明示stop後leafなし。原本active/begin934b84…/run d149a…・旧current pgpt-native-301・approvalなし不変。これは全8 policy合格/停止、Cleanup/Artemis起動、R2/R3ではない。 |

実行時刻・OS/JDK/Maven/JaCoCo・branch/基点93d769f61＋dirty source hash・command/exit・sanitized JUnit/coverage/static・Git外exec hashは両manifestに記録する。NATIVE031 native-only coverageと同byte host+nativeの4指標未実行0は区別し、後者はclean無し累積の限定合成であるため451の正式全scope coverageへ加算しない。原本の内容、raw journal/InvocationID、credential/tokenはGitへ保存しない。

未認定：残6実Unit配備/停止・全8終端、Artemis clean journal、M→同原本resume→A→INVALID、trusted approval/initial V023、backup/permit/業務main、実NK CHR-L01。実VMはCaddy/Backupだけloadedで、Web/API/Cleanup/Inspector/Expiry/Artemisの6件は`not-found`。PG319/320の単独成功を親全停止成功へ読み替えない。
