# NK-BAT-001 BatchRunRepository資源横展開結果

正式認定: PT-WEB-20260920-02/source21cf373541fc7d0d7e131f79ebc9d67db3c44d41/dev-foundation、2026-09-20 01:27:40～01:43:47 JST/16:06/exit0。全1455 PT・failed/error/skipped0、6 Java全4coverage100%、Production5静的解析未解決0、固定path3method限定review・coverage除外なし、38scope/46負canary成功。PG181/182/183の68/68/272＝408複合・BatchRun2NULL・元反例と既存回帰を認定、PG178以降の905複合は既存Test ID内で新JUnit/部品加算0。Batch95class/579method/3632line/1891branch全missed0。BUG207/YKT163完了、BUG195/206・YKT154/162・SSC063の別境界分類は継続。実NK CHR/親全体/PGPT/IT/ST未完了。実行環境・入力期待実際・source/test/hashは017/evidence/manifest.json、raw log SHA256=6654362af9ac97cc912a388172d1344400157201d7574b0f138a5325562214d4。以下の未認定表記は探索履歴。

PG183/SSC063/BUG195・206/YKT154・162、068・BAT151。選択成功、正式全reactor前。新JUnit/部品加算0。

反例 `/tmp/pgpt-pg183-red.log`: 2026-09-20 01:21:38 JST/10.568秒/exit1。Storage8成功、BAT151 1FAIL（assertAll内2反例）。history provider IAEと同一IllegalState row.next/closeがBatchRepositoryExceptionへ置換。Production0fffc827、test/probeのみ追加。SHA256=`e231190680ca2c9579ef3fb70608e337b6240a58a87e865c516724253cc98e29`。

初回修正 `/tmp/pgpt-pg183-green.log`: 01:24:07 JST/1分00秒/exit0。関連64 PT/static成功、272複合＋元2反例成功。ただしline/method/classは100%でもBatchRun本体branch122/124で、abandon/finishのNULL Statement2分岐が未実行。PGPT合格には未算入。SHA256=`1ac3196c0c8e8507491432c954680afa11e1b5223368e0729c2f123b6f9e285e`。

追加negative後 `/tmp/pgpt-pg183-green2.log`: 01:26:01 JST/56.008秒/exit0。Storage8＋Batch56＝64 PT、failed/error/skipped0。272複合、2 NULL取得境界と元2反例、既存399 JDBC位置/全不正projection/復旧/skip/replay/関連borrowed Serviceを成功。BatchRun本体1class/15method/234line/124branch＋History1class/2method/2line（branchなし）は全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。SQL分類prefix/注入数/取得済close1/未取得0/live0、caller rollback後の独立snapshot完全一致を確認。SHA256=`9ea74b71b47e118094e743536e2893b4385b9f5c8ab712ef9f406d2893616fe0`。

旧provider IAE固定期待の訂正は先行0fffc827/SSC063/BUG206/068の根拠による。不正DB id等の固定診断期待は保全し、SQL id getterはpure constructor検査の外。新coverage除外/静的抑止なし。

環境Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13/dev-foundation。commandは065のtoolchain/offline引数と同じで、選択 `ResourceScopeTest,BatchRunRepositoryTest,BatchStepValuesTest,BackupStepRepositoryTest,BackupCommitServiceTest,CleanupStepRepositoryTest,StepCleanupServiceTest`、goal test/JaCoCo report/SpotBugs check。反例は `ResourceScopeTest,BatchRunRepositoryTest#interruptionAndRuntime`、testのみ。正式source/run/38scope/46負canaryは次に認定する。残契約分類・全PGPT/実NK/IT/STは未完了。
