# 173 NK-OPS-001 Cleanup固定request限定実行結果

2026-09-28 JST、PG324/SSC104。Production `CleanupWorkerRequest`とPT-OPS-CREQ001～007。関連RD OPS-009/BAK-001、UI251、SS341/342/343、Program NK-OPS-001/NK-BAT-001。SSC104をcode前に914へ登録済み。

| 試験 | 実測 | 判定 |
|---|---|---|
| CREQ001～007 | 最終限定reactor実行：Storage8＋Bootstrap8＋Batch18＝34PT、Failure/Error/Skipped 0。新Cleanup request7件すべてPASS、SpotBugs 3module各0、NullAway/ErrorProne compile成功 | 限定PASS。全scope/実process完了ではない |
| 変更class coverage | JaCoCo no-clean累積：CleanupWorkerRequest line38/38、method6/6、class1/1、branch36/36。初回branch35/36は末尾非空反例追加後36/36 | 対象class限定4指標未網羅0。正式全scope認定ではない |
| OS/DB/業務 | root request source、systemd Cleanup oneshot、parent M/A handoff、DB lock、backup現物・実DELETE/transfer、Artemis起動未実施 | 未認定 |

実行command：`mvn -B -o -pl :schubert-nk-batch -am -Dtest=ResourceScopeTest,ReleaseApprovalTest,CleanupWorkerRequestTest,MaintenanceUnitStopClientTest test com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`、続いてBatch `org.jacoco:jacoco-maven-plugin:0.8.15:report`。JDK25.0.4、Maven3.9.12、Linux、branch dev-foundation、base HEAD7073052d2＋dirty source/test hash。最終exit0。暫定証跡 `evidence/provisional/PG324-cleanup-request/manifest.json`に日時、source・10 sanitized file hash、coverage、command/exit、関連SSCを記録。Full実行logはGit外に保全し、環境property/classpathやraw session/credentialをGitへ入れない。BUG追加0（TDD初期branch未網羅は実装済み仕様違反ではない）。

残：request codecは権限境界の一部に過ぎない。root親 publisher・LoadCredential/read・子真正context/DB/session lock・同run両backup現物・STEP/Inbox/Log/transfer・0/10/30の実Unit完了を接続しない限りCleanup成功やArtemis依存成立へ算入しない。正式認定source858713c/run PT-WEB-20260925-24/1964PT/53scope/48.3%は不変更。
