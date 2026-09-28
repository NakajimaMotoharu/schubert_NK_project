# 175 NK-OPS-001 Cleanup固定request原本IO限定実行結果

2026-09-28 JST、PG325/SSC104。Production `CleanupWorkerRequestFiles`、PT-OPS-CREQFILE001～008、Program NK-OPS-001/NK-BAT-001、RD OPS-009/BAK-001、UI251、SS341/342/343。

| 対象 | 実測 | 判定 |
|---|---|---|
| CREQFILE001～008＋依存 | Storage8＋Bootstrap8＋Batch34＝50件限定PT F/E/S0。新8件、既存Backup原本8件、Codec7件、停止client11件と依存16件が成功。SpotBugs3module0、NullAway/ErrorProne compile成功 | 限定PASS。全Cleanup/実OS受入ではない |
| 新file adapter coverage | JaCoCo no-clean累積：line116/116、method23/23、class1/1、branch46/46 | 対象class限定4指標未網羅0。正式全scopeではない |
| 実OS/Unit/削除 | fixed `/run` root・systemd private credential、親M/A/DB lock handoff、子oneshot、backup現物/SQL/transfer/Artemis未接続 | 未認定 |

最終限定commandは `mvn -B -o -pl :schubert-nk-batch -am -Dtest=ResourceScopeTest,ReleaseApprovalTest,BackupWorkerRequestFilesTest,CleanupWorkerRequestFilesTest,CleanupWorkerRequestTest,MaintenanceUnitStopClientTest test com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`、続いてBatch `org.jacoco:jacoco-maven-plugin:0.8.15:report`。Linux/JDK25.0.4/Maven3.9.12、branch dev-foundation、base HEAD4a425db62＋dirty PG325 source/test hash、exit0。sanitized JUnit/coverage/SpotBugs・実行日時/command/input/expected/actual/source/artifact hashは`evidence/provisional/PG325-cleanup-request-files/manifest.json`へ一意に対応させる。Full logはGit外。秘密・raw session/InvocationID/credentialは非格納。関連BUG新規0、SSC104継続。

停止条件未達：codecとroot source操作は「相関fileが正しく扱える」までであり、原本が真正か、backup成功か、子がDB advisoryを単独所有したかを示さない。Production親publisher/Unit/child、実消去なしのnegative→成功経路、Artemis実起動・journal、外部API/Web・CHRは別PT。正式858713c/run PT-WEB-20260925-24/1964PT/53scope/中心48.3%を変えない。
