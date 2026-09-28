# 178 NK-OPS-001 Cleanup子release単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。対象は `RootReleaseAdmission.verifyCleanup`/`verifyFor`、および固定CLEANUP actorを作る `RootStartupContext`。関連RD OPS-009/BAK-001、UI251、SS343 §6・341 §3、SSC-104/PG327。Test ID: PT-OPS-ROOTBOM009。既存 ROOTBOM001～008/ROOTCTX001～009を回帰対象とする。

前提・fixture: test-only `RootStartupContextTest.Fixture` の独立したliteral systemd `schubert-nk-cleanup.service`/cgroup/PIDを使用し、既存の承認済みreleaseの固定platform/build値と、独立2行schema vectorを渡す。mock Connectionのquery回数を数え、Productionの期待値生成methodを呼ばない。このfixtureは真正host署名・原本・Native Unit/実DB受入の代用ではない。

| Test ID | 入力・操作 | 独立期待値・根拠 |
|---|---|---|
| ROOTBOM009 | CLEANUP固定snapshotで `verifyCleanup`、同releaseの読取回数、wrong MORNING actor/変造snapshot、null Connection/caller、MORNING専用入口へのCLEANUP入力 | 正しい子actorでfresh release読取1増＋六列schema query1。wrong/nullではschema query0・固定拒否。SS343の子自身再承認、actor一致、親proof流用禁止から算出 |

正常、wrong actor、null、原本読取再実行、schema例外の経路は ROOTBOM001～009/ROOTCTX001～009の組で確認。実行はJDK25.0.4/Maven3.9.12/Linux、Batchと依存の `-Dtest=ResourceScopeTest,ReleaseApprovalTest,RootStartupContextTest,RootReleaseAdmissionTest,MorningDatabaseSessionTest,CleanupDatabaseSessionTest clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。対象commit/command/終了code、JaCoCo line/method/class/branch、static、実行日時、関連BUG/SSC、sanitized XML/hashは179とmanifestで特定する。正式gate・実Unit未認定は別記する。
