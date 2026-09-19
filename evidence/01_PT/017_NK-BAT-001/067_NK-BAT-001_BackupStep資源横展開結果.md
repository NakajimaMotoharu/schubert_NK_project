# NK-BAT-001 BackupStepRepository資源横展開結果

正式認定: PT-WEB-20260920-02/source21cf373541fc7d0d7e131f79ebc9d67db3c44d41/dev-foundation、2026-09-20 01:27:40～01:43:47 JST/16:06/exit0。全1455 PT・failed/error/skipped0、6 Java全4coverage100%、Production5静的解析未解決0、固定path3method限定review・coverage除外なし、38scope/46負canary成功。PG181/182/183の68/68/272＝408複合・BatchRun2NULL・元反例と既存回帰を認定、PG178以降の905複合は既存Test ID内で新JUnit/部品加算0。Batch95class/579method/3632line/1891branch全missed0。BUG207/YKT163完了、BUG195/206・YKT154/162・SSC063の別境界分類は継続。実NK CHR/親全体/PGPT/IT/ST未完了。実行環境・入力期待実際・source/test/hashは017/evidence/manifest.json、raw log SHA256=6654362af9ac97cc912a388172d1344400157201d7574b0f138a5325562214d4。以下の未認定表記は探索履歴。

PG182/SSC063/BUG195/YKT154・162、066・BAT216。選択成功、正式全reactor前。新JUnit/部品加算0。

修正前 `/tmp/pgpt-pg182-red.log` は2026-09-20 01:17:08 JST/9.649秒/exit1。Storage8成功、BAT216 1FAIL。同じIllegalStateExceptionをpair.row.next/closeへ注入し、期待元identityに対し実際Self-suppressionのIllegalArgumentException。source1e5d0441へtest/probeだけ追加、Production未修正。SHA256=`ea813cab8a18d43bced179079a86cc5c70b39366168176cccde25ecdf0558619`。

修正後 `/tmp/pgpt-pg182-green.log` は01:18:36 JST/48.586秒/exit0。Storage8＋Repository8＋CommitService8＝24 PT、BAT216内68複合と元反例、failed/error/skipped0。対象1class/9method/99line/72branch全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。全pair取得済close各1/未取得0/live0、注入数、borrowed Connection不変、caller rollback後RUNNING2行/0countsを確認。SQL-only catchは維持し、provider IAE5型も通過、YKT162直接原因非該当を実証。SHA256=`49b55b2820c6b587243ba166a4caf1107952bb153476587f285f5ec630720b3a`。

Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13、dev-foundation、公開合成fixture。commandは065と同じtoolchain/offline引数で選択を `ResourceScopeTest,BackupStepRepositoryTest,BackupCommitServiceTest` とする。反例は `ResourceScopeTest,BackupStepRepositoryTest#nullAndUnknownFailures`、goalはtestのみ。正式run/source/manifestは次全reactor後に追記する。BatchRun.finish等の残候補、実backup/親全体/IT/STは未完了。
