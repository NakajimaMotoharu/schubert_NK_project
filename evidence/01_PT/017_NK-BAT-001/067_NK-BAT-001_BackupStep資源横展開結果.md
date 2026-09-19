# NK-BAT-001 BackupStepRepository資源横展開結果

PG182/SSC063/BUG195/YKT154・162、066・BAT216。選択成功、正式全reactor前。新JUnit/部品加算0。

修正前 `/tmp/pgpt-pg182-red.log` は2026-09-20 01:17:08 JST/9.649秒/exit1。Storage8成功、BAT216 1FAIL。同じIllegalStateExceptionをpair.row.next/closeへ注入し、期待元identityに対し実際Self-suppressionのIllegalArgumentException。source1e5d0441へtest/probeだけ追加、Production未修正。SHA256=`ea813cab8a18d43bced179079a86cc5c70b39366168176cccde25ecdf0558619`。

修正後 `/tmp/pgpt-pg182-green.log` は01:18:36 JST/48.586秒/exit0。Storage8＋Repository8＋CommitService8＝24 PT、BAT216内68複合と元反例、failed/error/skipped0。対象1class/9method/99line/72branch全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。全pair取得済close各1/未取得0/live0、注入数、borrowed Connection不変、caller rollback後RUNNING2行/0countsを確認。SQL-only catchは維持し、provider IAE5型も通過、YKT162直接原因非該当を実証。SHA256=`49b55b2820c6b587243ba166a4caf1107952bb153476587f285f5ec630720b3a`。

Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13、dev-foundation、公開合成fixture。commandは065と同じtoolchain/offline引数で選択を `ResourceScopeTest,BackupStepRepositoryTest,BackupCommitServiceTest` とする。反例は `ResourceScopeTest,BackupStepRepositoryTest#nullAndUnknownFailures`、goalはtestのみ。正式run/source/manifestは次全reactor後に追記する。BatchRun.finish等の残候補、実backup/親全体/IT/STは未完了。
