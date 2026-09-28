# 177 NK-OPS-001 Cleanup親DB引渡し限定実行結果

2026-09-28 JST、PG326/SSC104、source commit `100b256d0`。Production `RootStartupContext.Service.CLEANUP` と `MorningDatabaseSession.Session.handoffCleanup`、PT-OPS-ROOTCTX009/MDB009～012。RD OPS-009/BAK-001、UI251、SS341/342/343。実行OS Linux、JDK25.0.4、Maven3.9.12、Node24.19.0、JaCoCo0.8.15、SpotBugs4.10.4.0、branch `dev-foundation`。

| 検証 | 実際値 | 判定 |
|---|---|---|
| 変更箇所選択PT | Storage8＋Bootstrap8＋RootContext9＋InspectorHandoff9＋MorningDB12＝46件、F/E/S0。実PostgreSQL別子Connectionのadvisory取得、親再取得・observer不取得を確認 | 限定PASS。子Unit/実Cleanup受入ではない |
| 静的・限定coverage | SpotBugs 3module0、NullAway/ErrorProne compile成功。JaCoCo `MorningDatabaseSession$Session` line48/48、method6/6、class1/1、branch18/18。`RootStartupContext` line67/67、method10/10、class1/1、branch42/42。`Service` enum line9/9、method3/3、class1/1、分岐定義0 | 変更class限定4指標未網羅0。単純な合計/branch0除外で全体100%とはしない |
| security横断全6 | source/test/config固定のProduction6module clean test＋SpotBugs、JaCoCo report：2,274件/336 suite、F/E/S0、静的0。Module別 Protocol80/Storage149/Bootstrap175/API742/Web555/Batch573 | 横断回帰PASS。正式451 gateではない |
| 全6coverage | Protocol/Storageのみ全4指標 missed0。Bootstrap branch37/line11/method4、API branch1/line19/method3、Web branch1/line19/method3、Batch branch0/line42/method19を残す。全module class missed0 | 全Production coverage100%未達、正式認定更新不可 |
| 実OS/Unit/削除 | 固定Cleanup Unit/LoadCredential・親M/A/backup現物/子release/schema・実DELETE/Artemis依存は未接続 | R2/R3未認定 |

失敗試行の扱い：初回選択runはSpotBugs stale-field3件でexit1（BUG-309）を修正前起票、volatile状態＋別thread/再入/二重/driver状態負試験を追加して再実行した。初回全root `clean test spotbugs:check` はProduction外Characterization基盤へdirect pluginを適用し既存11警告で停止したため、全6回帰へ混入・合格算入しない。選択46件の最終commandは `-pl :schubert-nk-batch -am -Dtest=ResourceScopeTest,ReleaseApprovalTest,RootStartupContextTest,MorningDatabaseSessionTest,InspectorLockHandoffTest test com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。横断runはmanifest記載の明示Production6 module `clean test ...:check` と別JaCoCo report、いずれもexit0。BUG-309/YKT-242は対象修正・横展開を完了、SSC-104は真正Cleanup全体未達で対応中。

`evidence/provisional/PG326-six-security/manifest.json`に日時、command、base/source SHA256、module別結果/coverage、外部log SHA256、sanitized JUnit336＋JaCoCo6＋SpotBugs6の348ファイルと各hashを記録。XMLのproperties/system-out/system-errは機械除去し、pattern秘密scan0・352 source/evidence hash一致。全原始logはGit外。対象commit `100b256d0`、manifestは同source byteの後続保存。正式source `858713c0bf310ae8bf62078b0a1cedbce4e968db`/run `PT-WEB-20260925-24`/1964PT/53scope/中心48.3%は不変更。
